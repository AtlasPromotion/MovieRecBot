import pandas as pd
import numpy as np
ratings_cols = ['user_id', 'movie_id', 'rating']
ratings = pd.read_csv('../ml-100k/u.data', sep='\t', names=ratings_cols, usecols=range(3),encoding = "ISO-8859-1")

movies_cols = ['movie_id', 'title']
movies = pd.read_csv('u.item', sep='|', names=movies_cols, usecols=range(10),encoding = "ISO-8859-1")
print(movies)
ratings = pd.merge(ratings, movies)
print(ratings)

movieRatings = ratings.pivot_table(index=['user_id'],columns=['title'],values='rating')

starWarsRatings = movieRatings['Toy Story (1995)']

similarMovies = movieRatings.corrwith(starWarsRatings)
similarMovies = similarMovies.dropna()
df = pd.DataFrame(similarMovies)

ratingsCount = 100
movieStats = ratings.groupby('title').agg({'rating': [np.size, np.mean]})
popularMovies = movieStats['rating']['size'] >= ratingsCount
movieStats[popularMovies].sort_values([('rating', 'mean')], ascending=False)[:15]

df = movieStats[popularMovies].join(pd.DataFrame(similarMovies, columns=['similarity']))
print(df.sort_values(['similarity'], ascending=False)[:15])

userRatings = ratings.pivot_table(index=['user_id'],columns=['title'],values='rating')
corrMatrix = userRatings.corr(method='pearson', min_periods=100)

myRatings = userRatings.loc[574].dropna()
simCandidates = pd.Series()
for i in range(574, len(myRatings.index)):
    # Извлекаем фильмы, похожие на оцененные мной
    sims = corrMatrix[myRatings.index[i]].dropna()
    # Далее оцениваем их сходство в зависимости от того, как я оценил тот или иной фильм
    sims = sims.map(lambda x: x * myRatings[i])
    # Добавляем индекс в список сравниваемых кандидатов
    simCandidates = simCandidates.append(sims)

simCandidates.sort_values(inplace=True, ascending=False)
simCandidates = simCandidates.groupby(simCandidates.index).sum()
simCandidates.sort_values(inplace = True, ascending = False)
print(simCandidates)
filteredSims = simCandidates.drop(myRatings.index)
print(filteredSims)