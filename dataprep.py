import numpy as np
import pandas as pd
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

def load_data():
    print("Loading data...")
    movies = pd.read_csv('data/tmdb_5000_movies.csv')
    credits = pd.read_csv('data/tmdb_5000_credits.csv')
    return movies, credits

def process_data(movies, credits):
    print("Merging datasets...")
    movies = movies.merge(credits, on='title')
    
    # Select relevant columns
    movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew', 'vote_average', 'release_date']]
    
    print("Dropping missing values...")
    movies.dropna(inplace=True)
    
    print("Processing columns...")
    def convert(obj):
        L = []
        for i in ast.literal_eval(obj):
            L.append(i['name'])
        return L

    def convert3(obj):
        L = []
        counter = 0
        for i in ast.literal_eval(obj):
            if counter != 3:
                L.append(i['name'])
                counter += 1
            else:
                break
        return L

    def fetch_director(obj):
        L = []
        for i in ast.literal_eval(obj):
            if i['job'] == 'Director':
                L.append(i['name'])
                break
        return L

    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(convert3)
    movies['crew'] = movies['crew'].apply(fetch_director)
    
    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    
    print("Removing spaces from tags...")
    movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])
    
    print("Creating 'tags' column...")
    movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
    
    # Keep metadata for the UI
    # Note: 'genres' is already a list of strings here, we might want to keep it readable
    # converting overview back to string for display (it was split for tags)
    movies['overview_display'] = movies['overview'].apply(lambda x: " ".join(x))
    
    new_df = movies[['movie_id', 'title', 'tags', 'overview_display', 'vote_average', 'release_date', 'genres']].copy()
    new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
    new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())
    
    return new_df

def create_model(new_df):
    print("Stemming tags...")
    ps = PorterStemmer()
    def stem(text):
        y = []
        for i in text.split():
            y.append(ps.stem(i))
        return " ".join(y)
    
    new_df['tags'] = new_df['tags'].apply(stem)
    
    print("Vectorizing...")
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(new_df['tags']).toarray()
    
    print("Calculating cosine similarity...")
    similarity = cosine_similarity(vectors)
    
    return new_df, similarity

def save_models(new_df, similarity):
    print("Saving models...")
    os.makedirs('models', exist_ok=True)
    pickle.dump(new_df.to_dict('records'), open('models/movie_dict.pkl', 'wb'))
    pickle.dump(similarity, open('models/similarity.pkl', 'wb'))
    print("Done!")

if __name__ == "__main__":
    try:
        movies, credits = load_data()
        new_df = process_data(movies, credits)
        new_df, similarity = create_model(new_df)
        save_models(new_df, similarity)
    except Exception as e:
        print(f"An error occurred: {e}")
