from telebot import *
from filter import *

bot = TeleBot("618592065:AAErIC2FWciq26gumbtJDNhAKRwmlSe1nk4")

currentMovie_id = 0
recommendations = pd.DataFrame
ratings = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                            names=['user_id', 'movie_id', 'rating', 'timestamp'])
isRec = 0
indexOfRow = 0
requestedFilms = 0
myRatings = pd.DataFrame
userAddRating = True

genreArray = [('Экшн','экшн','action'),
               ('Криминал','криминал','crime'),
               ('Триллер','триллер','thriller'),('Драма','драм','drama'),('Комедия','комед','смешн','comedy')
    ,('Романтика','романти','romance'),('Хоррор','хоррор','ужас','horror'),('Мистика','мисти','тайн','mystery'),('Фантастика','фантасти','sci-fi'),('Фэнтези','фэнтез','фентез','fantasy'),('Приключение','приключен','adventure'),('Документалистика','документал','documentary'),('Детское','детск','дет','children'),
               ('Война','войн','war'),('Мюзикл','мюзикл','музык','musical'),('Мультфильм','мульт','анимац','animation')]
headers = {'Accept': 'application/json'}
payload = {'api_key': 'd9ff9f47e912c90958ab3165c9ff713b'}
response = requests.get("http://api.themoviedb.org/3/configuration", params=payload, headers=headers)
response = json.loads(response.text)
base_url = response['images']['base_url'] + 'w185'


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,'Список доступных команд:\n'
                                     '1. /start\n'
                                     '2. /help\n'
                                     '3. /genres\n'
                                     '4. /recommend\n'
                                     '5. /me\n')
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     'Привет! Здесь ты можешь найти себе интересные фильмы! Чтобы получить персональные рекомендации - напиши "Порекомендуй"'
                     ,
                     parse_mode='Markdown',)
    bot.send_message(message.chat.id,
                     'Однако, для этого нужно оценить как минимум 10 фильмов! '
                     'Чтобы это сделать, просто напиши название фильма на английском языке, и оцени его как тебе вздумается!'
                     'Плюс, можно получить рекомендации по отдельным жанрам фильмов! Для этого напиши нужную тебе категорию!',
                     parse_mode='Markdown', )
    bot.send_message(message.chat.id,
                     'Каждый оцененный, и, надеюсь на это, просмотренный фильм можно увидеть, написав команду /me, или выбрав ее из главного меню!',
                     parse_mode='Markdown')

def pages_keyboard(first, current, movie_id, user_id):
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if first > 0:
        btns.append(types.InlineKeyboardButton(
        text='⬅', callback_data='for_{}'.format(first-1)))
    # ratings2 = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
    #                        names=['user_id', 'movie_id', 'rating', 'timestamp'])
    global myRatings
    myRatings = get_user_ratings(user_id)
    alreadyRated = myRatings.loc[(myRatings['movie_id']==movie_id)]
    if(alreadyRated.empty == True):
        btns.append(types.InlineKeyboardButton(
        text='Оценить', callback_data='rec_{}'.format(current-1)))
    if current < len(recommendations):
        btns.append(types.InlineKeyboardButton(
        text='➡', callback_data='for_{}'.format(current)))
    keyboard.add(*btns)
    return keyboard, alreadyRated # возвращаем объект клавиатуры

def my_movies_keyboard(first, current):
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if first > 0:
        btns.append(types.InlineKeyboardButton(
        text='⬅', callback_data='myM_{}'.format(first-1)))
    global myRatings
    if current < len(myRatings):
        btns.append(types.InlineKeyboardButton(
        text='➡', callback_data='myM_{}'.format(current)))
    keyboard.add(*btns)
    return keyboard
@bot.message_handler(commands=['genres'])
@bot.message_handler(func=lambda msg: msg.text.lower().find('жанр') != -1)
def listCommands(message):
    bot.send_message(message.chat.id,'Доступные жанры:\n'
                                 '1. Экшн\n'
                                 '2. Криминал\n'
                                 '3. Триллер\n'
                                 '4. Драма\n'
                                 '5. Комедия\n'
                                 '6. Романтика\n'
                                 '7. Хоррор\n'
                                 '8. Мистика\n'
                                 '9. Фантастика\n'
                                 '10. Фэнтези\n'
                                 '11. Приключения\n'
                                 '12. Документалистика\n'
                                 '13. Детское\n'
                                 '14. Война\n'
                                 '15. Мюзикл\n'
                     '16. Мультфильм'
                 )
@bot.message_handler(commands=['me'])
@bot.message_handler(func=lambda msg: msg.text.lower().find('мои фильмы') != -1)
def get_my_films(message):
    global ratings
    global myRatings
    ratings = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                           names=['user_id', 'movie_id', 'rating', 'timestamp'])
    myRatings = get_user_ratings(message.chat.id)
    myRatings = pd.merge(myRatings, movies, how='inner', on=['movie_id', 'movie_id'])
    movie_id = myRatings["movie_id"].iloc[0]

    url = get_poster(myRatings["title"].iloc[0], movie_id, base_url)

    bot.send_message(message.chat.id,
                     '[' + myRatings['title'].iloc[0] + '](' + url + ')\n' + myRatings['genres'].iloc[0]+'\nВы оценили этот фильм на: '
                    +str(myRatings['rating'].iloc[0]),
                     parse_mode='Markdown',
                     reply_markup=my_movies_keyboard(0, 1))

@bot.message_handler(func=lambda m: True)
def mainFunction(message):
    global requestedFilms
    global currentMovie_id
    m_text = str(message.text).lower()
    if(m_text.find('рекоменд') != -1 or m_text.find('совет') != -1 or
            str(message.text).lower() == '/recommend'
            or [i for i in genreArray if [string for string in i if m_text.find(str(string)) != -1]]):
            # or [i for i in genreArray if m_text.find(i) != -1]):
        numberOfUserFilms = check_user_ratings(message.chat.id)
        if (numberOfUserFilms < 10):
            bot.send_message(message.chat.id,
                             'Для более полезных рекомендаций нужно оценить как минимум 10 фильмов! Осталось ' + str(10-numberOfUserFilms) + '.',
                             parse_mode='Markdown')
        else:
            get_recommedations(message)
            # global recommendations
            # recommendations = get_rec(message.chat.id)
            # if (m_text in genresArray):
            #     recommendations = recommendations.loc[recommendations['genres'].str.lower().str.find(m_text) != -1]
            # movie_id = recommendations["movie_id"].iloc[0]
            # url = get_poster(message.text, movie_id, base_url)
            # global isRec
            # isRec = 1
            # keyboard, al_mov = pages_keyboard(0, 1, movie_id, message.chat.id)
            # text = '['+recommendations['title'].iloc[0]+']('+url+')\n'+recommendations['genres'].iloc[0]
            # if (al_mov.empty != True):
            #     text = text + '\nВы оценили этот фильм на: ' + str(al_mov['rating'].iloc[0])
            # bot.send_message(message.chat.id,
            #                  text,
            #                  parse_mode='Markdown',
            #                  reply_markup=keyboard)
                             # reply_markup=pages_keyboard(0, 1, movie_id, message.chat.id))
    else:
        requestedFilms = get_films_by_name(message.text)
        if(requestedFilms.empty):
            bot.send_message(message.chat.id,
                             'Прости, такого фильма нет! Попробуй с другим названием!',
                             parse_mode='Markdown')
        else:
            requestedFilms = requestedFilms.reset_index(drop=True)
            if(len(requestedFilms.index)>1):
                text = 'Слишком много совпадений. Уточните, вы имели в виду, написав цифру нужного фильма:\n'
                for index,row in requestedFilms.iterrows():
                    text = text+str(index+1)+'. *'+ row['title']+'* \n'+row['genres']+'\n'
                msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
                bot.register_next_step_handler(msg,filmClarification)
            else:
                currentMovie_id = int(requestedFilms["movie_id"].iloc[0])
                url = get_poster(message.text, currentMovie_id,base_url)
                create_img(url)
                img = open('out.jpg', 'rb')
                isRec = 0
                ratings = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                                           names=['user_id', 'movie_id', 'rating', 'timestamp'])
                ratings = ratings.loc[(ratings['movie_id']==currentMovie_id)&(ratings['user_id']==message.chat.id)]
                if(ratings.empty == True):
                    bot.send_photo(message.chat.id,img,caption='*'+requestedFilms['title'].all()+'*'+'\n'+ requestedFilms['genres'].all())
                    msg = bot.send_message(message.chat.id,'Можешь оценить этот фильм от 1 до 5!')
                    bot.register_next_step_handler(msg, film_rate)
                else:
                    bot.send_message(message.chat.id,
                                         '[' + requestedFilms['title'].iloc[0] + '](' + url + ')\n' + requestedFilms['genres'].iloc[
                                             0] + '\nВы оценили этот фильм на: '
                                         + str(ratings['rating'].iloc[0]),
                                         parse_mode='Markdown')

@bot.callback_query_handler(func=lambda c: c.data)
def pages(c):
    global currentMovie_id
    global indexOfRow
    global ratings

    indexOfRow = int(c.data[4:])

    if(c.data[:4] == 'rec_'):
        currentMovie_id = int(recommendations["movie_id"].iloc[indexOfRow])
        movie_title = recommendations["title"].iloc[indexOfRow]
        movie_genres = recommendations["genres"].iloc[indexOfRow]
        url = get_poster(recommendations["title"].iloc[indexOfRow], currentMovie_id, base_url)
        create_img(url)
        img = open('out.jpg', 'rb')
        film = get_films_by_name(movie_title,movie_genres)
        bot.send_photo(c.message.chat.id, img, caption=film['genres'].all())
        msg = bot.send_message(c.message.chat.id, 'Можешь оценить этот фильм от 1 до 5!')
        bot.register_next_step_handler(msg, film_rate)
    elif(c.data[:4] == 'myM_'):
        currentMovie_id = int(myRatings["movie_id"].iloc[indexOfRow])
        url = get_poster(myRatings["title"].iloc[indexOfRow], currentMovie_id, base_url)
        create_img(url)
        img = open('out.jpg', 'rb')

        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text = '[' + myRatings['title'].iloc[indexOfRow] +'](' + url + ')\n'+myRatings['genres'].iloc[indexOfRow]+
                    '\nВы оценили этот фильм на: '
                    +str(myRatings['rating'].iloc[indexOfRow]),
            parse_mode='Markdown',
            reply_markup=my_movies_keyboard(indexOfRow,indexOfRow+1))
    else:
        currentMovie_id = int(recommendations["movie_id"].iloc[indexOfRow])
        url = get_poster(recommendations["title"].iloc[indexOfRow], currentMovie_id, base_url)
        create_img(url)
        img = open('out.jpg', 'rb')
        keyboard, alr_mov = pages_keyboard(indexOfRow, indexOfRow + 1, currentMovie_id, c.message.chat.id)
        text = '[' + recommendations['title'].iloc[indexOfRow] + '](' + url + ')\n'+recommendations['genres'].iloc[indexOfRow]
        if(alr_mov.empty == False):
            text= text+'\nВы оценили этот фильм на: '+str(alr_mov['rating'].iloc[0])
        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text = text, parse_mode='Markdown',
            reply_markup=keyboard)


def filmClarification(message):
    global currentMovie_id
    currentMovie_id = int(requestedFilms["movie_id"].iloc[int(message.text)-1])
    url = get_poster(message.text, currentMovie_id, base_url)
    create_img(url)
    img = open('out.jpg', 'rb')
    isRec = 0
    global ratings
    # # ratings = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
    #                        names=['user_id', 'movie_id', 'rating', 'timestamp'])
    ratingOfFilm = ratings.loc[(ratings['movie_id'] == currentMovie_id) & (ratings['user_id'] == message.chat.id)]
    print(requestedFilms)
    if (ratingOfFilm.empty == True):
        bot.send_photo(message.chat.id, img, caption=requestedFilms['genres'].all())
        msg = bot.send_message(message.chat.id, 'Можешь оценить этот фильм от 1 до 5.')
        bot.register_next_step_handler(msg, film_rate)
    else:
        bot.send_message(message.chat.id,
                         '[' + requestedFilms['title'].iloc[0] + '](' + url + ')\n' + requestedFilms['genres'].iloc[
                             0] +'\nВы оценили этот фильм на '+ str(ratingOfFilm["rating"].iloc[0]) + '.',
                         parse_mode='Markdown')

def film_rate(message):
        # if(len(message.text)==1):
        #     message.text = message.text+'.0'
        # if not re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', m.text):
        if not re.match(r'^([1-5])$', message.text):
            msg = bot.send_message(message.chat.id, 'Некорректный балл!', parse_mode='Markdown')
            bot.register_next_step_handler(msg, film_rate)
        else:
            if (float(message.text)) not in range(1,6):
                mainFunction(message)
            else:
                global myRatings
                newRatings = add_rate(message.chat.id, currentMovie_id, float(message.text), message.date)
                newRatings = pd.merge(newRatings, movies, how='inner', on=['movie_id', 'movie_id'])
                myRatings = get_user_ratings(message.chat.id)
                if(myRatings.empty == True):
                    myRatings = newRatings
                else:
                    myRatings = myRatings.append(newRatings, ignore_index=True)
                hideBoard = types.ReplyKeyboardRemove()
                global userAddRating
                userAddRating = True
                bot.send_message(message.chat.id,
                                 'Отлично! Вы оценили этот фильм на '+str(float(message.text))+'!',
                                 # global userAddRating
                                 # userAddRating = True
                                 parse_mode='Markdown', reply_markup=hideBoard)

                if(isRec == 1):
                    currentMovie = recommendations.loc[recommendations['movie_id'] == currentMovie_id]
                    currentMovie = currentMovie['title'].iloc[0]
                    url = get_poster(currentMovie, currentMovie_id, base_url)
                    keyboard, al_mov = pages_keyboard(indexOfRow, indexOfRow+1, recommendations['movie_id'].iloc[indexOfRow], message.chat.id)
                    text = '[' + recommendations['title'].iloc[indexOfRow] + '](' + url + ')\n' + recommendations['genres'].iloc[indexOfRow]
                    if (al_mov.empty != True):
                        text = text + '\nВы оценили этот фильм на: ' + str(al_mov['rating'].iloc[0])
                    bot.send_message(message.chat.id,
                                     text,
                                     parse_mode='Markdown',
                                     reply_markup=keyboard)

def get_recommedations(message):
    global recommendations
    global userAddRating
    recommendations, userAddRating = get_rec(message.chat.id,userAddRating)
    m_text = str(message.text).lower()
    genre = ''
    for item in genreArray:
        for string in item:
            if m_text.find(str(string)) != -1:
                genre = str(item[-1])
                print('жанр'+str(genre))
                recommendations, userAddRating = get_rec(message.chat.id, userAddRating,genre )
                # recommendations = recommendations.loc[recommendations['genres'].str.lower().str.find(item[-1]) != -1]
                break;
    currentMovie_id = recommendations["movie_id"].iloc[0]
    url = get_poster(message.text, currentMovie_id, base_url)
    global isRec
    isRec = 1
    keyboard, al_mov = pages_keyboard(0, 1, currentMovie_id, message.chat.id)
    text = '[' + recommendations['title'].iloc[0] + '](' + url + ')\n' + recommendations['genres'].iloc[0]
    if (al_mov.empty != True):
        text = text + '\nВы оценили этот фильм на: ' + str(al_mov['rating'].iloc[0])
    if(genre != ''):
        bot.send_message(message.chat.id,'Держите фильмы с жанром "'+genre+'", как и просили!',parse_mode='Markdown')
    bot.send_message(message.chat.id,
                     text,
                     parse_mode='Markdown',
                     reply_markup=keyboard)


bot.polling(none_stop=True)
