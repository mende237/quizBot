from enum import Enum

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