# 高级搜索语法完整参考

## 通用语法

| 语法 | 示例 | 适用引擎 |
|------|------|----------|
| `site:` | `site:github.com react` | Google, 百度, 必应, DuckDuckGo |
| `filetype:` | `filetype:pdf 机器学习` | Google, 百度, 必应 |
| `""` | `"深度学习"` | 所有引擎 |
| `-` | `apple -fruit` | 所有引擎 |
| `OR` | `cat OR dog` | Google, 必应, DuckDuckGo |
| `intitle:` | `intitle:教程 Python` | Google, 百度 |
| `inurl:` | `inurl:blog AI` | Google, 百度 |
| `*` | `how to * in Python` | Google |

## 时间过滤

### Google
```
&tbs=qdr:h    # 过去一小时
&tbs=qdr:d    # 过去一天
&tbs=qdr:w    # 过去一周
&tbs=qdr:m    # 过去一月
&tbs=qdr:y    # 过去一年
```

### 百度
```
&gpc=stf={start_ts}%7C{end_ts}   # 自定义时间范围
&ft=1                              # 最近一天
&ft=2                              # 最近一周
&ft=7                              # 最近一月
```

### 必应
```
&filters=ex1:"ez1"    # 过去一天
&filters=ex1:"ez2"    # 过去一周
&filters=ex1:"ez3"    # 过去一月
```

## DuckDuckGo Bang 快捷方式

| Bang | 目标 | 示例 |
|------|------|------|
| `!g` | Google | `!g python tutorial` |
| `!gh` | GitHub | `!gh tensorflow` |
| `!so` | Stack Overflow | `!gso python async` |
| `!w` | Wikipedia | `!w machine learning` |
| `!yt` | YouTube | `!yt coding tutorial` |
| `!r` | Reddit | `!r programming` |
| `!b` | 百度 | `!b 深度学习` |

## 特殊搜索

### WolframAlpha（知识计算）
```
integrate x^2 dx          # 数学积分
100 USD to CNY            # 汇率转换
AAPL stock                # 股票信息
weather in Beijing        # 天气查询
population of China       # 人口数据
```

### 组合搜索技巧
```
# GitHub 项目搜索
site:github.com "open source" stars:>100 language:python

# 学术论文搜索
"machine learning" filetype:pdf site:arxiv.org

# 技术文档
site:docs.python.org "async await"

# 新闻搜索
AI 新闻 tbs=qdr:w    # Google: 过去一周的AI新闻
```
