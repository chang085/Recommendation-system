import pandas as pd

# Đọc các file CSV
users_df = pd.read_csv('user.csv')
ratings_df = pd.read_csv('rating.csv')
movies_df = pd.read_csv('data.csv')

def xoa_nguoi_dung(user_id):
    global users_df
    users_df = users_df[users_df['user_id'] != user_id]
    users_df.reset_index(drop=True, inplace=True)

def xoa_rating(user_id, movie_id):
    global ratings_df
    ratings_df.loc[user_id - 1, str(movie_id)] = 0

def xoa_phim(movie_id):
    global movies_df
    movies_df = movies_df[movies_df[''] != movie_id]
    movies_df.reset_index(drop=True, inplace=True)

def sua_nguoi_dung(user_id, cot, gia_tri_moi):
    global users_df
    users_df.loc[users_df['user_id'] == user_id, cot] = gia_tri_moi

def sua_rating(user_id, movie_id, rating_moi):
    global ratings_df
    ratings_df.loc[user_id - 1, str(movie_id)] = rating_moi

def sua_phim(movie_id, cot, gia_tri_moi):
    global movies_df
    movies_df.loc[movies_df[''] == movie_id, cot] = gia_tri_moi

# Lưu các thay đổi vào file CSV
def luu_thay_doi():
    users_df.to_csv('user.csv', index=False)
    ratings_df.to_csv('rating.csv', index=False)
    movies_df.to_csv('data.csv', index=False)

