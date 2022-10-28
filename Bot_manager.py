#!/home/dimitri/Quiz_bot/myvenv/bin python
from http import client
from unittest import async_case
import mysql.connector
from utils.config import config
from utils.utils import Category , Difficulty
from QuizBot import QuizBot
import asyncio
import schedule
import threading 
import time


class BotManager:
    QUIZ_API_TOKEN = "GMtZogjvXFZHn36AIygLrNrHRrzhWmZKzySbAVYL"
    TELEGRAM_API_TOKEN = "5401510818:AAF9L3gnfKEUzzk06JDe1U0Sm1bNBhkLpUg"


    quiz_API_url = "https://quizapi.io/api/v1/questions"
    telegram_bot_url = "https://api.telegram.org/bot{}/{}"

    quiz_urls = {"specific" : ["https://quizapi.io/api/v1/questions" , "GMtZogjvXFZHn36AIygLrNrHRrzhWmZKzySbAVYL"],
                "genral" : "https://opentdb.com/api.php?amount={nbr_limite}&category=18&difficulty={difficulty}"}
    

    #contient la liste des bots qui sont lancés
    bot_list = []
    #est un dictionnaire dont la cle est le nom d'utilisateur et la valeur nom d'utilisateur du canal associé
    connexions = {}
    
    def connect():
        conn = mysql.connector.connect(
            host = config.host,
            user = config.user,
            passwd = config.password,
            database = config.database,
            port = config.port
        )
        return conn
    
    
    #cette fonction verifie si l'identifiant du groupe passe existe dans la BD
    def verification_BD(groupe_id):
        conn = BotManager.connect()
        print(conn)
        my_cursor = conn.cursor()
                
        my_cursor.execute("SELECT username FROM Groupe WHERE username = %s" , (groupe_id,))
        results = my_cursor.fetchall()
        print(type(results))
        for x in results:
            if x[0] == groupe_id:
                conn.close()
                return 1
        
        conn.close()
        return 0
    
    #cette fonction insere le goupe et le bot associe dans la base de donne
    #si tout ce passe bien elle retoure l'identifiant du bot au cas contraire elle retourne None4
    def insert_group(user_name , parameters , description = None):
        conn = BotManager.connect()
        my_cursor = conn.cursor()
        
        #on verifie que le groupe n'existe pas encore dans la bd 
        rep = BotManager.verification_BD(user_name)
        if rep == 1:
            return None
        
        sql = "INSERT INTO Bot  ({params}) VALUES ("
        value = []
        params = ""
        
        keys = parameters.keys()
        
        for key in keys:
            if parameters[key] != None:
                value.append(parameters[key])
                params = params + key + " ,"
                sql = sql + "%s ,"
        
        if params[len(params) - 1] == ",":
            params = params[:-1:]
            
        if sql[len(sql) - 1] == ",":
            sql = sql[:-1:] 
        
        sql = sql + ")"
        sql = sql.format(params = params)
        print(sql)
        print(tuple(value))
        my_cursor.execute(sql , tuple(value))
        #conn.commit()
        #on recupere l'identifiant du bot que l'on vient d'inserer dans la BD
        my_cursor.execute("SELECT id FROM Bot ORDER BY id DESC LIMIT 1")
        id_Bot = (my_cursor.fetchall())[0][0]
        print(f"dsdssdsdddddddddddddddddddddddddddddddddddddd {id_Bot}")
        if description == None:
            my_cursor.execute("INSERT INTO Groupe (username , id_Bot) VALUES (%s , %s)" , (user_name , str(id_Bot)))
        else:
            my_cursor.execute("INSERT INTO Groupe (username , description , id_Bot) VALUES (%s , %s , %s)" , (user_name , description, str(id_Bot)))
        
        my_cursor.execute("UPDATE Bot SET username_Groupe = %s WHERE id = %s" , (user_name , id_Bot))

        conn.commit()
        conn.close()
    
        return id_Bot
    
        
    def update_parameter(user_name , parameters):        
        conn = BotManager.connect()
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT id FROM Bot WHERE username_Groupe = %s" , (user_name,))
        
        temp = my_cursor.fetchall()
        if len(temp) == 0:
            conn.close()
            return -1
        
        sql = "UPDATE Bot SET {params} WHERE username_Groupe = %s"
        params = ""
        value = []
        
        keys = parameters.keys()
        
        for key in keys:
            if parameters[key] != None:
                value.append(parameters[key])
                params = params + key + " = %s,"
                
                
        if params[len(params) - 1] == ",":
            params = params[:-1:]
        
        value.append(user_name)
        sql = sql.format(params = params)
        print(sql)
        print(tuple(value))
        my_cursor.execute(sql , tuple(value))
    
        conn.commit()
        conn.close()
        return 1
    

    # cette fonction permet de la category ou de la difficulte sous forme de texte a l'enumeration
    # associe
    def text_to_Enum(str , is_category = True):
        if is_category == True:
            if str.lower() == "Linux".lower():
                return  Category.LINUX
            if str.lower() == "bash".lower():
                return  Category.BASH
            elif str.lower() == "DevOps".lower():
                return Category.DEVOPS
            elif str.lower() == "sql".lower():
                return Category.SQL
            elif str.lower() == "code".lower():
                return  Category.CODE
            elif str.lower() == "cms".lower():
                return  Category.CMS
            elif str.lower() == "Docker".lower():
                return Category.DOCKER
            elif str.lower() == "random".lower():
                return Category.RANDOM
            elif str.lower() == "general".lower():
                return Category.GENERAL
            else:
                return None
        else:
            if str.lower() == "easy".lower():
                return Difficulty.EASY
            elif str.lower() == "medium".lower():
                return Difficulty.MEDIUM
            elif str.lower() == "hard".lower():
                return Difficulty.HARD
            else:
                return None
        
        
    async def load_all(app):
        print("*******************************************************************************")
        conn = BotManager.connect()
        print(conn)
        my_cursor = conn.cursor()
                
        my_cursor.execute("SELECT * FROM Bot")
        results = my_cursor.fetchall()
        #on selectionne tous les entêtes sauf username_Groupe
        column_names = [i[0] for i in my_cursor.description if i[0] != 'username_Groupe']
        data = [dict(zip(column_names , row)) for row in results]
        
        for line in data:
            my_cursor.execute("SELECT username FROM Groupe where id_Bot = %s" , (line["id"],))
            username = my_cursor.fetchall()[0][0]
            quizBot = QuizBot(line["id"] , username , app , BotManager.quiz_urls , BotManager.telegram_bot_url
                                        , BotManager.TELEGRAM_API_TOKEN , line)
            print(line)
            BotManager.bot_list.append(quizBot)
            await quizBot.schedule_quiz()
        conn.close()
    
        
    
    # cette fonction permet de renvoyer un message d'erreur a l'utilisateur
    def send_error_message(message):
        print(message)
        pass
    
    #cette fonction permet de parser les commandes envoyés par l'utilisateur
    def parse_parameter(command):
        attribut = None
        value = None
        
        category = None
        difficulty = None
        nbr_limite = None
        automatic = None
        hour = None
        period = None
        
        parameter = {}
        
        if (len(command) - 1) % 2 == 0:
            for i in range(1 , len(command) - 1 , 2):
                attribut = command[i]
                value = command[i+1]

                if attribut.lower() == "category".lower():
                    category = BotManager.text_to_Enum(value , True)
                    if category != None:
                        parameter["category"] = value
                    else:
                        print("errrrorrrr unknow category")
                        return None
                
                if attribut.lower() == "nbr_limite".lower():
                    #******************************** a modifie ************************
                    #*******************************************************************
                    nbr_limite = value
                    parameter["nbr_limite"] = nbr_limite
                    # if category != None:
                    # else:
                    #     print("errrrorrrr unknow category")

                if attribut.lower() == "automatic".lower():
                    if value.lower() == "false".lower():
                        automatic = 0
                    elif value.lower() == "true".lower():
                        value = 1
                        automatic = 1
                    else:
                        print("errrrrrrrror unknow boolean")
                        return None
                    
                    parameter["automatic"] = automatic
                
                if attribut.lower() == "difficulty".lower():
                    difficulty = BotManager.text_to_Enum(value , False)
                    if difficulty != None:
                        parameter["difficulty"] = value
                    else:
                        print("errrrorrrr unknow difficulty")
                        return None
                        
                if attribut.lower() == "hour".lower():
                    hour = BotManager.verify_hour(value)
                    if hour != None:
                        parameter["hour"] = hour
                    else:
                        print("errrrorrrr can able to format hour")
                        return None
                
                if attribut.lower() == "period".lower():
                    period = BotManager.verify_hour(value , False)
                    if period != None:
                        parameter["period"] = period
                    else:
                        print("errrrorrrr can able to format period")
                        return None
                    
            return parameter
        else:
            print("command errrrrorrrr")
            return None     

    def parse_connect_parameter(command):
        if len(command) == 2:
            return command[1]
        else:
            return None
        pass        
    
    #cette fonction permet gerer les erreur convertion
    def handle_error_parsed(parsed_command , is_register_command = True):
        
        pass
    
    #cette fonction est charge de veifier la chaine passe en parametre respecte
    #le format de l'heure
    def verify_hour(hour , is_hour = True):
        return hour
           
    def find_bot(groupe_id):
        for bot in BotManager.bot_list:
            if bot.groupe_id == groupe_id:
                return bot

        return None

    async def schedule_quizBot():
        while True:
            # Checks whether a scheduled task
            # is pending to run or not
            task = asyncio.create_task(asyncio.sleep(1))
            try:
                await task
            except asyncio.CancelledError:
                break
            
            print("cooollllllll")
            schedule.run_pending()
            time.sleep(1)
    
# BotManager.insert_group(user_name="tamo" , automatic="0" , nbr_limite="35" , period= "256")
# r = BotManager.update_parameter("tamo" , difficulty="hard" , category = "window")
# r = BotManager.update_automatic_parameter("tamo" , difficulty="easy" , category = "window" , period = "123")

# r = BotManager.update_base_parameter("tamo" , category = "window" , nbr_limite = "2" , automatic= "1")

# r = BotManager.verification_BD("tamo")
# print(r)



import asyncio
from pyrogram import Client , filters , enums , idle

api_id = 15150655
api_hash = "68e947ab567a62b78c70b8243307623c"
bot_token = "5401510818:AAF9L3gnfKEUzzk06JDe1U0Sm1bNBhkLpUg"

app = Client(
    "my_bot",
    api_id=api_id, 
    api_hash=api_hash,
    bot_token=bot_token
)



def extract_usefull_information(message , is_private_message = False):

    username = None
    if is_private_message == True:
        username = message.from_user.username
    else:
        username = message.sender_chat.username

    command = message.command
    description = None
    informations = {"username":username,
                    "command" : command,
                    "description" : description}
    
    
    return informations

async def register(app  , message , is_private_message = False):
	quizBot = None
	informations = extract_usefull_information(message , is_private_message = is_private_message)
	username = informations["username"]
	if is_private_message == True:
		if message.from_user.username not in BotManager.connexions.keys():
			print("connect you before")
			return None
		else:
			username = BotManager.connexions[username]
			
	quizBot = BotManager.find_bot(username)
	if quizBot != None:
		BotManager.send_error_message("group already register")
	else:
		command = BotManager.parse_parameter(informations["command"])
		if command == None or not bool(command):
			return None

		bot_id = BotManager.insert_group(username , command)
		#on verifie que l'insertion en BD c'est bien passé
		print("bot_id %s" , bot_id)
		if bot_id != None:
			quizBot = QuizBot(bot_id , app , username , BotManager.quiz_urls , BotManager.telegram_bot_url
											, BotManager.TELEGRAM_API_TOKEN , command)
			BotManager.bot_list.append(quizBot)
			await quizBot.schedule_quiz()
		print(command)
		print("register your group before")



async def update(app , message , is_private_message = False):
    informations = extract_usefull_information(message , is_private_message = is_private_message)
    username = informations["username"]

    if is_private_message == True:
        if message.from_user.username not in BotManager.connexions.keys():
            print("connect you before")
            return None
        else:
            username = BotManager.connexions[username]

    quizBot = BotManager.find_bot(username)
    if quizBot != None:
        command = BotManager.parse_parameter(informations["command"])
        if command == None or not bool(command):
            print("errorrrrrrrrrrrrrrrrrrr")
            return None

        BotManager.update_parameter(username , command)
        await quizBot.set_parameter_asynchronously(command)
        print(command)
        print("group already register")
    else:
        print("register your group before")

async def send(app , message , is_private_message = False):
    informations = extract_usefull_information(message , is_private_message = is_private_message)
    username = informations["username"]

    if is_private_message == True:
        if message.from_user.username not in BotManager.connexions.keys():
            print("connect you before")
            return None
        else:
            username = BotManager.connexions[username]

    quizBot = BotManager.find_bot(username)
    if quizBot != None:
        await quizBot.send_quiz()       
    else:
        print("register your group before")


@app.on_message(filters.command("register") & filters.channel)
async def register_from_channel(app , message):
   await register(app , message)

@app.on_message(filters.command("register") & filters.private)
async def register_from_private_chat(app , message):
	await register(app , message , is_private_message = True)

#update data from channel
@app.on_message(filters.command("update") & filters.channel)
async def update_info_from_channel(app , message):
    await update(app , message)

#update data from a private chat 
@app.on_message(filters.command("update") & filters.private)
async def update_info_from_private_chat(app , message):
    await update(app , message , is_private_message = True)


@app.on_message(filters.command("send") & filters.channel)
async def send_quiz_from_channel(app , message):
    await send(app , message)

@app.on_message(filters.command("send") & filters.private)
async def send_quiz_from_private_chat(app , message):
    await send(app , message , is_private_message = True)

@app.on_message(filters.command("connect") & filters.private)
async def connect(app , message):
    # print(message)
    informations = extract_usefull_information(message , is_private_message = True)
    username = informations["username"]
    canal_username = BotManager.parse_connect_parameter(informations["command"])

    if username in BotManager.connexions.keys():
        print("you are already connect")
    else:
        if canal_username == None:
            print("enter a username")
        else:
            BotManager.connexions[username] = canal_username
            print("connexion reussi")

@app.on_message(filters.command("disconnect") & filters.private)
async def connect(app , message):
    if message.from_user.username in BotManager.connexions.keys():
        BotManager.connexions.pop(message.from_user.username)
        print("succeful logout")
    else:
        print("unknow user")

        
print("I am alive")
app.run(BotManager.load_all(app))
app.start()
asyncio.gather(idle() , BotManager.schedule_quizBot())
# asyncio.run(BotManager.load_all(app))
# x = threading.Thread(target=BotManager.schedule_quizBot)
# x.start()
# BotManager.schedule_quizBot()


app.stop()
