import csv
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# ---------- movies ----------
with open("movies_100k.csv", encoding="latin-1") as f:
    reader = csv.reader(f, delimiter="|")
    rows = list(reader)

header = rows[0]
data = rows[1:]

fixed_data = [
    row + [None] * (len(header) - len(row))
    for row in data
]

movies = pd.DataFrame(fixed_data, columns=header)
movies["movie_id"] = movies["movie_id"].astype(int)


# ---------- ratings ----------
try:
    ratings = pd.read_csv("ratings_100k.csv", sep=None, engine='python', encoding='latin-1')
except Exception:
    try:
        ratings = pd.read_csv("ratings_100k.csv", sep='|', encoding='latin-1')
    except Exception:
        try:
            ratings = pd.read_csv("ratings_100k.csv", sep='\t', encoding='latin-1')
        except Exception:
            ratings = pd.read_csv("ratings_100k.csv", sep=' ', encoding='latin-1')

# 列名を正規化
ratings.columns = ratings.columns.str.strip().str.lower()

# 列名のマッピング
column_mapping = {}
for col in ratings.columns:
    col_lower = col.lower().strip()
    if 'user' in col_lower:
        column_mapping[col] = 'user_id'
    elif 'movie' in col_lower:
        column_mapping[col] = 'movie_id'
    elif 'rating' in col_lower or 'rate' in col_lower:
        column_mapping[col] = 'rating'
    elif 'time' in col_lower:
        column_mapping[col] = 'timestamp'

if column_mapping:
    ratings = ratings.rename(columns=column_mapping)

# 列名を手動設定（必要に応じて）
required_columns = ['user_id', 'movie_id', 'rating']
missing_cols = [col for col in required_columns if col not in ratings.columns]

if missing_cols:
    if len(ratings.columns) == 3:
        ratings.columns = ['user_id', 'movie_id', 'rating']
    elif len(ratings.columns) == 4:
        ratings.columns = ['user_id', 'movie_id', 'rating', 'timestamp']

# 型変換
ratings[['user_id', 'movie_id', 'rating']] = ratings[['user_id', 'movie_id', 'rating']].astype(int)


# ---------- functions ----------
def top_rated_movies(n=5):
    avg = ratings.groupby("movie_id")["rating"].mean()
    top_ids = avg.sort_values(ascending=False).head(n).index
    return movies[movies["movie_id"].isin(top_ids)][["movie_id", "movie_title"]]

def recommend_movies(selected_ids, n=5):
    virtual_user = pd.DataFrame({
        "user_id": [9999] * len(selected_ids),
        "movie_id": selected_ids,
        "rating": [5] * len(selected_ids),
        "timestamp": [0] * len(selected_ids)
    })

    df = pd.concat([ratings, virtual_user], ignore_index=True)

    matrix = df.pivot_table(
        index="user_id",
        columns="movie_id",
        values="rating"
    ).fillna(0)

    sim = cosine_similarity(matrix)
    sim_df = pd.DataFrame(sim, index=matrix.index, columns=matrix.index)

    similar_users = sim_df[9999].sort_values(ascending=False)[1:6].index

    candidate = df[df["user_id"].isin(similar_users)]
    scores = candidate.groupby("movie_id")["rating"].mean()

    scores = scores.drop(selected_ids, errors="ignore")
    top_ids = scores.sort_values(ascending=False).head(n).index

    return movies[movies["movie_id"].isin(top_ids)][["movie_id", "movie_title"]]