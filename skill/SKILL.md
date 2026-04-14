---
name: person-wiki
description: 人物专题学习工具。输入任意人名（中文或英文），自动从 Wikipedia、Wikidata、百度百科多源采集数据，经 LLM 提炼后生成精美的单页专题网站，包含：人物简介、生平时间线、核心思想、经典语录、延伸阅读（含跳转链接）、图片画廊。生成的 HTML 文件可直接用浏览器打开。当用户说"帮我生成XX的专题页"、"做一个关于XX的学习页面"、"生成XX的人物介绍网站"、"我想了解XX，帮我做个专题"、"person wiki"、"人物专题"、"人物学习页"时使用。即使用户只是说"帮我做个马斯克的页面"、"生成乔布斯专题"、"XX的人物介绍"也应触发。
---

# 人物专题学习工具 (Person Wiki)

根据用户输入的人名，自动生成一个精美的人物专题学习网站。

## 工具位置

核心工具位于：`M:\cat分身\代理\person-wiki\`

```
person-wiki/
├── src/
│   ├── main.py          # 主入口（完整流程）
│   ├── data_fetcher.py  # 数据采集（Wikipedia + Wikidata + 百度百科）
│   ├── llm_enricher.py  # LLM 提炼（简介/时间线/核心思想/语录/延伸阅读）
│   ├── renderer.py      # HTML 渲染
│   ├── llm_client.py    # LLM 客户端（Friday 优先，支持自定义）
│   └── config.py        # 配置
├── templates/
│   └── person.html      # HTML 模板（深空金属感暗色主题）
├── output/              # 生成的 HTML 文件输出目录
│   └── images/          # 本地化图片目录
└── generate_musk_demo.py # 马斯克演示脚本（预置内容，无需 LLM）
```

## 执行流程

### Step 1：确认人名

从用户消息中提取：
- **中文名**（如"埃隆·马斯克"）
- **英文名**（如"Elon Musk"，用于 Wikipedia 英文版和 Wikidata 查询）

如果用户只给了中文名，尝试推断英文名；如果是纯英文名，中文名留空即可。

### Step 2：运行生成脚本

```powershell
cd "M:\cat分身\代理\person-wiki\src"
python main.py "中文名" "English Name"
```

**示例：**
```powershell
cd "M:\cat分身\代理\person-wiki\src"
python main.py "埃隆·马斯克" "Elon Musk"
```

```powershell
cd "M:\cat分身\代理\person-wiki\src"
python main.py "史蒂夫·乔布斯" "Steve Jobs"
```

```powershell
cd "M:\cat分身\代理\person-wiki\src"
python main.py "查理·芒格" "Charlie Munger"
```

脚本会自动：
1. 从 Wikipedia（中英文）、Wikidata、百度百科采集数据
2. 调用 LLM 提炼简介、时间线、核心思想、语录、延伸阅读
3. 渲染为精美 HTML 页面
4. 保存到 `output/<人名>.html`

### Step 3：处理图片（可选增强）

如果需要为新人物下载真实图片，运行图片下载脚本：

```powershell
cd "M:\cat分身\代理\person-wiki"
python scripts/download_images.py "人名" "English Name"
```

详见 `references/image_guide.md`。

### Step 4：告知用户结果

生成完成后，告诉用户：
- 文件路径（绝对路径）
- 用浏览器打开即可查看
- 可以用 `start` 命令直接打开：`start "M:\cat分身\代理\person-wiki\output\人名.html"`

## LLM 配置

工具优先使用 Friday 内部 LLM（需要设置环境变量 `FRIDAY_APP_ID`）。

如果 Friday 不可用，会自动引导用户输入 OpenAI 兼容接口配置（API Key、Base URL、模型名）。配置保存在 `user_config.json`，下次无需重复输入。

**快速配置方式：**
```powershell
$env:FRIDAY_APP_ID = "你的Friday App ID"
cd "M:\cat分身\代理\person-wiki\src"
python main.py "人名" "English Name"
```

## 常见问题处理

**Q: Wikipedia 访问超时？**
工具会自动降级到百度百科 + Friday 搜索补充，最终 LLM 会基于自身知识生成内容。

**Q: 图片不显示？**
HTML 使用相对路径引用 `images/` 目录下的本地图片，需确保 `output/images/` 目录存在且有图片文件。

**Q: LLM 返回 None？**
Friday 图片 App ID 不支持对话，需要申请 LLM 专用 App ID，或使用 OpenAI 兼容接口。

**Q: 想快速看效果（不调用 LLM）？**
运行演示脚本（马斯克预置内容）：
```powershell
cd "M:\cat分身\代理\person-wiki"
python generate_musk_demo.py
```

## 输出效果

生成的 HTML 页面特性：
- 深空金属感暗色主题（深蓝 + 金色）
- 响应式单页布局
- 包含：头像 + 图片画廊、人物简介、生平时间线、核心思想卡片、经典语录、延伸阅读（含外链）
- 所有图片本地化（不依赖外网图片链接）
- 可直接用浏览器打开，无需服务器
