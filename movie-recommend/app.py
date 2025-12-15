from flask import Flask, render_template, request
import csv
import pandas as pd
from recommender import recommend_movies, top_rated_movies

app = Flask(__name__)

# movies_100k.csv を安全に読み込む
with open("movies_100k.csv", encoding="latin-1") as f:
    reader = csv.reader(f, delimiter="|")
    rows = list(reader)

header = rows[0]
data = rows[1:]

# 列数が足りない行を None で埋める
fixed_data = [
    row + [None] * (len(header) - len(row))
    for row in data
]

movies = pd.DataFrame(fixed_data, columns=header)
movies["movie_id"] = movies["movie_id"].astype(int)

@app.route("/")
def index():
    try:
        # トップ評価の映画を30本取得
        top_movies = top_rated_movies(n=30)
        print(f"Top movies count: {len(top_movies)}")
        print(f"Columns: {top_movies.columns.tolist()}")
        print(f"First movie: {top_movies.iloc[0].to_dict()}")
        return render_template("index.html", movies=top_movies)
    except Exception as e:
        print(f"Error in index: {e}")
        import traceback
        traceback.print_exc()
        return f"エラーが発生しました: {e}"

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        selected = request.form.getlist("movies")
        print(f"Selected movies: {selected}")
        
        if not selected or len(selected) < 3:
            # 3本未満の場合はトップ評価映画を表示
            recs = top_rated_movies(n=5)  # 10 → 5 に変更
            print("Not enough movies selected, showing top rated")
        else:
            # 選択された映画に基づいて推薦
            recs = recommend_movies(list(map(int, selected)), n=5)  # 10 → 5 に変更
            print(f"Recommendations: {len(recs)} movies")
        
        print(f"Recommendations columns: {recs.columns.tolist()}")
        print(f"First recommendation: {recs.iloc[0].to_dict() if len(recs) > 0 else 'None'}")
        
        return render_template("result.html", movies=recs)
    except Exception as e:
        print(f"Error in recommend: {e}")
        import traceback
        traceback.print_exc()
        return f"エラーが発生しました: {e}"

# ここを追加
if __name__ == "__main__":
    app.run(debug=True, port=5000)