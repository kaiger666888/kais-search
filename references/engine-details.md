# 引擎详细参数

## 国内引擎

### 百度
- 基础 URL: `https://www.baidu.com/s?wd={kw}`
- 图片搜索: `https://image.baidu.com/search/index?tn=baiduimage&word={kw}`
- 以图搜图: `https://image.baidu.com/n/pc_search?queryImageUrl={url}`
- 注意: 反爬严格，需要完整 UA 和 Cookie
- 时间过滤: `&gpc=stf={timestamp}%7C{timestamp}`

### 必应CN
- 基础 URL: `https://cn.bing.com/search?q={kw}&ensearch=0`
- 图片搜索: `https://cn.bing.com/images/search?q={kw}`
- 注意: 国内可直连，结果质量高
- 时间过滤: `&filters=ex1:"ez1"` (过去一天)

### 360搜索
- 基础 URL: `https://www.so.com/s?q={kw}`
- 注意: 对中文理解较好

### 搜狗
- 基础 URL: `https://sogou.com/web?query={kw}`
- 微信搜索: `https://wx.sogou.com/weixin?type=2&query={kw}`
- 注意: 微信公众号内容独有来源

### 神马
- 基础 URL: `https://m.sm.cn/s?q={kw}`
- 注意: 移动端优先，结果偏移动端

## 国际引擎

### DuckDuckGo
- HTML版: `https://duckduckgo.com/html/?q={kw}`
- 图片: `https://duckduckgo.com/html/?q={kw}&iax=images&ia=images`
- 注意: 无追踪，HTML版无Cookie要求，推荐首选
- Bang语法: `!gh tensorflow` → GitHub搜索

### Brave
- 基础 URL: `https://search.brave.com/search?q={kw}`
- 注意: 独立索引，隐私优先

### Google
- 基础 URL: `https://www.google.com/search?q={kw}`
- Google HK: `https://www.google.com.hk/search?q={kw}`
- 时间过滤: `&tbs=qdr:d` (天), `qdr:w` (周), `qdr:m` (月), `qdr:y` (年)
- 注意: 国内需代理

### Startpage
- 基础 URL: `https://www.startpage.com/sp/search?query={kw}`
- 注意: Google结果代理，隐私保护

### Yahoo
- 基础 URL: `https://search.yahoo.com/search?p={kw}`

### Ecosia
- 基础 URL: `https://www.ecosia.org/search?q={kw}`
- 注意: 搜索收益用于种树

### Qwant
- 基础 URL: `https://www.qwant.com/?q={kw}`
- 注意: 欧洲GDPR合规

## 视频平台

### B站
- 搜索: `https://search.bilibili.com/all?keyword={kw}`
- 注意: 无需API，web_fetch可直接解析，国内首选

### 抖音
- 搜索: `https://www.douyin.com/search/{kw}`
- 注意: 反爬严格，可能需要浏览器渲染

### YouTube
- 搜索: `https://www.youtube.com/results?search_query={kw}`
- 注意: 需代理

## 图片引擎

### Yandex
- 以图搜图: `https://yandex.com/images/search?rpt=imageview&url={url}`
- 注意: 以图搜图能力强，人脸识别佳

### Google Lens
- 以图搜图: `https://lens.google.com/uploadbyurl?url={url}`
- 注意: 综合能力最强，需代理

## 推荐请求头

```
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
```
