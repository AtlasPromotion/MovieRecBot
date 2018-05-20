import pandas  as pd
i_cols = ['movie_id','title','genres']
movies = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=i_cols,
 encoding='latin-1')

movies['title'] = movies['title'].str.rstrip(' ')
print(movies['title'])
movies.to_csv('ml-latest-small/movies.csv', index = False, header = False)