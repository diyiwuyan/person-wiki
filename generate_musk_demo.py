"""
马斯克专题页面 - 直接生成演示
使用预置的高质量内容（基于 AI 知识库），无需外部 API
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from renderer import render, save

# ── 基础信息 ──────────────────────────────────────────────────────────────────
basic = {
    "name_zh":     "埃隆·马斯克",
    "name_en":     "Elon Musk",
    "description": "特斯拉,SpaceX,X 创始人，当代最具影响力的科技企业家",
    "thumbnail":   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Elon_Musk_Royal_Society_%28crop2%29.jpg/440px-Elon_Musk_Royal_Society_%28crop2%29.jpg",
    "birth_date":  "1971-06-28",
    "birth_place": "南非比勒陀利亚",
    "death_date":  "",
    "nationality": "美国,加拿大,南非",
    "occupations": ["企业家", "工程师", "投资人", "发明家"],
    "wiki_url_zh": "https://zh.wikipedia.org/wiki/%E5%9F%83%E9%9A%86%C2%B7%E9%A9%AC%E6%96%AF%E5%85%8B",
    "wiki_url_en": "https://en.wikipedia.org/wiki/Elon_Musk",
    "awards": [
        {"name": "皇家学会院士", "date": "2018"},
        {"name": "时代年度人物", "date": "2021"},
        {"name": "斯蒂芬·霍金奖章", "date": "2023"},
        {"name": "美国国家工程院院士", "date": "2022"},
    ],
    "works": [
        {"name": "特斯拉", "year": "2004", "type": "公司"},
        {"name": "SpaceX", "year": "2002", "type": "公司"},
        {"name": "X（原推特）", "year": "2022", "type": "公司"},
        {"name": "Neuralink", "year": "2016", "type": "公司"},
        {"name": "The Boring Company", "year": "2016", "type": "公司"},
        {"name": "xAI", "year": "2023", "type": "公司"},
        {"name": "Zip2", "year": "1995", "type": "公司"},
        {"name": "PayPal（X.com）", "year": "1999", "type": "公司"},
    ],
    "related_people": [
        {"name": "彼得·蒂尔", "rel": "PayPal 联合创始人", "image": ""},
        {"name": "格雷西亚斯", "rel": "长期合作伙伴", "image": ""},
        {"name": "比尔·盖茨", "rel": "科技同行", "image": ""},
        {"name": "杰夫·贝索斯", "rel": "商业竞争对手", "image": ""},
        {"name": "史蒂夫·乔布斯", "rel": "精神偶像", "image": ""},
        {"name": "尼古拉·特斯拉", "rel": "公司命名来源", "image": ""},
    ],
    "positions": [],
}

# ── 人物简介 ──────────────────────────────────────────────────────────────────
intro = """埃隆·马斯克，1971年生于南非，是当代最具争议也最具影响力的科技企业家。他同时掌舵特斯拉,SpaceX,X（原推特）,Neuralink 和 xAI 等多家颠覆性公司，横跨电动汽车,航天,社交媒体,脑机接口和人工智能等领域，被视为21世纪最接近"钢铁侠"原型的现实人物。

马斯克的独特之处在于他将"人类文明存续"作为终极使命驱动力——SpaceX 的目标是让人类成为多星球物种，特斯拉的使命是加速全球向可持续能源的转型。他不是典型的商人，而是一个用商业手段推进宏大愿景的工程师型创始人。

他的成功路径充满戏剧性：从南非移民到加拿大，靠奖学金读完宾夕法尼亚大学，辍学创业，经历 Zip2 和 PayPal 的成功套现，随后将全部身家押注在"几乎必然失败"的 SpaceX 和特斯拉上，在2008年金融危机最黑暗的时刻险些同时破产，最终逆转成为全球首富。这段经历本身就是关于极端风险承受能力和执行力的最佳案例。"""

# ── 生平时间线 ────────────────────────────────────────────────────────────────
timeline = [
    {"year": "1971", "title": "出生于南非", "desc": "6月28日出生于南非比勒陀利亚，父亲是工程师，母亲梅耶·马斯克是营养师兼模特。"},
    {"year": "1983", "title": "自学编程卖游戏", "desc": "12岁自学 BASIC 编程，将自制游戏《Blastar》以500美元卖给一家杂志，展现出早期的商业天赋。"},
    {"year": "1989", "title": "移民加拿大", "desc": "18岁独自移民加拿大，靠打零工维生，后获得皇后大学奖学金。"},
    {"year": "1992", "title": "转学宾夕法尼亚大学", "desc": "转入宾夕法尼亚大学，获得经济学和物理学双学位，开始思考影响人类未来的关键问题。"},
    {"year": "1995", "title": "创立 Zip2", "desc": "与弟弟金博尔共同创立 Zip2，为报纸提供在线城市指南，后以3.07亿美元出售给康柏，马斯克个人获得2200万美元。"},
    {"year": "1999", "title": "创立 X.com", "desc": "创立在线金融服务公司 X.com，后与 Confinity 合并，更名为 PayPal，2002年以15亿美元出售给 eBay。"},
    {"year": "2002", "title": "创立 SpaceX", "desc": "将 PayPal 套现所得的1亿美元投入 SpaceX，目标是降低太空旅行成本，最终实现人类移民火星。"},
    {"year": "2004", "title": "投资特斯拉", "desc": "以630万美元领投特斯拉 A 轮融资，成为董事长，后出任 CEO，将特斯拉从一家小型初创公司打造成全球最有价值的汽车品牌。"},
    {"year": "2008", "title": "濒临破产", "desc": "金融危机中 SpaceX 前三次发射均失败，特斯拉资金告急，马斯克将最后一笔钱同时押注两家公司，险些全部破产。"},
    {"year": "2008", "title": "猎鹰1号成功入轨", "desc": "第四次发射猎鹰1号成功入轨，成为首枚私人研发的液体燃料火箭，SpaceX 随即获得 NASA 16亿美元合同。"},
    {"year": "2012", "title": "龙飞船对接空间站", "desc": "SpaceX 龙飞船成为首艘与国际空间站对接的私人飞船，开创商业航天新纪元。"},
    {"year": "2015", "title": "猎鹰9号一级回收", "desc": "猎鹰9号一级火箭首次成功垂直回收，实现火箭可重复使用，将发射成本降低90%以上。"},
    {"year": "2020", "title": "载人龙飞船首飞", "desc": "SpaceX 载人龙飞船将宇航员送上国际空间站，美国时隔9年重获载人航天能力。"},
    {"year": "2021", "title": "全球首富", "desc": "特斯拉股价飙升，马斯克超越贝索斯成为全球首富，净资产一度超过3000亿美元。"},
    {"year": "2022", "title": "收购推特", "desc": "以440亿美元收购推特，将其更名为 X，大幅裁员并推行激进改革，引发广泛争议。"},
    {"year": "2023", "title": "创立 xAI", "desc": "创立人工智能公司 xAI，推出 Grok 大语言模型，正式进入 AI 竞争赛道。"},
    {"year": "2024", "title": "星舰成功试飞", "desc": "SpaceX 星舰（Starship）完成多次成功试飞，并实现超重型助推器的机械臂回收，为火星移民奠定基础。"},
]

# ── 核心思想 ──────────────────────────────────────────────────────────────────
core_ideas = [
    {
        "title": "第一性原理思维",
        "desc": "不从类比出发，而是从最基本的物理事实和逻辑推导结论。马斯克认为大多数人的思维是【类比思维】——【别人都这么做，所以我也这么做】，而第一性原理思维能突破行业惯例，找到真正的解决方案。",
        "example": "分析火箭成本时，他从原材料价格出发重新计算，发现火箭造价可以降低到传统价格的2%，由此确信 SpaceX 的商业模式可行。"
    },
    {
        "title": "极端风险承受能力",
        "desc": "马斯克将【失败的可能性】视为必须接受的代价，而非需要规避的风险。他在2008年同时将最后的资金押注在两家濒临破产的公司上，这种极端的风险偏好是他能做到别人不敢做的事情的根本原因。",
        "example": "2008年金融危机时，他将最后4000万美元同时注入特斯拉和 SpaceX，并公开表示：如果失败，我会一无所有。"
    },
    {
        "title": "使命驱动而非利润驱动",
        "desc": "马斯克的所有商业决策都服务于两个终极使命：让人类成为多星球物种（SpaceX），以及加速可持续能源转型（特斯拉）。这种使命感使他能够承受常人无法忍受的压力和失败。",
        "example": "特斯拉上市后，他拒绝了多次高价收购要约，坚持独立运营，因为他认为被收购会偏离加速电动车普及的使命。"
    },
    {
        "title": "迭代速度即竞争优势",
        "desc": "马斯克相信快速迭代和接受失败是技术进步的最快路径。SpaceX 的[快速失败,快速学习]文化使其在火箭技术上的进步速度远超传统航天机构。",
        "example": "星舰的多次爆炸被马斯克公开称为[成功的测试]，每次失败都带来关键数据，最终实现了超重型助推器的机械臂回收。"
    },
    {
        "title": "垂直整合控制关键技术",
        "desc": "马斯克倾向于自己制造核心零部件，而非依赖供应链。特斯拉自研电池,芯片,软件；SpaceX 自研发动机,火箭,飞船。这种垂直整合虽然初期成本高，但长期带来成本优势和技术护城河。",
        "example": "特斯拉自研 FSD 芯片，拒绝使用英伟达现成方案，最终实现了比外购方案性能高出21倍,成本更低的自动驾驶芯片。"
    },
    {
        "title": "物理学思维框架",
        "desc": "马斯克将物理学的思维方式应用于商业和工程决策，用[白痴指数]（实际成本/原材料成本）衡量制造效率，用能量守恒等物理原理评估技术方案的可行性上限。",
        "example": "他用[白痴指数]发现特斯拉某零件的制造成本是原材料成本的1000倍，随即要求工程师重新设计，最终将成本降低了80%。"
    },
]

# ── 经典语录 ──────────────────────────────────────────────────────────────────
quotes = [
    {
        "text_zh": "当某件事足够重要，即使胜算不大，你也应该去做。",
        "text_en": "When something is important enough, you do it even if the odds are not in your favor.",
        "source": "TED 演讲",
        "year": "2013"
    },
    {
        "text_zh": "失败是一种选择。如果你没有失败，说明你创新得还不够。",
        "text_en": "Failure is an option here. If things are not failing, you are not innovating enough.",
        "source": "采访",
        "year": "2005"
    },
    {
        "text_zh": "我认为有可能创造一种让人们真正喜爱的电动汽车。",
        "text_en": "I think it's possible to create an electric car that people actually love.",
        "source": "特斯拉早期采访",
        "year": "2006"
    },
    {
        "text_zh": "持续性是非常重要的。你不应该放弃，除非你被迫放弃。",
        "text_en": "Persistence is very important. You should not give up unless you are forced to give up.",
        "source": "斯坦福大学演讲",
        "year": "2003"
    },
    {
        "text_zh": "我宁愿乐观地尝试某件事，然后失败，也不愿悲观地什么都不做。",
        "text_en": "I'd rather be optimistic and wrong than pessimistic and right.",
        "source": "推特",
        "year": "2019"
    },
    {
        "text_zh": "如果你早上醒来，觉得未来会很美好，那就是美好的一天。如果你早上醒来，觉得未来不会很美好，那就是糟糕的一天。",
        "text_en": "If you wake up in the morning and think the future is going to be better, it is a beautiful day.",
        "source": "采访",
        "year": "2014"
    },
    {
        "text_zh": "我们正在努力让人类成为多星球物种，这是我们这个时代最重要的事情。",
        "text_en": "We're working to make humanity a multi-planetary species, which is the most important thing of our time.",
        "source": "SpaceX 发布会",
        "year": "2016"
    },
    {
        "text_zh": "第一步是确认某件事是可能的，然后概率就会出现。",
        "text_en": "The first step is to establish that something is possible, then probability will occur.",
        "source": "采访",
        "year": "2012"
    },
]

# ── 延伸阅读 ──────────────────────────────────────────────────────────────────
further_reading = [
    {
        "title": "埃隆·马斯克传",
        "type": "书籍",
        "author": "沃尔特·艾萨克森",
        "desc": "授权传记，作者与马斯克深度访谈两年，详述其成长历程与商业帝国的建立过程。",
        "reason": "最权威的一手传记，2023年出版，覆盖推特收购等最新事件"
    },
    {
        "title": "硅谷钢铁侠",
        "type": "书籍",
        "author": "阿什利·万斯",
        "desc": "第一本深度马斯克传记，详细记录了 SpaceX 和特斯拉从濒临破产到逆转的全过程。",
        "reason": "经典传记，对早期创业历程的记录最为详尽"
    },
    {
        "title": "How Elon Musk Became the Real-Life Iron Man",
        "type": "纪录片",
        "author": "60 Minutes",
        "desc": "CBS 60分钟节目对马斯克的深度专访，涵盖 SpaceX 和特斯拉的核心理念。",
        "reason": "最经典的马斯克访谈之一，可在 YouTube 免费观看"
    },
    {
        "title": "Elon Musk: The Mind Behind Tesla, SpaceX, SolarCity",
        "type": "演讲",
        "author": "TED",
        "desc": "马斯克在 TED 的演讲，阐述第一性原理思维和对人类未来的思考。",
        "reason": "直接听马斯克讲述其核心思维方式，时长约22分钟"
    },
    {
        "title": "Wait But Why: The Cook and the Chef",
        "type": "文章",
        "author": "Tim Urban",
        "desc": "深度解析马斯克思维方式的长文，用[厨师与厨师长]的比喻解释第一性原理。",
        "reason": "目前最好的马斯克思维方式解析文章，waitbutwhy.com 免费阅读"
    },
    {
        "title": "马斯克的 X（推特）账号",
        "type": "社交媒体",
        "author": "@elonmusk",
        "desc": "马斯克本人的推特账号，实时发布其对科技,政治,AI 等话题的看法。",
        "reason": "了解马斯克最新动态和即时思考的第一手来源"
    },
]

# ── 渲染并保存 ────────────────────────────────────────────────────────────────
print("🎨 正在渲染马斯克专题页面...")
html = render(
    basic=basic,
    intro=intro,
    timeline=timeline,
    core_ideas=core_ideas,
    quotes=quotes,
    further_reading=further_reading,
)

output_path = save(html, "埃隆·马斯克")
print(f"✅ 生成完成！")
print(f"📄 文件路径：{output_path}")
print(f"\n用浏览器打开以上文件即可查看专题页面")
