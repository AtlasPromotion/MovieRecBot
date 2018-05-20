from filter import *
from telebot import *


bot = TeleBot("618592065:AAErIC2FWciq26gumbtJDNhAKRwmlSe1nk4")
movie_id = 0
page_num = 0
rec = 0
ratings1 = 0
isRec = 0
indexOfRow = 0
headers = {'Accept': 'application/json'}
payload = {'api_key': 'd9ff9f47e912c90958ab3165c9ff713b'}
response = requests.get("http://api.themoviedb.org/3/configuration", params=payload, headers=headers)
# print(response.content)
response = json.loads(response.text)
base_url = response['images']['base_url'] + 'w185'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     'Привет! Здесь ты можешь найти себе интересные фильмы! Чтобы получить персональные рекомендации - напиши "Предсказывай"'
                     ,
                     parse_mode='Markdown',)
    bot.send_message(message.chat.id,
                     'Однако, для этого нужно оценить как минимум 10 фильмов! '
                     'Чтобы это сделать, просто напиши название фильма на английском языке, и оцени его как тебе вздумается!',
                     parse_mode='Markdown', )

def pages_keyboard(first, current, movie_id, user_id):
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if first > 0:
        btns.append(types.InlineKeyboardButton(
        text='⬅', callback_data='to_{}'.format(first-1)))
    ratings2 = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                           names=['user_id', 'movie_id', 'rating', 'timestamp'])
    if(ratings2.loc[(ratings2['movie_id']==movie_id)&(ratings2['user_id']==user_id)].empty == True):
        btns.append(types.InlineKeyboardButton(
        text='Оценить', callback_data='rec{}'.format(current-1)))
    if current < len(ratings2):
        btns.append(types.InlineKeyboardButton(
        text='➡', callback_data='to_{}'.format(current)))
    keyboard.add(*btns)
    return keyboard # возвращаем объект клавиатуры

def my_mov_keyboard(first, current):
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if first > 0:
        btns.append(types.InlineKeyboardButton(
        text='⬅', callback_data='mym{}'.format(first-1)))
    global ratings1
    if current < len(ratings1):
        btns.append(types.InlineKeyboardButton(
        text='➡', callback_data='mym{}'.format(current)))
    keyboard.add(*btns)
    return keyboard # возвращаем объект клавиатуры

@bot.message_handler(commands=['me'])
def get_my_films(message):
    global ratings1
    ratings1 = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                           names=['user_id', 'movie_id', 'rating', 'timestamp'])
    ratings1 = ratings1.loc[ratings1['user_id']==message.chat.id]
    ratings1 = pd.merge(ratings1, movies, how='inner', on=['movie_id', 'movie_id'])
    movie_id = ratings1["movie_id"].iloc[0]

    url = get_poster(ratings1["title"].iloc[0], movie_id, base_url)
    bot.send_message(message.chat.id,
                     '[' + ratings1['title'].iloc[0] + '](' + url + ')\n' + ratings1['genres'].iloc[0]+'\nВы оценили этот фильм на: '
                    +str(ratings1['rating'].iloc[0]),
                     parse_mode='Markdown',
                     reply_markup=my_mov_keyboard(0, 1))

@bot.message_handler(func=lambda m: True)
def get_film_desc(message):
    if(str(message.text).lower() == 'предсказывай'):
        if (check_user_ratings(message.chat.id) == 0):
            bot.send_message(message.chat.id,
                             'Дорогуша, для этого тебе надо сначала оценить как минимум 10 фильмов! Осталось',
                             parse_mode='Markdown')
        else:
            global rec
            rec = get_rec(message.chat.id)
            global movie_id
            global page_num
            movie_id = rec["movie_id"].iloc[0]
            url = get_poster(message.text, movie_id, base_url)
            # f = open('out.jpg', 'wb')
            # f.write(urllib.request.urlopen(url).read())
            # f.close()
            # # send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
            # img = open('out.jpg', 'rb')
            global isRec
            isRec = 1
            bot.send_message(message.chat.id,
                             '['+rec['title'].iloc[0]+']('+url+')\n'+rec['genres'].iloc[0],
                             parse_mode='Markdown',
                             reply_markup=pages_keyboard(0, 1, movie_id, message.chat.id))
    else:
        message1 = get_film(message.text)

        if(message1.empty):
            bot.send_message(message.chat.id,
                             'Прости, такого фильма нет! Попробуй с другим названием!',
                             parse_mode='Markdown')
        else:
            movie_id = int(message1["movie_id"].iloc[0])
            url = get_poster(message.text, movie_id,base_url)
            create_img(url)
            img = open('out.jpg', 'rb')
            isRec = 0
            ratings3 = pd.read_csv('ml-latest-small/ratings.csv', sep=',', encoding='latin-1',
                                   names=['user_id', 'movie_id', 'rating', 'timestamp'])
            ratings3 = ratings3.loc[(ratings3['movie_id']==movie_id)&(ratings3['user_id']==message.chat.id)]
            if(ratings3.empty == True):
                bot.send_photo(message.chat.id,img,caption=message1['genres'].all())
                msg = bot.send_message(message.chat.id,'Можешь оценить этот фильм от 1.0 до 5.0, включая дробную часть.')
                bot.register_next_step_handler(msg, film_rate)
            else:
                bot.send_message(message.chat.id,
                                 '[' + message1['title'].iloc[0] + '](' + url + ')\n' + message1['genres'].iloc[
                                     0] + '\nВы оценили этот фильм на: '
                                 + str(ratings3['rating'].iloc[0]),
                                 parse_mode='Markdown')


def film_rate(m):
        if not re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', m.text):
            msg = bot.send_message(m.chat.id, 'Invalid', parse_mode='Markdown')
            bot.register_next_step_handler(msg, film_rate)
        else:
            if (float(m.text)*10) not in range(10,60):
                get_film_desc(m)
            else:
                add_rate(m.chat.id, movie_id, float(m.text), m.date)
                hideBoard = types.ReplyKeyboardRemove()
                bot.send_message(m.chat.id,
                                 'Отлично! Вы оценили этот фильм на '+str(float(m.text))+'!',
                                 parse_mode='Markdown', reply_markup=hideBoard)
                if(isRec == 1):
                    message1 = rec.loc[rec['movie_id'] == movie_id]
                    message1 = message1['title'].iloc[0]
                    url = get_poster(message1, movie_id, base_url)
                    bot.send_message(m.chat.id,
                                     '[' + rec['title'].iloc[indexOfRow] + '](' + url + ')\n' + rec['genres'].iloc[indexOfRow],
                                     parse_mode='Markdown',
                                     reply_markup=pages_keyboard(indexOfRow, indexOfRow+1,rec['movie_id'].iloc[indexOfRow], m.chat.id))


@bot.callback_query_handler(func=lambda c: c.data)
def pages(c):
    global movie_id
    global indexOfRow
    global ratings1
    indexOfRow = int(c.data[3:])
    if(c.data[:3] == 'rec'):

        movie_id = int(rec["movie_id"].iloc[int(c.data[3:])])
        movie_title = rec["title"].iloc[int(c.data[3:])]
        movie_genres = rec["genres"].iloc[int(c.data[3:])]
        url = get_poster(rec["title"].iloc[int(c.data[3:])], movie_id, base_url)
        create_img(url)
        img = open('out.jpg', 'rb')
        message1 = get_film(movie_title,movie_genres)
        #keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #keyboard.add(*[types.KeyboardButton(str(name)) for name in range(1, 6)])
        msg = bot.send_photo(c.message.chat.id, img, caption=message1['genres'].all())
        msg = bot.send_message(c.message.chat.id, 'Можешь оценить этот фильм от 1.0 до 5.0, включая дробную часть')
        bot.register_next_step_handler(msg, film_rate)
    elif(c.data[:3] == 'mym'):
        movie_id = int(ratings1["movie_id"].iloc[int(c.data[3:])])
        url = get_poster(ratings1["title"].iloc[int(c.data[3:])], movie_id, base_url)
        create_img(url)
        img = open('out.jpg', 'rb')
        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text = '[' + ratings1['title'].iloc[int(c.data[3:])] +'](' + url + ')\n'+ratings1['genres'].iloc[int(c.data[3:])]+
                    '\nВы оценили этот фильм на: '
                    +str(ratings1['rating'].iloc[int(c.data[3:])]),
            parse_mode='Markdown',
            reply_markup=my_mov_keyboard(int(c.data[3:]),int(c.data[3:])+1))
    else:
        movie_id = int(rec["movie_id"].iloc[int(c.data[3:])])
        print('mov_id'+str(movie_id))
        print(rec["title"].iloc[int(c.data[3:])])
        url = get_poster(rec["title"].iloc[int(c.data[3:])], movie_id, base_url)
        create_img(url)
        img = open('out.jpg', 'rb')
        bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text = '[' + rec['title'].iloc[int(c.data[3:])] + '](' + url + ')\n'+rec['genres'].iloc[int(c.data[3:])], parse_mode='Markdown',
            reply_markup=pages_keyboard(int(c.data[3:]),int(c.data[3:])+1,movie_id, c.message.chat.id))
bot.polling()
