#!/home/dimitri/Quiz_bot/myvenv/bin python
import random
import json
import os
from unicodedata import category
from utils.utils import Category , Difficulty
import asyncio
from pyrogram import Client , filters , enums
import schedule
import time

class QuizBot:
	__automatic = None
	__category = None
	__difficulty = None
	__nbr_limite = None
	__hour = None
	__period = None
	__job = None
	__message = "this series of quizz is about {category} difficulty {difficulty}"
	app = None
	index = 0
    
	def __init__(self , id , groupe_id , app , quiz_API_url , telegram_bot_url , QUIZ_API_TOKEN , TELEGRAM_API_TOKEN , parameters):
		self.__id = id
		self.groupe_id = groupe_id
		QuizBot.app = app
		self.__quiz_API_url = quiz_API_url
		self.__telegram_bot_url = telegram_bot_url
		self.__QUIZ_API_TOKEN = QUIZ_API_TOKEN
		self.__TELEGRAM_API_TOKEN = TELEGRAM_API_TOKEN
		self.__set_parameters(parameters)
		QuizBot.index = QuizBot.index + 1

		  

	def __set_parameters(self , parameters , is_init : bool = True):
		keys = parameters.keys()
		modif = False

		if "automatic" in keys:
			self.__automatic = parameters["automatic"]
   
		if "category" in keys:
			self.__category = parameters["category"]
			print(self.__category)

		if "difficulty" in keys:
			self.__difficulty = parameters["difficulty"]
   
		if "nbr_limite" in keys:
			self.__nbr_limite = parameters["nbr_limite"]
   
		if "hour" in keys:
			if self.__hour != parameters["hour"]:
				modif = True
			self.__hour = parameters["hour"]
		
		if "period" in keys:
			if self.__period != parameters["period"]:
				modif = True
			self.__period = parameters["period"]
			
		if is_init == False:
			if modif == True:
				schedule.cancel_job(self.__job)
				self.schedule_quiz()

		print(f"automatic {self.__automatic } category {self.__category} difficulty {self.__difficulty} nbr_limte {self.__nbr_limite } hour {self.__hour } preiod {self.__period}")

		
	async def set_parameter_asynchronously(self , parameters):
		keys = parameters.keys()
		modif = False

		if "automatic" in keys:
			self.__automatic = parameters["automatic"]
   
		if "category" in keys:
			self.__category = parameters["category"]

		if "difficulty" in keys:
			self.__difficulty = parameters["difficulty"]
   
		if "nbr_limite" in keys:
			self.__nbr_limite = parameters["nbr_limite"]
   
		if "hour" in keys:
			if self.__hour != parameters["hour"]:
				modif = True
			self.__hour = parameters["hour"]
		
		if "period" in keys:
			if self.__period != parameters["period"]:
				modif = True
			self.__period = parameters["period"]
			
		if modif == True:
			schedule.cancel_job(self.__job)
			await self.schedule_quiz()

		print(f"automatic {self.__automatic } category {self.__category} difficulty {self.__difficulty} nbr_limte {self.__nbr_limite } hour {self.__hour } preiod {self.__period}")

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
		if self.__category == Category.LINUX:
			return "Linux"
		if self.__category == Category.BASH:
			return "Bash"
		elif self.__category == Category.DEVOPS:
			return "DevOps"
		elif self.__category == Category.CODE:
			return "code"
		elif self.__category == Category.CMS:
			return "cms"
		elif self.__category == Category.SQL:
			return "sql"
		elif self.__category == Category.DOCKER:
			return "Docker"
		elif self.__category == Category.RANDOM:
			return "random"


	def __difficulty_switching(self):
		if self.__difficulty == Difficulty.EASY:
			return "easy"
		elif self.__difficulty == Difficulty.MEDIUM:
			return "medium"
		else:
			return "hard"


	def quiz_request(self):
		result = None
		print("limit " , self.__nbr_limite)
		print("difficulty " , self.__difficulty)
		print("category " , self.__category)
		if self.__category != Category.RANDOM:
			result = os.popen(f"""curl {self.__quiz_API_url} -G -d apiKey={self.__QUIZ_API_TOKEN}​\
																-d category={self.__category}\
																-d difficulty={self.__difficulty}\
																-d limit={self.__nbr_limite}""").read()
		else:
			result = os.popen(f"""curl {self.__quiz_API_url} -G -d apiKey={self.__QUIZ_API_TOKEN}​\
																-d limit={self.__nbr_limite}""").read()  
		response = json.loads(result)
		print(len(response))
		# print(response)
		return self.__parse_questions(response)


    
	def __parse_tags(self , tags):
		str_tag = tags[0]
		for i in range(1 , len(tags)):
			str_tag = str_tag + "," + tags[i]
		return str_tag

	def __construct_last_proposition(self , nbr_propositions):
		if(nbr_propositions < 2):
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

	def __parse_questions(self , json_question):
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


	async def send_quiz(self):
		questions = self.quiz_request()
		if self.__category == Category.RANDOM:
			self.__message = "this series of quizz is a random serie"
		else:
			self.__message = self.__message.format(category = self.__category , difficulty = self.__difficulty)

		if QuizBot.app.is_connected == True:
			await QuizBot.app.send_message(self.groupe_id , self.__message)
		else:
			async with QuizBot.app:
				await QuizBot.app.send_message(self.groupe_id , self.__message)

		print(type(questions))
		for question in questions:
			print(question)


		print("\n")
		print("\n")

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
			
			print(question["question"])
			print(propositions)

			print(index_correct)

			
			if QuizBot.app.is_connected == True:
				await QuizBot.app.send_poll(self.groupe_id , question["question"] , propositions , type = enums.PollType.QUIZ , correct_option_id = index_correct)
			else:
				async with QuizBot.app:
					await QuizBot.app.send_poll(self.groupe_id , question["question"] , propositions , type = enums.PollType.QUIZ , correct_option_id = index_correct)

		
	async def schedule_quiz(self):
		print("enter {}" , self.__period)
		if self.__automatic == 1 and self.__period != None:
			if int(self.__period / 24) == 0:
				self.__job = schedule.every(self.__period).hours.do(self.send_quiz)
				print("every {} hour(s)" , self.__period)
			elif self.__period/24 == 1:
				self.__job = schedule.every().day().at(self.__hour).do(self.send_quiz)
				print("every day")
			elif self.__period / 24 == 2:
				self.__job = schedule.every(2).days().at(self.__hour).do(self.send_quiz)
				print("every two days")
			elif self.__period / 24 == 3:
				self.__job = schedule.every(3).days().at(self.__hour).do(self.send_quiz)
				print("every three days")
			elif self.__period / 24 == 4:
				self.__job = schedule.every(4).days().at(self.__hour).do(self.send_quiz)
				print("every four days")
			elif self.__period / 24 == 5:
				self.__job = schedule.every(5).days().at(self.__hour).do(self.send_quiz)
				print("every five days")
			elif self.__period / 24 == 6:
				self.__job = schedule.every(6).days().at(self.__hour).do(self.send_quiz)
				print("every six days")
			else:
				self.__job = schedule.every().week().do(self.send_quiz)
				print("every week") 
			


		def __str__(self):
			return self.groupe_id
  
# QUIZ_API_TOKEN = "GMtZogjvXFZHn36AIygLrNrHRrzhWmZKzySbAVYL"
# TELEGRAM_API_TOKEN = "5401510818:AAF9L3gnfKEUzzk06JDe1U0Sm1bNBhkLpUg"

# quiz_API_url = "https://quizapi.io/api/v1/questions"
# telegram_bot_url = "https://api.telegram.org/bot{}/{}"

# app = None
# parameter = {"difficulty" : "easy", "category" : Category.LINUX, "nbr_limite" : 2}

# quiz = QuizBot(1 , "toto" , app , quiz_API_url , telegram_bot_url
#                         ,QUIZ_API_TOKEN , TELEGRAM_API_TOKEN ,  parameter)

# """ questions = quiz.quiz_request()
# for question in questions:
# 	print(question)


# print("\n")
# print("\n")
# print("\n")
#  """
# quiz.schedule_quiz()




