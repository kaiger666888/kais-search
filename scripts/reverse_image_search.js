#!/usr/bin/env node
/**
 * kais-search 以图搜图 — Playwright (Node.js)
 * 不依赖第三方搜索库，直接通过浏览器自动化访问搜索引擎。
 * Usage: node reverse_image_search.js <image_url> [--engine bing|yandex|google] [--limit N]
 */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);
const input = args[0];
const engineIdx = args.indexOf("--engine");
const limitIdx = args.indexOf("--limit");
const engine = engineIdx >= 0 ? args[engineIdx + 1] : "bing";
const limit = limitIdx >= 0 ? parseInt(args[limitIdx + 1]) : 10;

const isUrl = input?.startsWith("http://") || input?.startsWith("https://");
const isLocal = !isUrl && input && fs.existsSync(input);

if (!input || (!isUrl && !isLocal)) {
  console.log(JSON.stringify({ error: `Usage: reverse_image_search.js <image_url_or_path> [--engine bing|yandex|google|all] [--limit N]` }));
  process.exit(1);
}

async function searchBing(src, isUrl) {
  const results = [];
  const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  try {
    let url;
    if (isUrl) {
      url = `https://www.bing.com/images/search?view=detailv2&iss=sbi&imgurl=${encodeURIComponent(src)}`;
    } else {
      url = "https://www.bing.com/visualsearch";
    }
    await page.goto(url, { timeout: 20000 });
    await page.waitForTimeout(3000);

    if (!isUrl) {
      const upload = await page.$('input[type="file"]');
      if (upload) {
        await upload.setInputFiles(src);
        await page.waitForTimeout(5000);
      }
    }

    // Extract image URLs from iusc elements (Bing's image result containers)
    await page.waitForSelector(".iusc", { timeout: 5000 }).catch(() => {});
    const items = await page.$$(".iusc");
    const seen = new Set();
    for (let i = 0; i < Math.min(items.length, limit * 2); i++) {
      const m = await items[i].getAttribute("m");
      if (m) {
        try {
          const data = JSON.parse(m);
          const url = data.murl || data.purl || "";
          if (url && !seen.has(url)) {
            seen.add(url);
            results.push({
              title: (data.t || "").substring(0, 200),
              url,
              thumbnail: data.turl || "",
              source_engine: "bing"
            });
          }
        } catch {}
      }
      if (results.length >= limit) break;
    }
  } catch (e) {
    results.push({ error: e.message, source_engine: "bing" });
  } finally {
    await browser.close();
  }
  return results;
}

async function searchYandex(src, isUrl) {
  const results = [];
  const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  try {
    let url;
    if (isUrl) {
      url = `https://yandex.com/images/search?rpt=imageview&url=${encodeURIComponent(src)}`;
    } else {
      url = "https://yandex.com/images/";
    }
    await page.goto(url, { timeout: 20000 });
    await page.waitForTimeout(5000);

    if (!isUrl) {
      const upload = await page.$('input[type="file"]');
      if (upload) {
        await upload.setInputFiles(src);
        await page.waitForTimeout(5000);
      }
    }

    const content = await page.content();
    // Yandex: extract from CbirItem elements or general links
    const items = await page.$$(".CbirItem, .CbirSitesPage-item, a.Link");
    if (items.length > 0) {
      for (const item of items) {
        try {
          const href = await item.getAttribute("href");
          if (href && href.startsWith("http") && !href.includes("yandex") && !seen.has(href)) {
            seen.add(href);
            results.push({ url: href, source_engine: "yandex" });
          }
        } catch {}
        if (results.length >= limit) break;
      }
    }
    if (results.length === 0) {
      // Fallback: extract all non-yandex hrefs
      const hrefs = [...content.matchAll(/href="(https?:\/\/[^"]+)"/g)].map(m => m[1]);
      for (const u of hrefs) {
        if (u && !u.includes("yandex") && !seen.has(u)) {
          seen.add(u);
          results.push({ url: u, source_engine: "yandex" });
        }
        if (results.length >= limit) break;
      }
    }
  } catch (e) {
    results.push({ error: e.message, source_engine: "yandex" });
  } finally {
    await browser.close();
  }
  return results;
}

async function searchGoogle(src, isUrl) {
  const results = [];
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--proxy-server=http://127.0.0.1:7890"]
  });
  const page = await browser.newPage();
  try {
    let url;
    if (isUrl) {
      url = `https://lens.google.com/uploadbyurl?url=${encodeURIComponent(src)}`;
    } else {
      url = "https://lens.google.com/";
    }
    await page.goto(url, { timeout: 25000 });
    await page.waitForTimeout(5000);

    const content = await page.content();
    // Google Lens: extract from result elements
    const items = await page.$$(".G19kAf, .yuRUbf, .tF2Cxc a, .NJGmXe a");
    if (items.length > 0) {
      for (const item of items) {
        try {
          const href = await item.getAttribute("href");
          if (href && href.startsWith("http") && !href.includes("google.com") && !seen.has(href)) {
            seen.add(href);
            results.push({ url: href, source_engine: "google" });
          }
        } catch {}
        if (results.length >= limit) break;
      }
    }
    if (results.length === 0) {
      // Fallback
      const hrefs = [...content.matchAll(/href="(https?:\/\/[^"]+)"/g)].map(m => m[1]);
      for (const u of hrefs) {
        if (u && !u.includes("google.com") && !seen.has(u)) {
          seen.add(u);
          results.push({ url: u, source_engine: "google" });
        }
        if (results.length >= limit) break;
      }
    }
  } catch (e) {
    results.push({ error: e.message, source_engine: "google" });
  } finally {
    await browser.close();
  }
  return results;
}

(async () => {
  const engines = { bing: searchBing, yandex: searchYandex, google: searchGoogle };

  if (engine === "all") {
    const all = {};
    for (const [name, fn] of Object.entries(engines)) {
      const r = await fn(input, isUrl);
      all[name] = { count: r.filter(x => !x.error).length, results: r };
    }
    console.log(JSON.stringify({
      status: 200, query: input, is_url: isUrl, is_local: isLocal, engines: all
    }, null, 2));
  } else {
    const fn = engines[engine];
    if (!fn) {
      console.log(JSON.stringify({ error: `Unknown engine: ${engine}` }));
      process.exit(1);
    }
    const results = await fn(input, isUrl);
    console.log(JSON.stringify({
      status: 200, query: input, is_url: isUrl, is_local: isLocal,
      engine, total_found: results.filter(x => !x.error).length, results: results.slice(0, limit)
    }, null, 2));
  }
})();
