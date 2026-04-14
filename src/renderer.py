"""
HTML 渲染层 - 将结构化数据填充到 HTML 模板
使用纯 Python 字符串替换（无需 Jinja2 依赖）
"""
import re
import json
from datetime import datetime
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "person.html"
OUTPUT_DIR    = Path(__file__).parent.parent / "output"


def render(basic: dict, intro: str, timeline: list,
           core_ideas: list, quotes: list,
           further_reading: list) -> str:
    """
    将所有数据渲染为 HTML 字符串
    """
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    generated_at = datetime.now().strftime("%Y年%m月%d日 %H:%M")

    # 逐块替换 Jinja2 风格的模板标签
    html = template

    # ── 基础变量替换 ──────────────────────────────────────────────
    html = html.replace("{{ basic.name_zh }}", _esc(basic.get("name_zh", "")))
    html = html.replace("{{ basic.name_en }}", _esc(basic.get("name_en", "")))
    html = html.replace("{{ basic.description }}", _esc(basic.get("description", "")))
    html = html.replace("{{ basic.thumbnail }}", _esc(basic.get("thumbnail", "")))
    html = html.replace("{{ basic.birth_date }}", _esc(basic.get("birth_date", "")))
    html = html.replace("{{ basic.death_date }}", _esc(basic.get("death_date", "")))
    html = html.replace("{{ basic.birth_place }}", _esc(basic.get("birth_place", "")))
    html = html.replace("{{ basic.nationality }}", _esc(basic.get("nationality", "")))
    html = html.replace("{{ basic.wiki_url_zh }}", _esc(basic.get("wiki_url_zh", "")))
    html = html.replace("{{ basic.wiki_url_en }}", _esc(basic.get("wiki_url_en", "")))
    html = html.replace("{{ intro }}", intro.replace("\n", "<br>"))
    html = html.replace("{{ generated_at }}", generated_at)

    # ── 条件块处理 ────────────────────────────────────────────────
    # {% if X %}...{% endif %} 块
    html = _process_if_blocks(html, {
        "basic.thumbnail":      bool(basic.get("thumbnail")),
        "basic.name_en and basic.name_en != basic.name_zh":
            bool(basic.get("name_en") and basic.get("name_en") != basic.get("name_zh")),
        "basic.description":    bool(basic.get("description")),
        "basic.occupations":    bool(basic.get("occupations")),
        "basic.birth_date":     bool(basic.get("birth_date")),
        "basic.death_date":     bool(basic.get("death_date")),
        "basic.birth_place":    bool(basic.get("birth_place")),
        "basic.nationality":    bool(basic.get("nationality")),
        "basic.wiki_url_zh":    bool(basic.get("wiki_url_zh")),
        "basic.wiki_url_en":    bool(basic.get("wiki_url_en")),
        "timeline":             bool(timeline),
        "core_ideas":           bool(core_ideas),
        "quotes":               bool(quotes),
        "basic.works":          bool(basic.get("works")),
        "basic.related_people": bool(basic.get("related_people")),
        "basic.awards":         bool(basic.get("awards")),
        "further_reading":      bool(further_reading),
        "idea.example":         True,   # 在循环内处理
        "q.text_en":            True,
        "work.type":            True,
        "work.year":            True,
        "person.image":         True,
        "award.date":           True,
        "item.author":          True,
        "item.reason":          True,
    })

    # ── 循环块处理 ────────────────────────────────────────────────
    # 职业标签
    html = _replace_loop(
        html,
        r"\{% for occ in basic\.occupations\[:5\] %\}(.*?)\{% endfor %\}",
        basic.get("occupations", [])[:5],
        lambda occ, _: _esc(occ),
        "{{ occ }}"
    )

    # 时间线
    html = _replace_loop(
        html,
        r"\{% for item in timeline %\}(.*?)\{% endfor %\}",
        timeline,
        lambda item, tpl: (tpl
            .replace("{{ item.year }}", _esc(str(item.get("year", ""))))
            .replace("{{ item.title }}", _esc(item.get("title", "")))
            .replace("{{ item.desc }}", _esc(item.get("desc", "")))),
        None
    )

    # 核心思想
    def render_idea(idea, tpl):
        t = tpl
        t = t.replace("{{ loop.index }}", str(idea.get("_idx", 1)))
        t = t.replace("{{ idea.title }}", _esc(idea.get("title", "")))
        t = t.replace("{{ idea.desc }}", _esc(idea.get("desc", "")))
        # 处理 idea.example 条件
        if idea.get("example"):
            t = re.sub(r'\{% if idea\.example %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ idea.example }}", _esc(idea.get("example", "")))
        else:
            t = re.sub(r'\{% if idea\.example %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        return t

    ideas_with_idx = [{**idea, "_idx": i+1} for i, idea in enumerate(core_ideas)]
    html = _replace_loop(
        html,
        r"\{% for idea in core_ideas %\}(.*?)\{% endfor %\}",
        ideas_with_idx,
        render_idea,
        None
    )

    # 语录
    def render_quote(q, tpl):
        t = tpl
        t = t.replace("{{ q.text_zh }}", _esc(q.get("text_zh", "")))
        t = t.replace("{{ q.source }}", _esc(q.get("source", "")))
        t = t.replace("{{ q.year }}", _esc(str(q.get("year", ""))))
        if q.get("text_en"):
            t = re.sub(r'\{% if q\.text_en %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ q.text_en }}", _esc(q.get("text_en", "")))
        else:
            t = re.sub(r'\{% if q\.text_en %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        if q.get("year"):
            t = re.sub(r'\{% if q\.year %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
        else:
            t = re.sub(r'\{% if q\.year %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        return t

    html = _replace_loop(
        html,
        r"\{% for q in quotes %\}(.*?)\{% endfor %\}",
        quotes,
        render_quote,
        None
    )

    # 代表作品
    def render_work(work, tpl):
        t = tpl
        t = t.replace("{{ work.name }}", _esc(work.get("name", "")))
        if work.get("type"):
            t = re.sub(r'\{% if work\.type %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ work.type }}", _esc(work.get("type", "")))
        else:
            t = re.sub(r'\{% if work\.type %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        if work.get("year"):
            t = re.sub(r'\{% if work\.year %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ work.year }}", _esc(str(work.get("year", ""))))
        else:
            t = re.sub(r'\{% if work\.year %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        return t

    html = _replace_loop(
        html,
        r"\{% for work in basic\.works %\}(.*?)\{% endfor %\}",
        basic.get("works", []),
        render_work,
        None
    )

    # 相关人物
    def render_person(person, tpl):
        t = tpl
        t = t.replace("{{ person.name }}", _esc(person.get("name", "")))
        t = t.replace("{{ person.rel }}", _esc(person.get("rel", "")))
        if person.get("image"):
            t = re.sub(r'\{% if person\.image %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ person.image }}", _esc(person.get("image", "")))
            t = t.replace("{{ person.name }}", _esc(person.get("name", "")))
        else:
            t = re.sub(r'\{% if person\.image %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        return t

    html = _replace_loop(
        html,
        r"\{% for person in basic\.related_people %\}(.*?)\{% endfor %\}",
        basic.get("related_people", []),
        render_person,
        None
    )

    # 奖项
    def render_award(award, tpl):
        t = tpl
        t = t.replace("{{ award.name }}", _esc(award.get("name", "")))
        if award.get("date"):
            t = re.sub(r'\{% if award\.date %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ award.date }}", _esc(str(award.get("date", ""))))
        else:
            t = re.sub(r'\{% if award\.date %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        return t

    html = _replace_loop(
        html,
        r"\{% for award in basic\.awards %\}(.*?)\{% endfor %\}",
        basic.get("awards", []),
        render_award,
        None
    )

    # 延伸阅读
    def render_reading(item, tpl):
        t = tpl
        t = t.replace("{{ item.title }}", _esc(item.get("title", "")))
        t = t.replace("{{ item.type }}", _esc(item.get("type", "")))
        t = t.replace("{{ item.desc }}", _esc(item.get("desc", "")))
        if item.get("author"):
            t = re.sub(r'\{% if item\.author %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ item.author }}", _esc(item.get("author", "")))
        else:
            t = re.sub(r'\{% if item\.author %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        if item.get("reason"):
            t = re.sub(r'\{% if item\.reason %\}', '', t)
            t = re.sub(r'\{% endif %\}', '', t, count=1)
            t = t.replace("{{ item.reason }}", _esc(item.get("reason", "")))
        else:
            t = re.sub(r'\{% if item\.reason %\}.*?\{% endif %\}', '', t, flags=re.DOTALL)
        return t

    html = _replace_loop(
        html,
        r"\{% for item in further_reading %\}(.*?)\{% endfor %\}",
        further_reading,
        render_reading,
        None
    )

    # 清理残余模板标签
    html = re.sub(r'\{%[^%]+%\}', '', html)
    html = re.sub(r'\{\{[^}]+\}\}', '', html)

    return html


def save(html: str, name: str) -> Path:
    """保存 HTML 文件，返回文件路径"""
    safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)
    filename = f"{safe_name}.html"
    path = OUTPUT_DIR / filename
    path.write_text(html, encoding="utf-8")
    return path


# ── 内部工具函数 ──────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """HTML 转义"""
    return (str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;"))


def _process_if_blocks(html: str, conditions: dict) -> str:
    """处理 {% if X %}...{% endif %} 条件块"""
    for cond, value in conditions.items():
        escaped_cond = re.escape(cond)
        pattern = rf'\{{% if {escaped_cond} %\}}(.*?)\{{% endif %\}}'
        if value:
            # 保留内容，去掉标签
            html = re.sub(pattern, r'\1', html, flags=re.DOTALL)
        else:
            # 删除整个块
            html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def _replace_loop(html: str, pattern: str, items: list,
                  render_fn, simple_var: str) -> str:
    """处理 {% for ... %}...{% endfor %} 循环块"""
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return html

    item_tpl = match.group(1)
    rendered_items = []

    for item in items:
        if simple_var:
            rendered_items.append(item_tpl.replace(simple_var, _esc(str(item))))
        else:
            rendered_items.append(render_fn(item, item_tpl))

    html = html[:match.start()] + "".join(rendered_items) + html[match.end():]
    return html
