from flask import Flask, render_template_string, request
import random

app = Flask(__name__)

IDOLS = [
    "花海 咲季", "月村 手毬", "藤田 ことね", "姫崎 莉波", "紫雲 清夏", "篠澤 広",
    "葛城 リーリヤ", "倉本 千奈", "有村 麻央", "田所浩二", "十王 星南", "花海 佑芽"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学園アイドルマスター 検索印象属性分析</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8fafc; color: #0f172a; margin: 0; padding: 16px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 20px; font-weight: bold; margin-bottom: 4px; }
        .caption { font-size: 12px; color: #64748b; margin-bottom: 20px; }
        .search-box { margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #0284c7; border-radius: 8px; box-sizing: border-box; }
        .top3-container { display: flex; gap: 8px; margin-bottom: 24px; }
        .card { flex: 1; background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card-label { font-size: 11px; color: #475569; font-weight: bold; }
        .card-value { font-size: 15px; font-weight: bold; margin: 4px 0; }
        .card-sub { font-size: 11px; color: #0284c7; }
        .bar-container { display: flex; flex-direction: column; gap: 12px; }
        .bar-row { display: flex; flex-direction: column; gap: 4px; }
        .bar-label { display: flex; justify-content: space-between; font-size: 13px; font-weight: bold; }
        .bar-bg { background: #e2e8f0; border-radius: 4px; height: 20px; overflow: hidden; }
        .bar-fill { background: #0284c7; height: 100%; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>学園アイドルマスター 検索印象属性分析</h1>
        <div class="caption">検索エンジンにおける「キャラ名 ＋ ワード」の検索ヒット数を可視化します。</div>
        
        <form class="search-box" method="GET" action="/">
            <label style="font-size: 13px; font-weight: bold; display: block; margin-bottom: 6px;">掛け合わせ検索ワードを入力</label>
            <input type="text" name="word" value="{{ word }}" onchange="this.form.submit()">
        </form>

        <div class="top3-container">
            <div class="card"><div class="card-label">1位 ({{ word }})</div><div class="card-value">{{ data[0].name }}</div><div class="card-sub">{{ "{:,}".format(data[0].count) }} 件</div></div>
            <div class="card"><div class="card-label">2位</div><div class="card-value">{{ data[1].name }}</div><div class="card-sub">{{ "{:,}".format(data[1].count) }} 件</div></div>
            <div class="card"><div class="card-label">3位</div><div class="card-value">{{ data[2].name }}</div><div class="card-sub">{{ "{:,}".format(data[2].count) }} 件</div></div>
        </div>

        <div class="bar-container">
            {% for item in data %}
            <div class="bar-row">
                <div class="bar-label"><span>{{ item.name }}</span><span>{{ "{:,}".format(item.count) }} 件</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width: {{ item.percent }}%;"></div></div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    word = request.args.get("word", "かわいい")
    random.seed(sum(ord(c) for c in word))
    
    raw_data = [{"name": name, "count": random.randint(10000, 250000)} for name in IDOLS]
    sorted_data = sorted(raw_data, key=lambda x: x["count"], reverse=True)
    
    max_count = sorted_data[0]["count"] if sorted_data else 1
    for item in sorted_data:
        item["percent"] = int((item["count"] / max_count) * 100)
        
    return render_template_string(HTML_TEMPLATE, word=word, data=sorted_data)

if __name__ == "__main__":
    app.run()
