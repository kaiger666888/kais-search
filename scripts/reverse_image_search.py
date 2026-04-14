#!/usr/bin/env python3
"""
kais-search 以图搜图：基于 PicImageSearch 库
Usage: python3 reverse_image_search.py <image_url_or_path> [engine] [limit]
Engines: yandex (default), bing, all
"""
import sys, json, os, asyncio
from pathlib import Path

# 自动激活 venv
_VENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
if os.path.exists(_VENV):
    for d in os.listdir(os.path.join(_VENV, "lib")):
        sp = os.path.join(_VENV, "lib", d, "site-packages")
        if os.path.exists(sp):
            sys.path.insert(0, sp)
            break

try:
    from PicImageSearch import Bing, Yandex
except ImportError:
    print(json.dumps({"error": "PicImageSearch not installed. Run: bash scripts/setup.sh"}))
    sys.exit(1)

ENGINES = {"yandex": Yandex, "bing": Bing}


def is_local(path: str) -> bool:
    return not path.startswith(("http://", "https://")) and Path(path).exists()


def parse_results(resp, name: str) -> list[dict]:
    results = []
    if not (resp and resp.raw):
        return results
    for item in resp.raw:
        r = {
            "title": getattr(item, "title", "") or "",
            "url": getattr(item, "url", "") or "",
            "thumbnail": getattr(item, "thumbnail", "") or "",
            "source_engine": name,
        }
        for attr in ("similarity", "size", "source", "content"):
            val = getattr(item, attr, None)
            if val:
                r[attr] = str(val)[:300]
        if r["url"]:
            results.append(r)
    return results


async def search_one(cls, input_path: str, name: str) -> list[dict]:
    try:
        engine = cls()
        if is_local(input_path):
            resp = await engine.search(file=input_path)
        else:
            resp = await engine.search(url=input_path)
        return parse_results(resp, name)
    except Exception as e:
        return [{"error": f"[{name}] {e}", "source_engine": name}]


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: reverse_image_search.py <image_url_or_path> [engine] [limit]"}))
        sys.exit(1)

    input_path = sys.argv[1]
    engine = sys.argv[2] if len(sys.argv) > 2 else "yandex"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    if engine == "all":
        tasks = {n: search_one(cls, input_path, n) for n, cls in ENGINES.items()}
        all_r = {n: (await t)[:limit] for n, t in tasks.items()}
        output = {
            "status": 200, "query": input_path, "is_local": is_local(input_path),
            "engines": {k: {"count": len(v), "results": v} for k, v in all_r.items()},
        }
    elif engine in ENGINES:
        results = await search_one(ENGINES[engine], input_path, engine)
        output = {
            "status": 200, "query": input_path, "is_local": is_local(input_path),
            "engine": engine, "total_found": len(results), "results": results[:limit],
        }
    else:
        output = {"error": f"Unknown engine: {engine}. Available: {', '.join(ENGINES)}, all"}

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
