# -*- coding: utf-8 -*-
"""
通用人物图片下载脚本
用法: python download_images.py "中文名" "English Name"

从 Wikipedia REST API 获取人物头像，
其余图片使用 Unsplash 主题图（作为背景/装饰）。
"""
import sys
import json
import ssl
import urllib.request
import urllib.parse
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent.parent.parent / "cat分身" / "代理" / "person-wiki" / "output" / "images"

# 如果从 person-wiki 目录运行，调整路径
if not OUTPUT_DIR.exists():
    # 尝试相对于脚本位置推断
    OUTPUT_DIR = Path("M:/cat分身/代理/person-wiki/output/images")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {
        "User-Agent": "CatDeskPersonWiki/1.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=20, context=make_ctx()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  GET failed {url[:60]}: {e}")
        return None


def download_image(url, dest_path, label=""):
    req = urllib.request.Request(url, headers={
        "User-Agent": "CatDeskPersonWiki/1.0",
        "Accept": "image/*",
    })
    try:
        with urllib.request.urlopen(req, timeout=30, context=make_ctx()) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            print(f"  OK [{label}] {dest_path.name} ({len(data)} bytes)")
            return True
    except Exception as e:
        print(f"  FAIL [{label}]: {e}")
        return False


def get_wikipedia_photo(name_en):
    """从 Wikipedia REST API 获取人物头像 URL"""
    encoded = urllib.parse.quote(name_en.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    data = get_json(url)
    if data:
        thumb = data.get("thumbnail", {}).get("source", "")
        orig  = data.get("originalimage", {}).get("source", "")
        return thumb, orig
    return "", ""


def get_unsplash_images(query, count=5):
    """从 Unsplash 获取主题图片 URL（无需 API Key 的公开接口）"""
    urls = []
    # Unsplash Source API（已废弃但仍可用）
    for i in range(count):
        # 使用随机种子确保每次获取不同图片
        url = f"https://source.unsplash.com/800x600/?{urllib.parse.quote(query)}&sig={i}"
        urls.append(url)
    return urls


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_images.py <name_zh> [name_en]")
        print("Example: python download_images.py 史蒂夫乔布斯 'Steve Jobs'")
        sys.exit(1)

    name_zh = sys.argv[1]
    name_en = sys.argv[2] if len(sys.argv) > 2 else name_zh
    safe_name = name_zh.replace(" ", "_").replace("·", "")

    print(f"=== Downloading images for: {name_zh} / {name_en} ===")
    print(f"Output dir: {OUTPUT_DIR}")

    # 1. 头像（Wikipedia）
    print("\n[1] Fetching avatar from Wikipedia...")
    thumb_url, orig_url = get_wikipedia_photo(name_en)
    avatar_path = OUTPUT_DIR / f"{safe_name}_avatar.jpg"

    if thumb_url:
        download_image(thumb_url, avatar_path, "Wikipedia thumbnail")
    elif orig_url:
        download_image(orig_url, avatar_path, "Wikipedia original")
    else:
        print("  No Wikipedia photo found, skipping avatar")

    # 2. 主图（Wikipedia 原图，如果比头像大）
    main_path = OUTPUT_DIR / f"{safe_name}_main.jpg"
    if orig_url and orig_url != thumb_url:
        download_image(orig_url, main_path, "Wikipedia original (main)")
    elif thumb_url:
        download_image(thumb_url, main_path, "Wikipedia thumbnail (main)")

    # 3. 主题背景图（Unsplash）
    print(f"\n[2] Fetching thematic images from Unsplash (query: {name_en})...")
    theme_queries = [name_en, f"{name_en} work", f"{name_en} innovation"]
    img_names = ["img1", "img2", "img3"]

    for i, (query, img_name) in enumerate(zip(theme_queries, img_names)):
        dest = OUTPUT_DIR / f"{safe_name}_{img_name}.jpg"
        url = f"https://source.unsplash.com/800x600/?{urllib.parse.quote(query)}&sig={i+10}"
        download_image(url, dest, f"Unsplash: {query}")

    print(f"\nDone! Images saved to: {OUTPUT_DIR}")
    print("Files:")
    for f in OUTPUT_DIR.glob(f"{safe_name}_*.jpg"):
        print(f"  {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
