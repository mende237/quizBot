from http import client
from unittest import async_case
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.utils import Category , Difficulty
from QuizBot import QuizBot
from datetime import datetime
from utils.utils import connect_db



class BotManager:
	TELEGRAM_API_TOKEN = ""

	
	quiz_API_url = "https://quizapi.io/api/v1/questions"
	telegram_bot_url = "https://api.telegram.org/bot{}/{}"
							  
	quiz_urls = {"specific" : ["https://quizapi.io/api/v1/questions"],
				"genral" : "https://opentdb.com/api.php?amount={nbr_limite}&category=18&difficulty={difficulty}&encode=url3986"}
	

	#contient la liste des bots qui sont lancés
	bot_list = []
	#est un dictionnaire dont la cle est le nom d'utilisateur et la valeur nom d'utilisateur du canal associé
	connexions = {}
		
	def get_scheduler() -> AsyncIOScheduler:
		return AsyncIOScheduler()
	
	#cette fonction verifie si l'identifiant du groupe passe existe dans la BD
	def verification_BD(groupe_id):
		conn = connect_db()
		print(conn)
		my_cursor = conn.cursor()
				
		my_cursor.execute("SELECT USERNAME FROM GROUPE WHERE USERNAME = %s" , (groupe_id,))
		results = my_cursor.fetchall()
		# print(type(results))
		for x in results:
			if x[0] == groupe_id:
				conn.close()
				return 1
		
		conn.close()
		return 0
	
	#cette fonction insere le goupe et le bot associe dans la base de donne
	#si tout ce passe bien elle retoure l'identifiant du bot au cas contraire elle retourne None
	def insert_group(user_name , parameters , description = None):
		conn = connect_db()
		my_cursor = conn.cursor()
		
		#on verifie que le groupe n'existe pas encore dans la bd 
		rep = BotManager.verification_BD(user_name)
		if rep == 1:
			return None
		
		sql = "INSERT INTO BOT  ({params}) VALUES ("
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
		# print(sql)
		# print(tuple(value))
		my_cursor.execute(sql , tuple(value))
		#conn.commit()
		#on recupere l'identifiant du bot que l'on vient d'inserer dans la BD
		my_cursor.execute("SELECT ID FROM BOT ORDER BY ID DESC LIMIT 1")
		id_Bot = (my_cursor.fetchall())[0][0]
		if description == None:
			my_cursor.execute("INSERT INTO GROUPE (USERNAME , ID) VALUES (%s , %s)" , (user_name , str(id_Bot)))
		else:
			my_cursor.execute("INSERT INTO GROUPE (USERNAME , DESCRIPTION , ID) VALUES (%s , %s , %s)" , (user_name , description, str(id_Bot)))
		
		my_cursor.execute("UPDATE BOT SET USERNAME = %s WHERE ID = %s" , (user_name , id_Bot))

		conn.commit()
		conn.close()
	
		return id_Bot
	
		
	def update_parameter(user_name , parameters):        
		conn = connect_db()
		my_cursor = conn.cursor()
		my_cursor.execute("SELECT ID FROM BOT WHERE USERNAME = %s" , (user_name,))
		
		temp = my_cursor.fetchall()
		if len(temp) == 0:
			conn.close()
			return -1
		
		sql = "UPDATE BOT SET {params} WHERE USERNAME = %s"
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
		# print(sql)
		# print(tuple(value))
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
		
		
	async def load_all(app : client):
		conn = connect_db()
		# print(conn)
		my_cursor = conn.cursor()
				
		my_cursor.execute("SELECT * FROM BOT")
		results = my_cursor.fetchall()
		print(results)
		#on selectionne tous les entêtes sauf username_Groupe
		column_names = [i[0] for i in my_cursor.description]
		data = [dict(zip(column_names , row)) for row in results]
		
		for line in data:
			my_cursor.execute("SELECT USERNAME FROM GROUPE WHERE GROUPE.ID = %s" , (line["ID"],))
			username = my_cursor.fetchall()[0][0]
			# print(f"$$$$$$$$$$$$$$$$$$$$ load all {BotManager.quiz_urls} $$$$$$$$$$$$$$$$$$$$$$")
			quizBot = await QuizBot.new_Bot(line["ID"] , username , app , BotManager.quiz_urls , BotManager.telegram_bot_url
										, BotManager.TELEGRAM_API_TOKEN , line , time_zone=line['TIMEZONE'])
			# print(line)
			BotManager.bot_list.append(quizBot)
			await quizBot.schedule_quiz()
		conn.close()
	
		
	
	# cette fonction permet de renvoyer un message d'erreur a l'utilisateur
	def send_error_message(message):
		print(message)
		pass
	
	

	#cette fonction permet de parser les commandes envoyés par l'utilisateur
	def parse_parameter(command , groupe_id):
		attribut = None
		value = None
		
		category = None
		difficulty = None
		nbr_limite = None
		automatic = None
		hour = None
		period = None
		time_zone = None

		parameter = {}
		
		if (len(command) - 1) % 2 == 0:
			for i in range(1 , len(command) - 1 , 2):
				attribut = command[i]
				value = command[i+1]

				if attribut.lower() == "category".lower():
					category = BotManager.text_to_Enum(value , True)
					if category != None:
						parameter["CATEGORY"] = value
					else:
						print("errrrorrrr unknow category")
						return None
				
				if attribut.lower() == "nbr_limite".lower():
					#******************************** a modifie ************************
					#*******************************************************************
					nbr_limite = value
					parameter["NBR_LIMITE"] = nbr_limite
					# if category != None:
					# else:
					#     print("errrrorrrr unknow category")

				if attribut.lower() == "automatic".lower():
					if value.lower() == "false".lower():
						automatic = 0
					elif value.lower() == "true".lower():
						value = 1
						automatic = 1
						# #####
						# #a modifier 
						# now = datetime.now()
						# current_time = now.strftime("%H:%M:%S")
						# parameter["HOUR"] = current_time
						# ######
						# #####
					else:
						print("errrrrrrrror unknow boolean")
						return None
					
					parameter["AUTOMATIC"] = automatic
				
				if attribut.lower() == "difficulty".lower():
					difficulty = BotManager.text_to_Enum(value , False)
					if difficulty != None:
						parameter["DIFFICULTY"] = value
					else:
						print("errrrorrrr unknow difficulty")
						return None
						
				if attribut.lower() == "hour".lower():
					hour = BotManager.verify_hour(value)
					if hour != None:
						parameter["HOUR"] = hour = datetime.strptime(hour, "%H:%M:%S")
					else:
						print("errrrorrrr can able to format hour")
						return None
				
				if attribut.lower() == "period".lower():
					period = BotManager.verify_hour(value , False)
					if period != None:
						parameter["PERIOD"] = period
					else:
						print("errrrorrrr can able to format period")
						return None

				if attribut.lower() == "time_zone".lower():
					time_zone = value
					parameter["TIMEZONE"] = time_zone

				if attribut.lower() == "evaluation_period".lower():
					evaluation_period = BotManager.verify_hour(value , False)
					if evaluation_period != None:
						parameter["EVALUATION_PERIOD"] = evaluation_period
					else:
						print("errrrorrrr can able to format period")
						return None

				if attribut.lower() == "response_time".lower():
					response_time = BotManager.verify_hour(value , False)
					if response_time != None:
						parameter["RESPONSE_TIME"] = response_time
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
		   
	def find_bot(groupe_id) -> QuizBot:
		for bot in BotManager.bot_list:
			# print(f"parma {groupe_id} group_id {bot.groupe_id}")
			if bot.groupe_id == groupe_id:
				return bot

		return None

			

