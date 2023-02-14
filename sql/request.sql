CREATE DATABASE bot_db;

DROP TABLE IF EXISTS Groupe;
CREATE TABLE Groupe(
        username     Varchar (255),
        description     Varchar (255),
        id_Bot     int ,
        PRIMARY KEY (username)
);



DROP TABLE IF EXISTS Bot;
CREATE TABLE Bot(
        id     int AUTO_INCREMENT ,
        category    Varchar (255),
        difficulty     Varchar (255),
        nbr_limite     Int,
        automatic      Bool,
        hour     Time ,
        period     Int ,
        username_Groupe     Varchar (255),
        PRIMARY KEY (id)
);




ALTER TABLE Groupe ADD CONSTRAINT FK_Groupe_id_Bot FOREIGN KEY (id_Bot) REFERENCES Bot(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE Bot ADD CONSTRAINT FK_Bot_username_Groupe FOREIGN KEY (username_Groupe) REFERENCES Groupe(username) ON DELETE CASCADE ON UPDATE CASCADE;


ALTER TABLE Bot ADD time_zone Varchar (255) DEFAULT 'Africa/Douala'; 
ALTER TABLE Bot ADD poll_id Varchar (255); 