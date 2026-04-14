"""
配置文件 - LLM 接口和数据源设置
优先使用 Friday 内部接口，不可用时回退到用户自定义配置
"""
import os
import json
from pathlib import Path

# ─── Friday 内部 LLM 配置 ───────────────────────────────────────────────────
# 注意：FRIDAY_APP_ID 需要是 LLM 对话专用的 App ID（非图片生成 App ID）
# 在 Friday 平台申请：https://friday.sankuai.com → 我的应用 → 新建应用 → 选择 LLM 能力
FRIDAY_BASE_URL = "https://aigc.sankuai.com/v1"
FRIDAY_APP_ID   = os.environ.get("FRIDAY_APP_ID", "")   # 需要用户设置环境变量
FRIDAY_MODEL    = "gpt-4o"          # Friday 上挂载的 OpenAI 兼容模型

# ─── 用户自定义 LLM 配置（Friday 不可用时使用）────────────────────────────
USER_CONFIG_FILE = Path(__file__).parent.parent / "user_config.json"

def load_user_config() -> dict:
    """加载用户自定义 LLM 配置"""
    if USER_CONFIG_FILE.exists():
        with open(USER_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_config(config: dict):
    """保存用户自定义 LLM 配置"""
    with open(USER_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 配置已保存到 {USER_CONFIG_FILE}")

# ─── Wikipedia 配置 ──────────────────────────────────────────────────────────
WIKI_LANG_ZH = "zh"
WIKI_LANG_EN = "en"
WIKI_API_URL = "https://zh.wikipedia.org/api/rest_v1"
WIKI_EN_API_URL = "https://en.wikipedia.org/api/rest_v1"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

# ─── 百度百科配置 ─────────────────────────────────────────────────────────────
BAIDU_BAIKE_SEARCH = "https://baike.baidu.com/search/word?word={}"
BAIDU_BAIKE_ITEM   = "https://baike.baidu.com/item/{}"

# ─── 输出配置 ─────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
