import csv
import numpy as np
from scipy.spatial.distance import cosine

class MovieRecommendationSystem:
    def __init__(self):
        self.movies = {}
        self.user_data = {}
        self.user_ratings = {}
        self.logged_in_user = None

    def load_movie_data(self, file_path):
        with open(file_path, 'r') as file:
            next(file)  # Skip header
            for line in file:
                data = line.strip().split(',')
                if data[0]:  # Check if the first element is not empty
                    movie_id = int(data[0])
                    movie_info = {
                        "id": data[0],
                        "title": data[1],
                        "genre": data[2],
                        "view": int(data[4]),
                        "rating": float(data[5])
                    }
                    self.movies[movie_id] = movie_info

    def load_user_data(self, file_path):
        with open(file_path, 'r') as file:
            next(file)  # Skip header
            for line in file:
                data = line.strip().split(',')
                if data[0]:  # Check if the first element is not empty
                    try:
                        user_id = int(data[0])
                        name = data[1]
                        password = data[2]
                        age = int(data[3])
                        gender = data[4]
                        self.user_data[user_id] = {
                            'name': name,
                            'password': password,
                            'age': age,
                            'gender': gender,
                            'ratings': []  # Initialize an empty list for user ratings
                        }
                    except ValueError as e:
                        print(f"Skipping line due to error: {e}")

    def load_user_ratings(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip header
            for row in reader:
                if len(row) > 1:  # Check if row has enough elements
                    try:
                        user_id = int(row[0])
                        ratings = list(map(int, row[1:]))
                        self.user_ratings[user_id] = ratings
                    except ValueError as e:
                        print(f"Skipping line due to error: {e}")
                else:
                    print(f"Skipping incomplete row: {row}")

    def new_user_recommendations(self):
        sorted_movies_by_rating = sorted(self.movies.values(), key=lambda x: x["rating"], reverse=True)
        top_rated_movies = sorted_movies_by_rating[:5]

        sorted_movies_by_views = sorted(self.movies.values(), key=lambda x: x["view"], reverse=True)
        hot_movies = sorted_movies_by_views[:2]

        recommendations = top_rated_movies + hot_movies
        return recommendations

    def existing_user_recommendations(self):
        if self.logged_in_user is None:
            return "Please login first to get recommendations."

        user_ratings = self.user_ratings[self.logged_in_user]
        rated_movies = [(movie_id, rating) for movie_id, rating in enumerate(user_ratings, start=1) if rating > 0]
        top_rated_movies = sorted(rated_movies, key=lambda x: x[1], reverse=True)[:5]
        
        recommendations = [self.movies[movie_id] for movie_id, rating in top_rated_movies]
        return recommendations

    def find_similar_users(self, user_id):
        target_ratings = self.user_ratings[user_id]
        similarities = []

        for other_user_id, ratings in self.user_ratings.items():
            if other_user_id != user_id:
                similarity = self.calculate_similarity(target_ratings, ratings)
                similarities.append((other_user_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_users = [user for user, similarity in similarities[:5]]  # Top 5 similar users
        return similar_users

    def calculate_similarity(self, user_ratings, other_user_ratings):
        user_ratings = np.array(user_ratings)
        other_user_ratings = np.array(other_user_ratings)
        mask = (user_ratings != 0) & (other_user_ratings != 0)

        if np.sum(mask) == 0:
            return 0  # No ratings in common

        user_ratings = user_ratings[mask]
        other_user_ratings = other_user_ratings[mask]
        return 1 - cosine(user_ratings, other_user_ratings)  # Cosine similarity

    def predict_user_ratings(self):
        if self.logged_in_user is None:
            return "Please login first to get predictions."

        similar_users = self.find_similar_users(self.logged_in_user)
        user_ratings = self.user_ratings[self.logged_in_user]

        predictions = {}
        for movie_id in range(1, len(self.movies) + 1):
            if user_ratings[movie_id - 1] == 0:
                total_similarity = 0
                weighted_sum = 0

                for similar_user in similar_users:
                    similarity = self.calculate_similarity(user_ratings, self.user_ratings[similar_user])
                    weighted_sum += similarity * self.user_ratings[similar_user][movie_id - 1]
                    total_similarity += similarity

                if total_similarity > 0:
                    predicted_rating = weighted_sum / total_similarity
                else:
                    predicted_rating = 0  # No similar user ratings available

                predictions[movie_id] = predicted_rating

        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        recommended_movies = [self.movies[movie_id] for movie_id, rating in sorted_predictions[:5]]
        return recommended_movies

    def get_gender_based_recommendations(self, gender):
        if gender.lower() == 'male':
            preferred_genres = ['Action', 'Adventure', 'Crime', 'Horror']
        elif gender.lower() == 'female':
            preferred_genres = ['Drama']
        else:
            return []

        genre_movies = [movie for movie in self.movies.values() if any(genre in movie["genre"] for genre in preferred_genres)]
        top_genre_movies = sorted(genre_movies, key=lambda x: x["rating"], reverse=True)
        return top_genre_movies[:5]


class UserAuthentication:
    def __init__(self, movie_system):
        self.movie_system = movie_system

    def register_user(self, name, password, age, gender):
        user_id = len(self.movie_system.user_data) + 1
        with open('user.csv', 'a') as file:
            file.write(f"\n{user_id},{name},{password},{age},{gender}")
        
        self.movie_system.user_data[user_id] = {
            'name': name,
            'password': password,
            'age': age,
            'gender': gender,
            'ratings': []  # Initialize an empty list for user ratings
        }
        
        # Initialize the user's ratings to all 0s
        num_movies = len(self.movie_system.movies)
        new_user_ratings = [0] * num_movies
        self.movie_system.user_ratings[user_id] = new_user_ratings
        
        with open('ratings.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user_id] + new_user_ratings)
        
        # Log in the user immediately after registration
        self.movie_system.logged_in_user = user_id
        print("Registration successful! You are now logged in.")

    def login_user(self, name, password):
        for user_id, user_info in self.movie_system.user_data.items():
            if user_info['name'] == name and user_info['password'] == password:
                self.movie_system.logged_in_user = user_id
                return True
        return False

# Example usage:
movie_system = MovieRecommendationSystem()
user_auth = UserAuthentication(movie_system)

movie_system.load_movie_data('data.csv')
movie_system.load_user_data('user.csv')
movie_system.load_user_ratings('ratings.csv')

user_choice = input("Welcome! Enter 'login' to login or 'register' to register: ")
if user_choice.lower() == 'register':
    name = input("Enter your name: ")
    password = input("Enter your password: ")
    age = int(input("Enter your age: "))
    gender = input("Enter your gender: ")
    user_auth.register_user(name, password, age, gender)
    print("Registration successful! You are now logged in.")
elif user_choice.lower() == 'login':
    name = input("Enter your name: ")
    password = input("Enter your password: ")
    if user_auth.login_user(name, password):
        print("Login successful!")
    else:
        print("Invalid username or password.")
else:
    print("Invalid choice. Please restart the program.")

if movie_system.logged_in_user is not None:
    user_info = movie_system.user_data[movie_system.logged_in_user]
    gender = user_info['gender']

    # Predict ratings for the logged in user
    print("\nPredicted Ratings for New Movies:")
    predictions = movie_system.predict_user_ratings()
    for movie in predictions:
        print(f"id: {movie['id']} Title: {movie['title']}, Predicted Rating: {movie['rating']}")
