import os
import random
import requests
import json
from utils.utils import Category , Difficulty , Api ,VoteName , CATEGORY_TAB , DIFFICULTY_TAB , connect_db 
from utils.TimeManagement import get_time , time_in_second
from utils.StickersManagement import STICKERS
from Vote import Vote
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mysql.connector import MySQLConnection
from apscheduler.job import Job
from datetime import datetime
from datetime import timedelta
from urllib.parse import unquote
from pyrogram import Client , enums
import locale
from decouple import config


class QuizBot:
	__automatic = 0
	__category : str = "general"
	__difficulty : str= "easy"
	__nbr_limite : int = 5
	__hour : datetime = None
	__period : int = 24
	__job : Job = None
	__time_zone : str = 'Africa/Douala'
	__democracy : bool = True
	__evaluation_period : int = 7
	__response_time : int = 60
	
	__message = "this series of quizz is about {category} difficulty {difficulty}"

	#scheduler static variable
	scheduler : AsyncIOScheduler = None
	app : Client = None
	index = 0

	@classmethod
	async def new_Bot(cls , id , groupe_id , app:Client , quiz_urls , telegram_bot_url , TELEGRAM_API_TOKEN , parameters , time_zone = None):
		self = QuizBot()
		self.__id = id
		self.groupe_id = groupe_id
		if time_zone != None:
			self.__time_zone = time_zone
			
		QuizBot.app = app
		self.__quiz_urls = quiz_urls
		self.__telegram_bot_url = telegram_bot_url
		self.__TELEGRAM_API_TOKEN = TELEGRAM_API_TOKEN
		await self.set_parameters(parameters)
		QuizBot.index = QuizBot.index + 1
		return self

	
	async def set_parameters(self , parameters , is_init : bool = True):
		keys = parameters.keys()
		modif = False

		if "AUTOMATIC" in keys and parameters["AUTOMATIC"] != None:
			self.__automatic = parameters["AUTOMATIC"]
			# self.__hour = get_time(self.__time_zone)
			modif = True
   
		if "CATEGORY" in keys and parameters["CATEGORY"] != None:
			self.__category = parameters["CATEGORY"]

		if "DIFFICULTY" in keys and parameters["DIFFICULTY"] != None:
			self.__difficulty = parameters["DIFFICULTY"]
   
		if "NBR_LIMITE" in keys and parameters["NBR_LIMITE"] != None:
			self.__nbr_limite = parameters["NBR_LIMITE"]
   
		if "HOUR" in keys and parameters["HOUR"] != None:
			modif = True
			self.__hour = parameters["HOUR"]

			# try:
			# 	self.__hour = datetime.strptime(parameters["HOUR"] , "%Y-%m-%d %H:%M:%S")
			# except ValueError:
			# 	self.__hour = datetime.strptime(parameters["HOUR"] , "%H:%M:%S")
			# except TypeError:
			# 	self.__hour = parameters["HOUR"]
		
		if "PERIOD" in keys and parameters["PERIOD"] != None:
			modif = True
			self.__period = int(parameters["PERIOD"])
			
		print(f"automatic {self.__automatic } time zone {self.__time_zone} category {self.__category} difficulty {self.__difficulty} nbr_limte {self.__nbr_limite } hour {self.__hour } preiod {self.__period}")
		if is_init == False:
			if modif == True and self.__automatic == 1:
				if self.__job != None:
					self.__job.remove()

				await self.schedule_quiz()


	#*************************************setter**********************************
	def set_automatic(self , automatic):
		self.__automatic = automatic

	def set_category(self , category):
		self.__category = category
  
	def set_difficulty(self , difficulty):
		self.__difficulty = difficulty
	
	def set_nbr_limite(self , nbr_limite):
		self.__nbr_limite = nbr_limite
  
	def set_hour(self , hour):
		self.__hour = hour
  
	def set_period(self , period):
		self.__period = period


	def __category_switching(self):
		if self.__category.lower() == "Linux".lower():
			return  Category.LINUX
		if self.__category.lower() == "Bash".lower():
			return  Category.BASH
		elif self.__category.lower() == "DevOps".lower():
			return  Category.DEVOPS
		elif self.__category.lower() == "code".lower():
			return  Category.CODE
		elif self.__category.lower() == "cms".lower():
			return  Category.CMS
		elif self.__category.lower() == "sql".lower():
			return  Category.SQL
		elif self.__category.lower() == "Docker".lower():
			return  Category.DOCKER
		elif self.__category.lower() == "general".lower():
			return  Category.GENERAL
		elif self.__category.lower() == "random".lower():
			return Category.RANDOM


	def __difficulty_switching(self):
		if self.__difficulty == Difficulty.EASY:
			return "easy"
		elif self.__difficulty == Difficulty.MEDIUM:
			return "medium"
		else:
			return "hard"

	def quiz_request(self):
		result = None
		from_which_api = None
		if (self.__category_switching() == Category.BASH or self.__category_switching() == Category.CMS 
			or self.__category_switching() == Category.CODE or self.__category_switching() == Category.DEVOPS 
			or self.__category_switching() == Category.DOCKER or self.__category_switching() == Category.LINUX 
			or self.__category_switching() == Category.SQL or self.__category_switching() == Category.RANDOM):
			if self.__category_switching() != Category.RANDOM:
				from_which_api = Api.QUIZ_API
				result = os.popen(f"""curl {self.__quiz_urls["specific"][0]} -G -d apiKey={self.__quiz_urls["specific"][1]}\
																	            -d category={self.__category}\
																	            -d difficulty={self.__difficulty}\
																	            -d limit={self.__nbr_limite}""").read()
				temp = self.__quiz_urls["specific"][1]
				print(f"$$$ api_key {temp} category {self.__category} difficulty {self.__difficulty} limit {self.__nbr_limite}")
			else:
				from_which_api = Api.QUIZ_API
				result = os.popen(f"""curl {self.__quiz_urls["specific"][0]} -G -d apiKey={self.__quiz_urls["specific"][1]}\
																	            -d limit={self.__nbr_limite}""").read()  
			response = json.loads(result)
			# print(response)
			
		elif self.__category_switching() == Category.GENERAL:
			from_which_api = Api.TRIVIA_API
			api_url = self.__quiz_urls["genral"].format(nbr_limite = self.__nbr_limite , difficulty = self.__difficulty)
			response = requests.get(api_url)
			response = response.json()
			# print(response)
		
	
		# print(response)
		return self.__parse_questions(response , from_which_api)

    
	def __parse_tags(self , tags):
		str_tag = tags[0]
		for i in range(1 , len(tags)):
			str_tag = str_tag + "," + tags[i]
		return str_tag


	def __construct_last_proposition(self , nbr_propositions):
		if(nbr_propositions <= 2):
			return None

		print(nbr_propositions)
		nbr = random.choice(range(2 , nbr_propositions))
		characters_propositions = random.sample(range(97 , 96 + nbr_propositions),nbr)

		proposition = chr(characters_propositions[0])
		for i in range(1 , len(characters_propositions)):
			proposition = proposition + ' , ' + chr(characters_propositions[i])
		
		proposition = proposition + ' are true'
		return proposition


	def __get_correct_answer(self , correct_answers):
		keys = correct_answers.keys()
		propositions = ""
		#print(keys)
		for key in keys:
			if correct_answers[key].lower() == 'true'.lower():
				propositions = propositions + "," + key[7]

		return propositions[1:]


	def __parse_quiz_api_questions(self , json_question):
		questions = []
		for item in json_question:
			#print("********************item**************************")
			try:
				question_content = item['question']
			except TypeError:
				print(json_question)

			propositions = {"question" : question_content}
			#print("question_content " + question_content)
			proposed_answers = item['answers']
			#on obtien la liste des clés des propostion
			proposed_key_answers = list(proposed_answers.keys())

			nbr_propositions = 0
			#print("proposed_key_answers")
			#print(proposed_key_answers)
			for proposed_key_answer in proposed_key_answers:
				#on construit le dictionnaire des propositions le dernier caractere de "answer_x" est
				#la cle du dictionnaire proposition et sa valeur est la valeur de answer de "answer_x" dans le fichier json
				if proposed_answers[proposed_key_answer] != None:
					propositions[proposed_key_answer[7]] = proposed_answers[proposed_key_answer]
					nbr_propositions = nbr_propositions + 1
				


			multiple_correct_answers = item['multiple_correct_answers']
			correct_answers = item['correct_answers']
			#print("multi correct answers " + multiple_correct_answers)
			key = None
			if multiple_correct_answers.lower() == 'false'.lower():
			#key = str(chr(97 + nbr_propositions))
				last_p = self.__construct_last_proposition(nbr_propositions)
				if last_p != None:
					propositions[chr(97 + nbr_propositions)] = last_p

				propositions['correct_answer'] = self.__get_correct_answer(correct_answers)
			else:
				propositions[chr(97 + nbr_propositions)] = self.__get_correct_answer(correct_answers) + " are true"
				propositions['correct_answer'] = chr(97 + nbr_propositions)

			questions.append(propositions)
		return questions


	def __parse_trivia_questions(self , json_question : json):
		results = json_question["results"]
		questions = []
		for item in results:
			question_content = unquote(item['question'])
			propositions = {"question" : question_content}
			proposed_answers = item['incorrect_answers']

			nbr_propositions = 0
			enter = False
			correct_answer_key = None
			for proposed_answer in proposed_answers:
				if random.random() > 0.5 and enter == False:
					propositions[chr(97 + nbr_propositions)] = unquote(item["correct_answer"])
					correct_answer_key = chr(97 + nbr_propositions)
					enter = True
					nbr_propositions = nbr_propositions + 1
				
				propositions[chr(97 + nbr_propositions)] = unquote(proposed_answer)
				nbr_propositions = nbr_propositions + 1


			if not enter:
				propositions[chr(97 + nbr_propositions)] = unquote(item["correct_answer"])
				correct_answer_key = chr(97 + nbr_propositions)
				nbr_propositions = nbr_propositions + 1
			
			if self.__construct_last_proposition(nbr_propositions) != None:
				propositions[chr(97 + nbr_propositions)] = self.__construct_last_proposition(nbr_propositions)

			propositions['correct_answer'] = correct_answer_key
			questions.append(propositions)

		return questions


	def __parse_questions(self , json_question : json , from_which_api : Api):
		if from_which_api == Api.QUIZ_API:
			return self.__parse_quiz_api_questions(json_question)
		elif from_which_api == Api.TRIVIA_API:
			return self.__parse_trivia_questions(json_question)


	#on recupere les resultats des votes pour les questions 
	#et pour la difficulte
	async def __get_vote_result(self , conn:MySQLConnection):
		if self.__democracy:
			questions_vote = Vote.get_vote(conn , VoteName.CHOICE_QUESTIONS_TYPE)
			if questions_vote != None:
				difficulty_vote = Vote.get_vote(conn , VoteName.CHOICE_DIFFICUTY_TYPE) 
				if difficulty_vote != None:
					id_questions_vote = questions_vote.get_vote_id()
					id_difficulty_vote = difficulty_vote.get_vote_id()
					print(questions_vote.get_vote_id())
					print(difficulty_vote.get_vote_id())

					try:
						if QuizBot.app.is_connected == True:
							await QuizBot.app.stop_poll(self.groupe_id, 293)
							await QuizBot.app.stop_poll(self.groupe_id, 291)
						else:
							async with QuizBot.app:
								await QuizBot.app.stop_poll(self.groupe_id, 293)
								await QuizBot.app.stop_poll(self.groupe_id, 291)
					except IndexError:
						print("delete vote which was deleted before")
						pass
					
					question_winner = await questions_vote.get_result(QuizBot.app , self.groupe_id)
					difficulty_winner = await difficulty_vote.get_result(QuizBot.app , self.groupe_id)
					print(f"{question_winner} {difficulty_winner}")
					return  question_winner , difficulty_winner

		return None , None

	#cette fonction retourne la frequence de repetition d'une action 
	#en seconde
	def __get_period(self , period:int , now : datetime , hour:datetime = None):
		nbr_second : int = 0
		if period < 24:
			nbr_second = int(period) * 3600
		else:
			to_add  = (hour - now).seconds if hour > now else -(now - hour).seconds
			nbr_second = period * 3600 + to_add

		return nbr_second
	

	
	async def __send_vote(self , conn:MySQLConnection):	
		q_c = "In which domain you want the next serie of quizz be?"
		q_d = "Select the difficulty"
		now = get_time(self.__time_zone)
		hour = self.__hour
		nbr_second = self.__get_period(self.__period , now = now , hour = hour)
		time_change = timedelta(seconds=nbr_second)

		print(nbr_second)
		print(f"now {now}")
		print(f"end {now + time_change}")

		sticker_to_load = self.__get_sticker("category")
		await self.__send_sticker(sticker_to_load)
		vote_id_question = await Vote.send(QuizBot.app , self.groupe_id , q_c , CATEGORY_TAB)
		description = "il s'agit d'un vote pour les question"
		vote_q = Vote(vote_id_question , VoteName.CHOICE_QUESTIONS_TYPE , description , get_time(self.__time_zone) , self.__id)
		vote_q.save(conn)

		sticker_to_load = self.__get_sticker("difficulty")
		await self.__send_sticker(sticker_to_load)
		vote_id_difficulty = await Vote.send(QuizBot.app , self.groupe_id , q_d , DIFFICULTY_TAB)
		description = "il s'agit d'un vote pour le choix des difficultes"
		vote_d = Vote(vote_id_difficulty , VoteName.CHOICE_DIFFICUTY_TYPE , description , get_time(self.__time_zone) , self.__id)
		vote_d.save(conn)
		conn.commit()


	def __get_sticker(self , sticker_name:str):
		sticker_to_loads = STICKERS[sticker_name]
		nbr_stickers = len(sticker_to_loads)
		
		sticker_index = 0
		#on hoisi une image aleatoire que l'on va envoyé
		if nbr_stickers > 1:
			sticker_index = random.randint(0 , nbr_stickers - 1)

		return sticker_to_loads[sticker_index]
	


	async def __send_sticker(self , sticker_id:str):
		if QuizBot.app.is_connected == True:
			await QuizBot.app.send_sticker(self.groupe_id , sticker_id)
		else:
			async with QuizBot.app:
				await QuizBot.app.send_sticker(self.groupe_id , sticker_id)
		

	async def send_quiz(self ,  manual_call = True):
		conn = connect_db()
		if self.__automatic == 1:
			if not self.__democracy or self.__period == None:
				self.__category = random.choice(CATEGORY_TAB)
				self.__difficulty = random.choice(DIFFICULTY_TAB)
			else:
				cat , dif = await self.__get_vote_result(conn)
				if cat != None and dif != None:
					self.__category = cat
					self.__difficulty = dif
					print(f"cat {cat} diff {dif}")

		print(f"*******category -> {self.__category}")
		# print(self.__category)
		questions = self.quiz_request()
		if self.__category == Category.RANDOM:
			self.__message = "this series of quizz is a random serie"
		else:
			self.__message = self.__message.format(category = self.__category , difficulty = self.__difficulty)

		sticker_to_load = self.__get_sticker(self.__category)

		
		await self.__send_sticker(sticker_to_load)

		for question in questions:
			keys = question.keys()
			cmpt = 0
			index_correct = 0
			propositions = []
			#si la longueur la question est supperieur a 291 telegram ne peut pas 
			#prendre cette question en charge dans ce cas on annnule la question
			if len(question["question"]) > 291:
				continue
			
			interupt = False
			for key in keys:
				if key not in ["question" , "correct_answer"]:
					if key == question["correct_answer"]:
						index_correct = cmpt
						#si la longueur de l'option est supperieur a 100 telegram ne peut pas 
						#prendre cette question en charge dans ce cas on annule complement la 
						#question
					if len(question[key]) > 100:
						interupt = True
						break

					propositions.append(question[key])
					cmpt += 1

			if interupt == True:
				continue
			
			# print(question["question"])
			# print(propositions)

			# print(index_correct)
			if QuizBot.app.is_connected == True:
				await QuizBot.app.send_poll(self.groupe_id , question["question"] , propositions , type = enums.PollType.QUIZ , correct_option_id = index_correct)
			else: 
				async with QuizBot.app:
					await QuizBot.app.send_poll(self.groupe_id , question["question"] , propositions , type = enums.PollType.QUIZ , correct_option_id = index_correct)

		if manual_call == False:
			await self.__send_vote(conn)
		
		
		conn.close()



	async def schedule_quiz(self):
		nbr_second = 0
		if self.__automatic == 1 and self.__period != None:
			# if self.__period < 24 == 0:
			# 	nbr_second = int(self.__period) * 3600
			# else:
			new_hour = None
			now = None
			allow : bool = True
			if self.__period >= 24 and self.__hour == None:
				allow = False

			print(self.__hour)
			if self.__hour != None:
				now = get_time(self.__time_zone)
				if isinstance(self.__hour, datetime):
					new_hour = datetime(now.date().year , now.date().month , now.date().day ,
										self.__hour.time().hour , self.__hour.time().minute , self.__hour.time().second)
				elif isinstance(self.__hour, timedelta):
					temp = datetime.strptime(str(self.__hour), "%H:%M:%S")
					new_hour = datetime(now.date().year , now.date().month , now.date().day ,
										temp.time().hour , temp.time().minute , temp.time().second)

				
			print(new_hour)
			# if self.__hour != None:
			# 	hour = datetime.strptime(str(self.__hour), "%Y-%m-%d %H:%M:%S")
			
			# if self.__period >= 24 and self.__hour != None:
			# 	hour = datetime.strptime(str(self.__hour), "%Y-%m-%d %H:%M:%S")
			# elif self.__period >= 24 and self.__hour == None:
			# 	# if QuizBot.app.is_connected == True:
			# 	# 	await QuizBot.app.send_message(self.groupe_id , "you have to set a time zone")
			# 	# else:
			# 	# 	async with QuizBot.app:
			# 	# 		await QuizBot.app.send_message(self.groupe_id , "you have to set a time zone")
			# 	pass
			# elif (self.__period >= 24 and self.__hour != None) or  self.__period < 24:

			# 	pass
			if allow:
				now  = get_time(self.__time_zone)
				nbr_second = self.__get_period(self.__period , now = now, hour = new_hour)
				nbr_second = 60
				self.__job = QuizBot.scheduler.add_job(QuizBot.send_quiz , "interval" ,args = [self , False], seconds=nbr_second)

		
			# 	print(hour)
			# 	now  = get_time(self.__time_zone)
			# 	to_add  = (hour - now).seconds if hour > now else -(now - hour).seconds

			# 	nbr_second = self.__period * 3600 + to_add
				# s_hour = time_in_second(hour)
				# s_now = time_in_second(now)
				# if s_hour < s_now:
				# 	nbr_second = self.__period * 3600 - to_add
				# 	to_add = s_now - s_hour
				# else:
				# 	to_add = s_hour - s_now
				# 	nbr_second = self.__period * 3600 + to_add

				# print(f"now {now}")
				# print(f"to_add {to_add}")
				# print(f"nbr_second {nbr_second}")
			print(f"enter scheduler {nbr_second}")
			
		def __str__(self):
			return self.groupe_id
  





