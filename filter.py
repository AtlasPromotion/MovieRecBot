import numpy as np
import numpy as np
import pandas as pd
from surprise import Dataset
from scipy.sparse.linalg import svds
from surprise import Reader, Dataset, SVD, evaluate
from collections import defaultdict
from surprise import BaselineOnly
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
from surprise import KNNBasic
from surprise import accuracy
import os
from operator import itemgetter
from surprise.model_selection import KFold
from surprise.model_selection import GridSearchCV
import requests
import json
import urllib
from PIL import Image
import requests
import requests
import urllib
# # ratings = pd.read_csv('../ratings.csv', sep="::", encoding='latin-1', names=['user_id', 'movie_id', 'rating', 'timestamp'])
# # # # Reading users file
# # users = pd.read_csv('../users.csv', sep="::", encoding='latin-1', names=['user_id', 'gender', 'zipcode', 'age_desc', 'occ_desc'])
# # ratings = ratings.iloc[0:100000,:]
# # users = users.iloc[0:100000,:]
# # #
# # # # Reading movies file
# # movies = pd.read_csv('../movies.csv', sep="::", encoding='latin-1', names=['movie_id', 'title', 'genres'])
# # movies = movies.iloc[0:100000,:]
# # rating1 = ratings.merge(movies, how='left', left_on='movie_id', right_on='movie_id')
# # ratings2 = rating1.merge(users, how='left', left_on='user_id', right_on='user_id')
# # ratings2 = ratings2.drop("timestamp", axis = 1)
# # ratings2 = ratings2.drop("gender",axis = 1)
# # ratings2 = ratings2.drop("zipcode",axis = 1)
# # ratings2 = ratings2.drop("age_desc",axis = 1)
# # ratings2 = ratings2.drop("occ_desc",axis = 1)
# # sort_values(['rating'], ascending=False)
# n_users = ratings.user_id.unique().shape[0]
# n_movies = ratings.movie_id.unique().shape[0]
# print ('Number of users = ' + str(n_users) + ' | Number of movies = ' + str(n_movies))
# Ratings = ratings.pivot(index = 'user_id', columns ='movie_id', values = 'rating').fillna(0)
#
# R = Ratings.as_matrix()
# user_ratings_mean = np.mean(R, axis = 1)
# Ratings_demeaned = R - user_ratings_mean.reshape(-1, 1)
#
#
#
# sparsity = round(1.0 - len(ratings) / float(n_users * n_movies), 3)
# print ('The sparsity level of MovieLens1M dataset is ' +  str(sparsity * 100) + '%')
#
#
# U, sigma, Vt = svds(Ratings_demeaned, k = 50)
# sigma = np.diag(sigma)
# all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
#
#
# preds = pd.DataFrame(all_user_predicted_ratings, columns = Ratings.columns)
# preds.head()
#
#
# def recommend_movies(predictions, userID, movies, original_ratings, num_recommendations):
#     # Get and sort the user's predictions
#     user_row_number = userID - 1  # User ID starts at 1, not 0
#     sorted_user_predictions = preds.iloc[user_row_number].sort_values(ascending=False)  # User ID starts at 1
#
#     # Get the user's data and merge in the movie information.
#     user_data = original_ratings[original_ratings.user_id == (userID)]
#     user_full = (user_data.merge(movies, how='left', left_on='movie_id', right_on='movie_id').
#                  sort_values(['rating'], ascending=False)
#                  )
#
#     print ('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
#     print ('Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
#
#     # Recommend the highest predicted rating movies that the user hasn't seen yet.
#     recommendations = (movies[~movies['movie_id'].isin(user_full['movie_id'])].
#                            merge(pd.DataFrame(sorted_user_predictions).reset_index(), how='left',
#                                  left_on='movie_id',
#                                  right_on='movie_id').
#                            rename(columns={user_row_number: 'Predictions'}).
#                            sort_values('Predictions', ascending=False).
#                            iloc[:num_recommendations, :-1]
#                            )
#
#     return user_full, recommendations
#
#
#
# already_rated, predictions = recommend_movies(preds, 77, movies, ratings, 20)
# print(predictions)

ratings = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1', names=['user_id', 'movie_id', 'rating', 'timestamp'],
                      converters={'user_id':int,'movie_id':int,'rating':float, 'timestamp':int})
# # # # Reading users file
# # ratings = ratings.iloc[0:100000,:]
# # users = users.iloc[0:100000,:]
# # #
# # # # Reading movies file
#Reading items file:
# i_cols = ['movie_id', 'movie title' ,'release date','video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure',
#  'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
#  'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
i_cols = ['movie_id','title','genres']
movies = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=i_cols,
 encoding='latin-1')
i_cols2 = ['movie_id','imdb_id','otherid']
links = pd.read_csv('ml-latest-small/links.csv', sep=',', names=i_cols2, converters={'ibmd_id':str},
 encoding='latin-1')
def get_top_n(predictions, n=10):

    top_n = []
    for uid, iid, true_r, est, _ in predictions:
            top_n.append([iid, est])
    dfTest = pd.DataFrame(top_n, columns = ['movie_id', 'est rating'])
    dfTest.sort_values(by='est rating', ascending=False)
    # Then sort the predictions for each user and retrieve the k highest ones.
    # for user_ratings in top_n:
    #     user_ratings.sort(key=itemgetter(2))
    #     top_n = user_ratings[:n]

    return dfTest[:50]

def precision_recall_at_k(predictions, k=15, threshold=3.5):
    '''Return precision and recall at k metrics for each user.'''

    # First map the predictions to each user.
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = dict()
    recalls = dict()
    for uid, user_ratings in user_est_true.items():

        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)

        # Number of recommended items in top k
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])

        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                              for (est, true_r) in user_ratings[:k])

        # Precision@K: Proportion of recommended items that are relevant
        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 1

        # Recall@K: Proportion of relevant items that are recommended
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 1

    return precisions, recalls


# Get base url filepath structure. w185 corresponds to size of movie poster.
headers = {'Accept': 'application/json'}
payload = {'api_key': 'd9ff9f47e912c90958ab3165c9ff713b'}
response = requests.get("http://api.themoviedb.org/3/configuration", params=payload, headers=headers)
# print(response.content)
response = json.loads(response.text)
base_url = response['images']['base_url'] + 'w185'


def get_poster(title, movie_id,base_url):

    # Get IMDB movie ID
    movie_id1 = links.loc[links['movie_id'] == movie_id].iloc[0]['imdb_id']

    if(len(str(int(movie_id1))) == 6):
        movie_id1 = 'tt0'+str(int(movie_id1))
    elif(len(str(int(movie_id1))) == 5):
        movie_id1 = 'tt00' + str(int(movie_id1))
    else:
        movie_id1 = 'tt' + str(int(movie_id1))
    # movie_id1 = 'tt' + str(int(movie_id1))
    # print(movie_id1)
    # movie_id1 = 'tt0114709'
    # print(movie_id1)
    # Query themoviedb.org API for movie poster path.
    movie_url = 'http://api.themoviedb.org/3/movie/{:}/images'.format(movie_id1)
    headers = {'Accept': 'application/json'}
    payload = {'api_key': 'd9ff9f47e912c90958ab3165c9ff713b'}
    response = requests.get(movie_url, params=payload, headers=headers)
    try:
        file_path = json.loads(response.text)['posters'][0]['file_path']
    except:
        # IMDB movie ID is sometimes no good. Need to get correct one.
        movie_title = title
        payload['query'] = movie_title
        response = requests.get('http://api.themoviedb.org/3/search/movie', params=payload, headers=headers)
        movie_id = json.loads(response.text)['results'][0]['id']
        payload.pop('query', None)
        movie_url = 'http://api.themoviedb.org/3/movie/{:}/images'.format(movie_id)
        response = requests.get(movie_url, params=payload, headers=headers)
        file_path = json.loads(response.text)['posters'][0]['file_path']

    return base_url + file_path


ratings_dict = {'itemID': list(ratings.movie_id),
                'userID': list(ratings.user_id),
                'rating': list(ratings.rating)}

df = pd.DataFrame(ratings_dict)
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)
# param_grid = {'n_epochs': [5, 10], 'lr_all': [0.002, 0.005],
#               'reg_all': [0.4, 0.6]}
# gs = GridSearchCV(KNNBasic, param_grid, measures=['rmse', 'mae'], cv=3)
# gs.fit(data)
# # algo = gs.best_estimator['rmse']
# sim_options = {'name': 'pearson_baseline',
#                'user_based': False  # compute  similarities between items
#                }
# algo = KNNBasic(sim_options=sim_options)
# # algo = SVD()
# kf = KFold(n_splits=5)
# for trainset, testset in kf.split(data):
#     algo.fit(trainset)
#     predictions = algo.test(testset)
#     precisions, recalls = precision_recall_at_k(predictions, k=15, threshold=3.5)
#
#     # Precision and recall can then be averaged over all users
#     print(sum(prec for prec in precisions.values()) / len(precisions))
#     print(sum(rec for rec in recalls.values()) / len(recalls))
trainset, testset = train_test_split(data, test_size=.3)
# trainset = data.build_full_trainset()
# testset = [item for item in testset if item[0] == 77]
sim_options = {'name': 'cosine',
               'user_based': True  # compute  similarities between items
               }
algo = KNNBasic(sim_options=sim_options)
# algo = SVD()
algo.fit(trainset)
# testset = trainset.build_anti_testset()
# cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
def get_rec(id):
    global testset
    testset = [item for item in testset if item[0] == 77]
    predictions = algo.test(testset)
# print(predictions)
    accuracy.rmse(predictions)
    top_n = get_top_n(predictions, n=10)
    result = pd.merge(top_n, movies, how='inner', on=['movie_id', 'movie_id'])
    return result.sort_values(by='est rating', ascending=False).reset_index(drop=True)

# title = 'Toy Story'
# id = 'tt0114709'
# print(get_poster(title,id,base_url))
def check_user_ratings(user_id):
    number = ratings.loc[ratings['user_id'] == user_id]
    if(number.empty):
        return 0
    else:
        return number.count

def get_film(title, genres=0):
    if(genres == 0):
        # movies.title = movies.title.astype(str).str.lower()
        number = movies.loc[movies['title'].str.lower().str.find(str(title.lower())) != -1]
        return number
        # if(number.empty):
        #     return number
        # else:
        #     return number.iloc[0]
    else:
        number = movies.loc[movies['title'].str.lower().str.find(str(title.lower())) != -1]
        number = number.loc[number['genres'] == genres]
        return number

def add_rate(user_id, movie_id, rate, timestamp):
    user_id = str(user_id)
    movie_id = str(movie_id)
    rate = str(rate)
    timestamp = str(timestamp)
    ratings_user = pd.DataFrame([[int(user_id),int(movie_id),float(rate),int(timestamp)]],columns=['user_id', 'movie_id', 'rating', 'timestamp'])
    ratings = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                          names=['user_id', 'movie_id', 'rating', 'timestamp'])
    ratings = ratings.append(ratings_user, ignore_index=True)
    # ratings = pd.concat([ratings,ratings_user])
    ratings.to_csv('ml-latest-small/ratings.csv',header=False, index = False)

    # ratings.append([[int('182060084'),int('1'),float('2.0'),int('1526731591')]], ignore_index=True)

def create_img(url):
    f = open('out.jpg', 'wb')
    f.write(urllib.request.urlopen(url).read())
    f.close()