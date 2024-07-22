
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import messagebox, simpledialog
import csv
from scipy.spatial.distance import cosine

class MovieRecommendationSystem:
    def __init__(self):
        self.movies = {}
        self.user_data = {}
        self.user_ratings = {}
        self.logged_in_user = None
        self.similarity_matrix = None

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

    def load_similarity_matrix(self, file_path):
        self.similarity_matrix = pd.read_csv(file_path, index_col=0)

    def recommend_movies_based_on_similarity(self):
        if self.logged_in_user is None:
            return "Please login first to get recommendations."

        user_ratings = self.user_ratings[self.logged_in_user]

        # Collect all movies rated by the user with a rating from 1 to 10
        rated_movies = [(i + 1, rating) for i, rating in enumerate(user_ratings) if 1 <= rating <= 10]

        if not rated_movies:
            return "No valid ratings available for recommendations."

        movie_scores = {}

        for movie_id, rating in rated_movies:
            similar_movies = self.similarity_matrix.loc[movie_id].nlargest(6).index.tolist()
            similar_movies.remove(str(movie_id))  # Remove the movie itself from the list

            for similar_movie_id in similar_movies:
                similar_movie_id = int(similar_movie_id)
                if similar_movie_id in movie_scores:
                    movie_scores[similar_movie_id] += self.similarity_matrix.loc[movie_id, str(similar_movie_id)] * rating
                else:
                    movie_scores[similar_movie_id] = self.similarity_matrix.loc[movie_id, str(similar_movie_id)] * rating

        recommended_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        recommended_movies_info = [self.movies[movie_id] for movie_id, score in recommended_movies]
        return recommended_movies_info

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

    def generate_similarity_matrix(self, movie_data_file='data.csv', output_file='movie_similarity_matrix.csv'):
        df = pd.read_csv(movie_data_file)
        
        # Remove the 'view' column because it is not used to calculate similarity
        df = df.drop(columns=['view'])
        # Encoding the 'genre' Column
        encoder = OneHotEncoder(sparse_output=False)
        genre_encoded = encoder.fit_transform(df[['genre']])

        # Scaling the 'release_year' and 'rating' Columns
        scaler = MinMaxScaler()
        release_year_scaled = scaler.fit_transform(df[['release_year']])
        rating_scaled = scaler.fit_transform(df[['rating']])

        # Combining Features
        features = np.hstack([genre_encoded, release_year_scaled, rating_scaled])
        # Calculating the Cosine Similarity Matrix
        similarity_matrix = cosine_similarity(features) # type: ignore

        # Creating a DataFrame for the Similarity Matrix
        similarity_df = pd.DataFrame(similarity_matrix, index=df['id'], columns=df['id'])

        # Save to CSV file
        similarity_df.to_csv(output_file)


class UserAuthentication:
    def __init__(self, movie_system):
        self.movie_system = movie_system

    def register_user(self, name, password, age, gender):
        if not name or not password or age is None or gender not in ['Male', 'Female']:
            raise ValueError("All fields must be filled correctly.")

        if any(user_info['name'] == name for user_info in self.movie_system.user_data.values()):
            raise ValueError("Username already exists.")

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


class MovieRecommendationUI:
    def __init__(self, movie_system):
        self.movie_system = movie_system
        self.user_auth = UserAuthentication(movie_system)  
        self.window = tk.Tk()
        self.window.title("Movie Recommendation System")
        self.window.geometry("600x500")  
        self.window.resizable(False, False) 

        self.create_selection_widgets()

    def create_selection_widgets(self):
        self.selection_frame = tk.Frame(self.window, padx=20, pady=20, bg='lightgray')

        self.login_button = tk.Button(self.selection_frame, text="Log in", command=self.show_login, font=("Arial", 14), width=20)
        self.login_button.grid(row=0, column=0, padx=10, pady=10)

        self.register_button = tk.Button(self.selection_frame, text="Register", command=self.show_register, font=("Arial", 14), width=20)
        self.register_button.grid(row=1, column=0, padx=10, pady=10)

        self.selection_frame.pack(expand=True)

    def show_login(self):
        self.selection_frame.pack_forget()  
        self.create_login_widgets()  

    def show_register(self):
        self.selection_frame.pack_forget()  
        self.create_register_widgets()  

    def show_selection(self):
        if hasattr(self, 'login_frame'):
            self.login_frame.pack_forget()
        if hasattr(self, 'register_frame'):
            self.register_frame.pack_forget()
        self.selection_frame.pack(expand=True)

    def create_login_widgets(self):
        self.login_frame = tk.Frame(self.window, padx=20, pady=20, bg='lightgray')

        self.username_label = tk.Label(self.login_frame, text="User name:", font=("Arial", 14), bg='lightgray')
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 14))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = tk.Label(self.login_frame, text="Password:", font=("Arial", 14), bg='lightgray')
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.password_entry = tk.Entry(self.login_frame, show='*', font=("Arial", 14))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = tk.Button(self.login_frame, text="Log in", command=self.login, font=("Arial", 14), width=15)
        self.login_button.grid(row=2, column=0, padx=10, pady=10)

        self.back_button = tk.Button(self.login_frame, text="Back", command=self.show_selection, font=("Arial", 14), width=15)
        self.back_button.grid(row=2, column=1, padx=10, pady=10)

        self.login_frame.pack(expand=True)

    def create_register_widgets(self):
        self.register_frame = tk.Frame(self.window, padx=20, pady=20, bg='lightgray')

        self.username_label = tk.Label(self.register_frame, text="User name:", font=("Arial", 14), bg='lightgray')
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.username_entry = tk.Entry(self.register_frame, font=("Arial", 14))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = tk.Label(self.register_frame, text="Password:", font=("Arial", 14), bg='lightgray')
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.password_entry = tk.Entry(self.register_frame, show='*', font=("Arial", 14))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.age_label = tk.Label(self.register_frame, text="Age:", font=("Arial", 14), bg='lightgray')
        self.age_label.grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.age_entry = tk.Entry(self.register_frame, font=("Arial", 14))
        self.age_entry.grid(row=2, column=1, padx=10, pady=10)

        self.gender_label = tk.Label(self.register_frame, text="Gender (Male/Female):", font=("Arial", 14), bg='lightgray')
        self.gender_label.grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.gender_entry = tk.Entry(self.register_frame, font=("Arial", 14))
        self.gender_entry.grid(row=3, column=1, padx=10, pady=10)

        self.register_button = tk.Button(self.register_frame, text="Register", command=self.register, font=("Arial", 14), width=15)
        self.register_button.grid(row=4, column=0, padx=10, pady=10)

        self.back_button = tk.Button(self.register_frame, text="Back", command=self.show_selection, font=("Arial", 14), width=15)
        self.back_button.grid(row=4, column=1, padx=10, pady=10)

        self.register_frame.pack(expand=True)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.user_auth.login_user(username, password): 
            messagebox.showinfo("Log in", "Log in successfully!")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.login_frame.pack_forget()  
            self.create_recommendations_widgets() 
        else:
            messagebox.showerror("Log in", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            age = int(self.age_entry.get())
            gender = self.gender_entry.get()
        except ValueError:
            messagebox.showwarning("Register", "Age must be a number.")
            return

        if gender not in ['Male', 'Female']:
            messagebox.showwarning("Register", "Gender must be 'Male' or 'Female'.")
            return

        try:
            self.user_auth.register_user(username, password, age, gender)  
            messagebox.showinfo("Register", "Register successfully! You are logged in now.")
            self.register_frame.pack_forget()  
            self.create_recommendations_widgets()  
        except ValueError as e:
            messagebox.showerror("Register", str(e))

    def create_recommendations_widgets(self):
       # Recommendation section
        self.recommendations_frame = tk.Frame(self.window, padx=20, pady=20, bg='lightblue')

        # Recommendation button based on reviews
        self.recommendations_button = tk.Button(self.recommendations_frame, text="Recommendation based on reviews", command=lambda: self.get_recommendations("based_predict_user_ratings"), font=("Arial", 14), width=30)
        self.recommendations_button.grid(row=0, column=0, padx=10, pady=10)

        # Recommendation button by gender
        self.gender_recommendations_button = tk.Button(self.recommendations_frame, text="Recommendations by gender", command=lambda: self.get_recommendations("based_on_gender"), font=("Arial", 14), width=30)
        self.gender_recommendations_button.grid(row=1, column=0, padx=10, pady=10)

        # General recommendation button
        self.get_recommendations_button = tk.Button(self.recommendations_frame, text="Recommendations are based on historical reviews", command=lambda: self.get_recommendations("based_existing_user_recommendations"), font=("Arial", 14), width=30)
        self.get_recommendations_button.grid(row=2, column=0, padx=10, pady=10)

        # Recommendation list
        self.recommendations_list = tk.Listbox(self.recommendations_frame, width=50, height=10, font=("Arial", 12))
        self.recommendations_list.grid(row=3, column=0, padx=10, pady=10)

        self.recommendations_frame.pack(expand=True)

    def get_recommendations(self, recommendation_type="based_predict_user_ratings"):
        if self.movie_system.logged_in_user is None:
            messagebox.showwarning("Recommendations", "Please log in before receiving recommendations.")
            return

        if recommendation_type == "based_predict_user_ratings":
            recommendations = self.movie_system.predict_user_ratings()
        elif recommendation_type == "based_on_gender":
            user_gender = self.movie_system.user_data[self.movie_system.logged_in_user]['gender']
            recommendations = self.movie_system.get_gender_based_recommendations(user_gender)
        elif recommendation_type == "based_existing_user_recommendations":
            recommendations = self.movie_system.existing_user_recommendations()
        else:
            recommendations = self.movie_system.predict_user_ratings()  # Default if there is no specific recommendation type

        self.recommendations_list.delete(0, tk.END)

        for movie in recommendations:
            self.recommendations_list.insert(tk.END, f"{movie['title']} - Rating: {movie.get('rating', 'N/A'):.2f}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    movie_system = MovieRecommendationSystem()
    user_auth = UserAuthentication(movie_system)

    
    movie_system.load_movie_data('data.csv')
    movie_system.load_user_data('user.csv')
    movie_system.load_user_ratings('ratings.csv')

    app = MovieRecommendationUI(movie_system)
    app.run()
