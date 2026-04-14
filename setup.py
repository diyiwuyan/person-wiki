"""
快速配置向导 - 设置 LLM API Key
运行：python setup.py
"""
import json
import sys
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "user_config.json"

print("=" * 60)
print("🔧 人物专题学习工具 - LLM 配置向导")
print("=" * 60)
print()
print("支持以下 LLM 接口（任选其一）：")
print()
print("  1. OpenAI 官方（需要 OpenAI API Key）")
print("     Base URL: https://api.openai.com/v1")
print("     模型推荐: gpt-4o-mini（便宜）或 gpt-4o（效果好）")
print()
print("  2. 美团 Friday 内部（需要 LLM 专用 App ID）")
print("     Base URL: https://aigc.sankuai.com/v1")
print("     申请地址: https://friday.sankuai.com → 我的应用 → 新建")
print()
print("  3. 其他 OpenAI 兼容接口（如 DeepSeek、Moonshot 等）")
print()

choice = input("请选择（1/2/3，直接回车选1）: ").strip() or "1"

if choice == "1":
    base_url = "https://api.openai.com/v1"
    default_model = "gpt-4o-mini"
elif choice == "2":
    base_url = "https://aigc.sankuai.com/v1"
    default_model = "gpt-4o"
else:
    base_url = input("请输入 Base URL: ").strip()
    default_model = "gpt-4o-mini"

api_key = input(f"\n请输入 API Key: ").strip()
if not api_key:
    print("❌ API Key 不能为空")
    sys.exit(1)

model_input = input(f"请输入模型名称（直接回车使用 {default_model}）: ").strip()
model = model_input or default_model

config = {
    "api_key": api_key,
    "base_url": base_url,
    "model": model
}

with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"\n✅ 配置已保存到 {CONFIG_FILE}")
print(f"   Base URL: {base_url}")
print(f"   模型: {model}")
print()
print("现在可以运行：")
print("  cd src && python main.py 埃隆·马斯克 'Elon Musk'")
