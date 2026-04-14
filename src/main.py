"""
人物专题学习工具 - 主入口
用法：python main.py "人名" [英文名]
示例：python main.py "埃隆·马斯克" "Elon Musk"
"""
import sys
import json
import time
from pathlib import Path

# 将 src 目录加入路径
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import fetch_person_data
from llm_enricher import enrich_person
from renderer import render, save


def generate_person_wiki(name_zh: str, name_en: str = "") -> Path:
    """
    完整流程：采集 → 提炼 → 渲染 → 保存
    返回生成的 HTML 文件路径
    """
    start = time.time()

    # ── Step 1: 数据采集 ──────────────────────────────────────────
    raw_data = fetch_person_data(name_zh, name_en)

    # 保存原始数据（调试用）
    cache_dir = Path(__file__).parent.parent / "output" / "cache"
    cache_dir.mkdir(exist_ok=True)
    safe_name = name_zh.replace(" ", "_").replace("·", "")
    cache_file = cache_dir / f"{safe_name}_raw.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    print(f"  💾 原始数据已缓存：{cache_file}")

    # ── Step 2: LLM 提炼 ─────────────────────────────────────────
    enriched = enrich_person(raw_data)

    # ── Step 3: 渲染 HTML ────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"🎨 渲染 HTML 页面...")
    print(f"{'='*50}")

    html = render(
        basic          = enriched["basic"],
        intro          = enriched["intro"],
        timeline       = enriched["timeline"],
        core_ideas     = enriched["core_ideas"],
        quotes         = enriched["quotes"],
        further_reading= enriched["further_reading"],
    )

    # ── Step 4: 保存 ─────────────────────────────────────────────
    output_path = save(html, name_zh)
    elapsed = time.time() - start

    print(f"\n{'='*50}")
    print(f"🎉 生成完成！")
    print(f"{'='*50}")
    print(f"📄 文件路径：{output_path}")
    print(f"⏱️  耗时：{elapsed:.1f} 秒")
    print(f"\n提示：用浏览器打开以上文件即可查看专题页面")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python main.py <中文名> [英文名]")
        print("示例：python main.py 埃隆·马斯克 'Elon Musk'")
        sys.exit(1)

    name_zh = sys.argv[1]
    name_en = sys.argv[2] if len(sys.argv) > 2 else ""

    generate_person_wiki(name_zh, name_en)
