# 图片处理指南

## 图片来源策略

人物专题页面使用**本地化图片**（避免防盗链问题），图片存放在 `output/images/` 目录。

### 头像图片

优先从 **Wikipedia REST API** 获取：
```
https://en.wikipedia.org/api/rest_v1/page/summary/{英文名}
```
返回 JSON 中的 `thumbnail.source` 和 `originalimage.source` 字段。

### 主题图片

使用 **Unsplash Source API**（无需 Key）：
```
https://source.unsplash.com/800x600/?{关键词}&sig={随机数}
```

### Wikimedia Commons 直接下载

对于知名人物，可直接使用 Wikimedia Commons 的缩略图 URL：
```
https://upload.wikimedia.org/wikipedia/commons/thumb/{hash}/{filename}/{width}px-{filename}
```

注意：需要使用正确的 User-Agent，避免 429 错误。

## 图片命名规范

```
output/images/
├── {人名}_avatar.jpg    # 头像（正方形或竖版，用于页面顶部）
├── {人名}_main.jpg      # 主图（宽版，用于 Hero 区域）
├── {人名}_img1.jpg      # 画廊图 1
├── {人名}_img2.jpg      # 画廊图 2
└── {人名}_img3.jpg      # 画廊图 3
```

人名使用中文，去掉空格和中间点（·），例如：
- 埃隆·马斯克 → `埃隆马斯克_avatar.jpg`
- 史蒂夫·乔布斯 → `史蒂夫乔布斯_avatar.jpg`

## HTML 模板中的图片引用

模板使用相对路径引用图片：
```html
<img src="images/{人名}_avatar.jpg" alt="头像">
```

这样 HTML 文件和 images/ 目录在同一层级时，图片可以正常显示（包括 file:// 协议）。

## 常见问题

**Wikipedia 图片 429 错误**：Wikimedia 对直接下载有频率限制，需要：
1. 使用正确的 User-Agent（包含联系邮箱）
2. 使用 thumbnail 步骤 URL（`/thumb/` 路径）
3. 降低请求频率

**Unsplash 图片不相关**：Unsplash Source API 的搜索精度有限，对于非英语人名效果较差。建议使用英文关键词，或手动替换为更合适的图片。
