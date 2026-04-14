"""
数据采集层
- Wikipedia（中英文）：基础信息、摘要、Infobox、时间线章节
- Wikidata SPARQL：结构化关系数据（相关人物、奖项、职位）
- 百度百科：中文补充信息
"""
import re
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional
from config import WIKIDATA_SPARQL_URL


# ─── 通用 HTTP 工具 ───────────────────────────────────────────────────────────

def _get(url: str, headers: dict = None, timeout: int = 20) -> Optional[str]:
    """简单 GET 请求，返回响应文本"""
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers=headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  ⚠️  请求失败 {url[:80]}... : {e}")
        return None


def _get_json(url: str, headers: dict = None) -> Optional[dict]:
    text = _get(url, headers)
    if text:
        try:
            return json.loads(text)
        except Exception:
            return None
    return None


# ─── Wikipedia 采集 ───────────────────────────────────────────────────────────

class WikipediaFetcher:
    """从 Wikipedia 获取人物信息"""

    def __init__(self, name_zh: str, name_en: str = ""):
        self.name_zh = name_zh
        self.name_en = name_en or name_zh
        self.zh_data: dict = {}
        self.en_data: dict = {}

    def fetch_all(self) -> dict:
        """并行（串行模拟）获取中英文 Wikipedia 数据"""
        print(f"  📖 正在获取 Wikipedia 中文数据：{self.name_zh}")
        self.zh_data = self._fetch_zh()
        print(f"  📖 正在获取 Wikipedia 英文数据：{self.name_en}")
        self.en_data = self._fetch_en()
        return self._merge()

    # ── 中文 Wikipedia ──────────────────────────────────────────────────────

    def _fetch_zh(self) -> dict:
        result = {}
        encoded = urllib.parse.quote(self.name_zh)

        # 1. REST API 摘要
        url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        data = _get_json(url)
        if data:
            result["summary"]     = data.get("extract", "")
            result["description"] = data.get("description", "")
            result["thumbnail"]   = data.get("thumbnail", {}).get("source", "")
            result["wiki_url_zh"] = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        # 2. MediaWiki API 获取完整页面内容（含各章节）
        mw_url = (
            "https://zh.wikipedia.org/w/api.php"
            f"?action=parse&page={encoded}&prop=sections|text|wikitext"
            "&format=json&utf8=1"
        )
        mw_data = _get_json(mw_url)
        if mw_data and "parse" in mw_data:
            parse = mw_data["parse"]
            result["sections"] = [s["line"] for s in parse.get("sections", [])]
            wikitext = parse.get("wikitext", {}).get("*", "")
            result["infobox"] = self._parse_infobox(wikitext)
            result["wikitext_sections"] = self._extract_sections(wikitext)

        return result

    def _parse_infobox(self, wikitext: str) -> dict:
        """从 wikitext 中提取 Infobox 字段"""
        infobox = {}
        # 找到 {{Infobox ... }} 块
        match = re.search(r'\{\{Infobox[^}]*?\n(.*?)\n\}\}', wikitext, re.DOTALL | re.IGNORECASE)
        if not match:
            # 尝试中文 infobox
            match = re.search(r'\{\{人物信息[^}]*?\n(.*?)\n\}\}', wikitext, re.DOTALL)
        if match:
            block = match.group(0)
            # 提取 | key = value 格式
            for line in block.split("\n"):
                m = re.match(r'\s*\|\s*(\w+)\s*=\s*(.+)', line)
                if m:
                    key = m.group(1).strip()
                    val = re.sub(r'\[\[([^|\]]+)(?:\|[^\]]+)?\]\]', r'\1', m.group(2))
                    val = re.sub(r'\{\{[^}]+\}\}', '', val)
                    val = re.sub(r'<[^>]+>', '', val).strip()
                    if val:
                        infobox[key] = val
        return infobox

    def _extract_sections(self, wikitext: str) -> dict:
        """提取 wikitext 中各章节的纯文本内容"""
        sections = {}
        current = "intro"
        buf = []
        for line in wikitext.split("\n"):
            h = re.match(r'^(={2,4})\s*(.+?)\s*\1$', line)
            if h:
                if buf:
                    sections[current] = self._clean_wikitext("\n".join(buf))
                current = h.group(2)
                buf = []
            else:
                buf.append(line)
        if buf:
            sections[current] = self._clean_wikitext("\n".join(buf))
        return sections

    def _clean_wikitext(self, text: str) -> str:
        """清理 wikitext 标记，返回纯文本"""
        text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        text = re.sub(r"'{2,3}", '', text)
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    # ── 英文 Wikipedia ──────────────────────────────────────────────────────

    def _fetch_en(self) -> dict:
        result = {}
        encoded = urllib.parse.quote(self.name_en)

        # REST API 摘要
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        data = _get_json(url)
        if data:
            result["summary"]   = data.get("extract", "")
            result["thumbnail"] = data.get("thumbnail", {}).get("source", "")
            result["wiki_url_en"] = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        # MediaWiki API 获取章节
        mw_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=parse&page={encoded}&prop=sections|wikitext"
            "&format=json&utf8=1"
        )
        mw_data = _get_json(mw_url)
        if mw_data and "parse" in mw_data:
            parse = mw_data["parse"]
            wikitext = parse.get("wikitext", {}).get("*", "")
            result["infobox"]            = self._parse_infobox(wikitext)
            result["wikitext_sections"]  = self._extract_sections(wikitext)

        return result

    # ── 合并中英文数据 ──────────────────────────────────────────────────────

    def _merge(self) -> dict:
        """合并中英文数据，中文优先，英文补充"""
        merged = {
            "name_zh":      self.name_zh,
            "name_en":      self.name_en,
            "summary_zh":   self.zh_data.get("summary", ""),
            "summary_en":   self.en_data.get("summary", ""),
            "description":  self.zh_data.get("description", ""),
            "thumbnail":    self.zh_data.get("thumbnail") or self.en_data.get("thumbnail", ""),
            "wiki_url_zh":  self.zh_data.get("wiki_url_zh", ""),
            "wiki_url_en":  self.en_data.get("wiki_url_en", ""),
            "infobox":      {**self.en_data.get("infobox", {}), **self.zh_data.get("infobox", {})},
            "sections_zh":  self.zh_data.get("wikitext_sections", {}),
            "sections_en":  self.en_data.get("wikitext_sections", {}),
        }
        return merged


# ─── Wikidata SPARQL 采集 ─────────────────────────────────────────────────────

class WikidataFetcher:
    """通过 SPARQL 查询 Wikidata 获取结构化关系数据"""

    def __init__(self, name_en: str):
        self.name_en = name_en
        self.qid: str = ""

    def fetch_all(self) -> dict:
        """获取所有 Wikidata 数据"""
        print(f"  🔗 正在查询 Wikidata：{self.name_en}")
        self.qid = self._get_qid()
        if not self.qid:
            print(f"  ⚠️  未找到 Wikidata QID：{self.name_en}")
            return {}

        print(f"  ✅ Wikidata QID：{self.qid}")
        return {
            "qid":            self.qid,
            "basic":          self._fetch_basic(),
            "related_people": self._fetch_related_people(),
            "awards":         self._fetch_awards(),
            "works":          self._fetch_notable_works(),
            "positions":      self._fetch_positions(),
        }

    def _sparql(self, query: str) -> list:
        """执行 SPARQL 查询，返回 bindings 列表"""
        url = WIKIDATA_SPARQL_URL + "?query=" + urllib.parse.quote(query)
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "PersonWikiBot/1.0"
        }
        data = _get_json(url, headers)
        if data:
            return data.get("results", {}).get("bindings", [])
        return []

    def _val(self, binding: dict, key: str) -> str:
        return binding.get(key, {}).get("value", "")

    def _get_qid(self) -> str:
        """通过人名搜索获取 Wikidata QID"""
        url = (
            "https://www.wikidata.org/w/api.php"
            f"?action=wbsearchentities&search={urllib.parse.quote(self.name_en)}"
            "&language=en&type=item&format=json&limit=3"
        )
        data = _get_json(url)
        if data and data.get("search"):
            # 取第一个结果
            return data["search"][0].get("id", "")
        return ""

    def _fetch_basic(self) -> dict:
        """获取基本属性：出生日期、出生地、国籍、职业等"""
        query = f"""
        SELECT ?birthDate ?birthPlace ?birthPlaceLabel ?deathDate ?nationality ?nationalityLabel
               ?occupation ?occupationLabel ?image
        WHERE {{
          BIND(wd:{self.qid} AS ?person)
          OPTIONAL {{ ?person wdt:P569 ?birthDate. }}
          OPTIONAL {{ ?person wdt:P19 ?birthPlace. ?birthPlace rdfs:label ?birthPlaceLabel. FILTER(LANG(?birthPlaceLabel)="zh") }}
          OPTIONAL {{ ?person wdt:P570 ?deathDate. }}
          OPTIONAL {{ ?person wdt:P27 ?nationality. ?nationality rdfs:label ?nationalityLabel. FILTER(LANG(?nationalityLabel)="zh") }}
          OPTIONAL {{ ?person wdt:P106 ?occupation. ?occupation rdfs:label ?occupationLabel. FILTER(LANG(?occupationLabel)="zh") }}
          OPTIONAL {{ ?person wdt:P18 ?image. }}
        }} LIMIT 10
        """
        rows = self._sparql(query)
        result = {"occupations": [], "nationalities": []}
        for r in rows:
            if self._val(r, "birthDate") and not result.get("birth_date"):
                result["birth_date"] = self._val(r, "birthDate")[:10]
            if self._val(r, "birthPlaceLabel") and not result.get("birth_place"):
                result["birth_place"] = self._val(r, "birthPlaceLabel")
            if self._val(r, "deathDate") and not result.get("death_date"):
                result["death_date"] = self._val(r, "deathDate")[:10]
            if self._val(r, "nationalityLabel"):
                n = self._val(r, "nationalityLabel")
                if n not in result["nationalities"]:
                    result["nationalities"].append(n)
            if self._val(r, "occupationLabel"):
                o = self._val(r, "occupationLabel")
                if o not in result["occupations"]:
                    result["occupations"].append(o)
            if self._val(r, "image") and not result.get("image"):
                result["image"] = self._val(r, "image")
        return result

    def _fetch_related_people(self) -> list:
        """获取相关人物：老师、学生、配偶、合作者等"""
        query = f"""
        SELECT ?rel ?relLabel ?personLabel ?personImage
        WHERE {{
          BIND(wd:{self.qid} AS ?subject)
          VALUES (?rel ?relLabel) {{
            (wdt:P22  "父亲") (wdt:P25  "母亲") (wdt:P26  "配偶")
            (wdt:P1066 "老师") (wdt:P802 "学生") (wdt:P108 "雇主")
            (wdt:P463 "成员组织") (wdt:P3373 "兄弟姐妹")
          }}
          ?subject ?rel ?person.
          ?person rdfs:label ?personLabel. FILTER(LANG(?personLabel)="zh")
          OPTIONAL {{ ?person wdt:P18 ?personImage. }}
        }} LIMIT 20
        """
        rows = self._sparql(query)
        people = []
        seen = set()
        for r in rows:
            name = self._val(r, "personLabel")
            rel  = self._val(r, "relLabel")
            if name and name not in seen:
                seen.add(name)
                people.append({
                    "name":  name,
                    "rel":   rel,
                    "image": self._val(r, "personImage"),
                })
        return people

    def _fetch_awards(self) -> list:
        """获取获奖记录"""
        query = f"""
        SELECT ?awardLabel ?awardDate
        WHERE {{
          wd:{self.qid} p:P166 ?awardStatement.
          ?awardStatement ps:P166 ?award.
          ?award rdfs:label ?awardLabel. FILTER(LANG(?awardLabel)="zh")
          OPTIONAL {{ ?awardStatement pq:P585 ?awardDate. }}
        }} LIMIT 20
        """
        rows = self._sparql(query)
        awards = []
        for r in rows:
            label = self._val(r, "awardLabel")
            if label:
                awards.append({
                    "name": label,
                    "date": self._val(r, "awardDate")[:4] if self._val(r, "awardDate") else "",
                })
        return awards

    def _fetch_notable_works(self) -> list:
        """获取代表作品"""
        query = f"""
        SELECT ?workLabel ?workDate ?workType ?workTypeLabel
        WHERE {{
          wd:{self.qid} wdt:P800 ?work.
          ?work rdfs:label ?workLabel. FILTER(LANG(?workLabel)="zh")
          OPTIONAL {{ ?work wdt:P577 ?workDate. }}
          OPTIONAL {{ ?work wdt:P31 ?workType. ?workType rdfs:label ?workTypeLabel. FILTER(LANG(?workTypeLabel)="zh") }}
        }} LIMIT 15
        """
        rows = self._sparql(query)
        works = []
        seen = set()
        for r in rows:
            label = self._val(r, "workLabel")
            if label and label not in seen:
                seen.add(label)
                works.append({
                    "name": label,
                    "year": self._val(r, "workDate")[:4] if self._val(r, "workDate") else "",
                    "type": self._val(r, "workTypeLabel"),
                })
        return works

    def _fetch_positions(self) -> list:
        """获取担任过的职位"""
        query = f"""
        SELECT ?posLabel ?orgLabel ?startDate ?endDate
        WHERE {{
          wd:{self.qid} p:P39 ?posStatement.
          ?posStatement ps:P39 ?pos.
          ?pos rdfs:label ?posLabel. FILTER(LANG(?posLabel)="zh")
          OPTIONAL {{ ?posStatement pq:P580 ?startDate. }}
          OPTIONAL {{ ?posStatement pq:P582 ?endDate. }}
          OPTIONAL {{ ?posStatement pq:P642 ?org. ?org rdfs:label ?orgLabel. FILTER(LANG(?orgLabel)="zh") }}
        }} LIMIT 15
        """
        rows = self._sparql(query)
        positions = []
        for r in rows:
            pos = self._val(r, "posLabel")
            if pos:
                positions.append({
                    "title": pos,
                    "org":   self._val(r, "orgLabel"),
                    "start": self._val(r, "startDate")[:4] if self._val(r, "startDate") else "",
                    "end":   self._val(r, "endDate")[:4] if self._val(r, "endDate") else "",
                })
        return positions


# ─── 百度百科采集 ─────────────────────────────────────────────────────────────

class BaiduBaikeFetcher:
    """从百度百科获取中文补充信息"""

    def __init__(self, name: str):
        self.name = name

    def fetch(self) -> dict:
        """获取百度百科数据"""
        print(f"  📚 正在获取百度百科：{self.name}")
        encoded = urllib.parse.quote(self.name)
        url = f"https://baike.baidu.com/item/{encoded}"
        html = _get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        if not html:
            return {}
        return self._parse(html)

    def _parse(self, html: str) -> dict:
        """解析百度百科 HTML"""
        result = {}

        # 提取摘要（lemmaAbstract 区域）
        abstract_match = re.search(
            r'class="[^"]*lemmaAbstract[^"]*"[^>]*>(.*?)</div>',
            html, re.DOTALL
        )
        if abstract_match:
            text = re.sub(r'<[^>]+>', '', abstract_match.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            result["abstract"] = text[:800]

        # 提取基本信息表格
        info = {}
        rows = re.findall(
            r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>',
            html, re.DOTALL
        )
        for dt, dd in rows:
            key = re.sub(r'<[^>]+>', '', dt).strip()
            val = re.sub(r'<[^>]+>', '', dd).strip()
            val = re.sub(r'\s+', ' ', val)
            if key and val and len(key) < 20:
                info[key] = val
        result["info_table"] = info

        # 提取目录章节名
        toc = re.findall(r'class="[^"]*catalogItem[^"]*"[^>]*>.*?<span[^>]*>(.*?)</span>', html, re.DOTALL)
        result["toc"] = [re.sub(r'<[^>]+>', '', t).strip() for t in toc if t.strip()]

        return result


# ─── 主入口：聚合所有数据源 ───────────────────────────────────────────────────

def fetch_person_data(name_zh: str, name_en: str = "") -> dict:
    """
    聚合所有数据源，返回完整的人物原始数据
    name_zh: 中文名（如"埃隆·马斯克"）
    name_en: 英文名（如"Elon Musk"），为空则用中文名搜索
    """
    print(f"\n{'='*50}")
    print(f"🔍 开始采集人物数据：{name_zh} / {name_en or name_zh}")
    print(f"{'='*50}")

    result = {
        "name_zh": name_zh,
        "name_en": name_en or name_zh,
    }

    # 1. Wikipedia（可能因网络问题失败，失败后用搜索补充）
    wiki = WikipediaFetcher(name_zh, name_en)
    result["wikipedia"] = wiki.fetch_all()

    # 2. Wikidata
    wikidata = WikidataFetcher(name_en or name_zh)
    result["wikidata"] = wikidata.fetch_all()

    # 3. 百度百科
    baidu = BaiduBaikeFetcher(name_zh)
    result["baidu_baike"] = baidu.fetch()

    # 4. 如果 Wikipedia 和百度百科都失败，用 Friday 搜索补充
    wiki_ok  = bool(result["wikipedia"].get("summary_zh") or result["wikipedia"].get("summary_en"))
    baidu_ok = bool(result["baidu_baike"].get("abstract"))

    if not wiki_ok and not baidu_ok:
        print(f"  🔎 Wikipedia/百度百科均不可用，启用 Friday 搜索补充...")
        result["search_supplement"] = _friday_search_supplement(name_zh, name_en)
    else:
        result["search_supplement"] = {}

    print(f"\n✅ 数据采集完成！")
    print(f"   Wikipedia 摘要：{'✓' if wiki_ok else '✗'}")
    print(f"   Wikidata QID：{result['wikidata'].get('qid', '未找到')}")
    print(f"   百度百科：{'✓' if baidu_ok else '✗'}")
    print(f"   搜索补充：{'✓' if result.get('search_supplement') else '-'}")

    return result


def _friday_search_supplement(name_zh: str, name_en: str) -> dict:
    """
    当 Wikipedia/百度百科不可用时，通过 Friday MCP 搜索补充数据
    直接调用 Friday universal search API
    """
    import json as _json
    import os

    app_id = os.environ.get("FRIDAY_APP_ID", "22018892498218962980")
    results = {}

    queries = [
        f"{name_zh} 人物介绍 生平 经历",
        f"{name_zh} 核心思想 理念 观点",
        f"{name_zh} 经典语录 名言",
        f"{name_en} biography career achievements" if name_en else "",
    ]

    all_snippets = []
    for query in queries:
        if not query:
            continue
        url = "https://aigc.sankuai.com/v1/friday/universal-search"
        payload = _json.dumps({
            "query": query,
            "topK": 5,
            "isFast": False,
            "sources": ["baidu-search-v2"],
        }).encode("utf-8")

        import urllib.request as _req
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        request = _req.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {app_id}",
                "Content-Type": "application/json",
            },
            method="POST"
        )
        try:
            with _req.urlopen(request, timeout=30, context=ctx) as resp:
                data = _json.loads(resp.read().decode("utf-8"))
                items = data.get("data", {}).get("results", []) or data.get("results", [])
                for item in items[:3]:
                    snippet = item.get("snippet") or item.get("content") or item.get("summary", "")
                    title   = item.get("title", "")
                    if snippet:
                        all_snippets.append(f"【{title}】{snippet}")
        except Exception as e:
            print(f"  ⚠️  Friday 搜索失败（{query[:30]}）：{e}")

    if all_snippets:
        results["snippets"] = all_snippets
        results["combined_text"] = "\n\n".join(all_snippets)
        print(f"  ✅ Friday 搜索获取到 {len(all_snippets)} 条结果")
    else:
        print(f"  ⚠️  Friday 搜索也未获取到数据，将依赖 LLM 自身知识")

    return results
