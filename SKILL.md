---
name: "kais-search"
description: "统一搜索聚合引擎，融合网页搜索（16引擎+智能降级）、图片搜索（以图搜图+文字搜图）、视频搜索（抖音+B站+YouTube）。中文国内引擎优先，自动降级兜底。触发词：搜索、search、搜一下、查一下、找一下、帮我搜、帮我查、google一下、百度一下、搜图、找图片、图片搜索、image search、以图搜图、reverse image search、找图源、搜视频、找视频、视频搜索、video search、抖音搜、B站搜、聚合搜索、multi search、全网搜索、搜一搜。"
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

| 优先级 | 引擎 | URL 模板 | 说明 |
|--------|------|----------|------|
| P0 | 百度 | `https://www.baidu.com/s?wd={kw}` | 国内覆盖最广 |
| P0 | 必应CN | `https://cn.bing.com/search?q={kw}&ensearch=0` | 结果质量高 |
| P1 | 360 | `https://www.so.com/s?q={kw}` | 兜底 |
| P1 | 搜狗 | `https://sogou.com/web?query={kw}` | 微信公众号内容 |
| P2 | 神马 | `https://m.sm.cn/s?q={kw}` | 移动端补充 |
| P3 | 必应INT | `https://cn.bing.com/search?q={kw}&ensearch=1` | 国际补充 |

**英文/其他查询 → 国际引擎（按优先级排序）：**

| 优先级 | 引擎 | URL 模板 | 说明 |
|--------|------|----------|------|
| P0 | DuckDuckGo | `https://duckduckgo.com/html/?q={kw}` | 无追踪，免Cookie |
| P0 | Brave | `https://search.brave.com/search?q={kw}` | 独立索引 |
| P1 | Google | `https://www.google.com/search?q={kw}` | 覆盖最广（需代理） |
| P1 | Startpage | `https://www.startpage.com/sp/search?query={kw}` | Google结果+隐私 |
| P2 | Yahoo | `https://search.yahoo.com/search?p={kw}` | 补充 |
| P2 | Ecosia | `https://www.ecosia.org/search?q={kw}` | 环保引擎 |
| P3 | Qwant | `https://www.qwant.com/?q={kw}` | GDPR合规 |

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
兜底：web_search 内置工具
```

**执行规则：**
- 每轮内 2 个引擎并发请求
- 请求间 1-2 秒延迟（尊重服务器）
- 单个引擎超时 10 秒
- 403/429 时访问首页获取 Cookie 后重试一次（2秒延迟）
- **任一引擎成功即停止降级**，用成功引擎的结果

### Step 3：结果聚合

- 成功引擎结果合并
- 按 URL 去重
- 按相关性排序输出
- 格式：标题 + URL + 摘要

### Step 4：兜底

所有 web_fetch 引擎均失败时，使用 `web_search` 内置工具作为最终兜底。

---

## 图片搜索流程

### 文字搜图

| 优先级 | 引擎 | URL 模板 |
|--------|------|----------|
| P0 | 百度图片 | `https://image.baidu.com/search/index?tn=baiduimage&word={kw}` |
| P0 | 必应图片 | `https://cn.bing.com/images/search?q={kw}` |
| P1 | DuckDuckGo | `https://duckduckgo.com/html/?q={kw}&iax=images&ia=images` |

### 以图搜图（需提供图片 URL 或路径）

| 优先级 | 引擎 | 说明 |
|--------|------|------|
| P0 | 百度以图搜图 | `https://image.baidu.com/n/pc_search?queryImageUrl={url}` |
| P1 | Yandex | `https://yandex.com/images/search?rpt=imageview&url={url}` |
| P2 | Google Lens | `https://lens.google.com/uploadbyurl?url={url}` |

降级策略同网页搜索：P0 → P1 → P2。

---

## 视频搜索流程

| 平台 | 优先级 | URL 模板 | 说明 |
|------|--------|----------|------|
| B站 | P0 | `https://search.bilibili.com/all?keyword={kw}` | 无需API，国内首选 |
| 抖音 | P1 | `https://www.douyin.com/search/{kw}` | 需要浏览器解析 |
| YouTube | P2 | `https://www.youtube.com/results?search_query={kw}` | 需代理 |

**搜索结果提取：**
- B站：提取视频标题、UP主、播放量、时长
- 抖音：提取视频标题、作者、点赞数
- YouTube：提取视频标题、频道、观看次数

降级策略：B站 → 抖音 → YouTube，任一成功即停止。

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

**时间过滤（Google/百度）：**

| 参数 | 含义 |
|------|------|
| `tbs=qdr:d` | 过去一天 |
| `tbs=qdr:w` | 过去一周 |
| `tbs=qdr:m` | 过去一月 |
| `tbs=qdr:y` | 过去一年 |

---

## 输出格式

### 网页搜索结果

```markdown
## 🔍 搜索结果：{关键词}

### 来源：{引擎名称}

1. **[标题]({url})**
   > 摘要内容…

2. **[标题]({url})**
   > 摘要内容…

---
> 共 {N} 条结果，来自 {M} 个引擎 | 耗时 {T}s
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
1. **[标题]({url})** — UP: {作者} | ▶ {播放量} | ⏱ {时长}

### 抖音
1. **[标题]({url})** — 作者: {name} | ❤ {点赞}

---
> 共 {N} 个视频，来自 {M} 个平台
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

## 安全与隐私

- 不收集用户个人信息
- 不持久化 Cookie 或搜索历史
- 不向第三方传输数据
- 用户需遵守目标引擎的使用条款

---

## 参考文档

- `references/engine-details.md` — 各引擎详细参数和注意事项
- `references/advanced-operators.md` — 高级搜索语法完整参考
