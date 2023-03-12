					#  ██████╗ ██╗   ██╗██╗███████╗    ██████╗  ██████╗ ████████╗
					# ██╔═══██╗██║   ██║██║╚══███╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
					# ██║   ██║██║   ██║██║  ███╔╝     ██████╔╝██║   ██║   ██║   
					# ██║▄▄ ██║██║   ██║██║ ███╔╝      ██╔══██╗██║   ██║   ██║   
					# ╚██████╔╝╚██████╔╝██║███████╗    ██████╔╝╚██████╔╝   ██║   
					#  ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝   
                                                           

										
										# ██╗   ██╗ ██╗    ██████╗ 
										# ██║   ██║███║   ██╔═████╗
										# ██║   ██║╚██║   ██║██╔██║
										# ╚██╗ ██╔╝ ██║   ████╔╝██║
										#  ╚████╔╝  ██║██╗╚██████╔╝
										#   ╚═══╝   ╚═╝╚═╝ ╚═════╝ 
                         
from Bot_manager import BotManager
from QuizBot import QuizBot
from pyrogram import Client , filters , idle
from pyrogram.raw.functions.messages.get_poll_results import GetPollResults

import locale
from decouple import config
config.encoding = locale.getpreferredencoding(False)

api_id = config('TELEGRAM_API_ID')
api_hash = config('TELEGRAM_API_HASH')
bot_token = config('TELEGRAM_API_TOKEN')


QUIZ_API_TOKEN = config('QUIZ_API_TOKEN')
TELEGRAM_API_TOKEN = config('TELEGRAM_API_TOKEN')


BotManager.quiz_urls["specific"].append(QUIZ_API_TOKEN)
BotManager.TELEGRAM_API_TOKEN = TELEGRAM_API_TOKEN

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

async def register(app : Client , message , is_private_message = False):
	id = message.chat.id
	quizBot = None
	informations = extract_usefull_information(message , is_private_message = is_private_message)
	username = informations["username"]

	# print(informations)

	if is_private_message == True:
		if message.from_user.username not in BotManager.connexions.keys():
			await app.send_message(id, "connect you before")
			return None
		else:
			username = BotManager.connexions[username]
			
	quizBot = BotManager.find_bot(username)
	if quizBot != None:
		# BotManager.send_error_message("group already register")
		await app.send_message(id, "group already register")
	else:
		command = BotManager.parse_parameter(informations["command"])
		if command == None or not bool(command):
			return None

		bot_id = BotManager.insert_group(username , command)
		#on verifie que l'insertion en BD c'est bien passé
		if bot_id != None:
			quizBot = await QuizBot.new_Bot(bot_id , app , username , command["TIMEZONE"],  BotManager.quiz_urls , BotManager.telegram_bot_url
											, BotManager.TELEGRAM_API_TOKEN , command)
			BotManager.bot_list.append(quizBot)
			await app.send_message(id, "register successful")
			await quizBot.schedule_quiz()

		# print(command)
		# print("register your group before")



async def update(app : Client, message , is_private_message = False):
	informations = extract_usefull_information(message , is_private_message = is_private_message)
	username = informations["username"]
	id = message.chat.id
	if is_private_message == True:
		if message.from_user.username not in BotManager.connexions.keys():
			await app.send_message(id, "connect you before")
			return None
		else:
			username = BotManager.connexions[username]

	quizBot = BotManager.find_bot(username)
	if quizBot != None:
		command = BotManager.parse_parameter(informations["command"])
		if command == None or not bool(command):
			await app.send_message(id, "errorrrrrrrrrrrrrrrrrrr")
			return None

		BotManager.update_parameter(username , command)
		await quizBot.set_parameters(command)
		# print(command)
		# print("group already register")
	else:
		await app.send_message(id, "register your group before")


async def send(app : Client, message , is_private_message = False):
	id = message.chat.id
	informations = extract_usefull_information(message , is_private_message = is_private_message)
	username = informations["username"]

	if is_private_message == True:
		if message.from_user.username not in BotManager.connexions.keys():
			await app.send_message(id, "connect you before")
			return None
		else:
			username = BotManager.connexions[username]

	quizBot = BotManager.find_bot(username)
	conn = connect()
	if quizBot != None:
		await quizBot.send_quiz(conn)       
	else:
		await app.send_message(id, "register your group before")


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
	id = message.chat.id
	informations = extract_usefull_information(message , is_private_message = True)
	username = informations["username"]
	canal_username = BotManager.parse_connect_parameter(informations["command"])

	if username in BotManager.connexions.keys():
		await app.send_message(id, "you are already connect")
	else:
		if canal_username == None:
			await app.send_message(id, "enter your channel username")
		else:
			BotManager.connexions[username] = canal_username
			await app.send_message(id, "success connexion")

@app.on_message(filters.command("disconnect") & filters.private)
async def connect(app , message):
	id = message.chat.id
	if message.from_user.username in BotManager.connexions.keys():
		BotManager.connexions.pop(message.from_user.username)
		await app.send_message(id, "succeful logout")
	else:
		await app.send_message(id, "unknow user")


QuizBot.scheduler = BotManager.get_scheduler()
print("Botmanager is started .....")
app.run(BotManager.load_all(app))
QuizBot.scheduler.start()


app.start()
idle()
app.stop()
