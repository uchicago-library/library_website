// lwv browse <url> [--shot FILE] [--aria FILE] [--html FILE] [--login] [--wait SEL]
import { writeFileSync } from "node:fs";
import { adminLogin, artifact, fullShot, launch, url } from "./lwv.mjs";

const args = process.argv.slice(2);
const target = args.shift();
if (!target) {
  console.error("usage: lwv browse <url> [--shot F] [--aria F] [--html F] [--login] [--wait SEL]");
  process.exit(2);
}
const opts = {};
while (args.length) {
  const flag = args.shift();
  if (flag === "--login") opts.login = true;
  else opts[flag.replace(/^--/, "")] = args.shift();
}

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
} finally {
  await browser.close();
}
