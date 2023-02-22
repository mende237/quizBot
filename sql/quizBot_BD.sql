/*==============================================================*/
/* Nom de SGBD :  MySQL 5.0                                     */
/* Date de cr�ation :  2/18/2023 7:53:17 AM                     */
/*==============================================================*/


drop table if exists ANSWER;

drop table if exists BOT;

drop table if exists GROUPE;

drop table if exists QUESTION;

drop table if exists VOTE;

/*==============================================================*/
/* Table : ANSWER                                               */
/*==============================================================*/
create table ANSWER
(
   ANSWER_ID            INT  not null AUTO_INCREMENT,
   QUESTION_ID          INT  not null,
   ANSWER               VARCHAR(255),
   CORRECT              Bool,
   primary key (ANSWER_ID)
);

/*==============================================================*/
/* Table : BOT                                                  */
/*==============================================================*/
create table BOT
(
   ID                   INT not null AUTO_INCREMENT,
   USERNAME             VARCHAR(255),
   CATEGORY             VARCHAR(255),
   DIFFICULTY           VARCHAR(255),
   NBR_LIMITE           INT,
   AUTOMATIC            Bool,
   HOUR                 Time,
   EVALUATION_HOUR      Time,
   PERIOD               INT,
   EVALUATION_PERIOD    INT,
   RESPONSE_TIME        INT,
   primary key (ID)
);

/*==============================================================*/
/* Table : GROUPE                                               */
/*==============================================================*/
create table GROUPE
(
   USERNAME             VARCHAR(255) not null,
   ID                   INT not null,
   DESCRIPTION          VARCHAR(255),
   primary key (USERNAME)
);

/*==============================================================*/
/* Table : QUESTION                                             */
/*==============================================================*/
create table QUESTION
(
   QUESTION_ID          INT not null AUTO_INCREMENT,
   ID                   INT,
   INTITULE             VARCHAR(256),
   QUESTION_HOUR        Time,
   QUESTION_DATE        date,
   primary key (QUESTION_ID)
);

/*==============================================================*/
/* Table : VOTE                                                 */
/*==============================================================*/
create table VOTE
(
   VOTE_ID              INT  not null,
   ID                   INT,
   NAME                 VARCHAR(255),
   VOTE_DATE            date,
   VOTE_DESCRIPTION     VARCHAR(255),
   primary key (VOTE_ID)
);

alter table ANSWER add constraint FK_HAS foreign key (QUESTION_ID)
      references QUESTION (QUESTION_ID) on delete cascade;

alter table BOT add constraint FK_MANAGE2 foreign key (USERNAME)
      references GROUPE (USERNAME) on delete cascade;

alter table GROUPE add constraint FK_MANAGE foreign key (ID)
      references BOT (ID) on delete cascade;

alter table QUESTION add constraint FK_PUBLISH foreign key (ID)
      references BOT (ID) on delete cascade;

alter table VOTE add constraint FK_SEND foreign key (ID)
      references BOT (ID) on delete cascade;

