// Shared Playwright helpers for verification scripts. Run scripts through
// `lwv node <script.mjs>` so the LWV_* environment and NODE_PATH are set.
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, isAbsolute, join } from "node:path";

const require = createRequire(join(process.env.NODE_PATH, "noop.js"));
const { chromium } = require("playwright");

export const env = {
  run: process.env.LWV_RUN,
  publicUrl: process.env.LWV_PUBLIC_URL,
  loopUrl: process.env.LWV_LOOP_URL,
  adminUser: process.env.LWV_ADMIN_USER,
  adminPass: process.env.LWV_ADMIN_PASS,
  artifacts: process.env.LWV_ARTIFACTS,
};

// "loop:/path" -> intranet, "/path" -> public site, absolute URLs unchanged.
export function url(target) {
  if (/^https?:\/\//.test(target)) return target;
  if (target.startsWith("loop:")) return env.loopUrl + target.slice(5);
  return env.publicUrl + target;
}

// Relative artifact paths land in the run's artifacts directory.
export function artifact(path) {
  const full = isAbsolute(path) ? path : join(env.artifacts, path);
  mkdirSync(dirname(full), { recursive: true });
  return full;
}

export async function launch({ width = 1366, height = 900 } = {}) {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  page.on("pageerror", (err) => console.error(`[pageerror] ${err.message}`));
  return { browser, context, page };
}

// Sign in through the real Wagtail admin login form. Sessions are per host,
// so pass { loop: true } before visiting intranet pages.
export async function adminLogin(page, { loop = false } = {}) {
  await page.goto(url(loop ? "loop:/admin/login/" : "/admin/login/"));
  await page.locator("#id_username").fill(env.adminUser);
  await page.locator("#id_password").fill(env.adminPass);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL((u) => !u.pathname.startsWith("/admin/login"));
}

// Public pages scroll <body>, not the document, so Playwright's fullPage
// option leaves everything below the first viewport blank. Grow the viewport
// to the content height instead.
export async function fullShot(page, path) {
  const vp = page.viewportSize();
  const height = await page.evaluate(() =>
    Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
  );
  await page.setViewportSize({ width: vp.width, height: Math.min(height, 16000) });
  await page.screenshot({ path });
  await page.setViewportSize(vp);
}

export async function capture(page, name, { aria = true, shot = true } = {}) {
  const out = {};
  if (shot) {
    out.shot = artifact(`${name}.png`);
    await fullShot(page, out.shot);
  }
  if (aria) {
    out.aria = artifact(`${name}.aria.txt`);
    const snap = await page.locator("body").ariaSnapshot();
    writeFileSync(out.aria, `# ${page.url()}\n${snap}\n`);
  }
  console.log(JSON.stringify({ capture: name, url: page.url(), ...out }));
  return out;
}
