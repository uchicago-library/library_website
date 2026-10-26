// lwv browse <url> [--shot FILE] [--aria FILE] [--html FILE] [--login] [--wait SEL]
//
// Load one page in Chromium (headless by default) and print JSON: final URL, status, title,
// and artifact paths. Relative paths land in the run's artifacts directory.
// A "loop:" URL is the intranet. --login signs in on that host first.
import { writeFileSync } from "node:fs";
import { adminLogin, artifact, fullShot, launch, step, url } from "./lwv.mjs";

const args = process.argv.slice(2);
const target = args.shift();
if (!target) {
  console.error("usage: lwv browse <url> [--shot F] [--aria F] [--html F] [--login] [--wait SEL]");
  process.exit(2);
}
// --login is a flag. Every other option takes the following argument.
const opts = {};
while (args.length) {
  const flag = args.shift();
  if (flag === "--login") opts.login = true;
  else opts[flag.replace(/^--/, "")] = args.shift();
}

// Sign in on the target host, open the page, optionally wait, then capture.
const { browser, page } = await launch();
try {
  if (opts.login) await adminLogin(page, { loop: target.startsWith("loop:") });
  const resp = await page.goto(url(target), { waitUntil: "networkidle" });
  if (opts.wait) await page.locator(opts.wait).first().waitFor();
  const result = { url: page.url(), status: resp?.status(), title: await page.title() };
  if (opts.shot) {
    result.shot = artifact(opts.shot);
    await fullShot(page, result.shot);
  }
  if (opts.aria) {
    result.aria = artifact(opts.aria);
    writeFileSync(result.aria, `# ${page.url()}\n${await page.locator("body").ariaSnapshot()}\n`);
  }
  if (opts.html) {
    result.html = artifact(opts.html);
    writeFileSync(result.html, await page.content());
  }
  console.log(JSON.stringify(result, null, 2));
  // Keep a walkthrough window open until the viewer is done with the page.
  if (process.env.LWV_WALKTHROUGH) await step(page, `Loaded ${result.url}. Next: close the browser.`);
} finally {
  await browser.close();
}
