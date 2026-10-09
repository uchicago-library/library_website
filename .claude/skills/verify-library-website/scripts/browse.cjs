#!/usr/bin/env node
// Drive the verification stack in headless Chrome. Run it through
// `verify-site.sh browse`, which sets NODE_PATH and the VERIFY_* variables.
//
// Usage: verify-site.sh browse [--site public|loop] [--out NAME] [--user NAME]
//                              [--fresh] STEP...
//
// Steps run in order. Each one appends a line to <evidence>/<out>/actions.log.
// --fresh starts without saved cookies and, on exit, replaces only the chosen
// site's cookies in the saved state.
//
//   goto PATH          Open PATH on the chosen site (or a full URL).
//   login              Sign in through /admin/login/ as --user, then return to
//                      the page that was open.
//   click ROLE NAME    Click the element with ARIA role ROLE and name NAME.
//   fill LABEL VALUE   Type VALUE into the field whose label, accessible name,
//                      or placeholder is LABEL.
//   press KEY          Press KEY (for example Enter) in the focused element.
//   expect TEXT        Fail unless TEXT is visible on the page.
//   expect-url TEXT    Fail unless the current URL contains TEXT.
//   shot NAME          Save a full-page screenshot as NAME.png.
//   aria NAME          Save the ARIA snapshot of <body> as NAME.aria.yml.
//   html NAME          Save the page HTML as NAME.html.

const fs = require('fs')
const path = require('path')
const { chromium } = require('playwright-core')

const ARITY = {
  goto: 1,
  login: 0,
  click: 2,
  fill: 2,
  press: 1,
  expect: 1,
  'expect-url': 1,
  shot: 1,
  aria: 1,
  html: 1,
}
const HOSTS = { public: 'wwwdev', loop: 'loopdev' }
const NO_PERMISSION = 'https://www.lib.uchicago.edu/no-permission/'

function parseArgs(argv) {
  const opts = {
    site: 'public',
    out: 'browse',
    user: 'darthvader',
    fresh: false,
  }
  const steps = []
  for (let i = 0; i < argv.length;) {
    const arg = argv[i]
    if (arg === '--fresh') {
      opts.fresh = true
      i += 1
    } else if (['--site', '--out', '--user'].includes(arg)) {
      opts[arg.slice(2)] = argv[i + 1]
      i += 2
    } else if (arg in ARITY) {
      const args = argv.slice(i + 1, i + 1 + ARITY[arg])
      if (args.length !== ARITY[arg]) {
        throw new Error(`step ${arg} needs ${ARITY[arg]} argument(s)`)
      }
      steps.push({ verb: arg, args })
      i += 1 + ARITY[arg]
    } else {
      throw new Error(`unknown step or option: ${arg}`)
    }
  }
  if (!(opts.site in HOSTS)) throw new Error(`unknown site: ${opts.site}`)
  if (steps.length === 0) throw new Error('no steps given')
  return { opts, steps }
}

async function main() {
  const { opts, steps } = parseArgs(process.argv.slice(2))
  const port = process.env.VERIFY_HTTP_PORT
  const stateDir = process.env.VERIFY_STATE_DIR
  const outDir = path.join(process.env.VERIFY_EVIDENCE_DIR, opts.out)
  const storage = path.join(stateDir, 'browser-storage.json')
  const password = fs
    .readFileSync(path.join(stateDir, 'password'), 'utf8')
    .trim()
  const base = `http://${HOSTS[opts.site]}:${port}`
  fs.mkdirSync(outDir, { recursive: true })
  const logFile = path.join(outDir, 'actions.log')

  const browser = await chromium.launch({
    executablePath: process.env.VERIFY_CHROME || undefined,
    headless: true,
    args: ['--host-resolver-rules=MAP wwwdev 127.0.0.1, MAP loopdev 127.0.0.1'],
  })
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    storageState: !opts.fresh && fs.existsSync(storage) ? storage : undefined,
  })
  // Templates load some third-party scripts with protocol-relative URLs,
  // which become plain HTTP on the local http:// site. Production serves
  // HTTPS, so fetch them over HTTPS here too. Some networks block outbound
  // port 80, and a blocked script stalls the page.
  await context.route(
    url =>
      url.protocol === 'http:' && !Object.values(HOSTS).includes(url.hostname),
    async route => {
      const secure = route
        .request()
        .url()
        .replace(/^http:/, 'https:')
      try {
        await route.fulfill({
          response: await route.fetch({ url: secure, timeout: 15000 }),
        })
      } catch {
        await route.abort()
      }
    },
  )
  const page = await context.newPage()
  let status = '-'
  let deniedByLoop = false
  page.on('response', response => {
    if (
      response.request().isNavigationRequest() &&
      response.frame() === page.mainFrame()
    ) {
      status = response.status()
    }
  })
  page.on('request', request => {
    if (
      request.isNavigationRequest() &&
      request.url().startsWith(NO_PERMISSION)
    ) {
      deniedByLoop = true
    }
  })
  // The local path that login returns to.
  let lastLocalPath = '/admin/'

  const log = async step => {
    const line = [
      new Date().toISOString(),
      `site=${opts.site}`,
      `user=${opts.user}`,
      `step=${step}`,
      `status=${status}`,
      `url=${page.url()}`,
      `title=${JSON.stringify(await page.title().catch(() => ''))}`,
    ].join(' ')
    fs.appendFileSync(logFile, `${line}\n`)
    console.log(line)
  }
  // Some pages pull third-party scripts that never finish loading offline.
  // Wait a while for the load event, then carry on with the parsed DOM.
  const loaded = () =>
    page.waitForLoadState('load', { timeout: 15000 }).catch(() => {})
  // Run an action, then wait for the page load it triggers, if any.
  const settle = async action => {
    const navigated = page
      .waitForEvent('framenavigated', {
        predicate: frame => frame === page.mainFrame(),
        timeout: 3000,
      })
      .catch(() => null)
    await action()
    if (await navigated) {
      await page.waitForLoadState('domcontentloaded', { timeout: 120000 })
      await loaded()
    }
  }
  const resolve = target => (/^https?:/.test(target) ? target : base + target)
  const file = (name, ext) => path.join(outDir, `${name}${ext}`)

  const run = {
    goto: async target => {
      const url = resolve(target)
      if (url.startsWith(base)) {
        lastLocalPath = url.slice(base.length) || '/'
      }
      deniedByLoop = false
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 })
      await loaded()
      if (deniedByLoop) {
        console.error(
          'Redirected to the live no-permission page: this browser session is not logged in to local Loop, or the user is not in the Library group. Add the login step.',
        )
      } else if (!page.url().startsWith(base)) {
        console.error(`Left the local site: now at ${page.url()}`)
      }
    },
    login: async () => {
      const next = lastLocalPath
      await page.goto(`${base}/admin/login/?next=${encodeURIComponent(next)}`, {
        waitUntil: 'load',
      })
      await page.locator('input[name="username"]').fill(opts.user)
      await page.locator('input[name="password"]').fill(password)
      await Promise.all([
        page.waitForURL(url => !url.pathname.startsWith('/admin/login/'), {
          timeout: 60000,
        }),
        page.locator('form button[type="submit"]').first().click(),
      ])
    },
    click: async (role, name) => {
      await settle(() => page.getByRole(role, { name }).first().click())
    },
    fill: async (label, value) => {
      // Try exact matches before substring matches, and skip anything that
      // is not editable (a label can also name a section or a button).
      const candidates = [true, false].flatMap(exact => [
        page.getByRole('textbox', { name: label, exact }),
        page.getByRole('searchbox', { name: label, exact }),
        page.getByLabel(label, { exact }),
        page.getByPlaceholder(label, { exact }),
      ])
      const deadline = Date.now() + 30000
      while (Date.now() < deadline) {
        for (const candidate of candidates) {
          const field = candidate.first()
          if (
            (await field.count()) &&
            (await field.isEditable().catch(() => false))
          ) {
            await field.fill(value)
            return
          }
        }
        await page.waitForTimeout(500)
      }
      throw new Error(`no editable field named ${label}`)
    },
    press: async key => {
      await settle(() => page.keyboard.press(key))
    },
    expect: async text => {
      await page
        .getByText(text)
        .first()
        .waitFor({ state: 'visible', timeout: 30000 })
    },
    'expect-url': async text => {
      if (!page.url().includes(text)) {
        throw new Error(`URL ${page.url()} does not contain ${text}`)
      }
    },
    shot: async name => {
      await page.screenshot({ path: file(name, '.png'), fullPage: true })
    },
    aria: async name => {
      fs.writeFileSync(
        file(name, '.aria.yml'),
        await page.locator('body').ariaSnapshot(),
      )
    },
    html: async name => {
      fs.writeFileSync(file(name, '.html'), await page.content())
    },
  }

  let failed = false
  for (const [index, { verb, args }] of steps.entries()) {
    const label = [verb, ...args.map(a => JSON.stringify(a))].join(' ')
    try {
      await run[verb](...args)
      await log(label)
    } catch (error) {
      failed = true
      await log(`${label} FAILED: ${error.message.split('\n')[0]}`)
      await page
        .screenshot({
          path: file(`FAILED-step${index + 1}`, '.png'),
          fullPage: true,
        })
        .catch(() => {})
      break
    }
  }

  // Replace only this site's cookies in the saved state, so a --fresh run on
  // one site keeps the other site's login.
  const saved = fs.existsSync(storage)
    ? JSON.parse(fs.readFileSync(storage, 'utf8'))
    : { cookies: [], origins: [] }
  const current = await context.storageState()
  const host = HOSTS[opts.site]
  const replaced = cookie =>
    cookie.domain === host ||
    current.cookies.some(
      c =>
        c.name === cookie.name &&
        c.domain === cookie.domain &&
        c.path === cookie.path,
    )
  fs.writeFileSync(
    storage,
    JSON.stringify({
      cookies: [...saved.cookies.filter(c => !replaced(c)), ...current.cookies],
      origins: [
        ...saved.origins.filter(
          o => !current.origins.some(n => n.origin === o.origin),
        ),
        ...current.origins,
      ],
    }),
  )
  await browser.close()
  process.exit(failed ? 1 : 0)
}

main().catch(error => {
  console.error(error.message)
  process.exit(2)
})
