"""
LLM 提炼层
基于采集到的原始数据，用 LLM 提炼：
- 人物简介（精炼版）
- 生平时间线
- 核心思想（3-6条）
- 经典语录（5-10条）
- 延伸阅读推荐
"""
import json
from llm_client import get_llm


SYSTEM_PROMPT = """你是一位专业的人物传记研究员，擅长从大量资料中提炼人物的核心思想、生平脉络和经典语录。
你的输出必须：
1. 基于提供的真实资料，不编造内容
2. 语言准确、简洁、有深度
3. 严格按照要求的 JSON 格式输出
4. 中文输出"""


def enrich_person(raw_data: dict) -> dict:
    """
    用 LLM 对原始数据进行提炼和增强
    返回结构化的人物信息字典
    """
    llm = get_llm()
    name_zh = raw_data.get("name_zh", "")
    name_en = raw_data.get("name_en", "")

    print(f"\n{'='*50}")
    print(f"🤖 LLM 提炼中：{name_zh}")
    print(f"{'='*50}")

    # 准备上下文素材
    context = _build_context(raw_data)

    result = {}

    # 1. 基础信息整合
    print("  📝 提炼基础信息...")
    result["basic"] = _extract_basic(llm, name_zh, name_en, raw_data)

    # 2. 人物简介
    print("  📝 生成人物简介...")
    result["intro"] = _extract_intro(llm, name_zh, context)

    # 3. 生平时间线
    print("  📅 提炼生平时间线...")
    result["timeline"] = _extract_timeline(llm, name_zh, context)

    # 4. 核心思想
    print("  💡 提炼核心思想...")
    result["core_ideas"] = _extract_core_ideas(llm, name_zh, context)

    # 5. 经典语录
    print("  💬 整理经典语录...")
    result["quotes"] = _extract_quotes(llm, name_zh, name_en, context)

    # 6. 延伸阅读
    print("  📚 推荐延伸阅读...")
    result["further_reading"] = _extract_further_reading(llm, name_zh, name_en, context)

    print(f"\n✅ LLM 提炼完成！")
    return result


def _build_context(raw_data: dict) -> str:
    """将原始数据整合为 LLM 可读的上下文"""
    parts = []

    wiki = raw_data.get("wikipedia", {})
    if wiki.get("summary_zh"):
        parts.append(f"【Wikipedia 中文摘要】\n{wiki['summary_zh'][:1500]}")
    if wiki.get("summary_en"):
        parts.append(f"【Wikipedia 英文摘要】\n{wiki['summary_en'][:1000]}")

    # 英文章节（早年、职业生涯等）
    sections_en = wiki.get("sections_en", {})
    for key in ["Early life", "Career", "Personal life", "Legacy", "Philosophy"]:
        for sec_key, sec_val in sections_en.items():
            if key.lower() in sec_key.lower() and sec_val:
                parts.append(f"【{sec_key}】\n{sec_val[:800]}")
                break

    # 中文章节
    sections_zh = wiki.get("sections_zh", {})
    for sec_key, sec_val in list(sections_zh.items())[:5]:
        if sec_val and len(sec_val) > 50:
            parts.append(f"【{sec_key}】\n{sec_val[:600]}")

    wikidata = raw_data.get("wikidata", {})
    basic = wikidata.get("basic", {})
    if basic:
        info_lines = []
        if basic.get("birth_date"):
            info_lines.append(f"出生日期：{basic['birth_date']}")
        if basic.get("birth_place"):
            info_lines.append(f"出生地：{basic['birth_place']}")
        if basic.get("death_date"):
            info_lines.append(f"逝世日期：{basic['death_date']}")
        if basic.get("occupations"):
            info_lines.append(f"职业：{', '.join(basic['occupations'][:5])}")
        if basic.get("nationalities"):
            info_lines.append(f"国籍：{', '.join(basic['nationalities'])}")
        if info_lines:
            parts.append("【Wikidata 基本信息】\n" + "\n".join(info_lines))

    baidu = raw_data.get("baidu_baike", {})
    if baidu.get("abstract"):
        parts.append(f"【百度百科摘要】\n{baidu['abstract'][:1000]}")
    if baidu.get("info_table"):
        info_lines = [f"{k}：{v}" for k, v in list(baidu["info_table"].items())[:15]]
        parts.append("【百度百科基本信息】\n" + "\n".join(info_lines))

    # 搜索补充数据（当 Wikipedia/百度百科不可用时）
    supplement = raw_data.get("search_supplement", {})
    if supplement.get("combined_text"):
        parts.append(f"【网络搜索补充资料】\n{supplement['combined_text'][:3000]}")

    # 如果所有数据源都为空，提示 LLM 使用自身知识
    if not parts:
        name_zh = raw_data.get("name_zh", "")
        name_en = raw_data.get("name_en", "")
        parts.append(
            f"【说明】外部数据源暂时不可用。请基于你对{name_zh}（{name_en}）的训练知识，"
            f"生成准确、详实的内容。请确保内容的准确性，对不确定的信息请标注。"
        )

    return "\n\n".join(parts)


def _extract_basic(llm, name_zh: str, name_en: str, raw_data: dict) -> dict:
    """整合基础信息"""
    wiki = raw_data.get("wikipedia", {})
    wikidata = raw_data.get("wikidata", {})
    baidu = raw_data.get("baidu_baike", {})

    infobox = {**wiki.get("infobox", {})}
    wd_basic = wikidata.get("basic", {})
    baidu_info = baidu.get("info_table", {})

    # 字段映射（优先级：百度百科 > Wikidata > Wikipedia Infobox）
    def get_field(*keys):
        for k in keys:
            for src in [baidu_info, wd_basic, infobox]:
                if src.get(k):
                    return src[k]
        return ""

    birth_date = (
        wd_basic.get("birth_date") or
        baidu_info.get("出生日期") or baidu_info.get("出生") or
        infobox.get("birth_date") or infobox.get("born") or ""
    )
    birth_place = (
        wd_basic.get("birth_place") or
        baidu_info.get("出生地点") or baidu_info.get("出生地") or
        infobox.get("birth_place") or ""
    )
    nationality = (
        ", ".join(wd_basic.get("nationalities", [])) or
        baidu_info.get("国籍") or infobox.get("nationality") or ""
    )
    occupations = (
        wd_basic.get("occupations") or
        [baidu_info.get("职业", "")] or
        [infobox.get("occupation", "")]
    )
    occupations = [o for o in occupations if o]

    thumbnail = wiki.get("thumbnail") or wd_basic.get("image", "")

    return {
        "name_zh":     name_zh,
        "name_en":     name_en,
        "birth_date":  birth_date,
        "birth_place": birth_place,
        "death_date":  wd_basic.get("death_date", ""),
        "nationality": nationality,
        "occupations": occupations,
        "thumbnail":   thumbnail,
        "wiki_url_zh": wiki.get("wiki_url_zh", ""),
        "wiki_url_en": wiki.get("wiki_url_en", ""),
        "awards":      wikidata.get("awards", []),
        "positions":   wikidata.get("positions", []),
        "works":       wikidata.get("works", []),
        "related_people": wikidata.get("related_people", []),
    }


def _extract_intro(llm, name_zh: str, context: str) -> str:
    """生成 200-350 字的人物简介"""
    prompt = f"""基于以下关于{name_zh}的资料，写一段200-350字的人物简介。

要求：
- 涵盖：历史地位、核心贡献、为什么值得了解
- 语言精炼有力，不用"他是一位..."这种套话开头
- 直接输出文字，不要任何标题或格式

资料：
{context[:3000]}"""

    return llm.chat(prompt, SYSTEM_PROMPT, max_tokens=600)


def _extract_timeline(llm, name_zh: str, context: str) -> list:
    """提炼生平时间线，返回事件列表"""
    prompt = f"""基于以下关于{name_zh}的资料，提炼其生平重要时间节点。

要求：
- 提取10-18个关键时间节点
- 每个节点包含：年份、事件标题（10字以内）、事件描述（30-60字）
- 按时间顺序排列
- 只包含有明确年份的事件

严格按以下 JSON 格式输出（不要任何其他文字）：
[
  {{"year": "1971", "title": "出生于南非", "desc": "出生于南非比勒陀利亚，父亲是工程师，母亲是营养师兼模特。"}},
  ...
]

资料：
{context[:4000]}"""

    try:
        data = llm.chat_json(prompt, SYSTEM_PROMPT, max_tokens=2000)
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"  ⚠️  时间线解析失败：{e}")

    # 降级：返回空列表
    return []


def _extract_core_ideas(llm, name_zh: str, context: str) -> list:
    """提炼3-6个核心思想"""
    prompt = f"""基于以下关于{name_zh}的资料，提炼其3-6个最具代表性的核心思想或理念。

要求：
- 每个思想要有独特性，不是泛泛的"努力工作"之类
- 每个思想包含：标题（8字以内）、解释（60-100字）、代表案例（30-50字，举一个具体例子）
- 思想之间要有差异性，覆盖不同维度

严格按以下 JSON 格式输出（不要任何其他文字）：
[
  {{
    "title": "第一性原理思维",
    "desc": "不从类比出发，而是从最基本的物理事实推导结论。马斯克认为大多数人的思维是类比思维，而第一性原理思维能突破行业惯例，找到真正的解决方案。",
    "example": "在分析火箭成本时，他从原材料价格出发重新计算，发现火箭造价可以降低到传统价格的2%。"
  }},
  ...
]

资料：
{context[:4000]}"""

    try:
        data = llm.chat_json(prompt, SYSTEM_PROMPT, max_tokens=2000)
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"  ⚠️  核心思想解析失败：{e}")
    return []


def _extract_quotes(llm, name_zh: str, name_en: str, context: str) -> list:
    """整理5-10条经典语录"""
    prompt = f"""基于以下关于{name_zh}的资料，整理5-10条最具代表性的经典语录。

要求：
- 优先选择有明确出处的语录
- 每条语录包含：原文（中文）、英文原文（如有）、出处（书名/演讲/采访等）、年份（如知道）
- 语录要体现此人的核心思想和独特风格
- 如果资料中没有直接引用，可以基于其著名观点进行提炼，但要标注"提炼自其思想"

严格按以下 JSON 格式输出（不要任何其他文字）：
[
  {{
    "text_zh": "当某件事足够重要，即使胜算不大，你也应该去做。",
    "text_en": "When something is important enough, you do it even if the odds are not in your favor.",
    "source": "TED 演讲",
    "year": "2013"
  }},
  ...
]

资料：
{context[:3000]}"""

    try:
        data = llm.chat_json(prompt, SYSTEM_PROMPT, max_tokens=2000)
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"  ⚠️  语录解析失败：{e}")
    return []


def _extract_further_reading(llm, name_zh: str, name_en: str, context: str) -> list:
    """推荐延伸阅读"""
    prompt = f"""基于以下关于{name_zh}的资料，推荐5-8个延伸阅读/观看资源。

要求：
- 包含：书籍、纪录片、演讲、访谈等多种类型
- 每项包含：标题、类型（书籍/纪录片/演讲/访谈）、简介（20-40字）、推荐理由（20-30字）
- 优先推荐一手资料（此人自己写的书、亲自参与的访谈）

严格按以下 JSON 格式输出（不要任何其他文字）：
[
  {{
    "title": "埃隆·马斯克传",
    "type": "书籍",
    "author": "沃尔特·艾萨克森",
    "desc": "授权传记，详述马斯克的成长历程与商业帝国的建立过程。",
    "reason": "最权威的一手传记，作者与马斯克深度访谈两年"
  }},
  ...
]

资料：
{context[:2000]}"""

    try:
        data = llm.chat_json(prompt, SYSTEM_PROMPT, max_tokens=1500)
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"  ⚠️  延伸阅读解析失败：{e}")
    return []
