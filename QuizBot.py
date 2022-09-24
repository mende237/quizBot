import random
import json
import os
from utils.utils import Category , Difficulty
import schedule
import time

class QuizBot:
	__automatic = None
	__category = None
	__difficulty = None
	__nbr_limite = None
	__hour = None
	__period = None
    
	def __init__(self , id , groupe_id ,  quiz_API_url , telegram_bot_url , QUIZ_API_TOKEN , TELEGRAM_API_TOKEN , parameters):
		self.__id = id
		self.groupe_id = groupe_id
		self.__quiz_API_url = quiz_API_url
		self.__telegram_bot_url = telegram_bot_url
		self.__QUIZ_API_TOKEN = QUIZ_API_TOKEN
		self.__TELEGRAM_API_TOKEN = TELEGRAM_API_TOKEN
		self.set_parameters(parameters)

		  

	def set_parameters(self , parameters):
		keys = parameters.keys()
  
		if "automatic" in keys:
			self.__automatic = parameters["automatic"]
   
		if "category" in keys:
			self.__category = parameters["category"]

		if "difficulty" in keys:
			self.__difficulty = parameters["difficulty"]
   
		if "nbr_limite" in keys:
			self.__nbr_limite = parameters["nbr_limite"]
   
		if "hour" in keys:
			self.__hour = parameters["hour"]
		
		if "period" in keys:
			self.__period = parameters["period"]

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
		elif self.__category == Category.DEVOPS:
			return "DevOps"
		elif self.__category == Category.NETWORKING:
			return "Networking"
		elif self.__category == Category.PROGRAMMING:
			return "Programming"
		elif self.__category == Category.CLOUD:
			return "Cloud"
		elif self.__category == Category.DOCKER:
			return "Docker"
		elif self.__category == Category.KUBERNETES:
			return "Kubernetes"
		elif self.__category == Category.RANDOM:
			return "random"


	def __difficulty_switching(self):
		if self.__difficulty == Difficulty.EASY:
			return "easy"
		elif self.__difficulty == Difficulty.MEDIUM:
			return "medium"
		else:
			return "hard"


	def quiz_request(self , category , difficulty , limit):
		self.__category = category
		self.__difficulty = difficulty
		result = None
		if category != Category.RAMDOM:
			#print("limit " + limit)
			#print("difficulty " + self.__difficulty_switching())
			#print("category " + self.__category_switching())
			result = os.popen(f"""curl {self.__quiz_API_url} -G -d apiKey={self.__QUIZ_API_TOKEN}​\
																-d category={self.__category_switching()}\
																-d difficulty={self.__difficulty_switching()}\
																-d limit={limit}""").read()
		else:
			result = os.popen(f"""curl {self.__quiz_API_url} -G -d apiKey={self.__QUIZ_API_TOKEN}​\
															-d limit={limit}""").read()  
		response = json.loads(result)
		print(len(response))
		print(response)
		return self.__parse_questions(response)


    
	def __parse_tags(self , tags):
		str_tag = tags[0]
		for i in range(1 , len(tags)):
			str_tag = str_tag + "," + tags[i]
		return str_tag

	def __construct_last_proposition(self , nbr_propositions):
		if(nbr_propositions < 2):
			return None

		nbr = random.choice(range(2 , nbr_propositions))
		characters_propositions = random.sample(range(97 , 96 + nbr_propositions),nbr)

		proposition = chr(characters_propositions[0])
		#print(characters_propositions)
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
				propositions[chr(97 + nbr_propositions)] = self.__construct_last_proposition(nbr_propositions)
				propositions['correct_answer'] = self.__get_correct_answer(correct_answers)
			else:
				propositions[chr(97 + nbr_propositions)] = self.__get_correct_answer(correct_answers) + " are true"
				propositions['correct_answer'] = chr(97 + nbr_propositions)

			questions.append(propositions)

		return questions

	def __send_quiz(self):
		pass
	
	def schedule_quiz(self):
		if self.__period / 24 == 0:
			schedule.every(self.__hour).hours.do(self.__send_quiz)
		elif self.__period/24 == 1:
			schedule.every().day().at(self.__hour).do(self.__send_quiz)
		elif self.__period / 24 == 2:
			schedule.every(2).days().at(self.__hour).do(self.__send_quiz)
			print("every two days")
		elif self.__period / 24 == 3:
			schedule.every(3).days().at(self.__hour).do(self.__send_quiz)
			print("every three days")
		elif self.__period / 24 == 4:
			schedule.every(4).days().at(self.__hour).do(self.__send_quiz)
			print("every four days")
		elif self.__period / 24 == 5:
			schedule.every(5).days().at(self.__hour).do(self.__send_quiz)
			print("every five days")
		elif self.__period / 24 == 6:
			schedule.every(6).days().at(self.__hour).do(self.__send_quiz)
			print("every six days")
		else:
			schedule.every().week().do(self.__hour)
			print("every week")

  
# QUIZ_API_TOKEN = "GMtZogjvXFZHn36AIygLrNrHRrzhWmZKzySbAVYL"
# TELEGRAM_API_TOKEN = "5401510818:AAF9L3gnfKEUzzk06JDe1U0Sm1bNBhkLpUg"


# quiz_API_url = "https://quizapi.io/api/v1/questions"
# telegram_bot_url = "https://api.telegram.org/bot{}/{}"


# quiz = QuizBot(quiz_API_url , telegram_bot_url , QUIZ_API_TOKEN , TELEGRAM_API_TOKEN)

# questions = quiz.quiz_request(Category.LINUX , Difficulty.MEDIUM , "5")


