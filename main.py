from Bot_manager import BotManager
from QuizBot import QuizBot

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

	print(informations)

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
			quizBot = await QuizBot.new_Bot(bot_id , app , username , BotManager.quiz_urls , BotManager.telegram_bot_url
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
		await quizBot.set_parameters(command)
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

		
# async def run_together():
# 	asyncio.gather(await BotManager.schedule_quizBot() , 
# 				   await idle())

QuizBot.scheduler = BotManager.get_scheduler()
print("I am alive")
app.run(BotManager.load_all(app))
QuizBot.scheduler.start()

app.start()
idle()
app.stop()
