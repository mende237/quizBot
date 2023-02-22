#!/home/dimitri/Quiz_bot/myvenv/bin python
import os

from datetime import datetime
from mysql.connector import MySQLConnection

class Vote:
    __vote_id : int = None
    __name : str = None
    __vote_date : datetime = None
    __vote_description:str = None
    __bot_id : int = None
    
    def __init__(self , vote_id : int , name : str  , vote_description:str  , vote_date : datetime , bot_id : int):
        self.__vote_id = vote_id
        self.__name = name
        self.__vote_description = vote_description
        self.__vote_date = vote_date
        self.__bot_id = bot_id
    
    def save(self ,  conn: MySQLConnection) -> bool:
        my_cursor = conn.cursor()
        my_cursor.execute(
            """INSERT INTO VOTE (VOTE_ID , ID , NAME , VOTE_DATE , VOTE_DESCRIPTION) 
            VALUES ({VOTE_ID}, {ID}, {NAME} , {VOTE_DATE} , {VOTE_DESCRIPTION});"""
            .format(VOTE_ID = self.__vote_id , ID = self.__bot_id , 
            NAME = self.__name , VOTE_DATE = self.__vote_date.date() ,
            VOTE_DESCRIPTION = self.__vote_description))

        return True



    def get_vote(vote_name:str):

        pass
    

