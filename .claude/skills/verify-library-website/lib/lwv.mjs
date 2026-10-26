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

// LWV_WALKTHROUGH shows the browser, slows actions down and makes step() wait
// for Next. LWV_HEADED only shows the browser.
const walkthrough = Boolean(process.env.LWV_WALKTHROUGH);
const headed = walkthrough || Boolean(process.env.LWV_HEADED);

// Chromium at 1366x900, headless unless LWV_HEADED or LWV_WALKTHROUGH is set.
// Page errors are printed and do not fail the script.
export async function launch({ width = 1366, height = 900 } = {}) {
  if (headed && process.platform === "linux" && !process.env.DISPLAY && !process.env.WAYLAND_DISPLAY) {
    throw new Error("LWV_HEADED/LWV_WALKTHROUGH needs a display (DISPLAY or WAYLAND_DISPLAY); run headless instead");
  }
  const browser = await chromium.launch({ headless: !headed, slowMo: walkthrough ? 250 : 0 });
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

// Full-page PNG and an ARIA snapshot of <body>, under the artifacts directory.
// Pass { aria: false } or { shot: false } to skip one of them.
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

// Walkthrough controls live in their own window (a separate browser context),
// so the page under test and its captures are never modified.
const CONTROL_HTML = `<!doctype html><title>lwv walkthrough</title>
<style>
  body { font: 16px system-ui, sans-serif; margin: 16px; }
  #n { color: #555; font-size: 13px; }
  #t { margin: 8px 0 16px; white-space: pre-wrap; }
  button { font-size: 16px; padding: 6px 20px; }
</style>
<div id="n"></div><div id="t"></div><button id="next" disabled>Next</button>
<script>
  const next = document.getElementById("next");
  next.onclick = () => { next.disabled = true; next.textContent = "Running..."; window.lwvNext = true; };
</script>`;
const controls = new WeakMap();
let stepCount = 0;

// One control window per browser, opened on the first step().
async function controlPage(page) {
  const browser = page.context().browser();
  let control = controls.get(browser);
  if (control && !control.isClosed()) return control;
  control = await (await browser.newContext({ viewport: null })).newPage();
  await control.setContent(CONTROL_HTML);
  await placeControl(control);
  controls.set(browser, control);
  return control;
}

// Move the control window to the top-right of the screen, clear of the page.
// Some window managers ignore this; the window then stays where it opened.
async function placeControl(control) {
  try {
    const cdp = await control.context().newCDPSession(control);
    const { windowId } = await cdp.send("Browser.getWindowForTarget");
    const s = await control.evaluate(() => ({
      left: screen.availLeft ?? 0,
      top: screen.availTop ?? 0,
      width: screen.availWidth,
    }));
    const bounds = { left: s.left + s.width - 520, top: s.top, width: 520, height: 280 };
    await cdp.send("Browser.setWindowBounds", { windowId, bounds });
  } catch {
    // Placement is cosmetic.
  }
}

// A point where a walkthrough viewer stops. Describe what is on screen and
// what Next will do. Always prints {"step": n, "text": ...}; with
// LWV_WALKTHROUGH it also shows the text in the control window and waits,
// with no timeout, until Next is clicked.
export async function step(page, text) {
  stepCount += 1;
  console.log(JSON.stringify({ step: stepCount, text }));
  if (!walkthrough) return;
  const control = await controlPage(page);
  await control.evaluate(
    ([n, text]) => {
      document.getElementById("n").textContent = `Step ${n}`;
      document.getElementById("t").textContent = text;
      const next = document.getElementById("next");
      next.textContent = "Next";
      next.disabled = false;
      window.lwvNext = false;
    },
    [stepCount, text],
  );
  await control.waitForFunction(() => window.lwvNext, null, { timeout: 0 });
}
