# 引擎详细参数

## 代理配置

- **代理地址**: `http://127.0.0.1:7890`
- **代理软件**: mihomo (clash meta)
- **检测命令**: `curl -s --max-time 5 -x http://127.0.0.1:7890 -o /dev/null -w "%{http_code}" https://www.google.com`
- **返回 200** = 代理可用，**超时/非200** = 代理不可用，跳过需代理引擎

## 国内引擎（直连）

### 必应CN ⭐ 推荐首选
- 网页: `https://cn.bing.com/search?q={kw}&ensearch=0`
- 图片: `https://cn.bing.com/images/search?q={kw}`
- 时间过滤: `&filters=ex1:"ez1"` (一天), `"ez2"` (一周), `"ez3"` (一月)
- 优点: 结果质量高，稳定，反爬宽松
- 注意: 国内可直连，建议作为 P0

### 百度
- 网页: `https://www.baidu.com/s?wd={kw}`
- 图片: `https://image.baidu.com/search/index?tn=baiduimage&word={kw}`
- 以图搜图: `https://image.baidu.com/n/pc_search?queryImageUrl={url}`
- 时间过滤: `&ft=1` (一天), `&ft=2` (一周), `&ft=7` (一月)
- ⚠️ 反爬严格，频繁请求触发验证码
- 建议: 作为备选，不作为首选

### 360搜索
- 网页: `https://www.so.com/s?q={kw}`
- 优点: 对中文理解较好，稳定

### 搜狗
- 网页: `https://sogou.com/web?query={kw}`
- 微信: `https://wx.sogou.com/weixin?type=2&query={kw}`
- 优点: 微信公众号内容独有来源

### 神马
- 网页: `https://m.sm.cn/s?q={kw}`
- 优点: 移动端优先

## 国际引擎（需代理）

### Brave Search ⭐ 推荐首选
- 网页: `https://search.brave.com/search?q={kw}`
- 代理: ✅ 必须
- 优点: 独立索引，隐私优先，代理下稳定可用

### DuckDuckGo
- HTML版: `https://duckduckgo.com/html/?q={kw}`
- 图片: `https://duckduckgo.com/html/?q={kw}&iax=images&ia=images`
- 代理: ✅ 必须
- ⚠️ HTML版首次访问会 302 跳转（需获取 Cookie）
- Bang语法: `!gh tensorflow` → GitHub

### Google
- 网页: `https://www.google.com/search?q={kw}`
- 图片: `https://www.google.com/search?q={kw}&tbm=isch`
- 代理: ✅ 必须
- 时间过滤: `&tbs=qdr:d/w/m/y`
- 优点: 覆盖最广

### Google HK
- 网页: `https://www.google.com.hk/search?q={kw}`
- 代理: ✅ 必须

### Startpage
- 网页: `https://www.startpage.com/sp/search?query={kw}`
- 代理: ✅ 必须
- 优点: Google 结果 + 隐私保护

### Yahoo
- 网页: `https://search.yahoo.com/search?p={kw}`
- 代理: ✅ 必须

### Ecosia
- 网页: `https://www.ecosia.org/search?q={kw}`
- 代理: ✅ 必须
- 优点: 搜索收益用于种树

### Qwant
- 网页: `https://www.qwant.com/?q={kw}`
- 代理: ✅ 必须
- 优点: 欧洲 GDPR 合规

## 视频平台

### B站
- 搜索页: `https://search.bilibili.com/all?keyword={kw}`
- API: `https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={kw}`
- 代理: ❌ 直连
- ⚠️ SPA 应用，web_fetch 无法获取动态内容
- ✅ 推荐: `web_search("site:bilibili.com {kw}")` 或 `browser` 工具

### 抖音
- 搜索页: `https://www.douyin.com/search/{kw}`
- 代理: ❌ 直连
- ⚠️ SPA 应用，JS 渲染，web_fetch 返回空
- ✅ 推荐: `browser` 工具

### YouTube
- 搜索页: `https://www.youtube.com/results?search_query={kw}`
- 代理: ✅ 必须
- ⚠️ SPA 应用
- ✅ 推荐: `web_search("site:youtube.com {kw}")` 或 `browser` 工具

## 图片引擎

### TinEye（以图搜图备选）⭐ 推荐
- URL: `https://tineye.com/search/?url={url}`
- 代理: ❌ 直连
- 优点: 稳定，免费，支持 URL 上传

### Yandex（以图搜图）
- URL: `https://yandex.com/images/search?rpt=imageview&url={url}`
- 代理: ⚠️ 视情况
- 优点: 以图搜图能力强，人脸识别佳
- ⚠️ 偶尔维护中不可用

### ❌ Google Lens（已废弃）
- URL上传方式已废弃（返回 404）
- 不再作为以图搜图选项

## 推荐请求头

```
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
```
