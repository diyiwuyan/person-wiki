# 🧠 Person Wiki — 人物专题学习工具

> 输入任意人名，自动生成精美的人物专题学习网站。

**在线演示：** [埃隆·马斯克专题页](https://diyiwuyan.github.io/person-wiki/output/%E5%9F%83%E9%9A%86_%E9%A9%AC%E6%96%AF%E5%85%8B.html)

![预览](https://img.shields.io/badge/demo-live-brightgreen) ![Python](https://img.shields.io/badge/python-3.8+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ 功能特性

- **多源数据采集**：Wikipedia（中英文）、Wikidata SPARQL、百度百科
- **LLM 智能提炼**：人物简介、生平时间线、核心思想、经典语录、延伸阅读
- **精美单页网站**：深空金属感暗色主题（深蓝 + 金色），响应式布局
- **图片画廊**：头像 + 5 张主题图，全部本地化（无防盗链问题）
- **延伸阅读链接**：书籍、纪录片、演讲、访谈，含外部跳转链接
- **零依赖部署**：生成的 HTML 文件可直接用浏览器打开，无需服务器

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install openai
```

### 2. 配置 LLM

编辑 `user_config.json`，填入你的 API Key（支持 OpenAI、DeepSeek、Moonshot 等任何兼容接口）：

```json
{
  "api_key": "你的API Key",
  "base_url": "https://api.deepseek.com/v1",
  "model": "deepseek-chat"
}
```

> 如果你是美团内部用户，设置环境变量 `FRIDAY_APP_ID` 即可直接使用 Friday LLM，无需额外配置。

### 3. 生成专题页

```bash
cd src
python main.py "埃隆·马斯克" "Elon Musk"
python main.py "史蒂夫·乔布斯" "Steve Jobs"
python main.py "查理·芒格" "Charlie Munger"
python main.py "理查德·费曼" "Richard Feynman"
```

生成的 HTML 文件保存在 `output/` 目录，用浏览器直接打开即可。

### 4. 快速演示（无需 LLM）

```bash
python generate_musk_demo.py
```

使用预置的马斯克内容，无需调用 LLM，秒级生成。

---

## 📁 项目结构

```
person-wiki/
├── src/
│   ├── main.py           # 主入口（完整流程）
│   ├── data_fetcher.py   # 数据采集层
│   ├── llm_enricher.py   # LLM 提炼层
│   ├── renderer.py       # HTML 渲染层
│   ├── llm_client.py     # LLM 客户端（多接口兼容）
│   └── config.py         # 配置
├── templates/
│   └── person.html       # HTML 模板
├── output/               # 生成的 HTML 文件
│   └── images/           # 本地化图片
├── skill/                # CatDesk Skill（AI 助手集成）
│   └── SKILL.md
├── generate_musk_demo.py # 马斯克演示脚本
├── user_config.json      # LLM 配置示例
└── README.md
```

---

## 🤖 CatDesk Skill 集成

本项目包含 [CatDesk](https://catdesk.meituan.com) Skill，安装后可直接对 AI 说：

> "帮我生成史蒂夫·乔布斯的专题页"

AI 会自动完成采集 → 提炼 → 渲染的全流程。

**安装方式：**
1. 将 `skill/` 目录复制到 `~/.catpaw/skills/person-wiki/`
2. 重启 CatDesk，即可使用

---

## 🔧 LLM 兼容性

| 接口 | 配置方式 |
|------|---------|
| OpenAI (GPT-4o 等) | `base_url: https://api.openai.com/v1` |
| DeepSeek | `base_url: https://api.deepseek.com/v1` |
| Moonshot (Kimi) | `base_url: https://api.moonshot.cn/v1` |
| 本地 Ollama | `base_url: http://localhost:11434/v1` |
| 美团 Friday（内部） | 设置环境变量 `FRIDAY_APP_ID` |

---

## 📄 License

MIT License — 自由使用、修改、分发。

---

## 🙏 致谢

数据来源：[Wikipedia](https://wikipedia.org) · [Wikidata](https://wikidata.org) · [百度百科](https://baike.baidu.com)
