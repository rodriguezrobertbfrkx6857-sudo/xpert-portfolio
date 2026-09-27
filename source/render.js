const fs = require("fs");
const path = require("path");
const { chromium } = require("D:/github项目库/Xpert-Portfolio/extracted/local/02-qa-sentinel/node_modules/playwright");

const root = path.resolve(__dirname, "..");
const source = path.join(__dirname, "index.html");
const outputDir = path.join(root, "output", "pdf");
const outputName = process.argv[2] || "Xpert_Portfolio_V2.pdf";
const outputPdf = path.join(outputDir, outputName);

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 1 });
  await page.goto(`file:///${source.replace(/\\/g, "/")}`, { waitUntil: "load" });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.pdf({
    path: outputPdf,
    format: "A4",
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: false,
    margin: { top: "0mm", right: "0mm", bottom: "0mm", left: "0mm" },
  });
  await browser.close();
  console.log(outputPdf);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
