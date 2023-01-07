# Schedule Library imported
# import imp
# import schedule 
# import time

# from utils.utils import Difficulty

# # Functions setup
# def sudo_placement():
# 	print("Get ready for Sudo Placement at Geeksforgeeks")

# def good_luck():
# 	print("Good Luck for Test")

# def work():
# 	print("Study and work hard")

# def bedtime():
# 	print("It is bed time go rest")
	
# def geeks():
# 	print("Shaurya says Geeksforgeeks")

# def test_day():
# 	print("enter")

# # Task scheduling
# # After every 10mins geeks() is called.
# schedule.every().minute.do(geeks).tag("minute")

# # After every hour geeks() is called.
# schedule.every().hour.do(geeks)

# # Every day at 12am or 00:00 time bedtime() is called.
# schedule.every().day.at("00:00").do(bedtime)


# # After every 5 to 10mins in between run work()
# schedule.every(5).to(10).minutes.do(work)

# # Every monday good_luck() is called
# schedule.every().monday.do(good_luck)


# # Every tuesday at 18:00 sudo_placement() is called
# schedule.every().tuesday.at("18:00").do(sudo_placement)

# schedule.every(2).days.at("10:30").do(test_day)

# # Loop so that the scheduling task
# # keeps on running all time.
# while True:
# 	# Checks whether a scheduled task
# 	# is pending to run or not
# 	schedule.run_pending()
# 	time.sleep(1)

# import os
# import json

# QUIZ_API_TOKEN = "GMtZogjvXFZHn36AIygLrNrHRrzhWmZKzySbAVYL"
# difficulty = "easy"
# quiz_API_url = "https://quizapi.io/api/v1/questions"
# nbr_limite = 1
# category = "Kubernetes"
# category_tab = ["linux" , "bash" , "devops" , "code" , "cms" , "sql" , "docker" , "general" , "random"]



# for cat in category_tab:
# 	result = os.popen(f"""curl {quiz_API_url} -G -d apiKey={QUIZ_API_TOKEN}\
# 											     -d category={cat}\
# 										         -d difficulty={difficulty}\
# 												 -d limit={nbr_limite}""").read()

# 	response = json.loads(result)
# 	print(response.keys())

	#print(response)

# from QuizBot import QuizBot
# import random

# def construct_last_proposition(nbr_propositions):
# 	if(nbr_propositions <= 2):
# 		return None

# 	print(nbr_propositions)
# 	nbr = random.choice(range(2 , nbr_propositions))
# 	characters_propositions = random.sample(range(97 , 96 + nbr_propositions),nbr)

# 	proposition = chr(characters_propositions[0])
# 	for i in range(1 , len(characters_propositions)):
# 		proposition = proposition + ' , ' + chr(characters_propositions[i])
	
# 	proposition = proposition + ' are true'
# 	return proposition

# def get_correct_answer(correct_answers):
# 	keys = correct_answers.keys()
# 	propositions = ""
# 	#print(keys)
# 	for key in keys:
# 		if correct_answers[key].lower() == 'true'.lower():
# 			propositions = propositions + "," + key[7]

# 	return propositions[1:]


# def parse_questions(json_question):
# 	questions = []
# 	for item in json_question:
# 		#print("********************item**************************")
# 		question_content = item['question']
# 		propositions = {"question" : question_content}
# 		#print("question_content " + question_content)
# 		proposed_answers = item['answers']
# 		#on obtien la liste des clés des propostion
# 		proposed_key_answers = list(proposed_answers.keys())

# 		nbr_propositions = 0
# 		#print("proposed_key_answers")
# 		#print(proposed_key_answers)
# 		for proposed_key_answer in proposed_key_answers:
# 			#on construit le dictionnaire des propositions le dernier caractere de "answer_x" est
# 			#la cle du dictionnaire proposition et sa valeur est la valeur de answer de "answer_x" dans le fichier json
# 			if proposed_answers[proposed_key_answer] != "None":
# 				propositions[proposed_key_answer[7]] = proposed_answers[proposed_key_answer]
# 				print(proposed_answers[proposed_key_answer])
# 				nbr_propositions = nbr_propositions + 1
			
# 		multiple_correct_answers = item['multiple_correct_answers']
# 		correct_answers = item['correct_answers']
# 		#print("multi correct answers " + multiple_correct_answers)
# 		key = None
# 		if multiple_correct_answers.lower() == 'false'.lower():
# 		#key = str(chr(97 + nbr_propositions))
# 			last_p = construct_last_proposition(nbr_propositions)
# 			if last_p != None:
# 				propositions[chr(97 + nbr_propositions)] = last_p

# 			propositions['correct_answer'] = get_correct_answer(correct_answers)
# 		else:
# 			propositions[chr(97 + nbr_propositions)] = get_correct_answer(correct_answers) + " are true"
# 			propositions['correct_answer'] = chr(97 + nbr_propositions)

# 		questions.append(propositions)

# 	return questions


# def send_quiz():
# 	f = open('error.json')
# 	questions = json.load(f)
# 	questions = parse_questions(questions)

# 	print(type(questions))
# 	for question in questions:
# 		print(question)


# 	print("\n")
# 	print("\n")

# 	for question in questions:
# 		keys = question.keys()
# 		cmpt = 0
# 		index_correct = 0
# 		propositions = []
# 		#si la longueur la question est supperieur a 255 telegram ne peut pas 
# 		#prendre cette question en charge dans ce cas on annnule la question
# 		if len(question["question"]) > 255:
# 			continue
		
# 		interupt = False
# 		for key in keys:
# 			if key not in ["question" , "correct_answer"]:
# 				if key == question["correct_answer"]:
# 					index_correct = cmpt
# 					#si la longueur de l'option est supperieur a 100 telegram ne peut pas 
# 					#prendre cette question en charge dans ce cas on annule complement la 
# 					#question
# 				if len(question[key]) > 100:
# 					interupt = True
# 					break

# 				propositions.append(question[key])
# 				cmpt += 1

# 		if interupt == True:
# 			continue
		
# 		print(question["question"])
# 		print(propositions)

# 		print(index_correct)

		

# f = open('error.json')
  
# data = json.load(f)

# # print(data)
# # send_quiz()

# dic = {"k1": "toto" , "k2" : "tata" , "k3" : "titi"}

# tab = list(dic.keys())

#######################################################################################################
# from pyrogram import Client , filters , enums
# import asyncio

# api_id = 15150655
# api_hash = "68e947ab567a62b78c70b8243307623c"
# bot_token = "5401510818:AAF9L3gnfKEUzzk06JDe1U0Sm1bNBhkLpUg"
# chat_id ="Ox00000d3"


# async def main():
#     async with Client("my_account", api_id=api_id, 
# 									api_hash=api_hash,
# 									bot_token=bot_token) as app:
#         await app.send_sticker(chat_id , "CAACAgEAAxkBAAEZRu9jVUhO7ft0eDtO0yxrQY-N6fRR5gACHwMAAgi8MUdq6gAB8IylGzcqBA")


# asyncio.run(main())




# async def main():
#     async with Client("my_bot", api_id, api_hash) as app:
#        await app.send_message("Ox00000d3", "Greetings from **Pyrogram**!")


# asyncio.run(main())

###################################################################################################
# import requests , os
# import urllib.parse
# api_url = "https://opentdb.com/api.php?amount={nbr_limite}&category=18&difficulty={difficulty}&encode=url3986"


# response = requests.get(api_url.format(nbr_limite = 2 , difficulty = "easy"))
# result = response.json()
# # urllib.parse.unquote(result)
# print(result)

# link = "https://quizapi.io/api/v1/questions"
# token = "GMtZogjvXFZHn36AIygLrNrHRrzhWmZKzySbAVYL"
# nbr_limite = 5

# result = os.popen(f"""curl {link} -G -d apiKey={token}​ \
# 	                                 -d limit={nbr_limite}""").read()  

# from urllib.parse import unquote
# url = 'The%20programming%20language%20%22Python%22%20is%20based%20off%20a%20modified%20version%20of%20%22JavaScript%22'
# url = unquote(url)
# print(url)

################################################################################################
# import asyncio

# dsn = "..."

# class Foo(object):
# 	nom = "dimitri"
		
# 	@classmethod
# 	async def create(cls, settings):
# 		self = Foo()
# 		self.settings = settings
# 		self.pool = await Foo.__create_pool(dsn)
# 		return self

# 	async def __create_pool(x):
# 		print(x)
	

# async def main(settings):
# 	foo = await Foo.create(settings)
# 	print(foo.nom)
# 	print(foo.settings)


# asyncio.run(main('fc'))
from datetime import datetime
now  = datetime.now()
print(type(now))