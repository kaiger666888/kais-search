---
name: "kais-search"
description: "统一搜索聚合引擎，融合网页搜索（16引擎+智能降级）、图片搜索（以图搜图+文字搜图）、视频搜索（抖音+B站+YouTube）。中文国内引擎优先，需代理的引擎自动走代理，自动降级兜底。触发词：搜索、search、搜一下、查一下、找一下、帮我搜、帮我查、google一下、百度一下、搜图、找图片、图片搜索、image search、以图搜图、reverse image search、找图源、搜视频、找视频、视频搜索、video search、抖音搜、B站搜、聚合搜索、multi search、全网搜索、搜一搜。"
---

# kais-search

统一搜索聚合引擎——网页、图片、视频一个 Skill 搞定。

## 触发条件

| 搜索类型 | 触发词/场景 |
|----------|------------|
| 网页搜索 | "搜索…""查一下…""找…""search…" |
| 图片搜索 | "搜图…""找图片…""图片搜索…" |
| 以图搜图 | "以图搜图""reverse image""找图片来源" |
| 视频搜索 | "搜视频…""找视频…""抖音搜…""B站搜…" |

未明确指定类型时，默认执行**网页搜索**。

---

## 代理策略

<!-- FREEDOM:low -->

本机代理地址：`http://127.0.0.1:7890`（mihomo/clash）

**需要代理的引擎（国内无法直连）：**

| 引擎 | 代理 | 说明 |
|------|------|------|
| Google | ✅ 必须 | 完全屏蔽 |
| Google HK | ✅ 必须 | 完全屏蔽 |
| DuckDuckGo | ✅ 必须 | HTML版302跳转 |
| Brave Search | ✅ 必须 | 直连失败 |
| YouTube | ✅ 必须 | 完全屏蔽 |
| Google Lens | ✅ 必须 | 完全屏蔽 |
| Yandex | ⚠️ 视情况 | 偶尔可直连 |
| Startpage | ✅ 必须 | 基于 Google |

**无需代理的引擎（国内直连）：**

| 引擎 | 代理 | 说明 |
|------|------|------|
| 百度 | ❌ 直连 | 但有验证码风险 |
| 必应CN | ❌ 直连 | 稳定可用 |
| 360搜索 | ❌ 直连 | 稳定 |
| 搜狗 | ❌ 直连 | 稳定 |
| 神马 | ❌ 直连 | 稳定 |
| B站 | ❌ 直连 | API需Cookie |
| 抖音 | ❌ 直连 | SPA需浏览器 |
| TinEye | ❌ 直连 | 以图搜图备选 |

**执行方式：** `web_fetch` 不走系统代理，需代理的引擎必须用 `exec` + `curl -x http://127.0.0.1:7890` 请求。但 Brave/Google/DuckDuckGo 均为 SPA，curl 拿到的只是 JS bundle，无法提取搜索结果。

**因此国际引擎的实际策略：**
1. **web_search 内置工具**（首选，Brave API 自带代理，直接返回结构化结果）
2. **exec curl -x 代理**（仅对非 SPA 引擎有效，如 Startpage）
3. **browser 工具**（最后手段，完整渲染但速度慢）

<!-- /FREEDOM:low -->

---

## 搜索类型路由

```
用户请求 → 识别搜索类型 → 执行对应流程 → 去重聚合 → 输出结果
```

| 类型 | 流程 |
|------|------|
| 网页搜索 | §网页搜索流程 |
| 图片搜索 | §图片搜索流程 |
| 以图搜图 | §以图搜图流程 |
| 视频搜索 | §视频搜索流程 |

---

## 网页搜索流程

### Step 1：语言检测与引擎选择

检测查询语言，选择对应引擎池：

**中文查询 → 国内引擎（按优先级排序）：**

| 优先级 | 引擎 | URL 模板 | 代理 | 说明 |
|--------|------|----------|------|------|
| P0 | 必应CN | `https://cn.bing.com/search?q={kw}&ensearch=0` | ❌ | 结果质量高，稳定首选 |
| P1 | 360 | `https://www.so.com/s?q={kw}` | ❌ | 兜底 |
| P1 | 搜狗 | `https://sogou.com/web?query={kw}` | ❌ | 微信公众号独有 |
| P2 | 神马 | `https://m.sm.cn/s?q={kw}` | ❌ | 移动端补充 |

**英文/其他查询 → 国际引擎（按优先级排序）：**

| 优先级 | 引擎 | 方式 | 代理 | 说明 |
|--------|------|------|------|------|
| P0 | web_search（Brave API） | 内置工具 | ✅ 自动 | **首选**，自带代理，结构化结果 |
| P1 | Startpage | `exec curl -x` | ✅ 必须 | Google结果+隐私，非SPA |
| P2 | DuckDuckGo | `browser` 工具 | ✅ 必须 | 无追踪，需完整渲染 |
| P3 | Google | `browser` 工具 | ✅ 必须 | 覆盖最广，需完整渲染 |

> ⚠️ Brave/Google/DuckDuckGo 均为 SPA，`web_fetch` 和 `curl` 无法提取搜索结果，只能通过 `web_search` 内置工具或 `browser` 工具获取。

### Step 2：分级执行与降级策略

```
第一轮：P0 引擎（2个并发）
  ↓ 全部失败
第二轮：P1 引擎（2个并发）
  ↓ 全部失败
第三轮：P2 引擎（2个并发）
  ↓ 全部失败
第四轮：P3 引擎（1个）
  ↓ 仍失败
兜底：web_search 内置工具（Brave API，自带代理）
```

**执行规则：**
- 每轮内 2 个引擎并发请求
- 请求间 1-2 秒延迟（尊重服务器）
- 单个引擎超时 10 秒
- 403/429 时访问首页获取 Cookie 后重试一次（2秒延迟）
- **代理引擎先检测代理可用性**，不可用直接跳过
- **任一引擎成功即停止降级**，用成功引擎的结果

### Step 3：结果聚合

- 成功引擎结果合并
- 按 URL 去重
- 按相关性排序输出
- 格式：标题 + URL + 摘要

### Step 4：兜底

所有 web_fetch 引擎均失败时，使用 `web_search` 内置工具作为最终兜底（底层为 Brave Search API，已配置代理）。

---

## 图片搜索流程

### 文字搜图

**脚本：** `scripts/text_image_search.py`

```bash
# 基本搜索
python3 scripts/text_image_search.py "可爱猫咪"

# 指定意图和数量
python3 scripts/text_image_search.py "taylor swift official" --intent official --count 3

# 搜索并下载最佳图片
python3 scripts/text_image_search.py "aurora wallpaper 4k" --download
```

**引擎池：**

| 优先级 | 引擎 | 代理 | 说明 |
|--------|------|------|------|
| P0 | 必应图片 | ❌ | 直连，稳定首选 |
| P1 | 搜狗图片 | ❌ | 直连，补充召回 |

**智能特性：**

| 特性 | 说明 |
|------|------|
| 🎯 意图识别 | 自动分类：meme/official/portrait/wallpaper/avatar |
| 📊 置信度分级 | high→发送最佳图，medium→2-3张候选，low→搜索链接 |
| 🔍 质量过滤 | 拒绝 logo/sprite/缩略图，意图感知排序 |
| 📥 自动下载 | `--download` 下载最佳图片到本地发送 |
| 🔢 参数解析 | 支持 "3张"、"official"、"4k" 等自然语言参数 |

**意图关键词：**

| 意图 | 触发词 |
|------|--------|
| meme | meme、表情包、梗图 |
| official | official、官方、logo、标志、吉祥物 |
| avatar | avatar、头像、profile picture |
| wallpaper | wallpaper、壁纸、4k、hd、高清 |
| portrait | 默认，普通人物/物体 |

### 以图搜图（需提供图片 URL 或本地路径）

**脚本：** `scripts/reverse_image_search.py`

<!-- FREEDOM:low -->
**首次使用需安装依赖：**
```bash
bash scripts/setup.sh
```
<!-- /FREEDOM:low -->

```bash
# Yandex 以图搜图（默认，最稳定）
python3 scripts/reverse_image_search.py "https://example.com/photo.jpg"

# Bing 以图搜图
python3 scripts/reverse_image_search.py "/path/to/local/image.jpg" bing

# 多引擎并行
python3 scripts/reverse_image_search.py "https://example.com/photo.jpg" all
```

**引擎池（基于 PicImageSearch 库）：**

| 优先级 | 引擎 | 代理 | 说明 |
|--------|------|------|------|
| P0 | Yandex | ⚠️ | 人脸识别强，偶不稳定 |
| P1 | Bing | ❌ | 稳定补充 |

**输出：** JSON 结构化结果，包含标题、URL、缩略图、相似度。

**注意：** Google Lens 已废弃 URL 上传方式，不再作为选项。

降级策略同网页搜索：P0 → P1 → P2，任一成功即停止。

---

## 视频搜索流程

<!-- FREEDOM:low -->

**视频平台均为 SPA（单页应用），web_fetch 无法获取动态渲染内容。** 必须使用以下策略：

### 策略 A：web_search 兜底（首选，最稳定）

直接用 `web_search` 搜索，加上平台限定词：
```
web_search(query="site:bilibili.com {关键词}")
web_search(query="site:douyin.com {关键词}")
web_search(query="site:youtube.com {关键词}")
```

### 策略 B：浏览器工具（获取完整结果）

当需要详细数据（播放量、UP主信息等）时，使用 `browser` 工具：
```bash
# B站
browser action=open url="https://search.bilibili.com/all?keyword={kw}"

# 抖音
browser action=open url="https://www.douyin.com/search/{kw}"

# YouTube（需代理 profile）
browser action=open url="https://www.youtube.com/results?search_query={kw}"
```

### 策略 C：平台 API（需 Cookie/Token，最后手段）

| 平台 | API | 限制 |
|------|-----|------|
| B站 | `https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={kw}` | 需 Cookie 验证 |
| YouTube | YouTube Data API v3 | 需 API Key |

### 推荐执行顺序

```
1. web_search("site:bilibili.com {关键词}")  → 快速获取B站结果
2. web_search("site:youtube.com {关键词}")   → 快速获取YouTube结果
3. 如需详细数据 → browser 工具打开页面提取
```

<!-- /FREEDOM:low -->

---

## 高级搜索语法

支持以下语法（适用于支持的引擎）：

| 语法 | 示例 | 说明 |
|------|------|------|
| `site:` | `site:github.com react` | 站内搜索 |
| `filetype:` | `filetype:pdf 报告` | 指定文件类型 |
| `""` | `"机器学习"` | 精确匹配 |
| `-` | `python -snake` | 排除词 |
| `OR` | `cat OR dog` | 或运算 |

**时间过滤：**

| 引擎 | 过去一天 | 过去一周 | 过去一月 | 过去一年 |
|------|----------|----------|----------|----------|
| Google | `tbs=qdr:d` | `tbs=qdr:w` | `tbs=qdr:m` | `tbs=qdr:y` |
| 百度 | `ft=1` | `ft=2` | `ft=7` | 自定义时间戳 |
| 必应 | `filters=ex1:"ez1"` | `filters=ex1:"ez2"` | `filters=ex1:"ez3"` | — |

**DuckDuckGo Bang 快捷方式：**

| Bang | 目标 | 示例 |
|------|------|------|
| `!g` | Google | `!g python tutorial` |
| `!gh` | GitHub | `!gh tensorflow` |
| `!yt` | YouTube | `!yt coding` |
| `!w` | Wikipedia | `!w machine learning` |

---

## 输出格式

### 网页搜索结果

```markdown
## 🔍 搜索结果：{关键词}

1. **[标题]({url})**
   > 摘要内容…
   > 来源：{引擎名称}

2. **[标题]({url})**
   > 摘要内容…
   > 来源：{引擎名称}

---
> 共 {N} 条结果，来自 {M} 个引擎
```

### 图片搜索结果

```markdown
## 🖼️ 图片搜索结果：{关键词}

1. **[图片描述]({url})** — 来源：{网站}
2. **[图片描述]({url})** — 来源：{网站}

---
> 共 {N} 张图片
```

### 视频搜索结果

```markdown
## 🎬 视频搜索结果：{关键词}

### B站
1. **[标题]({url})** — UP: {作者}

### YouTube
1. **[标题]({url})** — 频道: {name}

---
> 共 {N} 个视频
```

---

## Cookie 管理

- **仅内存存储**：运行时动态获取，用完即清
- **按需获取**：仅在 403/429 时访问引擎首页获取
- **不持久化**：不写入任何文件
- **仅会话级**：搜索完成后立即清除

## 速率控制

- 引擎间请求：1-2 秒延迟
- 单引擎超时：10 秒
- 降级重试：最多 1 次（2 秒延迟后）
- 批次大小：每轮 2 个引擎并发

## 脚本工具

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `scripts/text_image_search.py` | 文字搜图：多引擎+意图识别+质量过滤+下载 | 无（纯标准库） |
| `scripts/reverse_image_search.py` | 以图搜图：PicImageSearch 库 | `bash scripts/setup.sh` |
| `scripts/setup.sh` | 安装以图搜图 Python 依赖 | python3 venv |

## 安全与隐私

- 不收集用户个人信息
- 不持久化 Cookie 或搜索历史
- 不向第三方传输数据
- 用户需遵守目标引擎的使用条款

---

## 参考文档

- `references/engine-details.md` — 各引擎详细参数、代理配置、注意事项
- `references/advanced-operators.md` — 高级搜索语法完整参考
