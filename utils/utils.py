from enum import Enum

class Category(Enum):
	LINUX = 1
	DEVOPS = 2
	NETWORKING = 3
	PROGRAMMING = 4
	CLOUD = 5
	DOCKER = 6
	KUBERNETES = 7
	RANDOM = 8
 
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3