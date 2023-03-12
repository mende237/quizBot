from enum import Enum
import  mysql.connector 
from  mysql.connector import MySQLConnection

from decouple import config

class Category(Enum):
	LINUX = 1
	BASH = 2
	DEVOPS = 3
	CODE = 4
	SQL = 5
	DOCKER = 6
	CMS = 7
	RANDOM = 8
	GENERAL = 9

 
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Api(Enum):
	QUIZ_API = 1
	TRIVIA_API = 2


class VoteName(Enum):
	CHOICE_QUESTIONS_TYPE = 1
	CHOICE_DIFFICUTY_TYPE = 2


CATEGORY_TAB = ["linux" , "bash" , "devops" , "code" , "cms" , "sql" , "docker" , "general" , "random"]
DIFFICULTY_TAB = ["easy" , "medium" , "hard"]


def connect() -> MySQLConnection:
	# config.encoding = locale.getpreferredencoding(False)
	conn = mysql.connector.connect(
		host = config('HOST'),
		user = config('DB_USER'),
		passwd = config('DB_PASS'),
		database = config('DATA_BASE'),
		port = config('PORT', cast = int),
	)
	return conn