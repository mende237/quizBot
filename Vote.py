import os
from utils.utils import VoteName
from datetime import datetime
from mysql.connector import MySQLConnection
from pyrogram import Client
from pyrogram.types.messages_and_media.poll_option import PollOption
from typing import List 

class Vote:
    __vote_id : int
    __name : VoteName = None
    __vote_date : datetime = None
    __vote_description:str = None
    __bot_id : int = None
    
    def __init__(self , vote_id : int , name : VoteName  , vote_description:str  , vote_date : datetime , bot_id : int):
        self.__vote_id = vote_id
        self.__name = name
        self.__vote_description = vote_description
        self.__vote_date = vote_date
        self.__bot_id = bot_id
    
    def save(self ,  conn: MySQLConnection) -> bool:
        my_cursor = conn.cursor()      
        my_cursor.execute(
            """INSERT INTO VOTE (VOTE_ID , ID , NAME , VOTE_DATE , VOTE_DESCRIPTION) 
            VALUES (%s, %s, %s , %s , %s);""",
            (self.__vote_id , self.__bot_id , self.__name.name ,
             self.__vote_date.strftime("%Y:%m:%d-%H:%M:%S"), self.__vote_description)
            )

        conn.commit()
        return True

    @staticmethod
    def get_vote(conn: MySQLConnection , vote_name:VoteName):
        my_cursor = conn.cursor()
        my_cursor.execute(""" SELECT * FROM VOTE WHERE  NAME = %s 
                              ORDER BY VOTE_DATE DESC LIMIT 1;
                            """ ,(vote_name.name,))

        results = my_cursor.fetchall()

        if(len(results) == 0):
            return None
        
        column_names = [i[0] for i in my_cursor.description]
        data = [dict(zip(column_names , row)) for row in results]

        
        return Vote(data[0]["VOTE_ID"] ,  data[0]["NAME"] ,data[0]["VOTE_DESCRIPTION"], data[0]["VOTE_DATE"]  ,  data[0]["ID"])
    

    def get_vote_id(self) -> int:
        return self.__vote_id


    @staticmethod
    async def send(app:Client , username_channel:str , question:str , 
                        options:list , close_date:datetime = None, open_period = None) -> int:
        
        poll = None
        if app.is_connected == True:
            poll = await app.send_poll(username_channel, question , options ,close_date=close_date)
        else:
            async with app:
                poll = await app.send_poll(username_channel, question , options , close_date=close_date)
                
        return poll.id


    async def get_result(self , app:Client , username_channel:str) -> str:
        result =  await app.get_messages(username_channel , self.__vote_id)
        if not result.empty:
            return Vote.__get_winner(result.poll.options)
    
        return None
    
    # @staticmethod
    # async def get_result(app:Client , username_channel:str , vote_id:int) -> str:
    #     result =  await app.get_messages(username_channel , vote_id)
    #     # print(type(result.poll.options[0]))
    #     if not result.empty:
    #         return Vote.__get_winner(result.poll.options)
    
    #     return None


    @staticmethod
    def __get_winner(options:List[PollOption]) -> str:
        max:int = 0
        winner:str = None

        for option in options:
            if option.voter_count > max:
                max = option.voter_count
                winner = option.text

        if winner == None:
            winner = options[0].text

        return winner


    def __str__(self) -> str:
        return """vote_id : {vote_id} bot_id {bot_id} name {name} vote_date {vote_date} vote_description {description}
                """.format(vote_id = self.__vote_id , bot_id = self.__bot_id , name = self.__name,
                           vote_date = self.__vote_date , description = self.__vote_description)