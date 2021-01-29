import  telebot
import  requests
import mysql.connector



url = 'http://api.openweathermap.org/data/2.5/weather'
api_weather = 'c4cbd5a2c52a90888cf3be7c25c65b79'
TOKEN = '1315160443:AAFmUQK7D2Oo9oU05PzIroxEE-E7iIAhOcY'
bot = telebot.TeleBot(TOKEN)


db = mysql.connector.connect(
      host="db",
      user="dev",
      passwd="dev",
      database = "weather"
    )



cursor = db.cursor()

user_data = {}

#create_test_table = """
#CREATE TABLE IF NOT EXISTS 'weather' (
#  id INT AUTO_INCREMENT,
#  first_name TEXT NOT NULL,
#  last_name TEXT NOT NULL,
#  description TEXT NOT NULL,
#  PRIMARY KEY (id)
#) ENGINE = InnoDB
#"""
#cursor.execute(create_test_table)

print('Start Bot')


class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.last_name = ''

@bot.message_handler(commands= ['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Hello {name}. It's bot for weather)".format(name = message.from_user.username + "\n" +
        "Run the comm /weather and enter the city" ))


@bot.message_handler(commands= ['register'])
def register(message):
    msg = bot.send_message(message.chat.id, "Enter you first name")
    bot.register_next_step_handler(msg, process_firstname_step)



def process_firstname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        msg = bot.send_message(message.chat.id, "Enter you last name")
        bot.register_next_step_handler(msg, process_lastname_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
def process_lastname_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.last_name = message.text
        sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
        val = (user.first_name, user.last_name, user_id)
        cursor.execute(sql, val)
        db.commit()
        bot.send_message(message.chat.id, "You are registered successfully")

        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        cursor.execute("SELECT first_name FROM users WHERE user_id = {0}".format(user_id))
        first = cursor.fetchone()
        bot.send_message(message.chat.id, "Hello")
        bot.send_message(message.chat.id, first)

    except Exception as e:
        bot.reply_to(message, 'It will be impossible, or you are have registered')


def process_city(message):
    user_id = message.from_user.id
    user = user_data[user_id]
    city = message
    sql = "INSERT INTO users  (city) VALUES (%s)"
    val = (city)
    cursor.execute(sql, val)
    db.commit()


bot.enable_save_next_step_handlers(delay=2)





@bot.message_handler(commands=['weather'])
def start(message):
    city = bot.send_message(message.chat.id, 'Enter the city where you want to know the weather')
    bot.register_next_step_handler(city, weather_send)

def weather_send(message):
    s_city = message.text

    try:

        params = {'APPID': api_weather, 'q': s_city, 'units': 'metric', 'lang': 'eng'}
        result = requests.get(url, params=params)
        weather = result.json()

        three_d = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={'q': s_city,
                                                                                           'appid': api_weather,
                                                                                           'units': 'metric',
                                                                                           'lang': 'eng',
                                                                                           'cnt': '4'}).json()

        array = [str(i['dt_txt']) + " " + str(i['weather'][0]['description']) + " " + str(i['main']['temp']) for i in
                 three_d['list']]
        #three_days = ('\n'.join(map(str, array)))



        bot.send_message(message.chat.id, "In  " + str(weather["name"]) + " temperature " + str(
            float(weather["main"]['temp'])) + "°C" + "\n" +
                         "Wind speed " + str(float(weather['wind']['speed'])) + "\n" +
                         #"Давление " + str(float(weather['main']['pressure'])) + "\n" +
                         "Humidity " + str(float(weather['main']['humidity'])) +" %" + "\n" +
                        #"Видимость " + str(weather['visibility']) +" m"  + "\n" +
                         "Description : " + str.title(weather['weather'][0]["description"]) )

    except:
        bot.send_message(message.chat.id, "The sity - " + s_city + " not found")

@bot.message_handler(content_types=['text'])
def all_text(message):
    bot.send_message(message.chat.id, "Enter one of the comands")
    bot.send_message(message.chat.id, "/register")
    bot.send_message(message.chat.id, "/weather")


    #user_id = message.from_user.id
    #user_data[user_id] = User(message.text)
    #cursor.execute("SELECT first_name FROM users WHERE user_id = {0}".format(user_id))
    #first = cursor.fetchone()
    #cursor.execute("SELECT last_name FROM users WHERE user_id = {0}".format(user_id))
    #last = cursor.fetchone()

    #bot.send_message(message.chat.id, user_id)
    #bot.send_message(message.chat.id, first)
    #bot.send_message(message.chat.id, last)



bot.enable_save_next_step_handlers(delay=2)


bot.load_next_step_handlers()





if __name__ == "__main__":
    bot.polling(none_stop=True)