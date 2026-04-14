#!/usr/bin/env python3
"""
kais-search 文字搜图：多引擎搜索 + 意图识别 + 质量过滤 + 置信度分级
Usage: python3 text_image_search.py <query> [--count N] [--intent meme|official|portrait|wallpaper|avatar]
"""
import re, json, sys, os, argparse
from urllib.parse import quote_plus
from pathlib import Path

# ── 意图识别 ──
INTENT_PATTERNS = [
    ("meme", ["meme", "表情包", "梗图", "reaction image", "funny image"]),
    ("official", ["official", "官方", "logo", "标志", "emblem", "mascot", "吉祥物", "brand"]),
    ("avatar", ["avatar", "头像", "profile picture", "icon", "图标"]),
    ("wallpaper", ["wallpaper", "壁纸", "4k", "hd", "高清", "background", "背景"]),
]

def detect_intent(query: str) -> str:
    ql = query.lower()
    for intent, kws in INTENT_PATTERNS:
        for kw in kws:
            if kw in ql:
                return intent
    return "portrait"

def parse_count(text: str) -> int:
    m = re.search(r"\b([1-5])\s*(?:张|图片|images?|pics?)\b", text, re.I)
    return max(1, min(5, int(m.group(1)))) if m else 3

def clean_query(raw: str) -> str:
    q = raw
    for _, kws in INTENT_PATTERNS:
        for kw in kws:
            q = re.sub(re.escape(kw), " ", q, flags=re.I)
    q = re.sub(r"\b\d+\s*(?:张|图片|images?|pics?)\b", " ", q, flags=re.I)
    q = re.sub(r"\b(hd|4k|高清|ultra)\b", " ", q, flags=re.I)
    return re.sub(r"\s+", " ", q).strip() or raw

# ── 搜索引擎 ──
def search_bing_images(query: str) -> list[dict]:
    """必应图片搜索（直连，首选）"""
    url = f"https://cn.bing.com/images/search?q={quote_plus(query)}"
    from urllib.request import urlopen, Request
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    })
    try:
        html = urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [{"error": str(e), "engine": "bing"}]

    results = []
    # 提取图片 URL
    patterns = [
        r'murl&quot;:&quot;(https?://[^&]+)&quot;',
        r'"murl":"(https?://[^"]+)"',
        r'src="(https?://[^"]+\.(?:jpg|jpeg|png|webp|gif)[^"]*)"',
    ]
    for pat in patterns:
        for m in re.findall(pat, html):
            if m not in [r.get("url") for r in results]:
                results.append({"url": m, "engine": "bing", "source": "bing"})
                if len(results) >= 10:
                    break
        if len(results) >= 10:
            break
    return results

def search_sogou_images(query: str) -> list[dict]:
    """搜狗图片搜索（直连，补充）"""
    url = f"https://pic.sogou.com/pics?query={quote_plus(query)}"
    from urllib.request import urlopen, Request
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    })
    try:
        html = urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [{"error": str(e), "engine": "sogou"}]

    results = []
    patterns = [
        r'"pic_url":"(https?://[^"]+)"',
        r'img_url="(https?://[^"]+\.(?:jpg|jpeg|png|webp|gif)[^"]*)"',
    ]
    for pat in patterns:
        for m in re.findall(pat, html):
            clean = m.replace("\\", "")
            if clean not in [r.get("url") for r in results]:
                results.append({"url": clean, "engine": "sogou", "source": "sogou"})
                if len(results) >= 10:
                    break
        if len(results) >= 10:
            break
    return results

# ── 质量过滤 ──
def url_quality(url: str) -> tuple[bool, int, str]:
    """返回 (accept, score_delta, reason)"""
    low = url.lower()
    if any(x in low for x in ["logo", "sprite", "icon", "common_ued", "blank"]):
        return False, -20, "site-asset"
    if "thumb" in low or "thumbnail" in low:
        return True, -3, "thumbnail"
    return True, 0, "ok"

def rank_results(results: list[dict], intent: str) -> list[dict]:
    """按意图相关性排序"""
    scored = []
    for r in results:
        if "error" in r:
            continue
        accept, delta, reason = url_quality(r.get("url", ""))
        if not accept:
            continue
        score = 10 + delta
        # wallpaper 偏好大图 URL
        if intent == "wallpaper" and any(x in r.get("url","").lower() for x in ["wallpaper","hd","4k","1920","2560"]):
            score += 3
        # meme 偏好社交媒体
        if intent == "meme" and any(x in r.get("url","").lower() for x in ["meme","funny","reddit","imgur"]):
            score += 2
        r["score"] = score
        r["quality"] = reason
        scored.append(r)
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored

def compute_confidence(results: list[dict]) -> str:
    if len(results) >= 3 and results[0].get("score", 0) >= 10:
        return "high"
    elif len(results) >= 1:
        return "medium"
    return "low"

def download_image(url: str, save_dir: str) -> str | None:
    """下载图片到本地，返回路径"""
    try:
        from urllib.request import urlopen, Request
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        data = urlopen(req, timeout=15).read()
        if len(data) < 12 * 1024:  # < 12KB 太小
            return None
        ext = ".jpg"
        ct = None
        try:
            ct = urlopen(req).headers.get("Content-Type", "")
        except:
            pass
        if ct and "png" in ct:
            ext = ".png"
        elif ct and "gif" in ct:
            ext = ".gif"
        elif ct and "webp" in ct:
            ext = ".webp"
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        path = os.path.join(save_dir, f"img_{os.getpid()}_{id(url) % 100000}{ext}")
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception:
        return None

# ── 主流程 ──
def main():
    parser = argparse.ArgumentParser(description="kais-search 文字搜图")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--count", type=int, default=3, help="返回图片数量 (1-5)")
    parser.add_argument("--intent", choices=["meme","official","portrait","wallpaper","avatar"], default=None)
    parser.add_argument("--download", action="store_true", help="下载最佳图片")
    parser.add_argument("--save-dir", default="/tmp/kais-search-images", help="下载目录")
    args = parser.parse_args()

    intent = args.intent or detect_intent(args.query)
    core = clean_query(args.query)
    count = args.count

    # 搜索
    all_results = []
    for fn in [search_bing_images, search_sogou_images]:
        try:
            r = fn(core)
            if isinstance(r, list):
                all_results.extend(r)
        except:
            pass

    # 去重
    seen = set()
    unique = []
    for r in all_results:
        if "error" in r:
            continue
        u = r.get("url", "")
        if u and u not in seen:
            seen.add(u)
            unique.append(r)

    # 排序 + 质量过滤
    ranked = rank_results(unique, intent)
    top = ranked[:count]
    confidence = compute_confidence(top)

    # 下载最佳图片
    downloaded = None
    if args.download and confidence in ("high", "medium") and top:
        downloaded = download_image(top[0]["url"], args.save_dir)

    output = {
        "status": "ok",
        "query": args.query,
        "core_query": core,
        "intent": intent,
        "confidence": confidence,
        "total_found": len(unique),
        "results": [
            {"url": r["url"], "engine": r["engine"], "score": r["score"], "quality": r["quality"]}
            for r in top
        ],
        "search_urls": {
            "bing": f"https://cn.bing.com/images/search?q={quote_plus(core)}",
            "sogou": f"https://pic.sogou.com/pics?query={quote_plus(core)}",
        },
    }
    if downloaded:
        output["downloaded_path"] = downloaded

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
