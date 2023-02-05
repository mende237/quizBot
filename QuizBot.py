#!/home/dimitri/Quiz_bot/myvenv/bin python
import os
import random
import requests
import json
import os
from utils.utils import Category , Difficulty , Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from datetime import datetime
from urllib.parse import unquote
from pyrogram import Client , enums
from datetime import datetime


class QuizBot:
	__automatic = 0
	__category = "general"
	__difficulty = "easy"
	__nbr_limite = 5
	__hour : datetime = None
	__period = None
	__job : Job = None
	__message = "this series of quizz is about {category} difficulty {difficulty}"

	#scheduler static variable
	scheduler : AsyncIOScheduler = None
	app : Client = None
	index = 0
	bash = ["CAACAgQAAxkBAAEZRzRjVVEnAYdigEUWUHc0M5WsgySOZQACSAsAAi7kmFKpMpEkFUXnUCoE",
			"CAACAgQAAxkBAAEZR0BjVVM4SSpUPRb314GRk4hRI7U7bAACcg4AAirXoVIWHf4FJ_SA8SoE",
			"CAACAgQAAxkBAAEZR0JjVVNM8PorBv2LIjBW2KHufcgeowACiQsAAh0LoFJ6drJASNHiRSoE"]

	cms = ["CAACAgQAAxkBAAEZR0RjVVNvoG8Y4tpzuFlwTFCk-2zHIAAC4QwAAupHoFKbhFiwc26_ASoE",
		   "CAACAgQAAxkBAAEZR0ZjVVOOd4_ysNAhDkURZVhLVo9wJQACIgwAAkMHoFIwP8IjwWywBioE",
		   "CAACAgQAAxkBAAEZR0pjVVOpfLH_rGcjCoqB_v9sUfIvhAACHQ0AAk__mFJODZOy7sMSCioE"]

	devops = ["CAACAgQAAxkBAAEZR0xjVVPEJSWq-R5d0XRepEz-lZSPsAAClw0AAleJmFL8HOmX5lCDISoE",
			  "CAACAgQAAxkBAAEZR1BjVVQVZqxoteIz26SWDtMV9T2S5QACQQwAAs7JmFKxFa6B_hTUKyoE"]

	sql = ["CAACAgQAAxkBAAEZR1RjVVQvIv-AZN6TEw2nw9u-9XK5UQACLAwAAsbkoVIlaqO0VFskBCoE",
	       "CAACAgQAAxkBAAEZR2tjVVVBYBKQDBU0DnzL9URoet1VPgACUQsAAiU1oVJLzfHPrwlVLCoE"]

	docker = ["CAACAgQAAxkBAAEZR2FjVVSpBRA0IFag8nEkG97xArVt7AACzg0AAqXNmFLnjQpwqWG-BCoE"]

	general = ["CAACAgQAAxkBAAEZR2NjVVTFY6gl0DykoqJwJnP1bygXsAACXgsAAgh7oFIBM3eNs7SNRyoE",
			   "CAACAgQAAxkBAAEZR2VjVVT32xzFQsiO3e0PTtgZ_1jclwACgwsAAgZWoVLixoKgf_yZHSoE"]

	code = ["CAACAgQAAxkBAAEZR2djVVUQtuTzDRmKxflI2PHQTLYlbgACBA0AAv1umFKywVn-M1px4ioE",
			"CAACAgQAAxkBAAEZR2ljVVUr6cKm95sB-H9uxqGeY0bVMgACbwwAAoeeoFJb1vQpOb0zCioE"]

	linux = ["CAACAgQAAxkBAAEZR21jVVVeLfNWE-ymvjtlmeNJhnO_ywACSgwAAsLJoVLjssjLsuYj2SoE"]

	random = ["CAACAgQAAxkBAAEZR9hjVWjM0dHlc-YobW-7ivwgU_Ic6QACIwsAAoHVsVJw7D5sBWCZfCoE",
	          "CAACAgQAAxkBAAEZR9pjVWjw1BZkzHeekZSQc5sFG7yPSgACbg0AAu9QqVLhLqTCW-Y70SoE",
			  "CAACAgQAAxkBAAEZR9xjVWkLXFB5Tsbc0nm0IdRhptCUZQACKgwAAiioqVINGGZkFK85wCoE"]
	
	stickers = {"bash" : bash , 
				"linux" : linux , 
				"code" : code , 
				"cms" : cms , 
				"docker" : docker,
				"devops" : devops,
				"sql" : sql,
				"general" : general,
				"random" : random}

	@classmethod
	async def new_Bot(cls , id , groupe_id , app , quiz_urls , telegram_bot_url , TELEGRAM_API_TOKEN , parameters):
		self = QuizBot()
		self.__id = id
		self.groupe_id = groupe_id
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

		if "automatic" in keys and parameters["automatic"] != None:
			self.__automatic = parameters["automatic"]
			modif = True
   
		if "category" in keys and parameters["category"] != None:
			self.__category = parameters["category"]

		if "difficulty" in keys and parameters["difficulty"] != None:
			self.__difficulty = parameters["difficulty"]
   
		if "nbr_limite" in keys and parameters["nbr_limite"] != None:
			self.__nbr_limite = parameters["nbr_limite"]
   
		if "hour" in keys and parameters["hour"] != None:
			if self.__hour != parameters["hour"]:
				print("$$$$$$$$$$$$$$$$$$$$$****************************$$$$$$$$$$$$$$$$$$$$$$$$")
				modif = True
			self.__hour = parameters["hour"]
		
		if "period" in keys and parameters["period"] != None:
			if self.__period != parameters["period"]:
				modif = True
			self.__period = parameters["period"]
			
		print(f"automatic {self.__automatic } category {self.__category} difficulty {self.__difficulty} nbr_limte {self.__nbr_limite } hour {self.__hour } preiod {self.__period}")
		if is_init == False:
			if modif == True:
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
			print(response)
			
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
			question_content = item['question']
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


	async def send_quiz(self):
		if self.__automatic == 1:
			category_tab = ["linux" , "bash" , "devops" , "code" , "cms" , "sql" , "docker" , "general" , "random"]
			difficulty_tab = ["easy" , "medium" , "hard"]
			self.__category = random.choice(category_tab)
			self.__difficulty = random.choice(difficulty_tab)
	
		# print(self.__category)
		questions = self.quiz_request()
		if self.__category == Category.RANDOM:
			self.__message = "this series of quizz is a random serie"
		else:
			self.__message = self.__message.format(category = self.__category , difficulty = self.__difficulty)

		sticker_to_loads = QuizBot.stickers[self.__category]
		nbr_stickers = len(sticker_to_loads)
		
		sticker_index = 0
		#on hoisi une image aleatoire que l'on va envoyé
		if nbr_stickers > 1:
			sticker_index = random.randint(0 , nbr_stickers - 1)

		sticker_to_load = sticker_to_loads[sticker_index]

		if QuizBot.app.is_connected == True:
			await QuizBot.app.send_sticker(self.groupe_id , sticker_to_load)
		else:
			async with QuizBot.app:
				await QuizBot.app.send_sticker(self.groupe_id , sticker_to_load)
		
		# print("pass sticker")
		# for question in questions:
		# 	print(question)


		# print("\n")
		# print("\n")

		for question in questions:
			keys = question.keys()
			cmpt = 0
			index_correct = 0
			propositions = []
			#si la longueur la question est supperieur a 255 telegram ne peut pas 
			#prendre cette question en charge dans ce cas on annnule la question
			if len(question["question"]) > 255:
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

			# print("quiz sending ............")

	def __time_in_second(time : datetime) -> int:
		return time.hour *3600 + time.minute*60 + time.second

	async def schedule_quiz(self):
		nbr_second = 0
		if self.__automatic == 1 and self.__period != None:
			if self.__period < 24 == 0:
				nbr_second = int(self.__period) * 3600
			else:
				hour = datetime.strptime(str(self.__hour), "%H:%M:%S")
				print(hour)
				now  = datetime.now()
				to_add : int = 0
				s_hour = QuizBot.__time_in_second(hour)
				s_now = QuizBot.__time_in_second(now)
				if s_hour < s_now:
					to_add = s_now - s_hour
					nbr_second = self.__period * 3600 - to_add
				else:
					to_add = s_hour - s_now
					nbr_second = self.__period * 3600 + to_add

				print(f"now {now}")
				print(f"to_add {to_add}")
				print(f"nbr_second {nbr_second}")
				
			self.__job = QuizBot.scheduler.add_job(QuizBot.send_quiz , "interval" ,args = [self], seconds=nbr_second)
			
		def __str__(self):
			return self.groupe_id
  





