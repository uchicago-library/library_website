// Edit a page title in the Wagtail admin, publish it, and check the public page.
// Usage: lwv node "$LWV_LIB/flows/admin-edit-publish.mjs" <page-id> <public-path> <new-title>
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";

const { adminLogin, artifact, capture, env, launch, url } = await import(
  process.env.LWV_LIB + "/lwv.mjs"
);

const [pageId, publicPath, newTitle] = process.argv.slice(2);
if (!pageId || !publicPath || !newTitle) {
  console.error("usage: admin-edit-publish.mjs <page-id> <public-path> <new-title>");
  process.exit(2);
}
const dir = `admin-edit-publish/${pageId}`;
const report = { run: env.run, pageId, publicPath, newTitle };

async function anonymousView(label) {
  const { browser, page } = await launch();
  const resp = await page.goto(url(publicPath), { waitUntil: "networkidle" });
  const h1 = (await page.getByRole("heading", { level: 1 }).first().textContent()).trim();
  report[label] = { status: resp.status(), h1, cache: resp.headers()["x-wagtail-cache"] ?? null };
  await capture(page, `${dir}/${label}`);
  await browser.close();
}

await anonymousView("public-before");

const { browser, page } = await launch();
try {
  await adminLogin(page);
  await page.goto(url(`/admin/pages/${pageId}/edit/`));
  report.oldTitle = await page.locator("#id_title").inputValue();
  await page.locator("#id_title").fill(newTitle);
  await capture(page, `${dir}/admin-edited`, { aria: false });
  await page.getByRole("button", { name: "More actions" }).click();
  await page.getByRole("button", { name: "Publish" }).click();
  const msg = page.locator(".messages .success, [role=status]").filter({ hasText: "published" });
  await msg.first().waitFor();
  report.adminMessage = (await msg.first().textContent()).trim().replace(/\s+/g, " ");
  await capture(page, `${dir}/admin-published`);
} finally {
  await browser.close();
}

// Anonymous responses come from wagtail-cache; publishing does not purge it.
await anonymousView("public-after");
report.staleAfterPublish = report["public-after"].h1 !== newTitle;
execFileSync(process.env.LWV_BIN, ["manage", "clear_wagtail_cache"], { stdio: "inherit" });
await anonymousView("public-after-clear");

report.pass = report["public-after-clear"].h1 === newTitle;
writeFileSync(artifact(`${dir}/report.json`), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
process.exit(report.pass ? 0 : 1);
