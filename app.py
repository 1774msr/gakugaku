from flask import Flask, render_template_string, request
import json
import os

app = Flask(__name__)

# 保存されたJSONファイルの読み込み
JSON_PATH = os.path.join(os.path.dirname(__file__), "data.json")

def load_and_process_data():
    if not os.path.exists(JSON_PATH):
        return {}

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # --- R18 と R-18 の統合処理 ---
    if "R18" in raw_data:
        r18_data = raw_data.pop("R18")  # R18を取り出して削除
        if "R-18" in raw_data:
            # R-18が存在する場合は各アイドルの件数を合算
            for idol, count in r18_data.items():
                raw_data["R-18"][idol] = raw_data["R-18"].get(idol, 0) + count
        else:
            raw_data["R-18"] = r18_data

    processed = {}
    for word, idols in raw_data.items():
        total_count = sum(idols.values())
        
        # 検索結果総数が少ない（合計20件未満）ものは排除
        if total_count < 20:
            continue

        # 各アイドルの占有率（％）を計算（小数第1位で四捨五入）
        processed[word] = []
        for name, count in idols.items():
            percent = round((count / total_count) * 100, 1) if total_count > 0 else 0
            processed[word].append({
                "name": name,
                "percent": percent
            })
        
        # 割合が高い順にソート
        processed[word].sort(key=lambda x: x["percent"], reverse=True)

    return processed

# データロード
DATA_STORE = load_and_process_data()

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
        select { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #0284c7; border-radius: 8px; box-sizing: border-box; background-color: #fff; cursor: pointer; }
        .top3-container { display: flex; gap: 8px; margin-bottom: 24px; }
        .card { flex: 1; background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card-label { font-size: 11px; color: #475569; font-weight: bold; }
        .card-value { font-size: 15px; font-weight: bold; margin: 4px 0; }
        .card-sub { font-size: 12px; color: #0284c7; font-weight: bold; }
        .bar-container { display: flex; flex-direction: column; gap: 12px; }
        .bar-row { display: flex; flex-direction: column; gap: 4px; }
        .bar-label { display: flex; justify-content: space-between; font-size: 13px; font-weight: bold; }
        .bar-bg { background: #e2e8f0; border-radius: 4px; height: 20px; overflow: hidden; }
        .bar-fill { background: #0284c7; height: 100%; border-radius: 4px; }
        .notice { font-size: 11px; color: #ef4444; margin-bottom: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>学園アイドルマスター 検索印象属性分析</h1>
        <div class="caption">二次創作検索ワードにおけるアイドル別占有率</div>
        
        <form class="search-box" method="GET" action="/">
            <label style="font-size: 13px; font-weight: bold; display: block; margin-bottom: 6px;">掛け合わせ検索ワードを選択</label>
            <select name="word" onchange="this.form.submit()">
                {% for w in keywords %}
                <option value="{{ w }}" {% if w == current_word %}selected{% endif %}>{{ w }}</option>
                {% endfor %}
            </select>
        </form>

        {% if error %}
        <div class="notice">※{{ error }}</div>
        {% endif %}

        {% if data %}
        <div class="top3-container">
            <div class="card">
                <div class="card-label">1位</div>
                <div class="card-value">{{ data[0].name }}</div>
                <div class="card-sub">{{ data[0].percent }} %</div>
            </div>
            <div class="card">
                <div class="card-label">2位</div>
                <div class="card-value">{{ data[1].name }}</div>
                <div class="card-sub">{{ data[1].percent }} %</div>
            </div>
            <div class="card">
                <div class="card-label">3位</div>
                <div class="card-value">{{ data[2].name }}</div>
                <div class="card-sub">{{ data[2].percent }} %</div>
            </div>
        </div>

        <div class="bar-container">
            {% for item in data %}
            <div class="bar-row">
                <div class="bar-label">
                    <span>{{ item.name }}</span>
                    <span>{{ item.percent }} %</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width: {{ item.percent }}%;"></div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    keywords = list(DATA_STORE.keys())
    
    if not keywords:
        return render_template_string(HTML_TEMPLATE, keywords=[], current_word="", data=[], error="有効なデータが見つかりませんでした。data.jsonを確認してください。")

    current_word = request.args.get("word", keywords[0])
    
    if current_word not in DATA_STORE:
        current_word = keywords[0]

    data = DATA_STORE.get(current_word, [])
    
    return render_template_string(
        HTML_TEMPLATE, 
        keywords=keywords, 
        current_word=current_word, 
        data=data, 
        error=None
    )

if __name__ == "__main__":
    app.run(debug=True)
