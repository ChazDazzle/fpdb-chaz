#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Returns a dict of SQL statements used in fpdb.
"""
#    Copyright 2008-2011, Ray E. Barker
#   
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#   
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#   
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

#    NOTES:  The sql statements use the placeholder %s for bind variables
#            which is then replaced by ? for sqlite. Comments can be included 
#            within sql statements using C style /* ... */ comments, BUT
#            THE COMMENTS MUST NOT INCLUDE %s OR ?.

########################################################################

#    Standard Library modules
import re

#    pyGTK modules

#    FreePokerTools modules

class Sql:
   
    def __init__(self, game='holdem', db_server='mysql'):
        self.query = {}
###############################################################################3
#    Support for the Free Poker DataBase = fpdb   http://fpdb.sourceforge.net/
#

        ################################
        # List tables
        ################################
        if db_server == 'mysql':
            self.query['list_tables'] = """SHOW TABLES"""
        elif db_server == 'postgresql':
            self.query['list_tables'] = """SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"""
        elif db_server == 'sqlite':
            self.query['list_tables'] = """SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name;"""

        ################################
        # List indexes
        ################################
        if db_server == 'mysql':
            self.query['list_indexes'] = """SHOW INDEXES"""
        elif db_server == 'postgresql':
            self.query['list_indexes'] = """SELECT tablename, indexname FROM PG_INDEXES""" 
        elif db_server == 'sqlite':
            self.query['list_indexes'] = """SELECT name FROM sqlite_master
                                            WHERE type='index'
                                            ORDER BY name;"""

        ##################################################################
        # Drop Tables - MySQL, PostgreSQL and SQLite all share same syntax
        ##################################################################

        self.query['drop_table'] = """DROP TABLE IF EXISTS """   


        ##################################################################
        # Set transaction isolation level
        ##################################################################

        if db_server == 'mysql' or db_server == 'postgresql':
            self.query['set tx level'] = """SET SESSION TRANSACTION
            ISOLATION LEVEL READ COMMITTED"""
        elif db_server == 'sqlite':
            self.query['set tx level'] = """ """


        ################################
        # Select basic info
        ################################

        self.query['getSiteId'] = """SELECT id from Sites where name = %s"""

        self.query['getGames'] = """SELECT DISTINCT category from Gametypes"""
        
        self.query['getCurrencies'] = """SELECT DISTINCT currency from Gametypes ORDER BY currency"""
        
        self.query['getLimits'] = """SELECT DISTINCT bigBlind from Gametypes ORDER by bigBlind DESC"""

        self.query['getTourneyTypesIds'] = "SELECT id FROM TourneyTypes"

        ################################
        # Create Settings
        ################################
        if db_server == 'mysql':
            self.query['createSettingsTable'] = """CREATE TABLE Settings (
                                        version SMALLINT NOT NULL)
                                ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createSettingsTable'] = """CREATE TABLE Settings (version SMALLINT NOT NULL)"""

        elif db_server == 'sqlite':
            self.query['createSettingsTable'] = """CREATE TABLE Settings
            (version INTEGER NOT NULL) """
            
        ################################
        # Create InsertLock
        ################################
        if db_server == 'mysql':
            self.query['createLockTable'] = """CREATE TABLE InsertLock (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        locked BOOLEAN NOT NULL DEFAULT FALSE)
                        ENGINE=INNODB"""

        ################################
        # Create RawHands (this table is all but identical with RawTourneys)
        ################################
        if db_server == 'mysql':
            self.query['createRawHands'] = """CREATE TABLE RawHands (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL,
                        rawHand TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createRawHands'] = """CREATE TABLE RawHands (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL,
                        rawHand TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        elif db_server == 'sqlite':
            self.query['createRawHands'] = """CREATE TABLE RawHands (
                        id INTEGER PRIMARY KEY,
                        handId BIGINT NOT NULL,
                        rawHand TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        
        ################################
        # Create RawTourneys (this table is all but identical with RawHands)
        ################################
        if db_server == 'mysql':
            self.query['createRawTourneys'] = """CREATE TABLE RawTourneys (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneyId BIGINT NOT NULL,
                        rawTourney TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createRawTourneys'] = """CREATE TABLE RawTourneys (
                        id BIGSERIAL, PRIMARY KEY (id),
                        tourneyId BIGINT NOT NULL,
                        rawTourney TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        elif db_server == 'sqlite':
            self.query['createRawTourneys'] = """CREATE TABLE RawTourneys (
                        id INTEGER PRIMARY KEY,
                        tourneyId BIGINT NOT NULL,
                        rawTourney TEXT NOT NULL,
                        complain BOOLEAN NOT NULL DEFAULT FALSE)"""
                        
        ################################
        # Create Actions
        ################################

        if db_server == 'mysql':
            self.query['createActionsTable'] = """CREATE TABLE Actions (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        name varchar(32) NOT NULL,
                        code char(4) NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createActionsTable'] = """CREATE TABLE Actions (
                        id SERIAL, PRIMARY KEY (id),
                        name varchar(32),
                        code char(4))"""
        elif db_server == 'sqlite':
            self.query['createActionsTable'] = """CREATE TABLE Actions (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        code TEXT NOT NULL)"""  
                        
        ################################
        # Create Rank
        ################################

        if db_server == 'mysql':
            self.query['createRankTable'] = """CREATE TABLE Rank (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id), 
                        name varchar(8) NOT NULL)
                        ENGINE=INNODB"""
                        
        elif db_server == 'postgresql':
            self.query['createRankTable'] = """CREATE TABLE Rank (
                        id SERIAL, PRIMARY KEY (id),
                        name varchar(8))"""
        elif db_server == 'sqlite':
            self.query['createRankTable'] = """CREATE TABLE Rank (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL)"""  
                        
        ################################
        # Create StartCards
        ################################

        if db_server == 'mysql':
            self.query['createStartCardsTable'] = """CREATE TABLE StartCards (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        category varchar(9) NOT NULL,
                        name varchar(32) NOT NULL,
                        rank SMALLINT NOT NULL,
                        combinations SMALLINT NOT NULL)
                        ENGINE=INNODB"""
                        
        elif db_server == 'postgresql':
            self.query['createStartCardsTable'] = """CREATE TABLE StartCards (
                        id SERIAL, PRIMARY KEY (id),
                        category varchar(9) NOT NULL,
                        name varchar(32),
                        rank SMALLINT NOT NULL,
                        combinations SMALLINT NOT NULL)"""
                        
        elif db_server == 'sqlite':
            self.query['createStartCardsTable'] = """CREATE TABLE StartCards (
                        id INTEGER PRIMARY KEY,
                        category TEXT NOT NULL,
                        name TEXT NOT NULL,
                        rank SMALLINT NOT NULL,
                        combinations SMALLINT NOT NULL)"""  
                        
        ################################
        # Create Sites
        ################################

        if db_server == 'mysql':
            self.query['createSitesTable'] = """CREATE TABLE Sites (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        name varchar(32) NOT NULL,
                        code char(2) NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createSitesTable'] = """CREATE TABLE Sites (
                        id SERIAL, PRIMARY KEY (id),
                        name varchar(32),
                        code char(2))"""
        elif db_server == 'sqlite':
            self.query['createSitesTable'] = """CREATE TABLE Sites (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        code TEXT NOT NULL)"""

        ################################
        # Create Backings
        ################################
        
        if db_server == 'mysql':
            self.query['createBackingsTable'] = """CREATE TABLE Backings (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneysPlayersId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        buyInPercentage FLOAT UNSIGNED NOT NULL,
                        payOffPercentage FLOAT UNSIGNED NOT NULL) ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createBackingsTable'] = """CREATE TABLE Backings (
                        id BIGSERIAL, PRIMARY KEY (id),
                        tourneysPlayersId INT NOT NULL, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        buyInPercentage FLOAT NOT NULL,
                        payOffPercentage FLOAT NOT NULL)"""
        elif db_server == 'sqlite':
            self.query['createBackingsTable'] = """CREATE TABLE Backings (
                        id INTEGER PRIMARY KEY,
                        tourneysPlayersId INT NOT NULL,
                        playerId INT NOT NULL,
                        buyInPercentage REAL UNSIGNED NOT NULL,
                        payOffPercentage REAL UNSIGNED NOT NULL)"""
        
        ################################
        # Create Gametypes
        ################################

        if db_server == 'mysql':
            self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        siteId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4) NOT NULL,
                        type char(4) NOT NULL,
                        base char(4) NOT NULL,
                        category varchar(9) NOT NULL,
                        limitType char(2) NOT NULL,
                        hiLo char(1) NOT NULL,
                        mix varchar(9) NOT NULL,
                        smallBlind bigint,
                        bigBlind bigint,
                        smallBet bigint NOT NULL,
                        bigBet bigint NOT NULL,
                        maxSeats TINYINT NOT NULL,
                        ante INT NOT NULL,
                        buyinType varchar(9) NOT NULL,
                        fast BOOLEAN,
                        newToGame BOOLEAN,
                        homeGame BOOLEAN,
                        split BOOLEAN)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                        id SERIAL NOT NULL, PRIMARY KEY (id),
                        siteId INTEGER NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4) NOT NULL,
                        type char(4) NOT NULL,
                        base char(4) NOT NULL,
                        category varchar(9) NOT NULL,
                        limitType char(2) NOT NULL,
                        hiLo char(1) NOT NULL,
                        mix varchar(9) NOT NULL,
                        smallBlind bigint,
                        bigBlind bigint,
                        smallBet bigint NOT NULL,
                        bigBet bigint NOT NULL,
                        maxSeats SMALLINT NOT NULL,
                        ante INT NOT NULL,
                        buyinType varchar(9) NOT NULL,
                        fast BOOLEAN,
                        newToGame BOOLEAN,
                        homeGame BOOLEAN,
                        split BOOLEAN)"""
        elif db_server == 'sqlite':
            self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                        id INTEGER PRIMARY KEY NOT NULL,
                        siteId INTEGER NOT NULL,
                        currency TEXT NOT NULL,
                        type TEXT NOT NULL,
                        base TEXT NOT NULL,
                        category TEXT NOT NULL,
                        limitType TEXT NOT NULL,
                        hiLo TEXT NOT NULL,
                        mix TEXT NOT NULL,
                        smallBlind INTEGER,
                        bigBlind INTEGER,
                        smallBet INTEGER NOT NULL,
                        bigBet INTEGER NOT NULL,
                        maxSeats INT NOT NULL,
                        ante INT NOT NULL,
                        buyinType TEXT NOT NULL,
                        fast INT,
                        newToGame INT,
                        homeGame INT,
                        split INT,
                        FOREIGN KEY(siteId) REFERENCES Sites(id) ON DELETE CASCADE)"""


        ################################
        # Create Players
        ################################

        if db_server == 'mysql':
            self.query['createPlayersTable'] = """CREATE TABLE Players (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        name VARCHAR(32) NOT NULL,
                        siteId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        hero BOOLEAN, 
                        chars char(3),
                        comment text,
                        commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createPlayersTable'] = """CREATE TABLE Players (
                        id SERIAL, PRIMARY KEY (id),
                        name VARCHAR(32),
                        siteId INTEGER, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        hero BOOLEAN,
                        chars char(3),
                        comment text,
                        commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createPlayersTable'] = """CREATE TABLE Players (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        siteId INTEGER,
                        hero BOOLEAN,
                        chars TEXT,
                        comment TEXT,
                        commentTs timestamp,
                        FOREIGN KEY(siteId) REFERENCES Sites(id) ON DELETE CASCADE)"""


        ################################
        # Create Autorates
        ################################

        if db_server == 'mysql':
            self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                            id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                            playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                            gametypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            description varchar(50) NOT NULL,
                            shortDesc char(8) NOT NULL,
                            ratingTime DATETIME NOT NULL,
                            handCount int NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                            id BIGSERIAL, PRIMARY KEY (id),
                            playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                            gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            description varchar(50),
                            shortDesc char(8),
                            ratingTime timestamp without time zone,
                            handCount int)"""
        elif db_server == 'sqlite':
            self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                            id INTEGER PRIMARY KEY,
                            playerId INT,
                            gametypeId INT,
                            description TEXT,
                            shortDesc TEXT,
                            ratingTime timestamp,
                            handCount int)"""


        ################################
        # Create Hands
        ################################

        if db_server == 'mysql':
            self.query['createHandsTable'] = """CREATE TABLE Hands (
                            id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                            tableName VARCHAR(50) NOT NULL,
                            siteHandNo BIGINT NOT NULL,
                            tourneyId INT UNSIGNED, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                            gametypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            sessionId INT UNSIGNED, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                            fileId INT(10) UNSIGNED NOT NULL, FOREIGN KEY (fileId) REFERENCES Files(id), 
                            startTime DATETIME NOT NULL,
                            importTime DATETIME NOT NULL,
                            seats TINYINT NOT NULL,
                            heroSeat TINYINT NOT NULL,
                            maxPosition TINYINT NOT NULL,
                            boardcard1 smallint,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 smallint,
                            boardcard3 smallint,
                            boardcard4 smallint,
                            boardcard5 smallint,
                            texture smallint,
                            runItTwice BOOLEAN,
                            playersVpi SMALLINT NOT NULL,         /* num of players vpi */
                            playersAtStreet1 SMALLINT NOT NULL,   /* num of players seeing flop/street4 */
                            playersAtStreet2 SMALLINT NOT NULL,
                            playersAtStreet3 SMALLINT NOT NULL,
                            playersAtStreet4 SMALLINT NOT NULL,
                            playersAtShowdown SMALLINT NOT NULL,
                            street0Raises TINYINT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                            street1Raises TINYINT NOT NULL, /* num small bets paid to see turn/street5 */
                            street2Raises TINYINT NOT NULL, /* num big bets paid to see river/street6 */
                            street3Raises TINYINT NOT NULL, /* num big bets paid to see sd/street7 */
                            street4Raises TINYINT NOT NULL, /* num big bets paid to see showdown */
                            street0Pot BIGINT,                  /* pot size at pre-flop/street2 */
                            street1Pot BIGINT,                  /* pot size at flop/street4 */
                            street2Pot BIGINT,                  /* pot size at turn/street5 */
                            street3Pot BIGINT,                  /* pot size at river/street6 */
                            street4Pot BIGINT,                  /* pot size at sd/street7 */
                            finalPot   BIGINT,                  /* final pot size */
                            comment TEXT,
                            commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsTable'] = """CREATE TABLE Hands (
                            id BIGSERIAL, PRIMARY KEY (id),
                            tableName VARCHAR(50) NOT NULL,
                            siteHandNo BIGINT NOT NULL,
                            tourneyId INT, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                            gametypeId INT NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                            sessionId INT, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                            fileId BIGINT NOT NULL, FOREIGN KEY (fileId) REFERENCES Files(id),
                            startTime timestamp without time zone NOT NULL,
                            importTime timestamp without time zone NOT NULL,
                            seats SMALLINT NOT NULL,
                            heroSeat SMALLINT NOT NULL,
                            maxPosition SMALLINT NOT NULL,
                            boardcard1 smallint,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 smallint,
                            boardcard3 smallint,
                            boardcard4 smallint,
                            boardcard5 smallint,
                            texture smallint,
                            runItTwice BOOLEAN,
                            playersVpi SMALLINT NOT NULL,         /* num of players vpi */
                            playersAtStreet1 SMALLINT NOT NULL,   /* num of players seeing flop/street4 */
                            playersAtStreet2 SMALLINT NOT NULL,
                            playersAtStreet3 SMALLINT NOT NULL,
                            playersAtStreet4 SMALLINT NOT NULL,
                            playersAtShowdown SMALLINT NOT NULL,
                            street0Raises SMALLINT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                            street1Raises SMALLINT NOT NULL, /* num small bets paid to see turn/street5 */
                            street2Raises SMALLINT NOT NULL, /* num big bets paid to see river/street6 */
                            street3Raises SMALLINT NOT NULL, /* num big bets paid to see sd/street7 */
                            street4Raises SMALLINT NOT NULL, /* num big bets paid to see showdown */
                            street0Pot BIGINT,                 /* pot size at preflop/street3 */
                            street1Pot BIGINT,                 /* pot size at flop/street4 */
                            street2Pot BIGINT,                 /* pot size at turn/street5 */
                            street3Pot BIGINT,                 /* pot size at river/street6 */
                            street4Pot BIGINT,                 /* pot size at sd/street7 */
                            finalPot   BIGINT,                 /* final pot size */
                            comment TEXT,
                            commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createHandsTable'] = """CREATE TABLE Hands (
                            id INTEGER PRIMARY KEY,
                            tableName TEXT(50) NOT NULL,
                            siteHandNo INT NOT NULL,
                            tourneyId INT,
                            gametypeId INT NOT NULL,
                            sessionId INT,
                            fileId INT NOT NULL,
                            startTime timestamp NOT NULL,
                            importTime timestamp NOT NULL,
                            seats INT NOT NULL,
                            heroSeat INT NOT NULL,
                            maxPosition INT NOT NULL,
                            boardcard1 INT,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 INT,
                            boardcard3 INT,
                            boardcard4 INT,
                            boardcard5 INT,
                            texture INT,
                            runItTwice BOOLEAN,
                            playersVpi INT NOT NULL,         /* num of players vpi */
                            playersAtStreet1 INT NOT NULL,   /* num of players seeing flop/street4 */
                            playersAtStreet2 INT NOT NULL,
                            playersAtStreet3 INT NOT NULL,
                            playersAtStreet4 INT NOT NULL,
                            playersAtShowdown INT NOT NULL,
                            street0Raises INT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                            street1Raises INT NOT NULL, /* num small bets paid to see turn/street5 */
                            street2Raises INT NOT NULL, /* num big bets paid to see river/street6 */
                            street3Raises INT NOT NULL, /* num big bets paid to see sd/street7 */
                            street4Raises INT NOT NULL, /* num big bets paid to see showdown */
                            street0Pot INT,                 /* pot size at preflop/street3 */
                            street1Pot INT,                 /* pot size at flop/street4 */
                            street2Pot INT,                 /* pot size at turn/street5 */
                            street3Pot INT,                 /* pot size at river/street6 */
                            street4Pot INT,                 /* pot size at sd/street7 */
                            finalPot INT,                   /* final pot size */
                            comment TEXT,
                            commentTs timestamp)"""
                            
        ################################
        # Create Boards
        ################################

        if db_server == 'mysql':
            self.query['createBoardsTable'] = """CREATE TABLE Boards (
                            id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                            handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                            boardId smallint,
                            boardcard1 smallint,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 smallint,
                            boardcard3 smallint,
                            boardcard4 smallint,
                            boardcard5 smallint)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createBoardsTable'] = """CREATE TABLE Boards (
                            id BIGSERIAL, PRIMARY KEY (id),
                            handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                            boardId smallint,
                            boardcard1 smallint,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 smallint,
                            boardcard3 smallint,
                            boardcard4 smallint,
                            boardcard5 smallint)"""
        elif db_server == 'sqlite':
            self.query['createBoardsTable'] = """CREATE TABLE Boards (
                            id INTEGER PRIMARY KEY,
                            handId INT NOT NULL,
                            boardId INT,
                            boardcard1 INT,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                            boardcard2 INT,
                            boardcard3 INT,
                            boardcard4 INT,
                            boardcard5 INT)"""


     ################################
        # Create TourneyTypes
        ################################

        if db_server == 'mysql':
            self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                        id SMALLINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        siteId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4),
                        buyIn BIGINT,
                        fee BIGINT,
                        category varchar(9) NOT NULL,
                        limitType char(2) NOT NULL,
                        buyInChips BIGINT,
                        stack varchar(8),
                        maxSeats INT,
                        rebuy BOOLEAN,
                        rebuyCost BIGINT,
                        rebuyFee BIGINT,
                        rebuyChips BIGINT,
                        addOn BOOLEAN,
                        addOnCost BIGINT,
                        addOnFee BIGINT,
                        addOnChips BIGINT,
                        knockout BOOLEAN,
                        koBounty BIGINT,
                        progressive BOOLEAN,
                        step BOOLEAN,
                        stepNo INT,
                        chance BOOLEAN,
                        chanceCount INT,
                        speed varchar(10),
                        shootout BOOLEAN,
                        matrix BOOLEAN,
                        multiEntry BOOLEAN,
                        reEntry BOOLEAN,
                        fast BOOLEAN, 
                        newToGame BOOLEAN,
                        homeGame BOOLEAN,
                        split BOOLEAN,
                        sng BOOLEAN,
                        fifty50 BOOLEAN,
                        time BOOLEAN,
                        timeAmt INT,
                        satellite BOOLEAN,
                        doubleOrNothing BOOLEAN,
                        cashOut BOOLEAN,
                        onDemand BOOLEAN,
                        flighted BOOLEAN,
                        guarantee BOOLEAN,
                        guaranteeAmt BIGINT)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                        id SERIAL, PRIMARY KEY (id),
                        siteId INT NOT NULL, FOREIGN KEY (siteId) REFERENCES Sites(id),
                        currency varchar(4),
                        buyin BIGINT,
                        fee BIGINT,
                        category varchar(9),
                        limitType char(2),
                        buyInChips BIGINT,
                        stack varchar(8),
                        maxSeats INT,
                        rebuy BOOLEAN,
                        rebuyCost BIGINT,
                        rebuyFee BIGINT,
                        rebuyChips BIGINT,
                        addOn BOOLEAN,
                        addOnCost BIGINT,
                        addOnFee BIGINT,
                        addOnChips BIGINT,
                        knockout BOOLEAN,
                        koBounty BIGINT,
                        progressive BOOLEAN,
                        step BOOLEAN,
                        stepNo INT,
                        chance BOOLEAN,
                        chanceCount INT,
                        speed varchar(10),
                        shootout BOOLEAN,
                        matrix BOOLEAN,
                        multiEntry BOOLEAN,
                        reEntry BOOLEAN,
                        fast BOOLEAN,
                        newToGame BOOLEAN,
                        homeGame BOOLEAN,
                        split BOOLEAN,
                        sng BOOLEAN,
                        fifty50 BOOLEAN,
                        time BOOLEAN,
                        timeAmt INT,
                        satellite BOOLEAN,
                        doubleOrNothing BOOLEAN,
                        cashOut BOOLEAN,
                        onDemand BOOLEAN,
                        flighted BOOLEAN,
                        guarantee BOOLEAN,
                        guaranteeAmt BIGINT)"""
        elif db_server == 'sqlite':
            self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                        id INTEGER PRIMARY KEY,
                        siteId INT NOT NULL,
                        currency VARCHAR(4),
                        buyin INT,
                        fee INT,
                        category TEXT,
                        limitType TEXT,
                        buyInChips INT,
                        stack VARCHAR(8),
                        maxSeats INT,
                        rebuy BOOLEAN,
                        rebuyCost INT,
                        rebuyFee INT,
                        rebuyChips INT,
                        addOn BOOLEAN,
                        addOnCost INT,
                        addOnFee INT,
                        addOnChips INT,
                        knockout BOOLEAN,
                        koBounty INT,
                        progressive BOOLEAN,
                        step BOOLEAN,
                        stepNo INT,
                        chance BOOLEAN,
                        chanceCount INT,
                        speed TEXT,
                        shootout BOOLEAN,
                        matrix BOOLEAN,
                        multiEntry BOOLEAN,
                        reEntry BOOLEAN,
                        fast BOOLEAN,
                        newToGame BOOLEAN,
                        homeGame BOOLEAN,
                        split BOOLEAN,
                        sng BOOLEAN,
                        fifty50 BOOLEAN,
                        time BOOLEAN,
                        timeAmt INT,
                        satellite BOOLEAN,
                        doubleOrNothing BOOLEAN,
                        cashOut BOOLEAN,
                        onDemand BOOLEAN,
                        flighted BOOLEAN,
                        guarantee BOOLEAN,
                        guaranteeAmt INT)"""

        ################################
        # Create Tourneys
        ################################

        if db_server == 'mysql':
            self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneyTypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        sessionId INT UNSIGNED, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                        siteTourneyNo BIGINT NOT NULL,
                        entries INT,
                        prizepool BIGINT,
                        startTime DATETIME,
                        endTime DATETIME,
                        tourneyName TEXT,
                        totalRebuyCount INT,
                        totalAddOnCount INT,
                        added BIGINT,
                        addedCurrency VARCHAR(4),
                        comment TEXT,
                        commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                        id SERIAL, PRIMARY KEY (id),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        sessionId INT, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                        siteTourneyNo BIGINT,
                        entries INT,
                        prizepool BIGINT,
                        startTime timestamp without time zone,
                        endTime timestamp without time zone,
                        tourneyName TEXT,
                        totalRebuyCount INT,
                        totalAddOnCount INT,
                        added BIGINT,
                        addedCurrency VARCHAR(4),
                        comment TEXT,
                        commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                        id INTEGER PRIMARY KEY,
                        tourneyTypeId INT,
                        sessionId INT,
                        siteTourneyNo INT,
                        entries INT,
                        prizepool INT,
                        startTime timestamp,
                        endTime timestamp,
                        tourneyName TEXT,
                        totalRebuyCount INT,
                        totalAddOnCount INT,
                        added INT,
                        addedCurrency VARCHAR(4),
                        comment TEXT,
                        commentTs timestamp)"""
                        
        ################################
        # Create HandsPlayers
        ################################

        if db_server == 'mysql':
            self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        startCash BIGINT NOT NULL,
                        effStack BIGINT NOT NULL,
                        startBounty BIGINT,
                        endBounty BIGINT,
                        position CHAR(1),
                        seatNo SMALLINT NOT NULL,
                        sitout BOOLEAN NOT NULL,
                    
                        card1 smallint NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        card2 smallint NOT NULL,
                        card3 smallint,
                        card4 smallint,
                        card5 smallint,
                        card6 smallint,
                        card7 smallint,
                        card8 smallint,  /* cards 8-20 for draw hands */
                        card9 smallint,
                        card10 smallint,
                        card11 smallint,
                        card12 smallint,
                        card13 smallint,
                        card14 smallint,
                        card15 smallint,
                        card16 smallint,
                        card17 smallint,
                        card18 smallint,
                        card19 smallint,
                        card20 smallint,
                        startCards SMALLINT UNSIGNED, FOREIGN KEY (startCards) REFERENCES StartCards(id),
                        
                        common BIGINT NOT NULL,
                        committed BIGINT NOT NULL,                        
                        winnings BIGINT NOT NULL,
                        rake BIGINT NOT NULL,
                        rakeDealt NUMERIC NOT NULL,
                        rakeContributed NUMERIC NOT NULL,
                        rakeWeighted NUMERIC NOT NULL,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        comment text,
                        commentTs DATETIME,
                        tourneysPlayersId BIGINT UNSIGNED, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),

                        wonWhenSeenStreet1 BOOLEAN,
                        wonWhenSeenStreet2 BOOLEAN,
                        wonWhenSeenStreet3 BOOLEAN,
                        wonWhenSeenStreet4 BOOLEAN,
                        wonAtSD BOOLEAN,
                        
                        street0VPIChance BOOLEAN,
                        street0VPI BOOLEAN,
                        street0AggrChance BOOLEAN,
                        street0Aggr BOOLEAN,
                        street0CalledRaiseChance TINYINT,
                        street0CalledRaiseDone TINYINT,
                        street0_2BChance BOOLEAN,
                        street0_2BDone BOOLEAN,
                        street0_3BChance BOOLEAN,
                        street0_3BDone BOOLEAN,
                        street0_4BChance BOOLEAN,
                        street0_C4BChance BOOLEAN,
                        street0_4BDone BOOLEAN,
                        street0_C4BDone BOOLEAN,
                        street0_FoldTo2BChance BOOLEAN,
                        street0_FoldTo2BDone BOOLEAN,
                        street0_FoldTo3BChance BOOLEAN,
                        street0_FoldTo3BDone BOOLEAN,
                        street0_FoldTo4BChance BOOLEAN,
                        street0_FoldTo4BDone BOOLEAN,
                        street0_SqueezeChance BOOLEAN,
                        street0_SqueezeDone BOOLEAN,

                        raiseToStealChance BOOLEAN,
                        raiseToStealDone BOOLEAN,
                        stealChance BOOLEAN,
                        stealDone BOOLEAN,
                        success_Steal BOOLEAN,

                        street1Seen BOOLEAN,
                        street2Seen BOOLEAN,
                        street3Seen BOOLEAN,
                        street4Seen BOOLEAN,
                        sawShowdown BOOLEAN,
                        showed      BOOLEAN,
                        
                        street0AllIn BOOLEAN,
                        street1AllIn BOOLEAN,
                        street2AllIn BOOLEAN,
                        street3AllIn BOOLEAN,
                        street4AllIn BOOLEAN,
                        wentAllIn BOOLEAN,
                        
                        street0InPosition BOOLEAN,
                        street1InPosition BOOLEAN,
                        street2InPosition BOOLEAN,
                        street3InPosition BOOLEAN,
                        street4InPosition BOOLEAN,
                        street0FirstToAct BOOLEAN,
                        street1FirstToAct BOOLEAN,
                        street2FirstToAct BOOLEAN,
                        street3FirstToAct BOOLEAN,
                        street4FirstToAct BOOLEAN,

                        street1Aggr BOOLEAN,
                        street2Aggr BOOLEAN,
                        street3Aggr BOOLEAN,
                        street4Aggr BOOLEAN,

                        otherRaisedStreet0 BOOLEAN,
                        otherRaisedStreet1 BOOLEAN,
                        otherRaisedStreet2 BOOLEAN,
                        otherRaisedStreet3 BOOLEAN,
                        otherRaisedStreet4 BOOLEAN,
                        foldToOtherRaisedStreet0 BOOLEAN,
                        foldToOtherRaisedStreet1 BOOLEAN,
                        foldToOtherRaisedStreet2 BOOLEAN,
                        foldToOtherRaisedStreet3 BOOLEAN,
                        foldToOtherRaisedStreet4 BOOLEAN,

                        raiseFirstInChance BOOLEAN,
                        raisedFirstIn BOOLEAN,
                        foldBbToStealChance BOOLEAN,
                        foldedBbToSteal BOOLEAN,
                        foldSbToStealChance BOOLEAN,
                        foldedSbToSteal BOOLEAN,

                        street1CBChance BOOLEAN,
                        street1CBDone BOOLEAN,
                        street2CBChance BOOLEAN,
                        street2CBDone BOOLEAN,
                        street3CBChance BOOLEAN,
                        street3CBDone BOOLEAN,
                        street4CBChance BOOLEAN,
                        street4CBDone BOOLEAN,

                        foldToStreet1CBChance BOOLEAN,
                        foldToStreet1CBDone BOOLEAN,
                        foldToStreet2CBChance BOOLEAN,
                        foldToStreet2CBDone BOOLEAN,
                        foldToStreet3CBChance BOOLEAN,
                        foldToStreet3CBDone BOOLEAN,
                        foldToStreet4CBChance BOOLEAN,
                        foldToStreet4CBDone BOOLEAN,

                        street1CheckCallRaiseChance BOOLEAN,
                        street1CheckCallDone BOOLEAN,
                        street1CheckRaiseDone BOOLEAN,
                        street2CheckCallRaiseChance BOOLEAN,
                        street2CheckCallDone BOOLEAN,
                        street2CheckRaiseDone BOOLEAN,
                        street3CheckCallRaiseChance BOOLEAN,
                        street3CheckCallDone BOOLEAN,
                        street3CheckRaiseDone BOOLEAN,
                        street4CheckCallRaiseChance BOOLEAN,
                        street4CheckCallDone BOOLEAN,
                        street4CheckRaiseDone BOOLEAN,

                        street0Calls TINYINT,
                        street1Calls TINYINT,
                        street2Calls TINYINT,
                        street3Calls TINYINT,
                        street4Calls TINYINT,
                        street0Bets TINYINT,
                        street1Bets TINYINT,
                        street2Bets TINYINT,
                        street3Bets TINYINT,
                        street4Bets TINYINT,
                        street0Raises TINYINT,
                        street1Raises TINYINT,
                        street2Raises TINYINT,
                        street3Raises TINYINT,
                        street4Raises TINYINT,
                        street1Discards TINYINT,
                        street2Discards TINYINT,
                        street3Discards TINYINT,
                        
                        handString TEXT,
                        actionString VARCHAR(15))
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        startCash BIGINT NOT NULL,
                        effStack BIGINT NOT NULL,
                        startBounty BIGINT,
                        endBounty BIGINT,
                        position CHAR(1),
                        seatNo SMALLINT NOT NULL,
                        sitout BOOLEAN NOT NULL,

                        card1 smallint NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        card2 smallint NOT NULL,
                        card3 smallint,
                        card4 smallint,
                        card5 smallint,
                        card6 smallint,
                        card7 smallint,
                        card8 smallint,  /* cards 8-20 for draw hands */
                        card9 smallint,
                        card10 smallint,
                        card11 smallint,
                        card12 smallint,
                        card13 smallint,
                        card14 smallint,
                        card15 smallint,
                        card16 smallint,
                        card17 smallint,
                        card18 smallint,
                        card19 smallint,
                        card20 smallint, 
                        startCards smallint, FOREIGN KEY (startCards) REFERENCES StartCards(id),

                        common BIGINT NOT NULL,
                        committed BIGINT NOT NULL,
                        winnings BIGINT NOT NULL,
                        rake BIGINT NOT NULL,
                        rakeDealt NUMERIC NOT NULL,
                        rakeContributed NUMERIC NOT NULL,
                        rakeWeighted NUMERIC NOT NULL,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        comment text,
                        commentTs timestamp without time zone,
                        tourneysPlayersId BIGINT, FOREIGN KEY (tourneysPlayersId) REFERENCES TourneysPlayers(id),

                        wonWhenSeenStreet1 BOOLEAN,
                        wonWhenSeenStreet2 BOOLEAN,
                        wonWhenSeenStreet3 BOOLEAN,
                        wonWhenSeenStreet4 BOOLEAN,
                        wonAtSD BOOLEAN,

                        street0VPIChance BOOLEAN,
                        street0VPI BOOLEAN,
                        street0AggrChance BOOLEAN,
                        street0Aggr BOOLEAN,
                        street0CalledRaiseChance SMALLINT,
                        street0CalledRaiseDone SMALLINT,
                        street0_2BChance BOOLEAN,
                        street0_2BDone BOOLEAN,
                        street0_3BChance BOOLEAN,
                        street0_3BDone BOOLEAN,
                        street0_4BChance BOOLEAN,
                        street0_4BDone BOOLEAN,
                        street0_C4BChance BOOLEAN,
                        street0_C4BDone BOOLEAN,
                        street0_FoldTo2BChance BOOLEAN,
                        street0_FoldTo2BDone BOOLEAN,
                        street0_FoldTo3BChance BOOLEAN,
                        street0_FoldTo3BDone BOOLEAN,
                        street0_FoldTo4BChance BOOLEAN,
                        street0_FoldTo4BDone BOOLEAN,
                        street0_SqueezeChance BOOLEAN,
                        street0_SqueezeDone BOOLEAN,

                        raiseToStealChance BOOLEAN,
                        raiseToStealDone BOOLEAN,
                        stealChance BOOLEAN,
                        stealDone BOOLEAN,
                        success_Steal BOOLEAN,

                        street1Seen BOOLEAN,
                        street2Seen BOOLEAN,
                        street3Seen BOOLEAN,
                        street4Seen BOOLEAN,
                        sawShowdown BOOLEAN,
                        showed      BOOLEAN,
                        
                        street0AllIn BOOLEAN,
                        street1AllIn BOOLEAN,
                        street2AllIn BOOLEAN,
                        street3AllIn BOOLEAN,
                        street4AllIn BOOLEAN,
                        wentAllIn BOOLEAN,
                        
                        street0InPosition BOOLEAN,
                        street1InPosition BOOLEAN,
                        street2InPosition BOOLEAN,
                        street3InPosition BOOLEAN,
                        street4InPosition BOOLEAN,
                        street0FirstToAct BOOLEAN,
                        street1FirstToAct BOOLEAN,
                        street2FirstToAct BOOLEAN,
                        street3FirstToAct BOOLEAN,
                        street4FirstToAct BOOLEAN,

                        street1Aggr BOOLEAN,
                        street2Aggr BOOLEAN,
                        street3Aggr BOOLEAN,
                        street4Aggr BOOLEAN,

                        otherRaisedStreet0 BOOLEAN,
                        otherRaisedStreet1 BOOLEAN,
                        otherRaisedStreet2 BOOLEAN,
                        otherRaisedStreet3 BOOLEAN,
                        otherRaisedStreet4 BOOLEAN,
                        foldToOtherRaisedStreet0 BOOLEAN,
                        foldToOtherRaisedStreet1 BOOLEAN,
                        foldToOtherRaisedStreet2 BOOLEAN,
                        foldToOtherRaisedStreet3 BOOLEAN,
                        foldToOtherRaisedStreet4 BOOLEAN,

                        raiseFirstInChance BOOLEAN,
                        raisedFirstIn BOOLEAN,
                        foldBbToStealChance BOOLEAN,
                        foldedBbToSteal BOOLEAN,
                        foldSbToStealChance BOOLEAN,
                        foldedSbToSteal BOOLEAN,

                        street1CBChance BOOLEAN,
                        street1CBDone BOOLEAN,
                        street2CBChance BOOLEAN,
                        street2CBDone BOOLEAN,
                        street3CBChance BOOLEAN,
                        street3CBDone BOOLEAN,
                        street4CBChance BOOLEAN,
                        street4CBDone BOOLEAN,

                        foldToStreet1CBChance BOOLEAN,
                        foldToStreet1CBDone BOOLEAN,
                        foldToStreet2CBChance BOOLEAN,
                        foldToStreet2CBDone BOOLEAN,
                        foldToStreet3CBChance BOOLEAN,
                        foldToStreet3CBDone BOOLEAN,
                        foldToStreet4CBChance BOOLEAN,
                        foldToStreet4CBDone BOOLEAN,

                        street1CheckCallRaiseChance BOOLEAN,
                        street1CheckCallDone BOOLEAN,
                        street1CheckRaiseDone BOOLEAN,
                        street2CheckCallRaiseChance BOOLEAN,
                        street2CheckCallDone BOOLEAN,
                        street2CheckRaiseDone BOOLEAN,
                        street3CheckCallRaiseChance BOOLEAN,
                        street3CheckCallDone BOOLEAN,
                        street3CheckRaiseDone BOOLEAN,
                        street4CheckCallRaiseChance BOOLEAN,
                        street4CheckCallDone BOOLEAN,
                        street4CheckRaiseDone BOOLEAN,

                        street0Calls SMALLINT,
                        street1Calls SMALLINT,
                        street2Calls SMALLINT,
                        street3Calls SMALLINT,
                        street4Calls SMALLINT,
                        street0Bets SMALLINT,
                        street1Bets SMALLINT,
                        street2Bets SMALLINT,
                        street3Bets SMALLINT,
                        street4Bets SMALLINT,
                        street0Raises SMALLINT,
                        street1Raises SMALLINT,
                        street2Raises SMALLINT,
                        street3Raises SMALLINT,
                        street4Raises SMALLINT,
                        street1Discards SMALLINT,
                        street2Discards SMALLINT,
                        street3Discards SMALLINT,
                        
                        handString TEXT,
                        actionString VARCHAR(15))"""
        elif db_server == 'sqlite':
            self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        playerId INT NOT NULL,
                        startCash INT NOT NULL,
                        effStack INT NOT NULL,
                        startBounty INT,
                        endBounty INT,
                        position TEXT,
                        seatNo INT NOT NULL,
                        sitout BOOLEAN NOT NULL,
                    
                        card1 INT NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        card2 INT NOT NULL,
                        card3 INT,
                        card4 INT,
                        card5 INT,
                        card6 INT,
                        card7 INT,
                        card8 INT,  /* cards 8-20 for draw hands */
                        card9 INT,
                        card10 INT,
                        card11 INT,
                        card12 INT,
                        card13 INT,
                        card14 INT,
                        card15 INT,
                        card16 INT,
                        card17 INT,
                        card18 INT,
                        card19 INT,
                        card20 INT,
                        startCards INT,
                    
                        common INT NOT NULL,
                        committed INT NOT NULL,
                        winnings INT NOT NULL,
                        rake INT NOT NULL,
                        rakeDealt decimal NOT NULL,
                        rakeContributed decimal NOT NULL,
                        rakeWeighted decimal NOT NULL,
                        totalProfit INT,
                        allInEV decimal,
                        comment TEXT,
                        commentTs timestamp,
                        tourneysPlayersId INT,

                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,

                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,

                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        showed      INT,
                        
                        street0AllIn INT,
                        street1AllIn INT,
                        street2AllIn INT,
                        street3AllIn INT,
                        street4AllIn INT,
                        wentAllIn INT,
                        
                        street0InPosition INT,
                        street1InPosition INT,
                        street2InPosition INT,
                        street3InPosition INT,
                        street4InPosition INT,
                        street0FirstToAct INT,
                        street1FirstToAct INT,
                        street2FirstToAct INT,
                        street3FirstToAct INT,
                        street4FirstToAct INT,

                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,

                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,

                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,

                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,

                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,

                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,

                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT,
                        
                        handString TEXT,
                        actionString VARCHAR(15))
                        """


     ################################
        # Create TourneysPlayers
        ################################

        if db_server == 'mysql':
            self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        tourneyId INT UNSIGNED NOT NULL, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        entryId INT,
                        rank INT,
                        winnings BIGINT,
                        winningsCurrency VARCHAR(4),
                        rebuyCount INT,
                        addOnCount INT,
                        koCount NUMERIC,
                        comment TEXT,
                        commentTs DATETIME)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                        id BIGSERIAL, PRIMARY KEY (id),
                        tourneyId INT, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        entryId INT,
                        rank INT,
                        winnings BIGINT,
                        winningsCurrency VARCHAR(4),
                        rebuyCount INT,
                        addOnCount INT,
                        koCount NUMERIC,
                        comment TEXT,
                        commentTs timestamp without time zone)"""
        elif db_server == 'sqlite':
            self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                        id INTEGER PRIMARY KEY,
                        tourneyId INT,
                        playerId INT,
                        entryId INT,
                        rank INT,
                        winnings INT,
                        winningsCurrency VARCHAR(4),
                        rebuyCount INT,
                        addOnCount INT,
                        koCount decimal,
                        comment TEXT,
                        commentTs timestamp,
                        FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        FOREIGN KEY (playerId) REFERENCES Players(id)
                        )"""


        ################################
        # Create HandsActions
        ################################

        if db_server == 'mysql':
            self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        street SMALLINT NOT NULL,
                        actionNo SMALLINT NOT NULL,
                        streetActionNo SMALLINT NOT NULL,
                        actionId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (actionId) REFERENCES Actions(id),
                        amount BIGINT NOT NULL,
                        raiseTo BIGINT NOT NULL,
                        amountCalled BIGINT NOT NULL,
                        numDiscarded SMALLINT NOT NULL,
                        cardsDiscarded varchar(14),
                        allIn BOOLEAN NOT NULL)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        street SMALLINT,
                        actionNo SMALLINT,
                        streetActionNo SMALLINT,
                        actionId SMALLINT, FOREIGN KEY (actionId) REFERENCES Actions(id),
                        amount BIGINT,
                        raiseTo BIGINT,
                        amountCalled BIGINT,
                        numDiscarded SMALLINT,
                        cardsDiscarded varchar(14),
                        allIn BOOLEAN)"""
        elif db_server == 'sqlite':
            self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        playerId INT NOT NULL,
                        street SMALLINT,
                        actionNo SMALLINT,
                        streetActionNo SMALLINT,
                        actionId SMALLINT,
                        amount INT,
                        raiseTo INT,
                        amountCalled INT,
                        numDiscarded SMALLINT,
                        cardsDiscarded TEXT,
                        allIn BOOLEAN
                        )""" 


        ################################
        # Create HandsStove
        ################################

        if db_server == 'mysql':
            self.query['createHandsStoveTable'] = """CREATE TABLE HandsStove (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        streetId SMALLINT,
                        boardId SMALLINT,
                        hiLo char(1) NOT NULL,
                        rankId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (rankId) REFERENCES Rank(id),
                        value BIGINT,
                        cards VARCHAR(5),
                        ev NUMERIC)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsStoveTable'] = """CREATE TABLE HandsStove (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        streetId SMALLINT,
                        boardId SMALLINT,
                        hiLo char(1) NOT NULL,
                        rankId SMALLINT NOT NULL, FOREIGN KEY (rankId) REFERENCES Rank(id),
                        value BIGINT,
                        cards VARCHAR(5),
                        ev NUMERIC)"""
        elif db_server == 'sqlite':
            self.query['createHandsStoveTable'] = """CREATE TABLE HandsStove (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        playerId INT NOT NULL,
                        streetId INT,
                        boardId INT,
                        hiLo TEXT NOT NULL,
                        rankId INT,
                        value INT,
                        cards TEXT,
                        ev decimal
                        )""" 
                        
        ################################
        # Create HandsPots
        ################################

        if db_server == 'mysql':
            self.query['createHandsPotsTable'] = """CREATE TABLE HandsPots (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        handId BIGINT UNSIGNED NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        potId SMALLINT,
                        boardId SMALLINT,
                        hiLo char(1) NOT NULL,
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        pot BIGINT,
                        collected BIGINT,
                        rake INT)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHandsPotsTable'] = """CREATE TABLE HandsPots (
                        id BIGSERIAL, PRIMARY KEY (id),
                        handId BIGINT NOT NULL, FOREIGN KEY (handId) REFERENCES Hands(id),
                        potId SMALLINT,
                        boardId SMALLINT,
                        hiLo char(1) NOT NULL,
                        playerId INT NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        pot BIGINT,
                        collected BIGINT,
                        rake INT)"""
        elif db_server == 'sqlite':
            self.query['createHandsPotsTable'] = """CREATE TABLE HandsPots (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        potId INT,
                        boardId INT,
                        hiLo TEXT NOT NULL,
                        playerId INT NOT NULL,
                        pot INT,
                        collected INT,
                        rake INT
                        )""" 
                        
        ################################
        # Create Files
        ################################
        
        if db_server == 'mysql':
            self.query['createFilesTable'] = """CREATE TABLE Files (
                        id INT(10) UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        file text NOT NULL,
                        site VARCHAR(32),
                        type VARCHAR(7),
                        startTime DATETIME NOT NULL,
                        lastUpdate DATETIME NOT NULL,
                        endTime DATETIME,
                        hands INT,
                        stored INT,
                        dups INT,
                        partial INT,
                        skipped INT,
                        errs INT,
                        ttime100 INT,
                        finished BOOLEAN)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createFilesTable'] = """CREATE TABLE Files (
                        id BIGSERIAL, PRIMARY KEY (id),
                        file TEXT NOT NULL,
                        site VARCHAR(32),
                        type VARCHAR(7),
                        startTime timestamp without time zone NOT NULL,
                        lastUpdate timestamp without time zone NOT NULL,
                        endTime timestamp without time zone,
                        hands INT,
                        stored INT,
                        dups INT,
                        partial INT,
                        skipped INT,
                        errs INT,
                        ttime100 INT,
                        finished BOOLEAN)"""
        elif db_server == 'sqlite':
            self.query['createFilesTable'] = """CREATE TABLE Files (
                        id INTEGER PRIMARY KEY,
                        file TEXT NOT NULL,
                        site VARCHAR(32),
                        type VARCHAR(7),
                        startTime timestamp NOT NULL,
                        lastUpdate timestamp NOT NULL,
                        endTime timestamp,
                        hands INT,
                        stored INT,
                        dups INT,
                        partial INT,
                        skipped INT,
                        errs INT,
                        ttime100 INT,
                        finished BOOLEAN
                        )""" 

        ################################
        # Create HudCache
        ################################

        if db_server == 'mysql':
            self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        gametypeId SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        seats SMALLINT NOT NULL,
                        position CHAR(1),
                        tourneyTypeId SMALLINT UNSIGNED, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        styleKey CHAR(7) NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        n INT NOT NULL,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,                        
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,                        
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,                        
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,                        
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,                        
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,                        
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                        id BIGSERIAL, PRIMARY KEY (id),
                        gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        seats SMALLINT,
                        position CHAR(1),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        styleKey CHAR(7) NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        n INT,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
        elif db_server == 'sqlite':
            self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                        id INTEGER PRIMARY KEY,
                        gametypeId INT,
                        playerId INT,
                        seats INT,
                        position TEXT,
                        tourneyTypeId INT,
                        styleKey TEXT NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                        n INT,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common INT,
                        committed INT,
                        winnings INT,
                        rake INT,
                        rakeDealt decimal,
                        rakeContributed decimal,
                        rakeWeighted decimal,
                        totalProfit INT,
                        allInEV decimal,
                        showdownWinnings INT,
                        nonShowdownWinnings INT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
                        
        ################################
        # Create CardsCache
        ################################

        if db_server == 'mysql':
            self.query['createCardsCacheTable'] = """CREATE TABLE CardsCache (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        weekId INT UNSIGNED, FOREIGN KEY (weekId) REFERENCES Weeks(id),
                        monthId INT UNSIGNED, FOREIGN KEY (monthId) REFERENCES Months(id),
                        gametypeId SMALLINT UNSIGNED, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        tourneyTypeId SMALLINT UNSIGNED, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        startCards SMALLINT UNSIGNED NOT NULL, FOREIGN KEY (startCards) REFERENCES StartCards(id),
                        n INT NOT NULL,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,                        
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,                        
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,                        
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,                        
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,                        
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createCardsCacheTable'] = """CREATE TABLE CardsCache (
                        id BIGSERIAL, PRIMARY KEY (id),
                        weekId INT, FOREIGN KEY (weekId) REFERENCES Weeks(id),
                        monthId INT, FOREIGN KEY (monthId) REFERENCES Months(id),
                        gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        startCards SMALLINT, FOREIGN KEY (startCards) REFERENCES StartCards(id),
                        n INT,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
        elif db_server == 'sqlite':
            self.query['createCardsCacheTable'] = """CREATE TABLE CardsCache (
                        id INTEGER PRIMARY KEY,
                        weekId INT,
                        monthId INT,
                        gametypeId INT,
                        tourneyTypeId INT,
                        playerId INT,
                        startCards INT,
                        n INT,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common INT,
                        committed INT,
                        winnings INT,
                        rake INT,
                        rakeDealt decimal,
                        rakeContributed decimal,
                        rakeWeighted decimal,
                        totalProfit INT,
                        allInEV decimal,
                        showdownWinnings INT,
                        nonShowdownWinnings INT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
                        
        ################################
        # Create PositionsCache
        ################################

        if db_server == 'mysql':
            self.query['createPositionsCacheTable'] = """CREATE TABLE PositionsCache (
                        id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        weekId INT UNSIGNED, FOREIGN KEY (weekId) REFERENCES Weeks(id),
                        monthId INT UNSIGNED, FOREIGN KEY (monthId) REFERENCES Months(id),
                        gametypeId SMALLINT UNSIGNED, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        tourneyTypeId SMALLINT UNSIGNED, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        seats SMALLINT NOT NULL,
                        maxPosition TINYINT NOT NULL,
                        position CHAR(1),
                        n INT NOT NULL,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,                        
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,                        
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,                        
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,                        
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,                        
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        ENGINE=INNODB"""
        elif db_server == 'postgresql':
            self.query['createPositionsCacheTable'] = """CREATE TABLE PositionsCache (
                        id BIGSERIAL, PRIMARY KEY (id),
                        weekId INT, FOREIGN KEY (weekId) REFERENCES Weeks(id),
                        monthId INT, FOREIGN KEY (monthId) REFERENCES Months(id),
                        gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        tourneyTypeId INT, FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        seats SMALLINT,
                        maxPosition SMALLINT NOT NULL,
                        position CHAR(1),
                        n INT,
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,                        
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
        elif db_server == 'sqlite':
            self.query['createPositionsCacheTable'] = """CREATE TABLE PositionsCache (
                        id INTEGER PRIMARY KEY,
                        weekId INT,
                        monthId INT,
                        gametypeId INT,
                        tourneyTypeId INT,
                        playerId INT,
                        seats INT,
                        maxPosition INT NOT NULL,
                        position TEXT,
                        n INT,
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common INT,
                        committed INT,
                        winnings INT,
                        rake INT,
                        rakeDealt decimal,
                        rakeContributed decimal,
                        rakeWeighted decimal,
                        totalProfit INT,
                        allInEV decimal,
                        showdownWinnings INT,
                        nonShowdownWinnings INT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
                        
        ################################
        # Create Weeks
        ################################

        if db_server == 'mysql':
            self.query['createWeeksTable'] = """CREATE TABLE Weeks (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        weekStart DATETIME NOT NULL)
                        ENGINE=INNODB
                        """
                        
        elif db_server == 'postgresql':
            self.query['createWeeksTable'] = """CREATE TABLE Weeks (
                        id SERIAL, PRIMARY KEY (id),
                        weekStart timestamp without time zone NOT NULL)
                        """
                        
        elif db_server == 'sqlite':
            self.query['createWeeksTable'] = """CREATE TABLE Weeks (
                        id INTEGER PRIMARY KEY,
                        weekStart timestamp NOT NULL)
                        """
                        
        ################################
        # Create Months
        ################################

        if db_server == 'mysql':
            self.query['createMonthsTable'] = """CREATE TABLE Months (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        monthStart DATETIME NOT NULL)
                        ENGINE=INNODB
                        """
                        
        elif db_server == 'postgresql':
            self.query['createMonthsTable'] = """CREATE TABLE Months (
                        id SERIAL, PRIMARY KEY (id),
                        monthStart timestamp without time zone NOT NULL)
                        """
                        
        elif db_server == 'sqlite':
            self.query['createMonthsTable'] = """CREATE TABLE Months (
                        id INTEGER PRIMARY KEY,
                        monthStart timestamp NOT NULL)
                        """
                        
        ################################
        # Create Sessions
        ################################

        if db_server == 'mysql':
            self.query['createSessionsTable'] = """CREATE TABLE Sessions (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        weekId INT UNSIGNED, FOREIGN KEY (weekId) REFERENCES Weeks(id),
                        monthId INT UNSIGNED, FOREIGN KEY (monthId) REFERENCES Months(id),
                        sessionStart DATETIME NOT NULL,
                        sessionEnd DATETIME NOT NULL)
                        ENGINE=INNODB
                        """
                        
        elif db_server == 'postgresql':
            self.query['createSessionsTable'] = """CREATE TABLE Sessions (
                        id SERIAL, PRIMARY KEY (id),
                        weekId INT, FOREIGN KEY (weekId) REFERENCES Weeks(id),
                        monthId INT, FOREIGN KEY (monthId) REFERENCES Months(id),
                        sessionStart timestamp without time zone NOT NULL,
                        sessionEnd timestamp without time zone NOT NULL)
                        """
                        
        elif db_server == 'sqlite':
            self.query['createSessionsTable'] = """CREATE TABLE Sessions (
                        id INTEGER PRIMARY KEY,
                        weekId INT,
                        monthId INT,
                        sessionStart timestamp NOT NULL,
                        sessionEnd timestamp NOT NULL)
                        """
                        
        ################################
        # Create SessionsCache
        ################################

        if db_server == 'mysql':
            self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        sessionId INT UNSIGNED, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                        startTime DATETIME NOT NULL,
                        endTime DATETIME NOT NULL,
                        gametypeId SMALLINT UNSIGNED, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        n INT NOT NULL,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,                        
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,                        
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,                        
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,                        
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,                        
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,                        
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        ENGINE=INNODB
                        """
                        
        elif db_server == 'postgresql':
            self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                        id SERIAL, PRIMARY KEY (id),
                        sessionId INT, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                        startTime timestamp without time zone NOT NULL,
                        endTime timestamp without time zone NOT NULL,
                        gametypeId INT, FOREIGN KEY (gametypeId) REFERENCES Gametypes(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        n INT,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,                        
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
                        
        elif db_server == 'sqlite':
            self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                        id INTEGER PRIMARY KEY,
                        sessionId INT,
                        startTime timestamp NOT NULL,
                        endTime timestamp NOT NULL,
                        gametypeId INT,
                        playerId INT,
                        n INT,
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,                        
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common INT,
                        committed INT,
                        winnings INT,
                        rake INT,
                        rakeDealt decimal,
                        rakeContributed decimal,
                        rakeWeighted decimal,
                        totalProfit INT,
                        allInEV decimal,
                        showdownWinnings INT,
                        nonShowdownWinnings INT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
                        
        ################################
        # Create TourneysCache
        ################################

        if db_server == 'mysql':
            self.query['createTourneysCacheTable'] = """CREATE TABLE TourneysCache (
                        id INT UNSIGNED AUTO_INCREMENT NOT NULL, PRIMARY KEY (id),
                        sessionId INT UNSIGNED, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                        startTime DATETIME NOT NULL,
                        endTime DATETIME NOT NULL,
                        tourneyId INT UNSIGNED NOT NULL, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        playerId INT UNSIGNED NOT NULL, FOREIGN KEY (playerId) REFERENCES Players(id),
                        n INT NOT NULL,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,                        
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,                        
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,                        
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,                        
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,                        
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,                        
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        ENGINE=INNODB
                        """
                        
        elif db_server == 'postgresql':
            self.query['createTourneysCacheTable'] = """CREATE TABLE TourneysCache (
                        id SERIAL, PRIMARY KEY (id),
                        sessionId INT, FOREIGN KEY (sessionId) REFERENCES Sessions(id),
                        startTime timestamp without time zone NOT NULL,
                        endTime timestamp without time zone NOT NULL,
                        tourneyId INT, FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                        playerId INT, FOREIGN KEY (playerId) REFERENCES Players(id),
                        n INT,                        
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,                        
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common BIGINT,
                        committed BIGINT,
                        winnings BIGINT,
                        rake BIGINT,
                        rakeDealt NUMERIC,
                        rakeContributed NUMERIC,
                        rakeWeighted NUMERIC,
                        totalProfit BIGINT,
                        allInEV NUMERIC,
                        showdownWinnings BIGINT,
                        nonShowdownWinnings BIGINT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
                        
        elif db_server == 'sqlite':
            self.query['createTourneysCacheTable'] = """CREATE TABLE TourneysCache (
                        id INTEGER PRIMARY KEY,
                        sessionId INT,
                        startTime timestamp NOT NULL,
                        endTime timestamp NOT NULL,
                        tourneyId INT,
                        playerId INT,
                        n INT,
                        street0VPIChance INT,
                        street0VPI INT,
                        street0AggrChance INT,
                        street0Aggr INT,
                        street0CalledRaiseChance INT,
                        street0CalledRaiseDone INT,
                        street0_2BChance INT,
                        street0_2BDone INT,
                        street0_3BChance INT,
                        street0_3BDone INT,
                        street0_4BChance INT,
                        street0_4BDone INT,
                        street0_C4BChance INT,
                        street0_C4BDone INT,
                        street0_FoldTo2BChance INT,
                        street0_FoldTo2BDone INT,
                        street0_FoldTo3BChance INT,
                        street0_FoldTo3BDone INT,
                        street0_FoldTo4BChance INT,
                        street0_FoldTo4BDone INT,
                        street0_SqueezeChance INT,
                        street0_SqueezeDone INT,
                        raiseToStealChance INT,
                        raiseToStealDone INT,
                        stealChance INT,
                        stealDone INT,
                        success_Steal INT,
                        street1Seen INT,
                        street2Seen INT,
                        street3Seen INT,
                        street4Seen INT,
                        sawShowdown INT,
                        street1Aggr INT,
                        street2Aggr INT,
                        street3Aggr INT,
                        street4Aggr INT,
                        otherRaisedStreet0 INT,
                        otherRaisedStreet1 INT,
                        otherRaisedStreet2 INT,
                        otherRaisedStreet3 INT,
                        otherRaisedStreet4 INT,
                        foldToOtherRaisedStreet0 INT,
                        foldToOtherRaisedStreet1 INT,
                        foldToOtherRaisedStreet2 INT,
                        foldToOtherRaisedStreet3 INT,
                        foldToOtherRaisedStreet4 INT,                     
                        wonWhenSeenStreet1 INT,
                        wonWhenSeenStreet2 INT,
                        wonWhenSeenStreet3 INT,
                        wonWhenSeenStreet4 INT,
                        wonAtSD INT,
                        raiseFirstInChance INT,
                        raisedFirstIn INT,
                        foldBbToStealChance INT,
                        foldedBbToSteal INT,
                        foldSbToStealChance INT,
                        foldedSbToSteal INT,
                        street1CBChance INT,
                        street1CBDone INT,
                        street2CBChance INT,
                        street2CBDone INT,
                        street3CBChance INT,
                        street3CBDone INT,
                        street4CBChance INT,
                        street4CBDone INT,
                        foldToStreet1CBChance INT,
                        foldToStreet1CBDone INT,
                        foldToStreet2CBChance INT,
                        foldToStreet2CBDone INT,
                        foldToStreet3CBChance INT,
                        foldToStreet3CBDone INT,
                        foldToStreet4CBChance INT,
                        foldToStreet4CBDone INT,
                        common INT,
                        committed INT,
                        winnings INT,
                        rake INT,
                        rakeDealt decimal,
                        rakeContributed decimal,
                        rakeWeighted decimal,
                        totalProfit INT,
                        allInEV decimal,
                        showdownWinnings INT,
                        nonShowdownWinnings INT,
                        street1CheckCallRaiseChance INT,
                        street1CheckCallDone INT,
                        street1CheckRaiseDone INT,
                        street2CheckCallRaiseChance INT,
                        street2CheckCallDone INT,
                        street2CheckRaiseDone INT,
                        street3CheckCallRaiseChance INT,
                        street3CheckCallDone INT,
                        street3CheckRaiseDone INT,
                        street4CheckCallRaiseChance INT,
                        street4CheckCallDone INT,
                        street4CheckRaiseDone INT,
                        street0Calls INT,
                        street1Calls INT,
                        street2Calls INT,
                        street3Calls INT,
                        street4Calls INT,
                        street0Bets INT,
                        street1Bets INT,
                        street2Bets INT,
                        street3Bets INT,
                        street4Bets INT,
                        street0Raises INT,
                        street1Raises INT,
                        street2Raises INT,
                        street3Raises INT,
                        street4Raises INT,
                        street1Discards INT,
                        street2Discards INT,
                        street3Discards INT)
                        """
            
        if db_server == 'mysql':
            self.query['addTourneyIndex'] = """ALTER TABLE Tourneys ADD UNIQUE INDEX siteTourneyNo(siteTourneyNo, tourneyTypeId)"""
        elif db_server == 'postgresql':
            self.query['addTourneyIndex'] = """CREATE UNIQUE INDEX siteTourneyNo ON Tourneys (siteTourneyNo, tourneyTypeId)"""
        elif db_server == 'sqlite':
            self.query['addTourneyIndex'] = """CREATE UNIQUE INDEX siteTourneyNo ON Tourneys (siteTourneyNo, tourneyTypeId)"""

        if db_server == 'mysql':
            self.query['addHandsIndex'] = """ALTER TABLE Hands ADD UNIQUE INDEX siteHandNo(siteHandNo, gametypeId<heroseat>)"""
        elif db_server == 'postgresql':
            self.query['addHandsIndex'] = """CREATE UNIQUE INDEX siteHandNo ON Hands (siteHandNo, gametypeId<heroseat>)"""
        elif db_server == 'sqlite':
            self.query['addHandsIndex'] = """CREATE UNIQUE INDEX siteHandNo ON Hands (siteHandNo, gametypeId<heroseat>)"""
            
        if db_server == 'mysql':
            self.query['addPlayersSeat'] = """ALTER TABLE HandsPlayers ADD UNIQUE INDEX playerSeat_idx(handId, seatNo)"""
        elif db_server == 'postgresql':
            self.query['addPlayersSeat'] = """CREATE UNIQUE INDEX playerSeat_idx ON HandsPlayers (handId, seatNo)"""
        elif db_server == 'sqlite':
            self.query['addPlayersSeat'] = """CREATE UNIQUE INDEX playerSeat_idx ON HandsPlayers (handId, seatNo)"""
             
        if db_server == 'mysql':
            self.query['addHeroSeat'] = """ALTER TABLE Hands ADD UNIQUE INDEX heroSeat_idx(id, heroSeat)"""
        elif db_server == 'postgresql':
            self.query['addHeroSeat'] = """CREATE UNIQUE INDEX heroSeat_idx ON Hands (id, heroSeat)"""
        elif db_server == 'sqlite':
            self.query['addHeroSeat'] = """CREATE UNIQUE INDEX heroSeat_idx ON Hands (id, heroSeat)"""
            
        if db_server == 'mysql':
            self.query['addHandsPlayersSeat'] = """ALTER TABLE HandsPlayers ADD UNIQUE INDEX handsPlayerSeat_idx(handId, seatNo)"""
        elif db_server == 'postgresql':
            self.query['addHandsPlayersSeat'] = """CREATE UNIQUE INDEX handsPlayerSeat_idx ON Hands (handId, seatNo)"""
        elif db_server == 'sqlite':
            self.query['addHandsPlayersSeat'] = """CREATE UNIQUE INDEX handsPlayerSeat_idx ON Hands (handId, seatNo)"""

        if db_server == 'mysql':
            self.query['addPlayersIndex'] = """ALTER TABLE Players ADD UNIQUE INDEX name(name, siteId)"""
        elif db_server == 'postgresql':
            self.query['addPlayersIndex'] = """CREATE UNIQUE INDEX name ON Players (name, siteId)"""
        elif db_server == 'sqlite':
            self.query['addPlayersIndex'] = """CREATE UNIQUE INDEX name ON Players (name, siteId)"""

        if db_server == 'mysql':
            self.query['addTPlayersIndex'] = """ALTER TABLE TourneysPlayers ADD UNIQUE INDEX _tourneyId(tourneyId, playerId, entryId)"""
        elif db_server == 'postgresql':
            self.query['addTPlayersIndex'] = """CREATE UNIQUE INDEX tourneyId ON TourneysPlayers (tourneyId, playerId, entryId)"""
        elif db_server == 'sqlite':
            self.query['addTPlayersIndex'] = """CREATE UNIQUE INDEX tourneyId ON TourneysPlayers (tourneyId, playerId, entryId)"""
            
        if db_server == 'mysql':
            self.query['addStartCardsIndex'] = """ALTER TABLE StartCards ADD UNIQUE INDEX cards_idx (category, rank)"""
        elif db_server == 'postgresql':
            self.query['addStartCardsIndex'] = """CREATE UNIQUE INDEX cards_idx ON StartCards (category, rank)"""
        elif db_server == 'sqlite':
            self.query['addStartCardsIndex'] = """CREATE UNIQUE INDEX cards_idx ON StartCards (category, rank)"""
            
        if db_server == 'mysql':
            self.query['addSeatsIndex'] = """ALTER TABLE Hands ADD INDEX seats_idx (seats)"""
        elif db_server == 'postgresql':
            self.query['addSeatsIndex'] = """CREATE INDEX seats_idx ON Hands (seats)"""
        elif db_server == 'sqlite':
            self.query['addSeatsIndex'] = """CREATE INDEX seats_idx ON Hands (seats)"""
            
        if db_server == 'mysql':
            self.query['addPositionIndex'] = """ALTER TABLE HandsPlayers ADD INDEX position_idx (position)"""
        elif db_server == 'postgresql':
            self.query['addPositionIndex'] = """CREATE INDEX position_idx ON HandsPlayers (position)"""
        elif db_server == 'sqlite':
            self.query['addPositionIndex'] = """CREATE INDEX position_idx ON HandsPlayers (position)"""
            
        if db_server == 'mysql':
            self.query['addStartCashIndex'] = """ALTER TABLE HandsPlayers ADD INDEX cash_idx (startCash)"""
        elif db_server == 'postgresql':
            self.query['addStartCashIndex'] = """CREATE INDEX cash_idx ON HandsPlayers (startCash)"""
        elif db_server == 'sqlite':
            self.query['addStartCashIndex'] = """CREATE INDEX cash_idx ON HandsPlayers (startCash)"""
            
        if db_server == 'mysql':
            self.query['addEffStackIndex'] = """ALTER TABLE HandsPlayers ADD INDEX eff_stack_idx (effStack)"""
        elif db_server == 'postgresql':
            self.query['addEffStackIndex'] = """CREATE INDEX eff_stack_idx ON HandsPlayers (effStack)"""
        elif db_server == 'sqlite':
            self.query['addEffStackIndex'] = """CREATE INDEX eff_stack_idx ON HandsPlayers (effStack)"""
            
        if db_server == 'mysql':
            self.query['addTotalProfitIndex'] = """ALTER TABLE HandsPlayers ADD INDEX profit_idx (totalProfit)"""
        elif db_server == 'postgresql':
            self.query['addTotalProfitIndex'] = """CREATE INDEX profit_idx ON HandsPlayers (totalProfit)"""
        elif db_server == 'sqlite':
            self.query['addTotalProfitIndex'] = """CREATE INDEX profit_idx ON HandsPlayers (totalProfit)"""
            
        if db_server == 'mysql':
            self.query['addWinningsIndex'] = """ALTER TABLE HandsPlayers ADD INDEX winnings_idx (winnings)"""
        elif db_server == 'postgresql':
            self.query['addWinningsIndex'] = """CREATE INDEX winnings_idx ON HandsPlayers (winnings)"""
        elif db_server == 'sqlite':
            self.query['addWinningsIndex'] = """CREATE INDEX winnings_idx ON HandsPlayers (winnings)"""
            
        if db_server == 'mysql':
            self.query['addFinalPotIndex'] = """ALTER TABLE Hands ADD INDEX pot_idx (finalPot)"""
        elif db_server == 'postgresql':
            self.query['addFinalPotIndex'] = """CREATE INDEX pot_idx ON Hands (finalPot)"""
        elif db_server == 'sqlite':
            self.query['addFinalPotIndex'] = """CREATE INDEX pot_idx ON Hands (finalPot)"""
            
        if db_server == 'mysql':
            self.query['addStreetIndex'] = """ALTER TABLE HandsStove ADD INDEX street_idx (streetId, boardId)"""
        elif db_server == 'postgresql':
            self.query['addStreetIndex'] = """CREATE INDEX street_idx ON HandsStove (streetId, boardId)"""
        elif db_server == 'sqlite':
            self.query['addStreetIndex'] = """CREATE INDEX street_idx ON HandsStove (streetId, boardId)"""

        self.query['addSessionsCacheCompundIndex'] = """CREATE INDEX SessionsCache_Compound_idx ON SessionsCache(gametypeId, playerId)"""
        self.query['addTourneysCacheCompundIndex'] = """CREATE UNIQUE INDEX TourneysCache_Compound_idx ON TourneysCache(tourneyId, playerId)"""
        self.query['addHudCacheCompundIndex'] = """CREATE UNIQUE INDEX HudCache_Compound_idx ON HudCache(gametypeId, playerId, seats, position, tourneyTypeId, styleKey)"""
        
        self.query['addCardsCacheCompundIndex'] = """CREATE UNIQUE INDEX CardsCache_Compound_idx ON CardsCache(weekId, monthId, gametypeId, tourneyTypeId, playerId, startCards)"""
        self.query['addPositionsCacheCompundIndex'] = """CREATE UNIQUE INDEX PositionsCache_Compound_idx ON PositionsCache(weekId, monthId, gametypeId, tourneyTypeId, playerId, seats, maxPosition, position)"""

        # (left(file, 255)) is not valid syntax on postgres psycopg2 on windows (postgres v8.4)
        # error thrown is HINT:  "No function matches the given name and argument types. You might need to add explicit type casts."
        # so we will just create the index with the full filename.
        if db_server == 'mysql':
            self.query['addFilesIndex'] = """CREATE UNIQUE INDEX index_file ON Files (file(255))"""
        elif db_server == 'postgresql':
            self.query['addFilesIndex'] = """CREATE UNIQUE INDEX index_file ON Files (file)"""
        elif db_server == 'sqlite':
            self.query['addFilesIndex'] = """CREATE UNIQUE INDEX index_file ON Files (file)"""
            
        self.query['addTableNameIndex'] = """CREATE INDEX index_tableName ON Hands (tableName)"""
        self.query['addPlayerNameIndex'] = """CREATE INDEX index_playerName ON Players (name)"""        
        self.query['addPlayerHeroesIndex'] = """CREATE INDEX player_heroes ON Players (hero)"""
        
        self.query['get_last_hand'] = "select max(id) from Hands"
        
        self.query['get_last_date'] = "SELECT MAX(startTime) FROM Hands"
        
        self.query['get_first_date'] = "SELECT MIN(startTime) FROM Hands"

        self.query['get_player_id'] = """
                select Players.id AS player_id 
                from Players, Sites
                where Players.name = %s
                and Sites.name = %s
                and Players.siteId = Sites.id
            """

        self.query['get_player_names'] = """
                select p.name
                from Players p
                where lower(p.name) like lower(%s)
                and   (p.siteId = %s or %s = -1)
            """

        self.query['get_gameinfo_from_hid'] = """
                SELECT
                        s.name,
                        g.category,
                        g.base,
                        g.type,
                        g.limitType,
                        g.hilo,
                        round(g.smallBlind / 100.0,2),
                        round(g.bigBlind / 100.0,2),
                        round(g.smallBet / 100.0,2),
                        round(g.bigBet / 100.0,2),
                        g.currency,
                        h.gametypeId
                    FROM
                        Hands as h,
                        Sites as s,
                        Gametypes as g,
                        HandsPlayers as hp,
                        Players as p
                    WHERE
                        h.id = %s
                    and g.id = h.gametypeId
                    and hp.handId = h.id
                    and p.id = hp.playerId
                    and s.id = p.siteId
                    limit 1
            """

        self.query['get_stats_from_hand'] = """
                SELECT hc.playerId                      AS player_id,
                    hp.seatNo                           AS seat,
                    p.name                              AS screen_name,
                    sum(hc.n)                           AS n,
                    sum(hc.street0VPIChance)            AS vpip_opp,
                    sum(hc.street0VPI)                  AS vpip,
                    sum(hc.street0AggrChance)           AS pfr_opp,
                    sum(hc.street0Aggr)                 AS pfr,
                    sum(hc.street0CalledRaiseChance)    AS CAR_opp_0,
                    sum(hc.street0CalledRaiseDone)      AS CAR_0,
                    sum(hc.street0_3BChance)            AS TB_opp_0,
                    sum(hc.street0_3BDone)              AS TB_0,
                    sum(hc.street0_4BChance)            AS FB_opp_0,
                    sum(hc.street0_4BDone)              AS FB_0,
                    sum(hc.street0_C4BChance)           AS CFB_opp_0,
                    sum(hc.street0_C4BDone)             AS CFB_0,
                    sum(hc.street0_FoldTo3BChance)      AS F3B_opp_0,
                    sum(hc.street0_FoldTo3BDone)        AS F3B_0,
                    sum(hc.street0_FoldTo4BChance)      AS F4B_opp_0,
                    sum(hc.street0_FoldTo4BDone)        AS F4B_0,
                    sum(hc.street0_SqueezeChance)       AS SQZ_opp_0,
                    sum(hc.street0_SqueezeDone)         AS SQZ_0,
                    sum(hc.raiseToStealChance)          AS RTS_opp,
                    sum(hc.raiseToStealDone)            AS RTS,
                    sum(hc.success_Steal)               AS SUC_ST,
                    sum(hc.street1Seen)                 AS saw_f,
                    sum(hc.street1Seen)                 AS saw_1,
                    sum(hc.street2Seen)                 AS saw_2,
                    sum(hc.street3Seen)                 AS saw_3,
                    sum(hc.street4Seen)                 AS saw_4,
                    sum(hc.sawShowdown)                 AS sd,
                    sum(hc.street1Aggr)                 AS aggr_1,
                    sum(hc.street2Aggr)                 AS aggr_2,
                    sum(hc.street3Aggr)                 AS aggr_3,
                    sum(hc.street4Aggr)                 AS aggr_4,
                    sum(hc.otherRaisedStreet1)          AS was_raised_1,
                    sum(hc.otherRaisedStreet2)          AS was_raised_2,
                    sum(hc.otherRaisedStreet3)          AS was_raised_3,
                    sum(hc.otherRaisedStreet4)          AS was_raised_4,
                    sum(hc.foldToOtherRaisedStreet1)    AS f_freq_1,
                    sum(hc.foldToOtherRaisedStreet2)    AS f_freq_2,
                    sum(hc.foldToOtherRaisedStreet3)    AS f_freq_3,
                    sum(hc.foldToOtherRaisedStreet4)    AS f_freq_4,
                    sum(hc.wonWhenSeenStreet1)          AS w_w_s_1,
                    sum(hc.wonAtSD)                     AS wmsd,
                    sum(hc.stealChance)                 AS steal_opp,
                    sum(hc.stealDone)                   AS steal,
                    sum(hc.foldSbToStealChance)         AS SBstolen,
                    sum(hc.foldedSbToSteal)             AS SBnotDef,
                    sum(hc.foldBbToStealChance)         AS BBstolen,
                    sum(hc.foldedBbToSteal)             AS BBnotDef,
                    sum(hc.street1CBChance)             AS CB_opp_1,
                    sum(hc.street1CBDone)               AS CB_1,
                    sum(hc.street2CBChance)             AS CB_opp_2,
                    sum(hc.street2CBDone)               AS CB_2,
                    sum(hc.street3CBChance)             AS CB_opp_3,
                    sum(hc.street3CBDone)               AS CB_3,
                    sum(hc.street4CBChance)             AS CB_opp_4,
                    sum(hc.street4CBDone)               AS CB_4,
                    sum(hc.foldToStreet1CBChance)       AS f_cb_opp_1,
                    sum(hc.foldToStreet1CBDone)         AS f_cb_1,
                    sum(hc.foldToStreet2CBChance)       AS f_cb_opp_2,
                    sum(hc.foldToStreet2CBDone)         AS f_cb_2,
                    sum(hc.foldToStreet3CBChance)       AS f_cb_opp_3,
                    sum(hc.foldToStreet3CBDone)         AS f_cb_3,
                    sum(hc.foldToStreet4CBChance)       AS f_cb_opp_4,
                    sum(hc.foldToStreet4CBDone)         AS f_cb_4,
                    sum(hc.totalProfit)                 AS net,
                    sum(gt.bigblind * hc.n)             AS bigblind,
                    sum(hc.street1CheckCallRaiseChance) AS ccr_opp_1,
                    sum(hc.street1CheckCallDone)        AS cc_1,
                    sum(hc.street1CheckRaiseDone)       AS cr_1,
                    sum(hc.street2CheckCallRaiseChance) AS ccr_opp_2,
                    sum(hc.street2CheckCallDone)        AS cc_2,
                    sum(hc.street2CheckRaiseDone)       AS cr_2,
                    sum(hc.street3CheckCallRaiseChance) AS ccr_opp_3,
                    sum(hc.street3CheckCallDone)        AS cc_3,
                    sum(hc.street3CheckRaiseDone)       AS cr_3,
                    sum(hc.street4CheckCallRaiseChance) AS ccr_opp_4,
                    sum(hc.street4CheckCallDone)        AS cc_4
                    sum(hc.street4CheckRaiseDone)       AS cr_4
                    sum(hc.street0Calls)                AS call_0,
                    sum(hc.street1Calls)                AS call_1,
                    sum(hc.street2Calls)                AS call_2,
                    sum(hc.street3Calls)                AS call_3,
                    sum(hc.street4Calls)                AS call_4,
                    sum(hc.street0Bets)                 AS bet_0,
                    sum(hc.street1Bets)                 AS bet_1,
                    sum(hc.street2Bets)                 AS bet_2,
                    sum(hc.street3Bets)                 AS bet_3,
                    sum(hc.street4Bets)                 AS bet_4,
                    sum(hc.street0Raises)               AS raise_0,
                    sum(hc.street1Raises)               AS raise_1,
                    sum(hc.street2Raises)               AS raise_2,
                    sum(hc.street3Raises)               AS raise_3,
                    sum(hc.street4Raises)               AS raise_4
                FROM Hands h
                     INNER JOIN HandsPlayers hp ON (hp.handId = h.id)
                     INNER JOIN HudCache hc ON (    hc.PlayerId = hp.PlayerId+0
                                                AND hc.gametypeId+0 = h.gametypeId+0)
                     INNER JOIN Players p ON (p.id = hp.PlayerId+0)
                     INNER JOIN Gametypes gt ON (gt.id = hc.gametypeId)
                WHERE h.id = %s
                AND   hc.styleKey > %s
                      /* styleKey is currently 'd' (for date) followed by a yyyymmdd
                         date key. Set it to 0000000 or similar to get all records  */
                /* also check activeseats here even if only 3 groups eg 2-3/4-6/7+ 
                   e.g. could use a multiplier:
                   AND   h.seats > X / 1.25  and  hp.seats < X * 1.25
                   where X is the number of active players at the current table (and
                   1.25 would be a config value so user could change it)
                */
                GROUP BY hc.PlayerId, hp.seatNo, p.name
                ORDER BY hc.PlayerId, hp.seatNo, p.name
            """

#    same as above except stats are aggregated for all blind/limit levels
        self.query['get_stats_from_hand_aggregated'] = """
                /* explain query plan */
                SELECT hc.playerId                         AS player_id,
                       max(case when hc.gametypeId = h.gametypeId
                                then hp.seatNo
                                else -1
                           end)                            AS seat,
                       p.name                              AS screen_name,
                       sum(hc.n)                           AS n,
                       sum(hc.street0VPIChance)            AS vpip_opp,
                       sum(hc.street0VPI)                  AS vpip,
                       sum(hc.street0AggrChance)           AS pfr_opp,
                       sum(hc.street0Aggr)                 AS pfr,
                       sum(hc.street0CalledRaiseChance)    AS CAR_opp_0,
                       sum(hc.street0CalledRaiseDone)      AS CAR_0,
                       sum(hc.street0_3BChance)            AS TB_opp_0,
                       sum(hc.street0_3BDone)              AS TB_0,
                       sum(hc.street0_4BChance)            AS FB_opp_0,
                       sum(hc.street0_4BDone)              AS FB_0,
                       sum(hc.street0_C4BChance)           AS CFB_opp_0,
                       sum(hc.street0_C4BDone)             AS CFB_0,
                       sum(hc.street0_FoldTo3BChance)      AS F3B_opp_0,
                       sum(hc.street0_FoldTo3BDone)        AS F3B_0,
                       sum(hc.street0_FoldTo4BChance)      AS F4B_opp_0,
                       sum(hc.street0_FoldTo4BDone)        AS F4B_0,
                       sum(hc.street0_SqueezeChance)       AS SQZ_opp_0,
                       sum(hc.street0_SqueezeDone)         AS SQZ_0,
                       sum(hc.raiseToStealChance)          AS RTS_opp,
                       sum(hc.raiseToStealDone)            AS RTS,
                       sum(hc.success_Steal)               AS SUC_ST,
                       sum(hc.street1Seen)                 AS saw_f,
                       sum(hc.street1Seen)                 AS saw_1,
                       sum(hc.street2Seen)                 AS saw_2,
                       sum(hc.street3Seen)                 AS saw_3,
                       sum(hc.street4Seen)                 AS saw_4,
                       sum(hc.sawShowdown)                 AS sd,
                       sum(hc.street1Aggr)                 AS aggr_1,
                       sum(hc.street2Aggr)                 AS aggr_2,
                       sum(hc.street3Aggr)                 AS aggr_3,
                       sum(hc.street4Aggr)                 AS aggr_4,
                       sum(hc.otherRaisedStreet1)          AS was_raised_1,
                       sum(hc.otherRaisedStreet2)          AS was_raised_2,
                       sum(hc.otherRaisedStreet3)          AS was_raised_3,
                       sum(hc.otherRaisedStreet4)          AS was_raised_4,
                       sum(hc.foldToOtherRaisedStreet1)    AS f_freq_1,
                       sum(hc.foldToOtherRaisedStreet2)    AS f_freq_2,
                       sum(hc.foldToOtherRaisedStreet3)    AS f_freq_3,
                       sum(hc.foldToOtherRaisedStreet4)    AS f_freq_4,
                       sum(hc.wonWhenSeenStreet1)          AS w_w_s_1,
                       sum(hc.wonAtSD)                     AS wmsd,
                       sum(hc.stealChance)                 AS steal_opp,
                       sum(hc.stealDone)                   AS steal,
                       sum(hc.foldSbToStealChance)         AS SBstolen,
                       sum(hc.foldedSbToSteal)             AS SBnotDef,
                       sum(hc.foldBbToStealChance)         AS BBstolen,
                       sum(hc.foldedBbToSteal)             AS BBnotDef,
                       sum(hc.street1CBChance)             AS CB_opp_1,
                       sum(hc.street1CBDone)               AS CB_1,
                       sum(hc.street2CBChance)             AS CB_opp_2,
                       sum(hc.street2CBDone)               AS CB_2,
                       sum(hc.street3CBChance)             AS CB_opp_3,
                       sum(hc.street3CBDone)               AS CB_3,
                       sum(hc.street4CBChance)             AS CB_opp_4,
                       sum(hc.street4CBDone)               AS CB_4,
                       sum(hc.foldToStreet1CBChance)       AS f_cb_opp_1,
                       sum(hc.foldToStreet1CBDone)         AS f_cb_1,
                       sum(hc.foldToStreet2CBChance)       AS f_cb_opp_2,
                       sum(hc.foldToStreet2CBDone)         AS f_cb_2,
                       sum(hc.foldToStreet3CBChance)       AS f_cb_opp_3,
                       sum(hc.foldToStreet3CBDone)         AS f_cb_3,
                       sum(hc.foldToStreet4CBChance)       AS f_cb_opp_4,
                       sum(hc.foldToStreet4CBDone)         AS f_cb_4,
                       sum(hc.totalProfit)                 AS net,
                       sum(gt.bigblind * hc.n)             AS bigblind,
                       sum(hc.street1CheckCallRaiseChance) AS ccr_opp_1,
                       sum(hc.street1CheckCallDone)        AS cc_1,
                       sum(hc.street1CheckRaiseDone)       AS cr_1,
                       sum(hc.street2CheckCallRaiseChance) AS ccr_opp_2,
                       sum(hc.street2CheckCallDone)        AS cc_2,
                       sum(hc.street2CheckRaiseDone)       AS cr_2,
                       sum(hc.street3CheckCallRaiseChance) AS ccr_opp_3,
                       sum(hc.street3CheckCallDone)        AS cc_3,
                       sum(hc.street3CheckRaiseDone)       AS cr_3,
                       sum(hc.street4CheckCallRaiseChance) AS ccr_opp_4,
                       sum(hc.street4CheckCallDone)        AS cc_4,
                       sum(hc.street4CheckRaiseDone)       AS cr_4,
                       sum(hc.street0Calls)                AS call_0,
                       sum(hc.street1Calls)                AS call_1,
                       sum(hc.street2Calls)                AS call_2,
                       sum(hc.street3Calls)                AS call_3,
                       sum(hc.street4Calls)                AS call_4,
                       sum(hc.street0Bets)                 AS bet_0,
                       sum(hc.street1Bets)                 AS bet_1,
                       sum(hc.street2Bets)                 AS bet_2,
                       sum(hc.street3Bets)                 AS bet_3,
                       sum(hc.street4Bets)                 AS bet_4,
                       sum(hc.street0Raises)               AS raise_0,
                       sum(hc.street1Raises)               AS raise_1,
                       sum(hc.street2Raises)               AS raise_2,
                       sum(hc.street3Raises)               AS raise_3,
                       sum(hc.street4Raises)               AS raise_4
                FROM Hands h
                     INNER JOIN HandsPlayers hp ON (hp.handId = h.id)
                     INNER JOIN HudCache hc     ON (hc.playerId = hp.playerId)
                     INNER JOIN Players p       ON (p.id = hc.playerId)
                     INNER JOIN Gametypes gt    ON (gt.id = hc.gametypeId)
                WHERE h.id = %s
                AND   (   /* 2 separate parts for hero and opponents */
                          (    hp.playerId != %s
                           AND hc.styleKey > %s
                           AND hc.gametypeId+0 in
                                 (SELECT gt1.id from Gametypes gt1, Gametypes gt2
                                  WHERE  gt1.siteid = gt2.siteid  /* find gametypes where these match: */
                                  AND    gt1.type = gt2.type               /* ring/tourney */
                                  AND    gt1.category = gt2.category       /* holdem/stud*/
                                  AND    gt1.limittype = gt2.limittype     /* fl/nl */
                                  AND    gt1.bigblind <= gt2.bigblind * %s  /* bigblind similar size */
                                  AND    gt1.bigblind >= gt2.bigblind / %s
                                  AND    gt2.id = %s)
                           AND hc.seats between %s and %s
                          )
                       OR
                          (    hp.playerId = %s
                           AND hc.styleKey > %s
                           AND hc.gametypeId+0 in
                                 (SELECT gt1.id from Gametypes gt1, Gametypes gt2
                                  WHERE  gt1.siteid = gt2.siteid  /* find gametypes where these match: */
                                  AND    gt1.type = gt2.type               /* ring/tourney */
                                  AND    gt1.category = gt2.category       /* holdem/stud*/
                                  AND    gt1.limittype = gt2.limittype     /* fl/nl */
                                  AND    gt1.bigblind <= gt2.bigblind * %s  /* bigblind similar size */
                                  AND    gt1.bigblind >= gt2.bigblind / %s
                                  AND    gt2.id = %s)
                           AND hc.seats between %s and %s
                          )
                      )
                GROUP BY hc.PlayerId, p.name
                ORDER BY hc.PlayerId, p.name
            """
                #  NOTES on above cursor:
                #  - Do NOT include %s inside query in a comment - the db api thinks 
                #  they are actual arguments.
                #  - styleKey is currently 'd' (for date) followed by a yyyymmdd
                #  date key. Set it to 0000000 or similar to get all records
                #  Could also check activeseats here even if only 3 groups eg 2-3/4-6/7+ 
                #  e.g. could use a multiplier:
                #  AND   h.seats > %s / 1.25  and  hp.seats < %s * 1.25
                #  where %s is the number of active players at the current table (and
                #  1.25 would be a config value so user could change it)

        if db_server == 'mysql':
            self.query['get_stats_from_hand_session'] = """
                    SELECT hp.playerId                                              AS player_id, /* playerId and seats must */
                           h.seats                                                  AS seats,     /* be first and second field */
                           hp.handId                                                AS hand_id,
                           hp.seatNo                                                AS seat,
                           p.name                                                   AS screen_name,
                           1                                                        AS n,
                           cast(hp2.street0VPIChance as <signed>integer)            AS vpip_opp,
                           cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                           cast(hp2.street0AggrChance as <signed>integer)           AS pfr_opp,
                           cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                           cast(hp2.street0CalledRaiseChance as <signed>integer)    AS CAR_opp_0,
                           cast(hp2.street0CalledRaiseDone as <signed>integer)      AS CAR_0,
                           cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                           cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                           cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                           cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                           cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                           cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                           cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                           cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                           cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                           cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                           cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                           cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                           cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                           cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                           cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                           cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                           cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                           cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                           cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                           cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                           cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                           cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                           cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                           cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                           cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                           cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                           cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                           cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                           cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                           cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                           cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                           cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                           cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                           cast(hp2.stealChance as <signed>integer)                 AS steal_opp,
                           cast(hp2.stealDone as <signed>integer)                   AS steal,
                           cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                           cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                           cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                           cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                           cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                           cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                           cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                           cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                           cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                           cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                           cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                           cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                           cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                           cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                           cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                           cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                           cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                           cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                           cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                           cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                           cast(hp2.totalProfit as <signed>bigint)                  AS net,
                           cast(gt.bigblind as <signed>bigint)                      AS bigblind,
                           cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                           cast(hp2.street1CheckCallDone as <signed>integer)        AS cc_1,
                           cast(hp2.street1CheckRaiseDone as <signed>integer)       AS cr_1,
                           cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                           cast(hp2.street2CheckCallDone as <signed>integer)        AS cc_2,
                           cast(hp2.street2CheckRaiseDone as <signed>integer)       AS cr_2,
                           cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                           cast(hp2.street3CheckCallDone as <signed>integer)        AS cc_3,
                           cast(hp2.street3CheckRaiseDone as <signed>integer)       AS cr_3,
                           cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                           cast(hp2.street4CheckCallDone as <signed>integer)        AS cc_4,
                           cast(hp2.street4CheckRaiseDone as <signed>integer)       AS cr_4,
                           cast(hp2.street0Calls as <signed>integer)                AS call_0,
                           cast(hp2.street1Calls as <signed>integer)                AS call_1,
                           cast(hp2.street2Calls as <signed>integer)                AS call_2,
                           cast(hp2.street3Calls as <signed>integer)                AS call_3,
                           cast(hp2.street4Calls as <signed>integer)                AS call_4,
                           cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                           cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                           cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                           cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                           cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                           cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                           cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                           cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                           cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                           cast(hp2.street4Raises as <signed>integer)               AS raise_4
                    FROM
                         Hands h
                         INNER JOIN Hands h2         ON (h2.id >= %s AND   h2.tableName = h.tableName)
                         INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)         /* players in this hand */
                         INNER JOIN HandsPlayers hp2 ON (hp2.playerId+0 = hp.playerId+0 AND (hp2.handId = h2.id+0))  /* other hands by these players */
                         INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                         INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                    WHERE hp.handId = %s
                    /* check activeseats once this data returned (don't want to do that here as it might
                       assume a session ended just because the number of seats dipped for a few hands)
                    */
                    AND   (   /* 2 separate parts for hero and opponents */
                              (    hp2.playerId != %s
                               AND h2.seats between %s and %s
                              )
                           OR
                              (    hp2.playerId = %s
                               AND h2.seats between %s and %s
                              )
                          )
                    ORDER BY h.startTime desc, hp2.PlayerId
                    /* order rows by handstart descending so that we can stop reading rows when
                       there's a gap over X minutes between hands (ie. when we get back to start of
                       the session */
                """
        elif db_server == 'postgresql':
            self.query['get_stats_from_hand_session'] = """
                    SELECT hp.playerId                                              AS player_id,
                           hp.handId                                                AS hand_id,
                           hp.seatNo                                                AS seat,
                           p.name                                                   AS screen_name,
                           h.seats                                                  AS seats,
                           1                                                        AS n,
                           cast(hp2.street0VPIChance as <signed>integer)            AS vpip_opp,
                           cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                           cast(hp2.street0AggrChance as <signed>integer)           AS pfr_opp,
                           cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                           cast(hp2.street0CalledRaiseChance as <signed>integer)    AS CAR_opp_0,
                           cast(hp2.street0CalledRaiseDone as <signed>integer)      AS CAR_0,
                           cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                           cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                           cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                           cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                           cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                           cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                           cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                           cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                           cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                           cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                           cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                           cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                           cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                           cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                           cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                           cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                           cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                           cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                           cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                           cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                           cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                           cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                           cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                           cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                           cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                           cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                           cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                           cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                           cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                           cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                           cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                           cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                           cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                           cast(hp2.stealChance as <signed>integer)                 AS steal_opp,
                           cast(hp2.stealDone as <signed>integer)                   AS steal,
                           cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                           cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                           cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                           cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                           cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                           cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                           cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                           cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                           cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                           cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                           cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                           cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                           cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                           cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                           cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                           cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                           cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                           cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                           cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                           cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                           cast(hp2.totalProfit as <signed>bigint)                  AS net,
                           cast(gt.bigblind as <signed>bigint)                      AS bigblind,
                           cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                           cast(hp2.street1CheckCallDone as <signed>integer)        AS cc_1,
                           cast(hp2.street1CheckRaiseDone as <signed>integer)       AS cr_1,
                           cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                           cast(hp2.street2CheckCallDone as <signed>integer)        AS cc_2,
                           cast(hp2.street2CheckRaiseDone as <signed>integer)       AS cr_2,
                           cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                           cast(hp2.street3CheckCallDone as <signed>integer)        AS cc_3,
                           cast(hp2.street3CheckRaiseDone as <signed>integer)       AS cr_3,
                           cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                           cast(hp2.street4CheckCallDone as <signed>integer)        AS cc_4,
                           cast(hp2.street4CheckRaiseDone as <signed>integer)       AS cr_4,
                           cast(hp2.street0Calls as <signed>integer)                AS call_0,
                           cast(hp2.street1Calls as <signed>integer)                AS call_1,
                           cast(hp2.street2Calls as <signed>integer)                AS call_2,
                           cast(hp2.street3Calls as <signed>integer)                AS call_3,
                           cast(hp2.street4Calls as <signed>integer)                AS call_4,
                           cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                           cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                           cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                           cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                           cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                           cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                           cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                           cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                           cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                           cast(hp2.street4Raises as <signed>integer)               AS raise_4
                         FROM Hands h                                                  /* this hand */
                         INNER JOIN Hands h2         ON (    h2.id >= %s           /* other hands */
                                                         AND h2.tableName = h.tableName)
                         INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)        /* players in this hand */
                         INNER JOIN HandsPlayers hp2 ON (    hp2.playerId+0 = hp.playerId+0
                                                         AND hp2.handId = h2.id)  /* other hands by these players */
                         INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                         INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                    WHERE h.id = %s
                    /* check activeseats once this data returned (don't want to do that here as it might
                       assume a session ended just because the number of seats dipped for a few hands)
                    */
                    AND   (   /* 2 separate parts for hero and opponents */
                              (    hp2.playerId != %s
                               AND h2.seats between %s and %s
                              )
                           OR
                              (    hp2.playerId = %s
                               AND h2.seats between %s and %s
                              )
                          )
                    ORDER BY h.startTime desc, hp2.PlayerId
                    /* order rows by handstart descending so that we can stop reading rows when
                       there's a gap over X minutes between hands (ie. when we get back to start of
                       the session */
                """
        elif db_server == 'sqlite':
            self.query['get_stats_from_hand_session'] = """
                    SELECT hp.playerId                                              AS player_id,
                           hp.handId                                                AS hand_id,
                           hp.seatNo                                                AS seat,
                           p.name                                                   AS screen_name,
                           h.seats                                                  AS seats,
                           1                                                        AS n,
                           cast(hp2.street0VPIChance as <signed>integer)            AS vpip_opp,
                           cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                           cast(hp2.street0AggrChance as <signed>integer)           AS pfr_opp,
                           cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                           cast(hp2.street0CalledRaiseChance as <signed>integer)    AS CAR_opp_0,
                           cast(hp2.street0CalledRaiseDone as <signed>integer)      AS CAR_0,
                           cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                           cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                           cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                           cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                           cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                           cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                           cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                           cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                           cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                           cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                           cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                           cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                           cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                           cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                           cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                           cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                           cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                           cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                           cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                           cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                           cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                           cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                           cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                           cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                           cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                           cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                           cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                           cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                           cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                           cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                           cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                           cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                           cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                           cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                           cast(hp2.stealChance as <signed>integer)                 AS steal_opp,
                           cast(hp2.stealDone as <signed>integer)                   AS steal,
                           cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                           cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                           cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                           cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                           cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                           cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                           cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                           cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                           cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                           cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                           cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                           cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                           cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                           cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                           cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                           cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                           cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                           cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                           cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                           cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                           cast(hp2.totalProfit as <signed>integer)                 AS net,
                           cast(gt.bigblind as <signed>integer)                     AS bigblind,
                           cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                           cast(hp2.street1CheckCallDone as <signed>integer)        AS cc_1,
                           cast(hp2.street1CheckRaiseDone as <signed>integer)       AS cr_1,
                           cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                           cast(hp2.street2CheckCallDone as <signed>integer)        AS cc_2,
                           cast(hp2.street2CheckRaiseDone as <signed>integer)       AS cr_2,
                           cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                           cast(hp2.street3CheckCallDone as <signed>integer)        AS cc_3,
                           cast(hp2.street3CheckRaiseDone as <signed>integer)       AS cr_3,
                           cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                           cast(hp2.street4CheckCallDone as <signed>integer)        AS cc_4,
                           cast(hp2.street4CheckRaiseDone as <signed>integer)       AS cr_4,
                           cast(hp2.street0Calls as <signed>integer)                AS call_0,
                           cast(hp2.street1Calls as <signed>integer)                AS call_1,
                           cast(hp2.street2Calls as <signed>integer)                AS call_2,
                           cast(hp2.street3Calls as <signed>integer)                AS call_3,
                           cast(hp2.street4Calls as <signed>integer)                AS call_4,
                           cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                           cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                           cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                           cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                           cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                           cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                           cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                           cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                           cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                           cast(hp2.street4Raises as <signed>integer)               AS raise_4
                         FROM Hands h                                                  /* this hand */
                         INNER JOIN Hands h2         ON (    h2.id >= %s           /* other hands */
                                                         AND h2.tableName = h.tableName)
                         INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)        /* players in this hand */
                         INNER JOIN HandsPlayers hp2 ON (    hp2.playerId+0 = hp.playerId+0
                                                         AND hp2.handId = h2.id)  /* other hands by these players */
                         INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                         INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                    WHERE h.id = %s
                    /* check activeseats once this data returned (don't want to do that here as it might
                       assume a session ended just because the number of seats dipped for a few hands)
                    */
                    AND   (   /* 2 separate parts for hero and opponents */
                              (    hp2.playerId != %s
                               AND h2.seats between %s and %s
                              )
                           OR
                              (    hp2.playerId = %s
                               AND h2.seats between %s and %s
                              )
                          )
                    ORDER BY h.startTime desc, hp2.PlayerId
                    /* order rows by handstart descending so that we can stop reading rows when
                       there's a gap over X minutes between hands (ie. when we get back to start of
                       the session */
                """
     
        self.query['get_players_from_hand'] = """
                SELECT HandsPlayers.playerId, seatNo, name
                FROM  HandsPlayers INNER JOIN Players ON (HandsPlayers.playerId = Players.id)
                WHERE handId = %s
            """
#                    WHERE handId = %s AND Players.id LIKE %s

        self.query['get_winners_from_hand'] = """
                SELECT name, winnings
                FROM HandsPlayers, Players
                WHERE winnings > 0
                    AND Players.id = HandsPlayers.playerId
                    AND handId = %s;
            """

        self.query['get_table_name'] = """
                SELECT h.tableName, gt.maxSeats, gt.category, gt.type, gt.fast, s.id, s.name
                     , count(1) as numseats
                FROM Hands h, Gametypes gt, Sites s, HandsPlayers hp
                WHERE h.id = %s
                    AND   gt.id = h.gametypeId
                    AND   s.id = gt.siteID
                    AND   hp.handId = h.id
                GROUP BY h.tableName, gt.maxSeats, gt.category, gt.type, gt.fast, s.id, s.name
            """

        self.query['get_actual_seat'] = """
                select seatNo
                from HandsPlayers
                where HandsPlayers.handId = %s
                and   HandsPlayers.playerId  = (select Players.id from Players
                                                where Players.name = %s)
            """

        self.query['get_cards'] = """
/*
    changed to activate mucked card display in draw games
    in draw games, card6->card20 contain 3 sets of 5 cards at each draw

    CASE code searches from the highest card number (latest draw) and when
    it finds a non-zero card, it returns that set of data
*/
            SELECT
                seatNo AS seat_number,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card16,0), NULLIF(card11,0), NULLIF(card6,0), card1)
                    else card1
                end card1,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card17,0), NULLIF(card12,0), NULLIF(card7,0), card2)
                    else card2
                end card2,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card18,0), NULLIF(card13,0), NULLIF(card8,0), card3)
                    else card3
                end card3,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card19,0), NULLIF(card14,0), NULLIF(card9,0), card4)
                    else card4
                end card4,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card20,0), NULLIF(card15,0), NULLIF(card10,0), card5)
                    else card5
                end card5,
                CASE Gametypes.base
                    when 'draw' then 0
                    else card6
                end card6,
                CASE Gametypes.base
                    when 'draw' then 0
                    else card7
                end card7

                FROM HandsPlayers, Hands, Gametypes
                WHERE handID = %s
                 AND HandsPlayers.handId=Hands.id
                 AND Hands.gametypeId = Gametypes.id
                ORDER BY seatNo
            """

        self.query['get_common_cards'] = """
                select
                boardcard1,
                boardcard2,
                boardcard3,
                boardcard4,
                boardcard5
                from Hands
                where Id = %s
            """

        if db_server == 'mysql':
            self.query['get_hand_1day_ago'] = """
                select coalesce(max(id),0)
                from Hands
                where startTime < date_sub(utc_timestamp(), interval '1' day)"""
        elif db_server == 'postgresql':
            self.query['get_hand_1day_ago'] = """
                select coalesce(max(id),0)
                from Hands
                where startTime < now() at time zone 'UTC' - interval '1 day'"""
        elif db_server == 'sqlite':
            self.query['get_hand_1day_ago'] = """
                select coalesce(max(id),0)
                from Hands
                where startTime < datetime(strftime('%J', 'now') - 1)"""

        # not used yet ...
        # gets a date, would need to use handsplayers (not hudcache) to get exact hand Id
        if db_server == 'mysql':
            self.query['get_date_nhands_ago'] = """
                select concat( 'd', date_format(max(h.startTime), '%Y%m%d') )
                from (select hp.playerId
                            ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                      from HandsPlayers hp
                      where hp.playerId = %s
                      group by hp.playerId) hp2
                inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                                and hp3.playerId = hp2.playerId)
                inner join Hands h          on (h.id = hp3.handId)
                """
        elif db_server == 'postgresql':
            self.query['get_date_nhands_ago'] = """
                select 'd' || to_char(max(h3.startTime), 'YYMMDD')
                from (select hp.playerId
                            ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                      from HandsPlayers hp
                      where hp.playerId = %s
                      group by hp.playerId) hp2
                inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                                and hp3.playerId = hp2.playerId)
                inner join Hands h          on (h.id = hp3.handId)
                """
        elif db_server == 'sqlite': # untested guess at query:
            self.query['get_date_nhands_ago'] = """
                select 'd' || strftime(max(h3.startTime), 'YYMMDD')
                from (select hp.playerId
                            ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                      from HandsPlayers hp
                      where hp.playerId = %s
                      group by hp.playerId) hp2
                inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                                and hp3.playerId = hp2.playerId)
                inner join Hands h          on (h.id = hp3.handId)
                """

        # Used in *Filters:
        #self.query['getLimits'] = already defined further up
        self.query['getLimits2'] = """SELECT DISTINCT type, limitType, bigBlind 
                                      from Gametypes
                                      ORDER by type, limitType DESC, bigBlind DESC"""
        self.query['getLimits3'] = """select DISTINCT type
                                           , gt.limitType
                                           , case type
                                                 when 'ring' then bigBlind 
-                                                else buyin
-                                            end as bb_or_buyin
                                      from Gametypes gt
                                      cross join TourneyTypes tt
                                      order by type, gt.limitType DESC, bb_or_buyin DESC"""
#         self.query['getCashLimits'] = """select DISTINCT type
#                                            , limitType
#                                            , bigBlind as bb_or_buyin
#                                       from Gametypes gt
#                                       WHERE type = 'ring'
#                                       order by type, limitType DESC, bb_or_buyin DESC"""

        self.query['getCashLimits'] = """select DISTINCT type
                                           , limitType
                                           , bigBlind as bb_or_buyin
                                      from Gametypes gt
                                      WHERE type = 'ring'
                                      order by type, limitType DESC, bb_or_buyin DESC"""
                                      
        self.query['getPositions'] = """select distinct position
                                      from HandsPlayers gt
                                      order by position"""
                                      
        #FIXME: Some stats not added to DetailedStats (miss raise to steal)
        if db_server == 'mysql':
            self.query['playerDetailedStats'] = """
                     select  <hgametypeId>                                                          AS hgametypeid
                            ,<playerName>                                                           AS pname
                            ,gt.base
                            ,gt.category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            ,gt.ante                                                                AS ante
                            ,gt.currency                                                            AS currency
                            /*,<hcgametypeId>                                                         AS gtid*/
                            ,<position>                                                             AS plposition
                            ,gt.fast                                                                AS fast
                            ,count(1)                                                               AS n
                            ,case when sum(cast(hp.street0VPIChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0VPI as <signed>integer))/sum(cast(hp.street0VPIChance as <signed>integer))
                             end                                                                    AS vpip
                            ,case when sum(cast(hp.street0AggrChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0Aggr as <signed>integer))/sum(cast(hp.street0AggrChance as <signed>integer))
                             end                                                                    AS pfr
                            ,case when sum(cast(hp.street0CalledRaiseChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0CalledRaiseDone as <signed>integer))/sum(cast(hp.street0CalledRaiseChance as <signed>integer))
                             end                                                                    AS car0
                            ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                             end                                                                    AS pf4
                            ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                             end                                                                    AS pff3
                            ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                             end                                                                    AS pff4

                            ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                       sum(cast(hp.raiseFirstInChance as <signed>integer))
                             end                                                                    AS rfi
                            ,case when sum(cast(hp.stealChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.stealDone as <signed>integer)) / 
                                       sum(cast(hp.stealChance as <signed>integer))
                             end                                                                    AS steals
                            ,case when sum(cast(hp.stealDone as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.success_Steal as <signed>integer)) / 
                                       sum(cast(hp.stealDone as <signed>integer))
                             end                                                                    AS suc_steal
                            ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonWhenSeenStreet1 as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wmsf
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                          /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                     /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                             end                                                                    AS aggfac
                            ,100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                       (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                       (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                                                                                                    AS aggfrq
                            ,100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                       / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                                                                                                    AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                            ,sqrt(variance(hp.totalProfit/100.0))                                                         AS stddev
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in <player_test>
                      <game_test>
                      <site_test>
                      <currency_test>
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats <seats_test>
                      <flagtest>
                      <cardstest>
                      <gtbigBlind_test>
                      and   date_format(h.startTime, '%Y-%m-%d %T') <datestest>
                      group by hgametypeId
                              ,pname
                              ,gt.base
                              ,gt.category
                              <groupbyseats>
                              ,plposition
                              ,upper(gt.limitType)
                              ,gt.fast
                              ,s.name
                      having 1 = 1 <havingclause>
                      order by pname
                              ,gt.base
                              ,gt.category
                              <orderbyseats>
                              ,case <position> when 'B' then 'B'
                                               when 'S' then 'S'
                                               else concat('Z', <position>)
                               end
                              <orderbyhgametypeId>
                              ,upper(gt.limitType) desc
                              ,maxbigblind desc
                              ,gt.fast
                              ,s.name
                      """
        elif db_server == 'postgresql':
            self.query['playerDetailedStats'] = """
                     select  <hgametypeId>                                                          AS hgametypeid
                            ,<playerName>                                                           AS pname
                            ,gt.base
                            ,gt.category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            ,gt.ante                                                                AS ante
                            ,gt.currency                                                            AS currency
                            /*,<hcgametypeId>                                                       AS gtid*/
                            ,<position>                                                             AS plposition
                            ,gt.fast                                                                AS fast
                            ,count(1)                                                               AS n
                            ,case when sum(cast(hp.street0VPIChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0VPI as <signed>integer))/sum(cast(hp.street0VPIChance as <signed>integer))
                             end                                                                    AS vpip
                            ,case when sum(cast(hp.street0AggrChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0Aggr as <signed>integer))/sum(cast(hp.street0AggrChance as <signed>integer))
                             end                                                                    AS pfr
                            ,case when sum(cast(hp.street0CalledRaiseChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0CalledRaiseDone as <signed>integer))/sum(cast(hp.street0CalledRaiseChance as <signed>integer))
                             end                                                                    AS car0
                            ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                             end                                                                    AS pf4
                            ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                             end                                                                    AS pff3
                            ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                             end                                                                    AS pff4
                            ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                       sum(cast(hp.raiseFirstInChance as <signed>integer))
                             end                                                                    AS rfi
                            ,case when sum(cast(hp.stealChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.stealDone as <signed>integer)) / 
                                       sum(cast(hp.stealChance as <signed>integer))
                             end                                                                    AS steals
                            ,case when sum(cast(hp.stealDone as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.success_Steal as <signed>integer)) / 
                                       sum(cast(hp.stealDone as <signed>integer))
                             end                                                                    AS suc_steal
                            ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonWhenSeenStreet1 as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wmsf
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                          /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                     /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                             end                                                                    AS aggfac
                            ,case when
                                sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))+
                                sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))+
                                sum(cast(hp.street1Aggr as <signed>integer))+ sum(cast(hp.street2Aggr as <signed>integer))+ sum(cast(hp.street3Aggr as <signed>integer))+ sum(cast(hp.street4Aggr as <signed>integer))
                                = 0 then -999
                            else
                            100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                       (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                       (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                              end                                                                   AS aggfrq
                            ,case when
                                sum(cast(hp.street1CBChance as <signed>integer))+
                                sum(cast(hp.street2CBChance as <signed>integer))+
                                sum(cast(hp.street3CBChance as <signed>integer))+
                                sum(cast(hp.street4CBChance as <signed>integer)) = 0 then -999
                            else
                             100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                       / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                            end                                                                     AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                            ,sqrt(variance(hp.totalProfit/100.0))                                                         AS stddev
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in <player_test>
                      <game_test>
                      <site_test>
                      <currency_test>
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats <seats_test>
                      <flagtest>
                      <cardstest>
                      <gtbigBlind_test>
                      and   to_char(h.startTime, 'YYYY-MM-DD HH24:MI:SS') <datestest>
                      group by hgametypeId
                              ,pname
                              ,gt.base
                              ,gt.category
                              ,gt.ante
                              ,gt.currency
                              <groupbyseats>
                              ,plposition
                              ,upper(gt.limitType)
                              ,gt.fast
                              ,s.name
                      having 1 = 1 <havingclause>
                      order by pname
                              ,gt.base
                              ,gt.category
                              <orderbyseats>
                              ,case <position> when 'B' then 'B'
                                               when 'S' then 'S'
                                               when '0' then 'Y'
                                               else 'Z'||<position>
                               end
                              <orderbyhgametypeId>
                              ,upper(gt.limitType) desc
                              ,maxbigblind desc
                              ,gt.fast
                              ,s.name
                      """
        elif db_server == 'sqlite':
            self.query['playerDetailedStats'] = """
                     select  <hgametypeId>                                                          AS hgametypeid
                            ,<playerName>                                                           AS pname
                            ,gt.base
                            ,gt.category                                                            AS category
                            ,upper(gt.limitType)                                                    AS limittype
                            ,s.name                                                                 AS name
                            ,min(gt.bigBlind)                                                       AS minbigblind
                            ,max(gt.bigBlind)                                                       AS maxbigblind
                            ,gt.ante                                                                AS ante
                            ,gt.currency                                                            AS currency
                            /*,<hcgametypeId>                                                       AS gtid*/
                            ,<position>                                                             AS plposition
                            ,gt.fast                                                                AS fast
                            ,count(1)                                                               AS n
                            ,case when sum(cast(hp.street0VPIChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0VPI as <signed>integer))/sum(cast(hp.street0VPIChance as <signed>integer))
                             end                                                                    AS vpip
                            ,case when sum(cast(hp.street0AggrChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0Aggr as <signed>integer))/sum(cast(hp.street0AggrChance as <signed>integer))
                             end                                                                    AS pfr
                            ,case when sum(cast(hp.street0CalledRaiseChance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0CalledRaiseDone as <signed>integer))/sum(cast(hp.street0CalledRaiseChance as <signed>integer))
                             end                                                                    AS car0
                            ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                             end                                                                    AS pf3
                            ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                             end                                                                    AS pf4
                            ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                             end                                                                    AS pff3
                            ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                             end                                                                    AS pff4
                            ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                       sum(cast(hp.raiseFirstInChance as <signed>integer))
                             end                                                                    AS rfi
                            ,case when sum(cast(hp.stealChance as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.stealDone as <signed>integer)) / 
                                       sum(cast(hp.stealChance as <signed>integer))
                             end                                                                    AS steals
                            ,case when sum(cast(hp.stealDone as <signed>integer)) = 0 then -999
                                  else 100.0 * sum(cast(hp.success_Steal as <signed>integer)) / 
                                       sum(cast(hp.stealDone as <signed>integer))
                             end                                                                    AS suc_steal
                            ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                            ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonWhenSeenStreet1 as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wmsf
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS wtsdwsf
                            ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                             end                                                                    AS wmsd
                            ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                             end                                                                    AS flafq
                            ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                  else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                             end                                                                    AS tuafq
                            ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                             end                                                                    AS rvafq
                            ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                 else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                          /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                             end                                                                    AS pofafq
                            ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                 else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                     /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                             end                                                                    AS aggfac
                            ,100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                       / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                       (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                       (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                                                                                                    AS aggfrq
                            ,100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                       / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                                                                                                    AS conbet
                            ,sum(hp.totalProfit)/100.0                                              AS net
                            ,sum(hp.rake)/100.0                                                     AS rake
                            ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                            ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                            ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                            ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                            ,avg(h.seats+0.0)                                                       AS avgseats
                            ,variance(hp.totalProfit/100.0)                                         AS variance
                            ,sqrt(variance(hp.totalProfit/100.0))                                                         AS stddev
                      from HandsPlayers hp
                           inner join Hands h       on  (h.id = hp.handId)
                           inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                           inner join Sites s       on  (s.Id = gt.siteId)
                           inner join Players p     on  (p.Id = hp.playerId)
                      where hp.playerId in <player_test>
                      <game_test>
                      <site_test>
                      <currency_test>
                      /*and   hp.tourneysPlayersId IS NULL*/
                      and   h.seats <seats_test>
                      <flagtest>
                      <cardstest>
                      <gtbigBlind_test>
                      and   datetime(h.startTime) <datestest>
                      group by hgametypeId
                              ,hp.playerId
                              ,gt.base
                              ,gt.category
                              <groupbyseats>
                              ,plposition
                              ,upper(gt.limitType)
                              ,gt.fast
                              ,s.name
                      having 1 = 1 <havingclause>
                      order by hp.playerId
                              ,gt.base
                              ,gt.category
                              <orderbyseats>
                              ,case <position> when 'B' then 'B'
                                               when 'S' then 'S'
                                               when '0' then 'Y'
                                               else 'Z'||<position>
                               end
                              <orderbyhgametypeId>
                              ,upper(gt.limitType) desc
                              ,max(gt.bigBlind) desc
                              ,gt.fast
                              ,s.name
                      """

        #FIXME: 3/4bet and foldTo don't added four tournaments yet
        if db_server == 'mysql':
            self.query['tourneyPlayerDetailedStats'] = """
                      select s.name                                                                 AS siteName
                            ,t.tourneyTypeId                                                        AS tourneyTypeId
                            ,tt.currency                                                            AS currency
                            ,(CASE
                                WHEN tt.currency = 'play' THEN tt.buyIn
                                ELSE tt.buyIn/100.0
                              END)                                                                  AS buyIn
                            ,tt.fee/100.0                                                           AS fee
                            ,tt.category                                                            AS category
                            ,tt.limitType                                                           AS limitType
                            ,tt.speed                                                                AS speed
                            ,p.name                                                                 AS playerName
                            ,COUNT(1)                                                               AS tourneyCount
                            ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS unknownRank
                            ,(CAST(SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END) AS SIGNED BIGINT)/CAST(COUNT(1) AS SIGNED BIGINT))*100                 AS itm
                            ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS _1st
                            ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS _2nd
                            ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS _3rd
                            ,SUM(tp.winnings)/100.0                                                 AS won
                            ,SUM(CASE
                                   WHEN tt.currency = 'play' THEN tt.buyIn
                                   ELSE (tt.buyIn+tt.fee)/100.0
                                 END)                                                               AS spent
                            ,ROUND(
                                (CAST(SUM(tp.winnings - tt.buyin - tt.fee) AS SIGNED BIGINT)/
                                CAST(SUM(tt.buyin+tt.fee) AS SIGNED BIGINT))* 100.0
                             ,2)                                                                    AS roi
                            ,SUM(tp.winnings-(tt.buyin+tt.fee))/100.0/(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS profitPerTourney
                      from TourneysPlayers tp
                           inner join Tourneys t        on  (t.id = tp.tourneyId)
                           inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                           inner join Sites s           on  (s.Id = tt.siteId)
                           inner join Players p         on  (p.Id = tp.playerId)
                      where tp.playerId in <nametest> <sitetest>
                      AND   ((t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                                        OR t.startTime is NULL)
                      group by tourneyTypeId, playerName
                      order by tourneyTypeId
                              ,playerName
                              ,siteName"""
        elif db_server == 'postgresql':
            # sc: itm and profitPerTourney changed to "ELSE 0" to avoid divide by zero error as temp fix
            # proper fix should use coalesce() or case ... when ... to work in all circumstances
            self.query['tourneyPlayerDetailedStats'] = """
                      select s.name                                                                 AS "siteName"
                            ,t.tourneyTypeId                                                        AS "tourneyTypeId"
                            ,tt.currency                                                            AS "currency"
                            ,(CASE
                                WHEN tt.currency = 'play' THEN tt.buyIn
                                ELSE tt.buyIn/100.0
                              END)                                                                  AS "buyIn"
                            ,tt.fee/100.0                                                           AS "fee"
                            ,tt.category                                                            AS "category"
                            ,tt.limitType                                                           AS "limitType"
                            ,tt.speed                                                                AS "speed"
                            ,p.name                                                                 AS "playerName"
                            ,COUNT(1)                                                               AS "tourneyCount"
                            ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS "unknownRank"
                            ,(CAST(SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END) AS BIGINT)/CAST(COUNT(1) AS BIGINT))*100                 AS itm
                            ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS "_1st"
                            ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS "_2nd"
                            ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS "_3rd"
                            ,SUM(tp.winnings)/100.0                                                 AS "won"
                            ,SUM(CASE
                                   WHEN tt.currency = 'play' THEN tt.buyIn
                                   ELSE (tt.buyIn+tt.fee)/100.0
                                 END)                                                               AS "spent"
                            ,ROUND(
                                (CAST(SUM(tp.winnings - tt.buyin - tt.fee) AS BIGINT)/
                                CAST(SUM(tt.buyin+tt.fee) AS BIGINT))* 100.0
                             ,2)                                                                    AS "roi"
                            ,SUM(tp.winnings-(tt.buyin+tt.fee))/100.0
                             /(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 0 END))               AS "profitPerTourney"
                      from TourneysPlayers tp
                           inner join Tourneys t        on  (t.id = tp.tourneyId)
                           inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                           inner join Sites s           on  (s.Id = tt.siteId)
                           inner join Players p         on  (p.Id = tp.playerId)
                      where tp.playerId in <nametest> <sitetest>
                      AND   ((t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                                        OR t.startTime is NULL)
                      group by t.tourneyTypeId, s.name, p.name, tt.currency, tt.buyin, tt.fee
                             , tt.category, tt.limitType, tt.speed
                      order by t.tourneyTypeId
                              ,p.name
                              ,s.name"""
        elif db_server == 'sqlite':
            self.query['tourneyPlayerDetailedStats'] = """
                      select s.name                                                                 AS siteName
                            ,t.tourneyTypeId                                                        AS tourneyTypeId
                            ,tt.currency                                                            AS currency
                            ,(CASE
                                WHEN tt.currency = 'play' THEN tt.buyIn
                                ELSE tt.buyIn/100.0
                              END)                                                                  AS buyIn
                            ,tt.fee/100.0                                                           AS fee
                            ,tt.category                                                            AS category
                            ,tt.limitType                                                           AS limitType
                            ,tt.speed                                                                AS speed
                            ,p.name                                                                 AS playerName
                            ,COUNT(1)                                                               AS tourneyCount
                            ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS unknownRank
                            ,(CAST(SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END) AS REAL)/CAST(COUNT(1) AS REAL))*100                 AS itm
                            ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS _1st
                            ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS _2nd
                            ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS _3rd
                            ,SUM(tp.winnings)/100.0                                                 AS won
                            ,SUM(CASE
                                   WHEN tt.currency = 'play' THEN tt.buyIn
                                   ELSE (tt.buyIn+tt.fee)/100.0
                                 END)                                                               AS spent
                            ,ROUND(
                                (CAST(SUM(tp.winnings - tt.buyin - tt.fee) AS REAL)/
                                CAST(SUM(tt.buyin+tt.fee) AS REAL))* 100.0
                             ,2)                                                                    AS roi
                            ,SUM(tp.winnings-(tt.buyin+tt.fee))/100.0/(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS profitPerTourney
                      from TourneysPlayers tp
                           inner join Tourneys t        on  (t.id = tp.tourneyId)
                           inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                           inner join Sites s           on  (s.Id = tt.siteId)
                           inner join Players p         on  (p.Id = tp.playerId)
                      where tp.playerId in <nametest> <sitetest>
                      AND   ((t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                                        OR t.startTime is NULL)
                      group by tourneyTypeId, playerName
                      order by tourneyTypeId
                              ,playerName
                              ,siteName"""

        if db_server == 'mysql':
            self.query['playerStats'] = """
                SELECT
                      concat(upper(stats.limitType), ' '
                            ,concat(upper(substring(stats.category,1,1)),substring(stats.category,2) ), ' '
                            ,stats.name, ' '
                            ,cast(stats.bigBlindDesc as char)
                            )                                                      AS Game
                     ,stats.n
                     ,stats.vpip
                     ,stats.pfr
                     ,stats.pf3
                     ,stats.pf4
                     ,stats.pff3
                     ,stats.pff4
                     ,stats.steals
                     ,stats.saw_f
                     ,stats.sawsd
                     ,stats.wtsdwsf
                     ,stats.wmsd
                     ,stats.FlAFq
                     ,stats.TuAFq
                     ,stats.RvAFq
                     ,stats.PoFAFq
                     ,stats.Net
                     ,stats.BBper100
                     ,stats.Profitperhand
                     ,case when hprof2.variance = -999 then '-'
                           else format(hprof2.variance, 2)
                      end                                                          AS Variance
                     ,case when hprof2.stddev = -999 then '-'
                           else format(hprof2.stddev, 2)
                      end                                                          AS Stddev
                     ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category
                           ,upper(gt.limitType) as limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,sum(n)                                                          AS n
                           ,case when sum(street0VPIChance) = 0 then '0'
                                 else format(100.0*sum(street0VPI)/sum(street0VPIChance),1)
                            end                                                             AS vpip
                           ,case when sum(street0AggrChance) = 0 then '0'
                                 else format(100.0*sum(street0Aggr)/sum(street0AggrChance),1)
                            end                                                             AS pfr
                           ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                 else format(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),1)
                            end                                                             AS car0
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else format(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                            end                                                             AS steals
                           ,format(100.0*sum(street1Seen)/sum(n),1)                         AS saw_f
                           ,format(100.0*sum(sawShowdown)/sum(n),1)                         AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(sawShowdown)/sum(street1Seen),1)
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else format(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(street1Aggr)/sum(street1Seen),1)
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else format(100.0*sum(street2Aggr)/sum(street2Seen),1)
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else format(100.0*sum(street3Aggr)/sum(street3Seen),1)
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else format(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                            end                                                             AS PoFAFq
                           ,format(sum(totalProfit)/100.0,2)                                AS Net
                           ,format((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0),2)
                                                                                            AS BBper100
                           ,format( (sum(totalProfit)/100.0) / sum(n), 4)                   AS Profitperhand
                           ,format( sum(seats*n)/(sum(n)+0.0), 2)                           AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     <gtbigBlind_test>
                     and   hc.seats <seats_test>
                     and   concat( '20', substring(hc.styleKey,2,2), '-', substring(hc.styleKey,4,2), '-'
                                 , substring(hc.styleKey,6,2) ) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                    ) stats
                inner join
                    ( select # profit from handsplayers/handsactions
                             hprof.gtId, sum(hprof.profit) sum_profit,
                             avg(hprof.profit/100.0) profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                            ,sqrt(variance(hprof.profit/100.0))                                                         AS stddev
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h        ON h.id            = hp.handId
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   date_format(h.startTime, '%Y-%m-%d') <datestest>
                           group by hp.handId, gtId, hp.totalProfit
                          ) hprof
                      group by hprof.gtId
                     ) hprof2
                    on hprof2.gtId = stats.gtId
                order by stats.category, stats.limittype, stats.bigBlindDesc desc <orderbyseats>"""
        elif db_server == 'sqlite':
            self.query['playerStats'] = """
                SELECT
                      upper(substr(stats.category,1,1)) || substr(stats.category,2) || ' ' ||
                      stats.name || ' ' ||
                      cast(stats.bigBlindDesc as char) || ' ' || stats.maxSeats || ' seat'  AS Game
                     ,stats.n,stats.vpip,stats.pfr,stats.pf3,stats.pf4,stats.pff3,stats.pff4
                     ,stats.steals,stats.saw_f,stats.sawsd,stats.wtsdwsf,stats.wmsd,stats.FlAFq
                     ,stats.TuAFq,stats.RvAFq,stats.PoFAFq,stats.Net,stats.BBper100,stats.Profitperhand
                     ,case when hprof2.variance = -999 then '-' else round(hprof2.variance, 2)
                      end                                                                   AS Variance
                     ,case when hprof2.stddev = -999 then '-' else round(hprof2.stddev, 2)
                      end                                                                   AS Stddev
                     ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category,maxSeats,gt.bigBlind,gt.currency
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,sum(n)                                                          AS n
                           ,case when sum(street0VPIChance) = 0 then '0'
                                 else round(100.0*sum(street0VPI)/sum(street0VPIChance),1)
                            end                                                             AS vpip
                           ,case when sum(street0AggrChance) = 0 then '0'
                                 else round(100.0*sum(street0Aggr)/sum(street0AggrChance),1)
                            end                                                             AS pfr
                           ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                 else round(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),1)
                            end                                                             AS car0
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else round(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                            end                                                             AS steals
                           ,round(100.0*sum(street1Seen)/sum(n),1)                          AS saw_f
                           ,round(100.0*sum(sawShowdown)/sum(n),1)                          AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else round(100.0*sum(sawShowdown)/sum(street1Seen),1)
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else round(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else round(100.0*sum(street1Aggr)/sum(street1Seen),1)
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else round(100.0*sum(street2Aggr)/sum(street2Seen),1)
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else round(100.0*sum(street3Aggr)/sum(street3Seen),1)
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else round(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                            end                                                             AS PoFAFq
                           ,round(sum(totalProfit)/100.0,2)                                 AS Net
                           ,round((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0),2)
                                                                                            AS BBper100
                           ,round( (sum(totalProfit)/100.0) / sum(n), 4)                    AS Profitperhand
                           ,round( sum(seats*n)/(sum(n)+0.0), 2)                            AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     <gtbigBlind_test>
                     and   hc.seats <seats_test>
                     and   '20' || substr(hc.styleKey,2,2) || '-' || substr(hc.styleKey,4,2) || '-' ||
                                   substr(hc.styleKey,6,2) <datestest>
                     group by gt.base,gt.category,upper(gt.limitType),s.name <groupbygt.bigBlind>,gtId
                    ) stats
                inner join
                    ( select /* profit from handsplayers/handsactions */
                             hprof.gtId, sum(hprof.profit) sum_profit,
                             avg(hprof.profit/100.0) profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                             ,case when hprof.gtId = -1 then -999
                                  else sqrt(variance(hprof.profit/100.0))
                             end as stddev
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h        ON h.id            = hp.handId
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   datetime(h.startTime) <datestest>
                           group by hp.handId, gtId, hp.totalProfit
                          ) hprof
                      group by hprof.gtId
                     ) hprof2
                    on hprof2.gtId = stats.gtId
                order by stats.category, stats.bigBlind, stats.limittype, stats.currency, stats.maxSeats <orderbyseats>"""
        else:  # assume postgres
            self.query['playerStats'] = """
                SELECT upper(stats.limitType) || ' '
                       || initcap(stats.category) || ' '
                       || stats.name || ' '
                       || stats.bigBlindDesc                                          AS Game
                      ,stats.n
                      ,stats.vpip
                      ,stats.pfr
                      ,stats.pf3
                      ,stats.pf4
                      ,stats.pff3
                      ,stats.pff4
                      ,stats.steals
                      ,stats.saw_f
                      ,stats.sawsd
                      ,stats.wtsdwsf
                      ,stats.wmsd
                      ,stats.FlAFq
                      ,stats.TuAFq
                      ,stats.RvAFq
                      ,stats.PoFAFq
                      ,stats.Net
                      ,stats.BBper100
                      ,stats.Profitperhand
                      ,case when hprof2.variance = -999 then '-'
                            else to_char(hprof2.variance, '0D00')
                       end                                                          AS Variance
                      ,case when hprof2.stddev = -999 then '-'
                            else to_char(hprof2.stddev, '0D00')
                       end                                                          AS Stddev
                      ,AvgSeats
                FROM
                    (select gt.base
                           ,gt.category
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,sum(n)                                                          AS n
                           ,case when sum(street0VPIChance) = 0 then '0'
                                 else to_char(100.0*sum(street0VPI)/sum(street0VPIChance),'990D0')
                            end                                                             AS vpip
                           ,case when sum(street0AggrChance) = 0 then '0'
                                 else to_char(100.0*sum(street0Aggr)/sum(street0AggrChance),'90D0')
                            end                                                             AS pfr
                           ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                 else to_char(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),'90D0')
                            end                                                             AS car0
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),'90D0')
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else to_char(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),'90D0')
                            end                                                             AS steals
                           ,to_char(100.0*sum(street1Seen)/sum(n),'90D0')                   AS saw_f
                           ,to_char(100.0*sum(sawShowdown)/sum(n),'90D0')                   AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(100.0*sum(sawShowdown)/sum(street1Seen),'90D0')
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else to_char(100.0*sum(wonAtSD)/sum(sawShowdown),'90D0')
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(100.0*sum(street1Aggr)/sum(street1Seen),'90D0')
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else to_char(100.0*sum(street2Aggr)/sum(street2Seen),'90D0')
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else to_char(100.0*sum(street3Aggr)/sum(street3Seen),'90D0')
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else to_char(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),'90D0')
                            end                                                             AS PoFAFq
                           ,round(sum(totalProfit)/100.0,2)                                 AS Net
                           ,to_char((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0), '990D00')
                                                                                            AS BBper100
                           ,to_char(sum(totalProfit/100.0) / (sum(n)+0.0), '990D0000')    AS Profitperhand
                           ,to_char(sum(seats*n)/(sum(n)+0.0),'90D00')            AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     <gtbigBlind_test>
                     and   hc.seats <seats_test>
                     and   '20' || SUBSTR(hc.styleKey,2,2) || '-' || SUBSTR(hc.styleKey,4,2) || '-'
                           || SUBSTR(hc.styleKey,6,2) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                    ) stats
                inner join
                    ( select
                             hprof.gtId, sum(hprof.profit) AS sum_profit,
                             avg(hprof.profit/100.0) AS profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                             ,case when hprof.gtId = -1 then -999
                                  else sqrt(variance(hprof.profit/100.0))
                             end as stddev
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h   ON (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   to_char(h.startTime, 'YYYY-MM-DD') <datestest>
                           group by hp.handId, gtId, hp.totalProfit
                          ) hprof
                      group by hprof.gtId
                     ) hprof2
                    on hprof2.gtId = stats.gtId
                order by stats.base, stats.limittype, stats.bigBlindDesc desc <orderbyseats>"""

        if db_server == 'mysql':
            self.query['playerStatsByPosition'] = """
                SELECT
                      concat(upper(stats.limitType), ' '
                            ,concat(upper(substring(stats.category,1,1)),substring(stats.category,2) ), ' '
                            ,stats.name, ' '
                            ,cast(stats.bigBlindDesc as char)
                            )                                                      AS Game
                     ,case when stats.PlPosition = -2 then 'BB'
                           when stats.PlPosition = -1 then 'SB'
                           when stats.PlPosition =  0 then 'Btn'
                           when stats.PlPosition =  1 then 'CO'
                           when stats.PlPosition =  2 then 'MP'
                           when stats.PlPosition =  5 then 'EP'
                           else 'xx'
                      end                                                          AS PlPosition
                     ,stats.n
                     ,stats.vpip
                     ,stats.pfr
                     ,stats.car0
                     ,stats.pf3
                     ,stats.pf4
                     ,stats.pff3
                     ,stats.pff4
                     ,stats.steals
                     ,stats.saw_f
                     ,stats.sawsd
                     ,stats.wtsdwsf
                     ,stats.wmsd
                     ,stats.FlAFq
                     ,stats.TuAFq
                     ,stats.RvAFq
                     ,stats.PoFAFq
                     ,stats.Net
                     ,stats.BBper100
                     ,stats.Profitperhand
                     ,case when hprof2.variance = -999 then '-'
                           else format(hprof2.variance, 2)
                      end                                                          AS Variance
                     ,case when hprof2.stddev = -999 then '-'
                           else format(hprof2.stddev, 2)
                      end                                                          AS Stddev
                     ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,case when hc.position = 'B' then -2
                                 when hc.position = 'S' then -1
                                 when hc.position = 'D' then  0
                                 when hc.position = 'C' then  1
                                 when hc.position = 'M' then  2
                                 when hc.position = 'E' then  5
                                 else 9
                            end                                                             as PlPosition
                           ,sum(n)                                                          AS n
                           ,case when sum(street0VPIChance) = 0 then '0'
                                 else format(100.0*sum(street0VPI)/sum(street0VPIChance),1)
                            end                                                             AS vpip
                           ,case when sum(street0AggrChance) = 0 then '0'
                                 else format(100.0*sum(street0Aggr)/sum(street0AggrChance),1)
                            end                                                             AS pfr
                           ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                 else format(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),1)
                            end                                                             AS car0
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else format(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else format(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                            end                                                             AS steals
                           ,format(100.0*sum(street1Seen)/sum(n),1)                         AS saw_f
                           ,format(100.0*sum(sawShowdown)/sum(n),1)                         AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(sawShowdown)/sum(street1Seen),1)
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else format(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else format(100.0*sum(street1Aggr)/sum(street1Seen),1)
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else format(100.0*sum(street2Aggr)/sum(street2Seen),1)
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else format(100.0*sum(street3Aggr)/sum(street3Seen),1)
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else format(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                            end                                                             AS PoFAFq
                           ,format(sum(totalProfit)/100.0,2)                                AS Net
                           ,format((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0),2)
                                                                                            AS BBper100
                           ,format( (sum(totalProfit)/100.0) / sum(n), 4)                   AS Profitperhand
                           ,format( sum(seats*n)/(sum(n)+0.0), 2)                          AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     <gtbigBlind_test>
                     and   hc.seats <seats_test>
                     and   concat( '20', substring(hc.styleKey,2,2), '-', substring(hc.styleKey,4,2), '-'
                                 , substring(hc.styleKey,6,2) ) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                          <groupbyseats>
                          ,PlPosition
                    ) stats
                inner join
                    ( select # profit from handsplayers/handsactions
                             hprof.gtId,
                             case when hprof.position = 'B' then -2
                                  when hprof.position = 'S' then -1
                                  when hprof.position in ('3','4') then 2
                                  when hprof.position in ('6','7') then 5
                                  else hprof.position
                             end                                      as PlPosition,
                             sum(hprof.profit) as sum_profit,
                             avg(hprof.profit/100.0) as profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                             ,case when hprof.gtId = -1 then -999
                                  else sqrt(variance(hprof.profit/100.0))
                             end as stddev
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.position
                                , hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h  ON  (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   date_format(h.startTime, '%Y-%m-%d') <datestest>
                           group by hp.handId, gtId, hp.position, hp.totalProfit
                          ) hprof
                      group by hprof.gtId, PlPosition
                     ) hprof2
                    on (    hprof2.gtId = stats.gtId
                        and hprof2.PlPosition = stats.PlPosition)
                order by stats.category, stats.limitType, stats.bigBlindDesc desc
                         <orderbyseats>, cast(stats.PlPosition as signed)
                """
        elif db_server == 'sqlite':
            self.query['playerStatsByPosition'] = """
                SELECT
                      upper(substr(stats.category,1,1)) || substr(stats.category,2) || ' ' ||
                      stats.name || ' ' ||
                      cast(stats.bigBlindDesc as char) || ' ' || stats.maxSeats || ' seat'  AS Game
                     ,case when stats.PlPosition = -2 then 'BB'
                           when stats.PlPosition = -1 then 'SB'
                           when stats.PlPosition =  0 then 'Btn'
                           when stats.PlPosition =  1 then 'CO'
                           when stats.PlPosition =  2 then 'MP'
                           when stats.PlPosition =  5 then 'EP'
                           else 'xx'
                      end                                                                   AS PlPosition
                     ,stats.n,stats.vpip,stats.pfr,stats.pf3,stats.pf4,stats.pff3,stats.pff4
                     ,stats.steals,stats.saw_f,stats.sawsd,stats.wtsdwsf,stats.wmsd,stats.FlAFq
                     ,stats.TuAFq,stats.RvAFq,stats.PoFAFq,stats.Net,stats.BBper100,stats.Profitperhand
                     ,case when hprof2.variance = -999 then '-'
                           else round(hprof2.variance, 2)
                      end                                                                   AS Variance
                     ,case when hprof2.variance = -999 then '-'
                           else round(hprof2.stddev, 2)
                      end                                                                   AS Stddev
                     ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category,maxSeats,gt.bigBlind,gt.currency
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,case when hc.position = 'B' then -2
                                 when hc.position = 'S' then -1
                                 when hc.position = 'D' then  0
                                 when hc.position = 'C' then  1
                                 when hc.position = 'M' then  2
                                 when hc.position = 'E' then  5
                                 else 9
                            end                                                             AS PlPosition
                           ,sum(n)                                                          AS n
                           ,case when sum(street0VPIChance) = 0 then '0'
                                 else round(100.0*sum(street0VPI)/sum(street0VPIChance),1)
                            end                                                             AS vpip
                           ,case when sum(street0AggrChance) = 0 then '0'
                                 else round(100.0*sum(street0Aggr)/sum(street0AggrChance),1)
                            end                                                             AS pfr
                           ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                 else round(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),1)
                            end                                                             AS car0
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else round(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else round(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                            end                                                             AS steals
                           ,round(100.0*sum(street1Seen)/sum(n),1)                          AS saw_f
                           ,round(100.0*sum(sawShowdown)/sum(n),1)                          AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else round(100.0*sum(sawShowdown)/sum(street1Seen),1)
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else round(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else round(100.0*sum(street1Aggr)/sum(street1Seen),1)
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else round(100.0*sum(street2Aggr)/sum(street2Seen),1)
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else round(100.0*sum(street3Aggr)/sum(street3Seen),1)
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else round(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                            end                                                             AS PoFAFq
                           ,round(sum(totalProfit)/100.0,2)                                 AS Net
                           ,round((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0),2)
                                                                                            AS BBper100
                           ,round( (sum(totalProfit)/100.0) / sum(n), 4)                    AS Profitperhand
                           ,round( sum(seats*n)/(sum(n)+0.0), 2)                            AS AvgSeats
                     from Gametypes gt
                          inner join Sites s on s.Id = gt.siteId
                          inner join HudCache hc on hc.gametypeId = gt.Id
                     where hc.playerId in <player_test>
                     <gtbigBlind_test>
                     and   hc.seats <seats_test>
                     and   '20' || substr(hc.styleKey,2,2) || '-' || substr(hc.styleKey,4,2) || '-' ||
                                   substr(hc.styleKey,6,2) <datestest>
                     group by gt.base,gt.category,upper(gt.limitType),s.name
                              <groupbygt.bigBlind>,gtId<groupbyseats>,PlPosition
                    ) stats
                inner join
                    ( select /* profit from handsplayers/handsactions */
                             hprof.gtId,
                             cast(case when hprof.position = 'B' then -2
                                  when hprof.position = 'S' then -1
                                  when hprof.position in ('3','4') then 2
                                  when hprof.position in ('6','7') then 5
                                  else hprof.position
                             end as signed)                           as PlPosition,
                             sum(hprof.profit) as sum_profit,
                             avg(hprof.profit/100.0) as profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                             ,case when hprof.gtId = -1 then -999
                                  else sqrt(variance(hprof.profit/100.0))
                             end as stddev
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.position
                                , hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h  ON  (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   datetime(h.startTime) <datestest>
                           group by hp.handId, gtId, hp.position, hp.totalProfit
                          ) hprof
                      group by hprof.gtId, PlPosition
                     ) hprof2
                    on (    hprof2.gtId = stats.gtId
                        and hprof2.PlPosition = stats.PlPosition)
                order by stats.category, stats.bigBlind, stats.limitType, stats.currency, stats.maxSeats <orderbyseats>
                        ,cast(stats.PlPosition as signed)
                """
        else:  # assume postgresql
            self.query['playerStatsByPosition'] = """
                select /* stats from hudcache */
                       upper(stats.limitType) || ' '
                       || upper(substr(stats.category,1,1)) || substr(stats.category,2) || ' '
                       || stats.name || ' '
                       || stats.bigBlindDesc                                        AS Game
                      ,case when stats.PlPosition = -2 then 'BB'
                            when stats.PlPosition = -1 then 'SB'
                            when stats.PlPosition =  0 then 'Btn'
                            when stats.PlPosition =  1 then 'CO'
                            when stats.PlPosition =  2 then 'MP'
                            when stats.PlPosition =  5 then 'EP'
                            else 'xx'
                       end                                                          AS PlPosition
                      ,stats.n
                      ,stats.vpip
                      ,stats.pfr
                      ,stats.pf3
                      ,stats.pf4
                      ,stats.pff3
                      ,stats.pff4
                      ,stats.steals
                      ,stats.saw_f
                      ,stats.sawsd
                      ,stats.wtsdwsf
                      ,stats.wmsd
                      ,stats.FlAFq
                      ,stats.TuAFq
                      ,stats.RvAFq
                      ,stats.PoFAFq
                      ,stats.Net
                      ,stats.BBper100
                      ,stats.Profitperhand
                      ,case when hprof2.variance = -999 then '-'
                            else to_char(hprof2.variance, '0D00')
                       end                                                          AS Variance
                      ,case when hprof2.stddev = -999 then '-'
                            else to_char(hprof2.stddev, '0D00')
                       end                                                          AS Stddev
                      ,stats.AvgSeats
                FROM
                    (select /* stats from hudcache */
                            gt.base
                           ,gt.category
                           ,upper(gt.limitType)                                             AS limitType
                           ,s.name
                           ,<selectgt.bigBlind>                                             AS bigBlindDesc
                           ,<hcgametypeId>                                                  AS gtId
                           ,case when hc.position = 'B' then -2
                                 when hc.position = 'S' then -1
                                 when hc.position = 'D' then  0
                                 when hc.position = 'C' then  1
                                 when hc.position = 'M' then  2
                                 when hc.position = 'E' then  5
                                 else 9
                            end                                                             AS PlPosition
                           ,sum(n)                                                          AS n
                           ,case when sum(street0VPIChance) = 0 then '0'
                                 else to_char(100.0*sum(street0VPI)/sum(street0VPIChance),'990D0')
                            end                                                             AS vpip
                           ,case when sum(street0AggrChance) = 0 then '0'
                                 else to_char(100.0*sum(street0Aggr)/sum(street0AggrChance),'90D0')
                            end                                                             AS pfr
                           ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                 else to_char(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),'90D0')
                            end                                                             AS car0
                           ,case when sum(street0_3Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),'90D0')
                            end                                                             AS pf3
                           ,case when sum(street0_4Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),'90D0')
                            end                                                             AS pf4
                           ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),'90D0')
                            end                                                             AS pff3
                           ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                 else to_char(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),'90D0')
                            end                                                             AS pff4
                           ,case when sum(raiseFirstInChance) = 0 then '-'
                                 else to_char(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),'90D0')
                            end                                                             AS steals
                           ,to_char(round(100.0*sum(street1Seen)/sum(n)),'90D0')            AS saw_f
                           ,to_char(round(100.0*sum(sawShowdown)/sum(n)),'90D0')            AS sawsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(round(100.0*sum(sawShowdown)/sum(street1Seen)),'90D0')
                            end                                                             AS wtsdwsf
                           ,case when sum(sawShowdown) = 0 then '-'
                                 else to_char(round(100.0*sum(wonAtSD)/sum(sawShowdown)),'90D0')
                            end                                                             AS wmsd
                           ,case when sum(street1Seen) = 0 then '-'
                                 else to_char(round(100.0*sum(street1Aggr)/sum(street1Seen)),'90D0')
                            end                                                             AS FlAFq
                           ,case when sum(street2Seen) = 0 then '-'
                                 else to_char(round(100.0*sum(street2Aggr)/sum(street2Seen)),'90D0')
                            end                                                             AS TuAFq
                           ,case when sum(street3Seen) = 0 then '-'
                                else to_char(round(100.0*sum(street3Aggr)/sum(street3Seen)),'90D0')
                            end                                                             AS RvAFq
                           ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                                else to_char(round(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                         /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen))),'90D0')
                            end                                                             AS PoFAFq
                           ,to_char(sum(totalProfit)/100.0,'9G999G990D00')                  AS Net
                           ,case when sum(n) = 0 then '0'
                                 else to_char(sum(totalProfit/(gt.bigBlind+0.0)) / (sum(n)/100.0), '990D00')
                            end                                                             AS BBper100
                           ,case when sum(n) = 0 then '0'
                                 else to_char( (sum(totalProfit)/100.0) / sum(n), '90D0000')
                            end                                                             AS Profitperhand
                           ,to_char(sum(seats*n)/(sum(n)+0.0),'90D00')                      AS AvgSeats
                     from Gametypes gt
                          inner join Sites s     on (s.Id = gt.siteId)
                          inner join HudCache hc on (hc.gametypeId = gt.Id)
                     where hc.playerId in <player_test>
                     <gtbigBlind_test>
                     and   hc.seats <seats_test>
                     and   '20' || SUBSTR(hc.styleKey,2,2) || '-' || SUBSTR(hc.styleKey,4,2) || '-'
                           || SUBSTR(hc.styleKey,6,2) <datestest>
                     group by gt.base
                          ,gt.category
                          ,upper(gt.limitType)
                          ,s.name
                          <groupbygt.bigBlind>
                          ,gtId
                          <groupbyseats>
                          ,PlPosition
                    ) stats
                inner join
                    ( select /* profit from handsplayers/handsactions */
                             hprof.gtId,
                             case when hprof.position = 'B' then -2
                                  when hprof.position = 'S' then -1
                                  when hprof.position in ('3','4') then 2
                                  when hprof.position in ('6','7') then 5
                                  else cast(hprof.position as smallint)
                             end                                      as PlPosition,
                             sum(hprof.profit) as sum_profit,
                             avg(hprof.profit/100.0) as profitperhand,
                             case when hprof.gtId = -1 then -999
                                  else variance(hprof.profit/100.0)
                             end as variance
                             ,case when hprof.gtId = -1 then -999
                                  else sqrt(variance(hprof.profit/100.0))
                             end as stddev
                      from
                          (select hp.handId, <hgametypeId> as gtId, hp.position
                                , hp.totalProfit as profit
                           from HandsPlayers hp
                           inner join Hands h  ON  (h.id = hp.handId)
                           where hp.playerId in <player_test>
                           and   hp.tourneysPlayersId IS NULL
                           and   to_char(h.startTime, 'YYYY-MM-DD') <datestest>
                           group by hp.handId, gametypeId, hp.position, hp.totalProfit
                          ) hprof
                      group by hprof.gtId, PlPosition
                    ) hprof2
                    on (    hprof2.gtId = stats.gtId
                        and hprof2.PlPosition = stats.PlPosition)
                order by stats.category, stats.limitType, stats.bigBlindDesc desc
                         <orderbyseats>, cast(stats.PlPosition as smallint)
                """

        ####################################
        # Cash Game Graph query
        ####################################
        self.query['getRingProfitAllHandsPlayerIdSite'] = """
            SELECT hp.handId, hp.totalProfit, hp.sawShowdown
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            AND   gt.type = 'ring'
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit
            ORDER BY h.startTime"""

        self.query['getRingProfitAllHandsPlayerIdSiteInBB'] = """
            SELECT hp.handId, ( hp.totalProfit / ( gt.bigBlind  * 2.0 ) ) * 100 , hp.sawShowdown, ( hp.allInEV / ( gt.bigBlind * 2.0 ) ) * 100
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            <currency_test>
            AND   hp.tourneysPlayersId IS NULL
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit, hp.allInEV, gt.bigBlind
            ORDER BY h.startTime"""

        self.query['getRingProfitAllHandsPlayerIdSiteInDollars'] = """
            SELECT hp.handId, hp.totalProfit, hp.sawShowdown, hp.allInEV
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            <currency_test>
            AND   hp.tourneysPlayersId IS NULL
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit, hp.allInEV
            ORDER BY h.startTime"""

        ####################################
        # Tourney Results query
        ####################################
        self.query['tourneyResults'] = """
            SELECT tp.tourneyId, (coalesce(tp.winnings,0) - coalesce(tt.buyIn,0) - coalesce(tt.fee,0)) as profit, tp.koCount, tp.rebuyCount, tp.addOnCount, tt.buyIn, tt.fee, t.siteTourneyNo
            FROM TourneysPlayers tp
            INNER JOIN Players pl      ON  (pl.id = tp.playerId)
            INNER JOIN Tourneys t         ON  (t.id  = tp.tourneyId)
            INNER JOIN TourneyTypes tt    ON  (tt.id = t.tourneyTypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   ((t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                    OR t.startTime is NULL)
            GROUP BY t.startTime, tp.tourneyId, tp.winningsCurrency,
                     tp.winnings, tp.koCount,
                     tp.rebuyCount, tp.addOnCount,
                     tt.buyIn, tt.fee, t.siteTourneyNo
            ORDER BY t.startTime"""

            #AND   gt.type = 'ring'
            #<limit_test>
            #<game_test>
            
        ####################################
        # Tourney Graph query
        # FIXME this is a horrible hack to prevent nonsense data
        #  being graphed - needs proper fix mantis #180 +#182
        ####################################
        self.query['tourneyGraph'] = """
            SELECT tp.tourneyId, (coalesce(tp.winnings,0) - coalesce(tt.buyIn,0) - coalesce(tt.fee,0)) as profit, tp.koCount, tp.rebuyCount, tp.addOnCount, tt.buyIn, tt.fee, t.siteTourneyNo
            FROM TourneysPlayers tp
            INNER JOIN Players pl      ON  (pl.id = tp.playerId)
            INNER JOIN Tourneys t         ON  (t.id  = tp.tourneyId)
            INNER JOIN TourneyTypes tt    ON  (tt.id = t.tourneyTypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   (t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                 <currency_test>
            GROUP BY t.startTime, tp.tourneyId, tp.winningsCurrency,
                     tp.winnings, tp.koCount,
                     tp.rebuyCount, tp.addOnCount,
                     tt.buyIn, tt.fee, t.siteTourneyNo
            ORDER BY t.startTime"""

            #AND   gt.type = 'ring'
            #<limit_test>
            #<game_test>
        ####################################
        # Session stats query
        ####################################
        if db_server == 'mysql':
            self.query['sessionStats'] = """
                SELECT UNIX_TIMESTAMP(h.startTime) as time, hp.totalProfit
                FROM HandsPlayers hp
                 INNER JOIN Hands h       on  (h.id = hp.handId)
                 INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                 INNER JOIN Sites s       on  (s.Id = gt.siteId)
                 INNER JOIN Players p     on  (p.Id = hp.playerId)
                WHERE hp.playerId in <player_test>
                 AND  date_format(h.startTime, '%Y-%m-%d') <datestest>
                 AND  gt.type LIKE 'ring'
                 <limit_test>
                 <game_test>
                 <seats_test>
                 <currency_test>
                ORDER by time"""
        elif db_server == 'postgresql':
            self.query['sessionStats'] = """
                SELECT EXTRACT(epoch from h.startTime) as time, hp.totalProfit
                FROM HandsPlayers hp
                 INNER JOIN Hands h       on  (h.id = hp.handId)
                 INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                 INNER JOIN Sites s       on  (s.Id = gt.siteId)
                 INNER JOIN Players p     on  (p.Id = hp.playerId)
                WHERE hp.playerId in <player_test>
                 AND  h.startTime <datestest>
                 AND  gt.type LIKE 'ring'
                 <limit_test>
                 <game_test>
                 <seats_test>
                 <currency_test>
                ORDER by time"""
        elif db_server == 'sqlite':
            self.query['sessionStats'] = """
                SELECT STRFTIME('<ampersand_s>', h.startTime) as time, hp.totalProfit
                FROM HandsPlayers hp
                 INNER JOIN Hands h       on  (h.id = hp.handId)
                 INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                 INNER JOIN Sites s       on  (s.Id = gt.siteId)
                 INNER JOIN Players p     on  (p.Id = hp.playerId)
                WHERE hp.playerId in <player_test>
                 AND  h.startTime <datestest>
                 AND  gt.type is 'ring'
                 <limit_test>
                 <game_test>
                 <seats_test>
                 <currency_test>
                ORDER by time"""

        ####################################
        # Querry to get all hands in a date range
        ####################################
        self.query['handsInRange'] = """
            select h.id
                from Hands h
                join HandsPlayers hp on h.id = hp.handId
                join Gametypes gt on gt.id = h.gametypeId
            where h.startTime <datetest>
                and hp.playerId in <player_test>
                <game_test>
                <limit_test>
                <position_test>"""

        ####################################
        # Query to get a single hand for the replayer
        ####################################
        self.query['singleHand'] = """
                 SELECT h.*
                    FROM Hands h
                    WHERE id = %s"""

        ####################################
        # Query to get run it twice boards for the replayer
        ####################################
        self.query['singleHandBoards'] = """
                 SELECT b.*
                    FROM Boards b
                    WHERE handId = %s"""

        ####################################
        # Query to get a single player hand for the replayer
        ####################################
        self.query['playerHand'] = """
            SELECT
                        hp.seatno,
                        round(hp.winnings / 100.0,2) as winnings,
                        p.name,
                        round(hp.startCash / 100.0,2) as chips,
                        hp.card1,hp.card2,hp.card3,hp.card4,hp.card5,
                        hp.card6,hp.card7,hp.card8,hp.card9,hp.card10,
                        hp.card11,hp.card12,hp.card13,hp.card14,hp.card15,
                        hp.card16,hp.card17,hp.card18,hp.card19,hp.card20,
                        hp.position,
                        round(hp.startBounty / 100.0,2) as bounty,
                        hp.sitout
                    FROM
                        HandsPlayers as hp,
                        Players as p
                    WHERE
                        hp.handId = %s
                        and p.id = hp.playerId
                    ORDER BY
                        hp.seatno
                """

        ####################################
        # Query for the actions of a hand
        ####################################
        self.query['handActions'] = """
            SELECT
                      ha.actionNo,
                      p.name,
                      ha.street,
                      ha.actionId,
                      ha.allIn,
                      round(ha.amount / 100.0,2) as bet,
                      ha.numDiscarded,
                      ha.cardsDiscarded
                FROM
                      HandsActions as ha,
                      Players as p,
                      Hands as h
                WHERE
                          h.id = %s
                      AND ha.handId = h.id
                      AND ha.playerId = p.id
                ORDER BY
                      ha.id ASC
                """

        ####################################
        # Queries to rebuild/modify hudcache
        ####################################
      
        self.query['clearHudCache'] = """DELETE FROM HudCache"""
        self.query['clearCardsCache'] = """DELETE FROM CardsCache"""
        self.query['clearPositionsCache'] = """DELETE FROM PositionsCache"""
        
        self.query['clearHudCacheTourneyType'] = """DELETE FROM HudCache WHERE tourneyTypeId = %s"""
        self.query['clearCardsCacheTourneyType'] = """DELETE FROM CardsCache WHERE tourneyTypeId = %s"""
        self.query['clearPositionsCacheTourneyType'] = """DELETE FROM PositionsCache WHERE tourneyTypeId = %s"""  
        
        self.query['fetchNewHudCacheTourneyTypeIds'] = """SELECT TT.id
                                                    FROM TourneyTypes TT
                                                    LEFT OUTER JOIN HudCache HC ON (TT.id = HC.tourneyTypeId)
                                                    WHERE HC.tourneyTypeId is NULL
                """
                
        self.query['fetchNewCardsCacheTourneyTypeIds'] = """SELECT TT.id
                                                    FROM TourneyTypes TT
                                                    LEFT OUTER JOIN CardsCache CC ON (TT.id = CC.tourneyTypeId)
                                                    WHERE CC.tourneyTypeId is NULL
                """
                
        self.query['fetchNewPositionsCacheTourneyTypeIds'] = """SELECT TT.id
                                                    FROM TourneyTypes TT
                                                    LEFT OUTER JOIN PositionsCache PC ON (TT.id = PC.tourneyTypeId)
                                                    WHERE PC.tourneyTypeId is NULL
                """
        
        self.query['clearCardsCacheWeeksMonths'] = """DELETE FROM CardsCache WHERE weekId = %s AND monthId = %s"""
        self.query['clearPositionsCacheWeeksMonths'] = """DELETE FROM PositionsCache WHERE weekId = %s AND monthId = %s"""  
        
        self.query['selectSessionWithWeekId'] = """SELECT id FROM Sessions WHERE weekId = %s"""
        self.query['selectSessionWithMonthId'] = """SELECT id FROM Sessions WHERE monthId = %s"""
        
        self.query['deleteWeekId'] = """DELETE FROM Weeks WHERE id = %s"""
        self.query['deleteMonthId'] = """DELETE FROM Months WHERE id = %s"""
        
        self.query['fetchNewCardsCacheWeeksMonths'] = """SELECT SCG.weekId, SCG.monthId
                                            FROM (SELECT DISTINCT weekId, monthId FROM Sessions) SCG
                                            LEFT OUTER JOIN CardsCache CC ON (SCG.weekId = CC.weekId AND SCG.monthId = CC.monthId)
                                            WHERE CC.weekId is NULL OR CC.monthId is NULL
        """
        
        self.query['fetchNewPositionsCacheWeeksMonths'] = """SELECT SCG.weekId, SCG.monthId
                                            FROM (SELECT DISTINCT weekId, monthId FROM Sessions) SCG
                                            LEFT OUTER JOIN PositionsCache PC ON (SCG.weekId = PC.weekId AND SCG.monthId = PC.monthId)
                                            WHERE PC.weekId is NULL OR PC.monthId is NULL
        """
        
            

        if db_server == 'mysql':
            self.query['rebuildCache'] = """insert into <insert>
                ,n
                ,street0VPIChance
                ,street0VPI
                ,street0AggrChance
                ,street0Aggr
                ,street0CalledRaiseChance
                ,street0CalledRaiseDone
                ,street0_2BChance
                ,street0_2BDone
                ,street0_3BChance
                ,street0_3BDone
                ,street0_4BChance
                ,street0_4BDone
                ,street0_C4BChance
                ,street0_C4BDone
                ,street0_FoldTo2BChance
                ,street0_FoldTo2BDone
                ,street0_FoldTo3BChance
                ,street0_FoldTo3BDone
                ,street0_FoldTo4BChance
                ,street0_FoldTo4BDone
                ,street0_SqueezeChance
                ,street0_SqueezeDone
                ,raiseToStealChance
                ,raiseToStealDone
                ,stealChance
                ,stealDone
                ,success_Steal
                ,street1Seen
                ,street2Seen
                ,street3Seen
                ,street4Seen
                ,sawShowdown
                ,street1Aggr
                ,street2Aggr
                ,street3Aggr
                ,street4Aggr
                ,otherRaisedStreet0
                ,otherRaisedStreet1
                ,otherRaisedStreet2
                ,otherRaisedStreet3
                ,otherRaisedStreet4
                ,foldToOtherRaisedStreet0
                ,foldToOtherRaisedStreet1
                ,foldToOtherRaisedStreet2
                ,foldToOtherRaisedStreet3
                ,foldToOtherRaisedStreet4
                ,wonWhenSeenStreet1
                ,wonWhenSeenStreet2
                ,wonWhenSeenStreet3
                ,wonWhenSeenStreet4
                ,wonAtSD
                ,raiseFirstInChance
                ,raisedFirstIn
                ,foldBbToStealChance
                ,foldedBbToSteal
                ,foldSbToStealChance
                ,foldedSbToSteal
                ,street1CBChance
                ,street1CBDone
                ,street2CBChance
                ,street2CBDone
                ,street3CBChance
                ,street3CBDone
                ,street4CBChance
                ,street4CBDone
                ,foldToStreet1CBChance
                ,foldToStreet1CBDone
                ,foldToStreet2CBChance
                ,foldToStreet2CBDone
                ,foldToStreet3CBChance
                ,foldToStreet3CBDone
                ,foldToStreet4CBChance
                ,foldToStreet4CBDone
                ,common
                ,committed
                ,winnings
                ,rake
                ,rakeDealt
                ,rakeContributed
                ,rakeWeighted
                ,totalProfit
                ,allInEV
                ,showdownWinnings
                ,nonShowdownWinnings
                ,street1CheckCallRaiseChance
                ,street1CheckCallDone
                ,street1CheckRaiseDone
                ,street2CheckCallRaiseChance
                ,street2CheckCallDone
                ,street2CheckRaiseDone
                ,street3CheckCallRaiseChance
                ,street3CheckCallDone
                ,street3CheckRaiseDone
                ,street4CheckCallRaiseChance
                ,street4CheckCallDone
                ,street4CheckRaiseDone
                ,street0Calls
                ,street1Calls
                ,street2Calls
                ,street3Calls
                ,street4Calls
                ,street0Bets
                ,street1Bets
                ,street2Bets
                ,street3Bets
                ,street4Bets
                ,street0Raises
                ,street1Raises
                ,street2Raises
                ,street3Raises
                ,street4Raises
                ,street1Discards
                ,street2Discards
                ,street3Discards
                )
                SELECT <select>
                      ,count(1)
                      ,sum(street0VPIChance)
                      ,sum(street0VPI)
                      ,sum(street0AggrChance)
                      ,sum(street0Aggr)
                      ,sum(street0CalledRaiseChance)
                      ,sum(street0CalledRaiseDone)
                      ,sum(street0_2BChance)
                      ,sum(street0_2BDone)
                      ,sum(street0_3BChance)
                      ,sum(street0_3BDone)
                      ,sum(street0_4BChance)
                      ,sum(street0_4BDone)
                      ,sum(street0_C4BChance)
                      ,sum(street0_C4BDone)
                      ,sum(street0_FoldTo2BChance)
                      ,sum(street0_FoldTo2BDone)
                      ,sum(street0_FoldTo3BChance)
                      ,sum(street0_FoldTo3BDone)
                      ,sum(street0_FoldTo4BChance)
                      ,sum(street0_FoldTo4BDone)
                      ,sum(street0_SqueezeChance)
                      ,sum(street0_SqueezeDone)
                      ,sum(raiseToStealChance)
                      ,sum(raiseToStealDone)
                      ,sum(stealChance)
                      ,sum(stealDone)
                      ,sum(success_Steal)
                      ,sum(street1Seen)
                      ,sum(street2Seen)
                      ,sum(street3Seen)
                      ,sum(street4Seen)
                      ,sum(sawShowdown)
                      ,sum(street1Aggr)
                      ,sum(street2Aggr)
                      ,sum(street3Aggr)
                      ,sum(street4Aggr)
                      ,sum(otherRaisedStreet0)
                      ,sum(otherRaisedStreet1)
                      ,sum(otherRaisedStreet2)
                      ,sum(otherRaisedStreet3)
                      ,sum(otherRaisedStreet4)
                      ,sum(foldToOtherRaisedStreet0)
                      ,sum(foldToOtherRaisedStreet1)
                      ,sum(foldToOtherRaisedStreet2)
                      ,sum(foldToOtherRaisedStreet3)
                      ,sum(foldToOtherRaisedStreet4)
                      ,sum(wonWhenSeenStreet1)
                      ,sum(wonWhenSeenStreet2)
                      ,sum(wonWhenSeenStreet3)
                      ,sum(wonWhenSeenStreet4)
                      ,sum(wonAtSD)
                      ,sum(raiseFirstInChance)
                      ,sum(raisedFirstIn)
                      ,sum(foldBbToStealChance)
                      ,sum(foldedBbToSteal)
                      ,sum(foldSbToStealChance)
                      ,sum(foldedSbToSteal)
                      ,sum(street1CBChance)
                      ,sum(street1CBDone)
                      ,sum(street2CBChance)
                      ,sum(street2CBDone)
                      ,sum(street3CBChance)
                      ,sum(street3CBDone)
                      ,sum(street4CBChance)
                      ,sum(street4CBDone)
                      ,sum(foldToStreet1CBChance)
                      ,sum(foldToStreet1CBDone)
                      ,sum(foldToStreet2CBChance)
                      ,sum(foldToStreet2CBDone)
                      ,sum(foldToStreet3CBChance)
                      ,sum(foldToStreet3CBDone)
                      ,sum(foldToStreet4CBChance)
                      ,sum(foldToStreet4CBDone)
                      ,sum(common)
                      ,sum(committed)
                      ,sum(winnings)
                      ,sum(rake)
                      ,sum(rakeDealt)
                      ,sum(rakeContributed)
                      ,sum(rakeWeighted)
                      ,sum(totalProfit)
                      ,sum(allInEV)
                      ,sum(case when sawShowdown = 1 then totalProfit else 0 end)
                      ,sum(case when sawShowdown = 0 then totalProfit else 0 end)
                      ,sum(street1CheckCallRaiseChance)
                      ,sum(street1CheckCallDone)
                      ,sum(street1CheckRaiseDone)
                      ,sum(street2CheckCallRaiseChance)
                      ,sum(street2CheckCallDone)
                      ,sum(street2CheckRaiseDone)
                      ,sum(street3CheckCallRaiseChance)
                      ,sum(street3CheckCallDone)
                      ,sum(street3CheckRaiseDone)
                      ,sum(street4CheckCallRaiseChance)
                      ,sum(street4CheckCallDone)
                      ,sum(street4CheckRaiseDone)
                      ,sum(street0Calls)
                      ,sum(street1Calls)
                      ,sum(street2Calls)
                      ,sum(street3Calls)
                      ,sum(street4Calls)
                      ,sum(street0Bets)
                      ,sum(street1Bets)
                      ,sum(street2Bets)
                      ,sum(street3Bets)
                      ,sum(street4Bets)
                      ,sum(hp.street0Raises)
                      ,sum(hp.street1Raises)
                      ,sum(hp.street2Raises)
                      ,sum(hp.street3Raises)
                      ,sum(hp.street4Raises)
                      ,sum(street1Discards)
                      ,sum(street2Discards)
                      ,sum(street3Discards)
                FROM Hands h
                INNER JOIN HandsPlayers hp ON (h.id = hp.handId<hero_join>)
                INNER JOIN Gametypes g ON (h.gametypeId = g.id)
                <sessions_join_clause>
                <tourney_join_clause>
                <where_clause>
                GROUP BY <group>
"""
        elif db_server == 'postgresql':
            self.query['rebuildCache'] = """insert into <insert>
                ,n
                ,street0VPIChance
                ,street0VPI
                ,street0AggrChance
                ,street0Aggr
                ,street0CalledRaiseChance
                ,street0CalledRaiseDone
                ,street0_2BChance
                ,street0_2BDone
                ,street0_3BChance
                ,street0_3BDone
                ,street0_4BChance
                ,street0_4BDone
                ,street0_C4BChance
                ,street0_C4BDone
                ,street0_FoldTo2BChance
                ,street0_FoldTo2BDone
                ,street0_FoldTo3BChance
                ,street0_FoldTo3BDone
                ,street0_FoldTo4BChance
                ,street0_FoldTo4BDone
                ,street0_SqueezeChance
                ,street0_SqueezeDone
                ,raiseToStealChance
                ,raiseToStealDone
                ,stealChance
                ,stealDone
                ,success_Steal
                ,street1Seen
                ,street2Seen
                ,street3Seen
                ,street4Seen
                ,sawShowdown
                ,street1Aggr
                ,street2Aggr
                ,street3Aggr
                ,street4Aggr
                ,otherRaisedStreet0
                ,otherRaisedStreet1
                ,otherRaisedStreet2
                ,otherRaisedStreet3
                ,otherRaisedStreet4
                ,foldToOtherRaisedStreet0
                ,foldToOtherRaisedStreet1
                ,foldToOtherRaisedStreet2
                ,foldToOtherRaisedStreet3
                ,foldToOtherRaisedStreet4                
                ,wonWhenSeenStreet1
                ,wonWhenSeenStreet2
                ,wonWhenSeenStreet3
                ,wonWhenSeenStreet4
                ,wonAtSD
                ,raiseFirstInChance
                ,raisedFirstIn
                ,foldBbToStealChance
                ,foldedBbToSteal
                ,foldSbToStealChance
                ,foldedSbToSteal
                ,street1CBChance
                ,street1CBDone
                ,street2CBChance
                ,street2CBDone
                ,street3CBChance
                ,street3CBDone
                ,street4CBChance
                ,street4CBDone
                ,foldToStreet1CBChance
                ,foldToStreet1CBDone
                ,foldToStreet2CBChance
                ,foldToStreet2CBDone
                ,foldToStreet3CBChance
                ,foldToStreet3CBDone
                ,foldToStreet4CBChance
                ,foldToStreet4CBDone
                ,common
                ,committed
                ,winnings
                ,rake
                ,rakeDealt
                ,rakeContributed
                ,rakeWeighted
                ,totalProfit
                ,allInEV
                ,showdownWinnings
                ,nonShowdownWinnings
                ,street1CheckCallRaiseChance
                ,street1CheckCallDone
                ,street1CheckRaiseDone
                ,street2CheckCallRaiseChance
                ,street2CheckCallDone
                ,street2CheckRaiseDone
                ,street3CheckCallRaiseChance
                ,street3CheckCallDone
                ,street3CheckRaiseDone
                ,street4CheckCallRaiseChance
                ,street4CheckCallDone
                ,street4CheckRaiseDone
                ,street0Calls
                ,street1Calls
                ,street2Calls
                ,street3Calls
                ,street4Calls
                ,street0Bets
                ,street1Bets
                ,street2Bets
                ,street3Bets
                ,street4Bets
                ,street0Raises
                ,street1Raises
                ,street2Raises
                ,street3Raises
                ,street4Raises
                ,street1Discards
                ,street2Discards
                ,street3Discards
                )
                SELECT <select>
                      ,count(1)
                      ,sum(CAST(street0VPIChance as integer))
                      ,sum(CAST(street0VPI as integer))
                      ,sum(CAST(street0AggrChance as integer))
                      ,sum(CAST(street0Aggr as integer))
                      ,sum(CAST(street0CalledRaiseChance as integer))
                      ,sum(CAST(street0CalledRaiseDone as integer))
                      ,sum(CAST(street0_2BChance as integer))
                      ,sum(CAST(street0_2BDone as integer))
                      ,sum(CAST(street0_3BChance as integer))
                      ,sum(CAST(street0_3BDone as integer))
                      ,sum(CAST(street0_4BChance as integer))
                      ,sum(CAST(street0_4BDone as integer))
                      ,sum(CAST(street0_C4BChance as integer))
                      ,sum(CAST(street0_C4BDone as integer))
                      ,sum(CAST(street0_FoldTo2BChance as integer))
                      ,sum(CAST(street0_FoldTo2BDone as integer))
                      ,sum(CAST(street0_FoldTo3BChance as integer))
                      ,sum(CAST(street0_FoldTo3BDone as integer))
                      ,sum(CAST(street0_FoldTo4BChance as integer))
                      ,sum(CAST(street0_FoldTo4BDone as integer))
                      ,sum(CAST(street0_SqueezeChance as integer))
                      ,sum(CAST(street0_SqueezeDone as integer))
                      ,sum(CAST(raiseToStealChance as integer))
                      ,sum(CAST(raiseToStealDone as integer))
                      ,sum(CAST(stealChance as integer))
                      ,sum(CAST(stealDone as integer))
                      ,sum(CAST(success_Steal as integer))
                      ,sum(CAST(street1Seen as integer))
                      ,sum(CAST(street2Seen as integer))
                      ,sum(CAST(street3Seen as integer))
                      ,sum(CAST(street4Seen as integer))
                      ,sum(CAST(sawShowdown as integer))
                      ,sum(CAST(street1Aggr as integer))
                      ,sum(CAST(street2Aggr as integer))
                      ,sum(CAST(street3Aggr as integer))
                      ,sum(CAST(street4Aggr as integer))
                      ,sum(CAST(otherRaisedStreet0 as integer))
                      ,sum(CAST(otherRaisedStreet1 as integer))
                      ,sum(CAST(otherRaisedStreet2 as integer))
                      ,sum(CAST(otherRaisedStreet3 as integer))
                      ,sum(CAST(otherRaisedStreet4 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet0 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet1 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet2 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet3 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet4 as integer))                      
                      ,sum(CAST(wonWhenSeenStreet1 as integer))
                      ,sum(CAST(wonWhenSeenStreet2 as integer))
                      ,sum(CAST(wonWhenSeenStreet3 as integer))
                      ,sum(CAST(wonWhenSeenStreet4 as integer))
                      ,sum(CAST(wonAtSD as integer))
                      ,sum(CAST(raiseFirstInChance as integer))
                      ,sum(CAST(raisedFirstIn as integer))
                      ,sum(CAST(foldBbToStealChance as integer))
                      ,sum(CAST(foldedBbToSteal as integer))
                      ,sum(CAST(foldSbToStealChance as integer))
                      ,sum(CAST(foldedSbToSteal as integer))
                      ,sum(CAST(street1CBChance as integer))
                      ,sum(CAST(street1CBDone as integer))
                      ,sum(CAST(street2CBChance as integer))
                      ,sum(CAST(street2CBDone as integer))
                      ,sum(CAST(street3CBChance as integer))
                      ,sum(CAST(street3CBDone as integer))
                      ,sum(CAST(street4CBChance as integer))
                      ,sum(CAST(street4CBDone as integer))
                      ,sum(CAST(foldToStreet1CBChance as integer))
                      ,sum(CAST(foldToStreet1CBDone as integer))
                      ,sum(CAST(foldToStreet2CBChance as integer))
                      ,sum(CAST(foldToStreet2CBDone as integer))
                      ,sum(CAST(foldToStreet3CBChance as integer))
                      ,sum(CAST(foldToStreet3CBDone as integer))
                      ,sum(CAST(foldToStreet4CBChance as integer))
                      ,sum(CAST(foldToStreet4CBDone as integer))
                      ,sum(common)
                      ,sum(committed)
                      ,sum(winnings)
                      ,sum(rake)
                      ,sum(rakeDealt)
                      ,sum(rakeContributed)
                      ,sum(rakeWeighted)
                      ,sum(totalProfit)
                      ,sum(allInEV)
                      ,sum(case when sawShowdown then totalProfit else 0 end)
                      ,sum(case when sawShowdown then 0 else totalProfit end)
                      ,sum(CAST(street1CheckCallRaiseChance as integer))
                      ,sum(CAST(street1CheckCallDone as integer))
                      ,sum(CAST(street1CheckRaiseDone as integer))
                      ,sum(CAST(street2CheckCallRaiseChance as integer))
                      ,sum(CAST(street2CheckCallDone as integer))
                      ,sum(CAST(street2CheckRaiseDone as integer))
                      ,sum(CAST(street3CheckCallRaiseChance as integer))
                      ,sum(CAST(street3CheckCallDone as integer))
                      ,sum(CAST(street3CheckRaiseDone as integer))
                      ,sum(CAST(street4CheckCallRaiseChance as integer))
                      ,sum(CAST(street4CheckCallDone as integer))
                      ,sum(CAST(street4CheckRaiseDone as integer))
                      ,sum(CAST(street0Calls as integer))
                      ,sum(CAST(street1Calls as integer))
                      ,sum(CAST(street2Calls as integer))
                      ,sum(CAST(street3Calls as integer))
                      ,sum(CAST(street4Calls as integer))
                      ,sum(CAST(street0Bets as integer))
                      ,sum(CAST(street1Bets as integer))
                      ,sum(CAST(street2Bets as integer))
                      ,sum(CAST(street3Bets as integer))
                      ,sum(CAST(street4Bets as integer))
                      ,sum(CAST(hp.street0Raises as integer))
                      ,sum(CAST(hp.street1Raises as integer))
                      ,sum(CAST(hp.street2Raises as integer))
                      ,sum(CAST(hp.street3Raises as integer))
                      ,sum(CAST(hp.street4Raises as integer))
                      ,sum(CAST(street1Discards as integer))
                      ,sum(CAST(street2Discards as integer))
                      ,sum(CAST(street3Discards as integer))
                FROM Hands h
                INNER JOIN HandsPlayers hp ON (h.id = hp.handId<hero_join>)
                INNER JOIN Gametypes g ON (h.gametypeId = g.id)
                <sessions_join_clause>
                <tourney_join_clause>
                <where_clause>
                GROUP BY <group>
"""
        elif db_server == 'sqlite':
            self.query['rebuildCache'] = """insert into <insert>
                ,n
                ,street0VPIChance
                ,street0VPI
                ,street0AggrChance
                ,street0Aggr
                ,street0CalledRaiseChance
                ,street0CalledRaiseDone
                ,street0_2BChance
                ,street0_2BDone
                ,street0_3BChance
                ,street0_3BDone
                ,street0_4BChance
                ,street0_4BDone
                ,street0_C4BChance
                ,street0_C4BDone
                ,street0_FoldTo2BChance
                ,street0_FoldTo2BDone
                ,street0_FoldTo3BChance
                ,street0_FoldTo3BDone
                ,street0_FoldTo4BChance
                ,street0_FoldTo4BDone
                ,street0_SqueezeChance
                ,street0_SqueezeDone
                ,raiseToStealChance
                ,raiseToStealDone
                ,stealChance
                ,stealDone
                ,success_Steal
                ,street1Seen
                ,street2Seen
                ,street3Seen
                ,street4Seen
                ,sawShowdown
                ,street1Aggr
                ,street2Aggr
                ,street3Aggr
                ,street4Aggr
                ,otherRaisedStreet0
                ,otherRaisedStreet1
                ,otherRaisedStreet2
                ,otherRaisedStreet3
                ,otherRaisedStreet4
                ,foldToOtherRaisedStreet0
                ,foldToOtherRaisedStreet1
                ,foldToOtherRaisedStreet2
                ,foldToOtherRaisedStreet3
                ,foldToOtherRaisedStreet4
                ,wonWhenSeenStreet1
                ,wonWhenSeenStreet2
                ,wonWhenSeenStreet3
                ,wonWhenSeenStreet4
                ,wonAtSD
                ,raiseFirstInChance
                ,raisedFirstIn
                ,foldBbToStealChance
                ,foldedBbToSteal
                ,foldSbToStealChance
                ,foldedSbToSteal
                ,street1CBChance
                ,street1CBDone
                ,street2CBChance
                ,street2CBDone
                ,street3CBChance
                ,street3CBDone
                ,street4CBChance
                ,street4CBDone
                ,foldToStreet1CBChance
                ,foldToStreet1CBDone
                ,foldToStreet2CBChance
                ,foldToStreet2CBDone
                ,foldToStreet3CBChance
                ,foldToStreet3CBDone
                ,foldToStreet4CBChance
                ,foldToStreet4CBDone
                ,common
                ,committed
                ,winnings
                ,rake
                ,rakeDealt
                ,rakeContributed
                ,rakeWeighted
                ,totalProfit
                ,allInEV
                ,showdownWinnings
                ,nonShowdownWinnings
                ,street1CheckCallRaiseChance
                ,street1CheckCallDone
                ,street1CheckRaiseDone
                ,street2CheckCallRaiseChance
                ,street2CheckCallDone
                ,street2CheckRaiseDone
                ,street3CheckCallRaiseChance
                ,street3CheckCallDone
                ,street3CheckRaiseDone
                ,street4CheckCallRaiseChance
                ,street4CheckCallDone
                ,street4CheckRaiseDone
                ,street0Calls
                ,street1Calls
                ,street2Calls
                ,street3Calls
                ,street4Calls
                ,street0Bets
                ,street1Bets
                ,street2Bets
                ,street3Bets
                ,street4Bets
                ,street0Raises
                ,street1Raises
                ,street2Raises
                ,street3Raises
                ,street4Raises
                ,street1Discards
                ,street2Discards
                ,street3Discards
                )
                SELECT <select>
                      ,count(1)
                      ,sum(CAST(street0VPIChance as integer))
                      ,sum(CAST(street0VPI as integer))
                      ,sum(CAST(street0AggrChance as integer))
                      ,sum(CAST(street0Aggr as integer))
                      ,sum(CAST(street0CalledRaiseChance as integer))
                      ,sum(CAST(street0CalledRaiseDone as integer))
                      ,sum(CAST(street0_2BChance as integer))
                      ,sum(CAST(street0_2BDone as integer))
                      ,sum(CAST(street0_3BChance as integer))
                      ,sum(CAST(street0_3BDone as integer))
                      ,sum(CAST(street0_4BChance as integer))
                      ,sum(CAST(street0_4BDone as integer))
                      ,sum(CAST(street0_C4BChance as integer))
                      ,sum(CAST(street0_C4BDone as integer))
                      ,sum(CAST(street0_FoldTo2BChance as integer))
                      ,sum(CAST(street0_FoldTo2BDone as integer))
                      ,sum(CAST(street0_FoldTo3BChance as integer))
                      ,sum(CAST(street0_FoldTo3BDone as integer))
                      ,sum(CAST(street0_FoldTo4BChance as integer))
                      ,sum(CAST(street0_FoldTo4BDone as integer))
                      ,sum(CAST(street0_SqueezeChance as integer))
                      ,sum(CAST(street0_SqueezeDone as integer))
                      ,sum(CAST(raiseToStealChance as integer))
                      ,sum(CAST(raiseToStealDone as integer))
                      ,sum(CAST(stealChance as integer))
                      ,sum(CAST(stealDone as integer))
                      ,sum(CAST(success_Steal as integer))
                      ,sum(CAST(street1Seen as integer))
                      ,sum(CAST(street2Seen as integer))
                      ,sum(CAST(street3Seen as integer))
                      ,sum(CAST(street4Seen as integer))
                      ,sum(CAST(sawShowdown as integer))
                      ,sum(CAST(street1Aggr as integer))
                      ,sum(CAST(street2Aggr as integer))
                      ,sum(CAST(street3Aggr as integer))
                      ,sum(CAST(street4Aggr as integer))
                      ,sum(CAST(otherRaisedStreet0 as integer))
                      ,sum(CAST(otherRaisedStreet1 as integer))
                      ,sum(CAST(otherRaisedStreet2 as integer))
                      ,sum(CAST(otherRaisedStreet3 as integer))
                      ,sum(CAST(otherRaisedStreet4 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet0 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet1 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet2 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet3 as integer))
                      ,sum(CAST(foldToOtherRaisedStreet4 as integer))
                      ,sum(CAST(wonWhenSeenStreet1 as integer))
                      ,sum(CAST(wonWhenSeenStreet2 as integer))
                      ,sum(CAST(wonWhenSeenStreet3 as integer))
                      ,sum(CAST(wonWhenSeenStreet4 as integer))
                      ,sum(CAST(wonAtSD as integer))
                      ,sum(CAST(raiseFirstInChance as integer))
                      ,sum(CAST(raisedFirstIn as integer))
                      ,sum(CAST(foldBbToStealChance as integer))
                      ,sum(CAST(foldedBbToSteal as integer))
                      ,sum(CAST(foldSbToStealChance as integer))
                      ,sum(CAST(foldedSbToSteal as integer))
                      ,sum(CAST(street1CBChance as integer))
                      ,sum(CAST(street1CBDone as integer))
                      ,sum(CAST(street2CBChance as integer))
                      ,sum(CAST(street2CBDone as integer))
                      ,sum(CAST(street3CBChance as integer))
                      ,sum(CAST(street3CBDone as integer))
                      ,sum(CAST(street4CBChance as integer))
                      ,sum(CAST(street4CBDone as integer))
                      ,sum(CAST(foldToStreet1CBChance as integer))
                      ,sum(CAST(foldToStreet1CBDone as integer))
                      ,sum(CAST(foldToStreet2CBChance as integer))
                      ,sum(CAST(foldToStreet2CBDone as integer))
                      ,sum(CAST(foldToStreet3CBChance as integer))
                      ,sum(CAST(foldToStreet3CBDone as integer))
                      ,sum(CAST(foldToStreet4CBChance as integer))
                      ,sum(CAST(foldToStreet4CBDone as integer))
                      ,sum(CAST(common as integer))
                      ,sum(CAST(committed as integer))
                      ,sum(CAST(winnings as integer))
                      ,sum(CAST(rake as integer))
                      ,sum(CAST(rakeDealt as integer))
                      ,sum(CAST(rakeContributed as integer))
                      ,sum(CAST(rakeWeighted as integer))
                      ,sum(CAST(totalProfit as integer))
                      ,sum(allInEV)
                      ,sum(CAST(case when sawShowdown = 1 then totalProfit else 0 end as integer))
                      ,sum(CAST(case when sawShowdown = 0 then totalProfit else 0 end as integer))
                      ,sum(CAST(street1CheckCallRaiseChance as integer))
                      ,sum(CAST(street1CheckCallDone as integer))
                      ,sum(CAST(street1CheckRaiseDone as integer))
                      ,sum(CAST(street2CheckCallRaiseChance as integer))
                      ,sum(CAST(street2CheckCallDone as integer))
                      ,sum(CAST(street2CheckRaiseDone as integer))
                      ,sum(CAST(street3CheckCallRaiseChance as integer))
                      ,sum(CAST(street3CheckCallDone as integer))
                      ,sum(CAST(street3CheckRaiseDone as integer))
                      ,sum(CAST(street4CheckCallRaiseChance as integer))
                      ,sum(CAST(street4CheckCallDone as integer))
                      ,sum(CAST(street4CheckRaiseDone as integer))
                      ,sum(CAST(street0Calls as integer))
                      ,sum(CAST(street1Calls as integer))
                      ,sum(CAST(street2Calls as integer))
                      ,sum(CAST(street3Calls as integer))
                      ,sum(CAST(street4Calls as integer))
                      ,sum(CAST(street0Bets as integer))
                      ,sum(CAST(street1Bets as integer))
                      ,sum(CAST(street2Bets as integer))
                      ,sum(CAST(street3Bets as integer))
                      ,sum(CAST(street4Bets as integer))
                      ,sum(CAST(hp.street0Raises as integer))
                      ,sum(CAST(hp.street1Raises as integer))
                      ,sum(CAST(hp.street2Raises as integer))
                      ,sum(CAST(hp.street3Raises as integer))
                      ,sum(CAST(hp.street4Raises as integer))
                      ,sum(CAST(street1Discards as integer))
                      ,sum(CAST(street2Discards as integer))
                      ,sum(CAST(street3Discards as integer))
                FROM Hands h
                INNER JOIN HandsPlayers hp ON (h.id = hp.handId<hero_join>)
                INNER JOIN Gametypes g ON (h.gametypeId = g.id)
                <sessions_join_clause>
                <tourney_join_clause>
                <where_clause>
                GROUP BY <group>
"""


        self.query['insert_hudcache'] = """insert into HudCache (
                gametypeId,
                playerId,
                seats,
                position,
                tourneyTypeId,
                styleKey,
                n,
                street0VPIChance,
                street0VPI,
                street0AggrChance,
                street0Aggr,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_2BChance,
                street0_2BDone,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                showdownWinnings,
                nonShowdownWinnings,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)"""

        self.query['update_hudcache'] = """
            UPDATE HudCache SET
            n=n+%s,
            street0VPIChance=street0VPIChance+%s,
            street0VPI=street0VPI+%s,
            street0AggrChance=street0AggrChance+%s,
            street0Aggr=street0Aggr+%s,
            street0CalledRaiseChance=street0CalledRaiseChance+%s,
            street0CalledRaiseDone=street0CalledRaiseDone+%s,
            street0_2BChance=street0_2BChance+%s,
            street0_2BDone=street0_2BDone+%s,
            street0_3BChance=street0_3BChance+%s,
            street0_3BDone=street0_3BDone+%s,
            street0_4BChance=street0_4BChance+%s,
            street0_4BDone=street0_4BDone+%s,
            street0_C4BChance=street0_C4BChance+%s,
            street0_C4BDone=street0_C4BDone+%s,
            street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
            street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
            street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
            street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
            street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
            street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
            street0_SqueezeChance=street0_SqueezeChance+%s,
            street0_SqueezeDone=street0_SqueezeDone+%s,
            raiseToStealChance=raiseToStealChance+%s,
            raiseToStealDone=raiseToStealDone+%s,
            stealChance=stealChance+%s,
            stealDone=stealDone+%s,
            success_Steal=success_Steal+%s,
            street1Seen=street1Seen+%s,
            street2Seen=street2Seen+%s,
            street3Seen=street3Seen+%s,
            street4Seen=street4Seen+%s,
            sawShowdown=sawShowdown+%s,
            street1Aggr=street1Aggr+%s,
            street2Aggr=street2Aggr+%s,
            street3Aggr=street3Aggr+%s,
            street4Aggr=street4Aggr+%s,
            otherRaisedStreet0=otherRaisedStreet0+%s,
            otherRaisedStreet1=otherRaisedStreet1+%s,
            otherRaisedStreet2=otherRaisedStreet2+%s,
            otherRaisedStreet3=otherRaisedStreet3+%s,
            otherRaisedStreet4=otherRaisedStreet4+%s,
            foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
            foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
            foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
            foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
            foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
            wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
            wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
            wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
            wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
            wonAtSD=wonAtSD+%s,
            raiseFirstInChance=raiseFirstInChance+%s,
            raisedFirstIn=raisedFirstIn+%s,
            foldBbToStealChance=foldBbToStealChance+%s,
            foldedBbToSteal=foldedBbToSteal+%s,
            foldSbToStealChance=foldSbToStealChance+%s,
            foldedSbToSteal=foldedSbToSteal+%s,
            street1CBChance=street1CBChance+%s,
            street1CBDone=street1CBDone+%s,
            street2CBChance=street2CBChance+%s,
            street2CBDone=street2CBDone+%s,
            street3CBChance=street3CBChance+%s,
            street3CBDone=street3CBDone+%s,
            street4CBChance=street4CBChance+%s,
            street4CBDone=street4CBDone+%s,
            foldToStreet1CBChance=foldToStreet1CBChance+%s,
            foldToStreet1CBDone=foldToStreet1CBDone+%s,
            foldToStreet2CBChance=foldToStreet2CBChance+%s,
            foldToStreet2CBDone=foldToStreet2CBDone+%s,
            foldToStreet3CBChance=foldToStreet3CBChance+%s,
            foldToStreet3CBDone=foldToStreet3CBDone+%s,
            foldToStreet4CBChance=foldToStreet4CBChance+%s,
            foldToStreet4CBDone=foldToStreet4CBDone+%s,
            common=common+%s,
            committed=committed+%s,
            winnings=winnings+%s,
            rake=rake+%s,
            rakeDealt=rakeDealt+%s,
            rakeContributed=rakeContributed+%s,
            rakeWeighted=rakeWeighted+%s,
            totalProfit=totalProfit+%s,
            allInEV=allInEV+%s,
            showdownWinnings=showdownWinnings+%s,
            nonShowdownWinnings=nonShowdownWinnings+%s,
            street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
            street1CheckCallDone=street1CheckCallDone+%s,
            street1CheckRaiseDone=street1CheckRaiseDone+%s,
            street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
            street2CheckCallDone=street2CheckCallDone+%s,
            street2CheckRaiseDone=street2CheckRaiseDone+%s,
            street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
            street3CheckCallDone=street3CheckCallDone+%s,
            street3CheckRaiseDone=street3CheckRaiseDone+%s,
            street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
            street4CheckCallDone=street4CheckCallDone+%s,
            street4CheckRaiseDone=street4CheckRaiseDone+%s,
            street0Calls=street0Calls+%s,
            street1Calls=street1Calls+%s,
            street2Calls=street2Calls+%s,
            street3Calls=street3Calls+%s,
            street4Calls=street4Calls+%s,
            street0Bets=street0Bets+%s, 
            street1Bets=street1Bets+%s,
            street2Bets=street2Bets+%s, 
            street3Bets=street3Bets+%s,
            street4Bets=street4Bets+%s, 
            street0Raises=street0Raises+%s,
            street1Raises=street1Raises+%s,
            street2Raises=street2Raises+%s,
            street3Raises=street3Raises+%s,
            street4Raises=street4Raises+%s,            
            street1Discards=street1Discards+%s,
            street2Discards=street2Discards+%s,
            street3Discards=street3Discards+%s
        WHERE id=%s"""
            
        self.query['select_hudcache_ring'] = """
                    SELECT id
                    FROM HudCache
                    WHERE gametypeId=%s
                    AND   playerId=%s
                    AND   seats=%s
                    AND   position=%s
                    AND   tourneyTypeId is NULL
                    AND   styleKey = %s"""
                    
        self.query['select_hudcache_tour'] = """
                    SELECT id
                    FROM HudCache
                    WHERE gametypeId=%s
                    AND   playerId=%s
                    AND   seats=%s
                    AND   position=%s
                    AND   tourneyTypeId=%s
                    AND   styleKey = %s"""
            
        self.query['get_hero_hudcache_start'] = """select min(hc.styleKey)
                                                   from HudCache hc
                                                   where hc.playerId in <playerid_list>
                                                   and   hc.styleKey like 'd%'"""
                                                   
        ####################################
        # Queries to insert/update cardscache
        ####################################
                                                   
        self.query['insert_cardscache'] = """insert into CardsCache (
                weekId,
                monthId,
                gametypeId,
                tourneyTypeId,
                playerId,
                startCards,
                n,
                street0VPIChance,
                street0VPI,
                street0AggrChance,
                street0Aggr,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_3BChance,
                street0_3BDone,
                street0_2BChance,
                street0_2BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                showdownWinnings,
                nonShowdownWinnings,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)"""

        self.query['update_cardscache'] = """
            UPDATE CardsCache SET
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
        WHERE     id=%s"""
            
        self.query['select_cardscache_ring'] = """
                    SELECT id
                    FROM CardsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId is NULL
                    AND   playerId=%s
                    AND   startCards=%s"""
                    
        self.query['select_cardscache_tour'] = """
                    SELECT id
                    FROM CardsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId=%s
                    AND   playerId=%s
                    AND   startCards=%s"""
                   
        ####################################
        # Queries to insert/update positionscache
        ####################################
                   
        self.query['insert_positionscache'] = """insert into PositionsCache (
                weekId,
                monthId,
                gametypeId,
                tourneyTypeId,
                playerId,
                seats,
                maxPosition,
                position,
                n,
                street0VPIChance,
                street0VPI,
                street0AggrChance,
                street0Aggr,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_2BChance,
                street0_2BDone,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                showdownWinnings,
                nonShowdownWinnings,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                    )"""

        self.query['update_positionscache'] = """
            UPDATE PositionsCache SET
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
        WHERE id=%s"""
            
        self.query['select_positionscache_ring'] = """
                    SELECT id
                    FROM PositionsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId is NULL
                    AND   playerId=%s
                    AND   seats=%s
                    AND   maxPosition=%s
                    AND   position=%s"""
                    
        self.query['select_positionscache_tour'] = """
                    SELECT id
                    FROM PositionsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId=%s
                    AND   playerId=%s
                    AND   seats=%s
                    AND   maxPosition=%s
                    AND   position=%s"""
            
        ####################################
        # Queries to rebuild/modify sessionscache
        ####################################

        self.query['clear_S_H'] = "UPDATE Hands SET sessionId = NULL"
        self.query['clear_S_T'] = "UPDATE Tourneys SET sessionId = NULL"
        self.query['clear_S_SC'] = "UPDATE SessionsCache SET sessionId = NULL"
        self.query['clear_S_TC'] = "UPDATE TourneysCache SET sessionId = NULL"
        self.query['clear_W_S'] = "UPDATE Sessions SET weekId = NULL"
        self.query['clear_M_S'] = "UPDATE Sessions SET monthId = NULL"
        self.query['clearSessionsCache'] = "DELETE FROM SessionsCache WHERE 1"
        self.query['clearTourneysCache'] = "DELETE FROM TourneysCache WHERE 1"
        self.query['clearSessions'] = "DELETE FROM Sessions WHERE 1"
        self.query['clearWeeks'] = "DELETE FROM Weeks WHERE 1"
        self.query['clearMonths'] = "DELETE FROM Months WHERE 1"
        self.query['update_RSC_H'] = "UPDATE Hands SET sessionId = %s WHERE id = %s"
                    
        ####################################
        # select
        ####################################
        
        self.query['select_S_all'] = """
                    SELECT SC.id as id,
                    sessionStart,
                    weekStart,
                    monthStart,
                    weekId,
                    monthId
                    FROM Sessions SC
                    INNER JOIN Weeks WC ON (SC.weekId = WC.id)
                    INNER JOIN Months MC ON (SC.monthId = MC.id)
                    WHERE sessionEnd>=%s
                    AND sessionStart<=%s"""
        
        self.query['select_S'] = """
                    SELECT SC.id as id,
                    sessionStart,
                    sessionEnd,
                    weekStart,
                    monthStart,
                    weekId,
                    monthId
                    FROM Sessions SC
                    INNER JOIN Weeks WC ON (SC.weekId = WC.id)
                    INNER JOIN Months MC ON (SC.monthId = MC.id)
                    WHERE (sessionEnd>=%s AND sessionStart<=%s)
                    <TOURSELECT>"""
                    
        self.query['select_W'] = """
                    SELECT id
                    FROM Weeks
                    WHERE weekStart = %s"""
        
        self.query['select_M'] = """
                    SELECT id
                    FROM Months
                    WHERE monthStart = %s"""
                    
        self.query['select_SC'] = """
                    SELECT id,
                    sessionId,
                    startTime,
                    endTime,
                    n,
                    street0VPIChance,
                    street0VPI,
                    street0AggrChance,
                    street0Aggr,
                    street0CalledRaiseChance,
                    street0CalledRaiseDone,
                    street0_2BChance,
                    street0_2BDone,
                    street0_3BChance,
                    street0_3BDone,
                    street0_4BChance,
                    street0_4BDone,
                    street0_C4BChance,
                    street0_C4BDone,
                    street0_FoldTo2BChance,
                    street0_FoldTo2BDone,
                    street0_FoldTo3BChance,
                    street0_FoldTo3BDone,
                    street0_FoldTo4BChance,
                    street0_FoldTo4BDone,
                    street0_SqueezeChance,
                    street0_SqueezeDone,
                    raiseToStealChance,
                    raiseToStealDone,
                    stealChance,
                    stealDone,
                    success_Steal,
                    street1Seen,
                    street2Seen,
                    street3Seen,
                    street4Seen,
                    sawShowdown,
                    street1Aggr,
                    street2Aggr,
                    street3Aggr,
                    street4Aggr,
                    otherRaisedStreet0,
                    otherRaisedStreet1,
                    otherRaisedStreet2,
                    otherRaisedStreet3,
                    otherRaisedStreet4,
                    foldToOtherRaisedStreet0,
                    foldToOtherRaisedStreet1,
                    foldToOtherRaisedStreet2,
                    foldToOtherRaisedStreet3,
                    foldToOtherRaisedStreet4,
                    wonWhenSeenStreet1,
                    wonWhenSeenStreet2,
                    wonWhenSeenStreet3,
                    wonWhenSeenStreet4,
                    wonAtSD,
                    raiseFirstInChance,
                    raisedFirstIn,
                    foldBbToStealChance,
                    foldedBbToSteal,
                    foldSbToStealChance,
                    foldedSbToSteal,
                    street1CBChance,
                    street1CBDone,
                    street2CBChance,
                    street2CBDone,
                    street3CBChance,
                    street3CBDone,
                    street4CBChance,
                    street4CBDone,
                    foldToStreet1CBChance,
                    foldToStreet1CBDone,
                    foldToStreet2CBChance,
                    foldToStreet2CBDone,
                    foldToStreet3CBChance,
                    foldToStreet3CBDone,
                    foldToStreet4CBChance,
                    foldToStreet4CBDone,
                    common,
                    committed,
                    winnings,
                    rake,
                    rakeDealt,
                    rakeContributed,
                    rakeWeighted,
                    totalProfit,
                    allInEV,
                    showdownWinnings,
                    nonShowdownWinnings,
                    street1CheckCallRaiseChance,
                    street1CheckCallDone,
                    street1CheckRaiseDone,
                    street2CheckCallRaiseChance,
                    street2CheckCallDone,
                    street2CheckRaiseDone,
                    street3CheckCallRaiseChance,
                    street3CheckCallDone,
                    street3CheckRaiseDone,
                    street4CheckCallRaiseChance,
                    street4CheckCallDone,
                    street4CheckRaiseDone,
                    street0Calls,
                    street1Calls,
                    street2Calls,
                    street3Calls,
                    street4Calls,
                    street0Bets,
                    street1Bets,
                    street2Bets,
                    street3Bets,
                    street4Bets,
                    street0Raises,
                    street1Raises,
                    street2Raises,
                    street3Raises,
                    street4Raises,
                    street1Discards,
                    street2Discards,
                    street3Discards
                    FROM SessionsCache
                    WHERE endTime>=%s
                    AND startTime<=%s
                    AND gametypeId=%s
                    AND playerId=%s"""
                    
        self.query['select_TC'] = """
                    SELECT id, startTime, endTime
                    FROM TourneysCache TC
                    WHERE tourneyId=%s
                    AND playerId=%s"""
                    
        ####################################
        # insert
        ####################################
        
        self.query['insert_W'] = """insert into Weeks (
                    weekStart)
                    values (%s)"""
        
        self.query['insert_M'] = """insert into Months (
                    monthStart)
                    values (%s)"""
                            
        self.query['insert_S'] = """insert into Sessions (
                    weekId,
                    monthId,
                    sessionStart,
                    sessionEnd)
                    values (%s, %s, %s, %s)"""
                            
        self.query['insert_SC'] = """insert into SessionsCache (
                    sessionId,
                    startTime,
                    endTime,
                    gametypeId,
                    playerId,
                    n,
                    street0VPIChance,
                    street0VPI,
                    street0AggrChance,
                    street0Aggr,
                    street0CalledRaiseChance,
                    street0CalledRaiseDone,
                    street0_2BChance,
                    street0_2BDone,
                    street0_3BChance,
                    street0_3BDone,
                    street0_4BChance,
                    street0_4BDone,
                    street0_C4BChance,
                    street0_C4BDone,
                    street0_FoldTo2BChance,
                    street0_FoldTo2BDone,
                    street0_FoldTo3BChance,
                    street0_FoldTo3BDone,
                    street0_FoldTo4BChance,
                    street0_FoldTo4BDone,
                    street0_SqueezeChance,
                    street0_SqueezeDone,
                    raiseToStealChance,
                    raiseToStealDone,
                    stealChance,
                    stealDone,
                    success_Steal,
                    street1Seen,
                    street2Seen,
                    street3Seen,
                    street4Seen,
                    sawShowdown,
                    street1Aggr,
                    street2Aggr,
                    street3Aggr,
                    street4Aggr,
                    otherRaisedStreet0,
                    otherRaisedStreet1,
                    otherRaisedStreet2,
                    otherRaisedStreet3,
                    otherRaisedStreet4,
                    foldToOtherRaisedStreet0,
                    foldToOtherRaisedStreet1,
                    foldToOtherRaisedStreet2,
                    foldToOtherRaisedStreet3,
                    foldToOtherRaisedStreet4,
                    wonWhenSeenStreet1,
                    wonWhenSeenStreet2,
                    wonWhenSeenStreet3,
                    wonWhenSeenStreet4,
                    wonAtSD,
                    raiseFirstInChance,
                    raisedFirstIn,
                    foldBbToStealChance,
                    foldedBbToSteal,
                    foldSbToStealChance,
                    foldedSbToSteal,
                    street1CBChance,
                    street1CBDone,
                    street2CBChance,
                    street2CBDone,
                    street3CBChance,
                    street3CBDone,
                    street4CBChance,
                    street4CBDone,
                    foldToStreet1CBChance,
                    foldToStreet1CBDone,
                    foldToStreet2CBChance,
                    foldToStreet2CBDone,
                    foldToStreet3CBChance,
                    foldToStreet3CBDone,
                    foldToStreet4CBChance,
                    foldToStreet4CBDone,
                    common,
                    committed,
                    winnings,
                    rake,
                    rakeDealt,
                    rakeContributed,
                    rakeWeighted,
                    totalProfit,
                    allInEV,
                    showdownWinnings,
                    nonShowdownWinnings,
                    street1CheckCallRaiseChance,
                    street1CheckCallDone,
                    street1CheckRaiseDone,
                    street2CheckCallRaiseChance,
                    street2CheckCallDone,
                    street2CheckRaiseDone,
                    street3CheckCallRaiseChance,
                    street3CheckCallDone,
                    street3CheckRaiseDone,
                    street4CheckCallRaiseChance,
                    street4CheckCallDone,
                    street4CheckRaiseDone,
                    street0Calls,
                    street1Calls,
                    street2Calls,
                    street3Calls,
                    street4Calls,
                    street0Bets,
                    street1Bets,
                    street2Bets,
                    street3Bets,
                    street4Bets,
                    street0Raises,
                    street1Raises,
                    street2Raises,
                    street3Raises,
                    street4Raises,
                    street1Discards,
                    street2Discards,
                    street3Discards
                    )
                    values (%s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s)"""
                            
        self.query['insert_TC'] = """insert into TourneysCache (
                    sessionId,
                    startTime,
                    endTime,
                    tourneyId,
                    playerId,
                    n,
                    street0VPIChance,
                    street0VPI,
                    street0AggrChance,
                    street0Aggr,
                    street0CalledRaiseChance,
                    street0CalledRaiseDone,
                    street0_2BChance,
                    street0_2BDone,
                    street0_3BChance,
                    street0_3BDone,
                    street0_4BChance,
                    street0_4BDone,
                    street0_C4BChance,
                    street0_C4BDone,
                    street0_FoldTo2BChance,
                    street0_FoldTo2BDone,
                    street0_FoldTo3BChance,
                    street0_FoldTo3BDone,
                    street0_FoldTo4BChance,
                    street0_FoldTo4BDone,
                    street0_SqueezeChance,
                    street0_SqueezeDone,
                    raiseToStealChance,
                    raiseToStealDone,
                    stealChance,
                    stealDone,
                    success_Steal,
                    street1Seen,
                    street2Seen,
                    street3Seen,
                    street4Seen,
                    sawShowdown,
                    street1Aggr,
                    street2Aggr,
                    street3Aggr,
                    street4Aggr,
                    otherRaisedStreet0,
                    otherRaisedStreet1,
                    otherRaisedStreet2,
                    otherRaisedStreet3,
                    otherRaisedStreet4,
                    foldToOtherRaisedStreet0,
                    foldToOtherRaisedStreet1,
                    foldToOtherRaisedStreet2,
                    foldToOtherRaisedStreet3,
                    foldToOtherRaisedStreet4,
                    wonWhenSeenStreet1,
                    wonWhenSeenStreet2,
                    wonWhenSeenStreet3,
                    wonWhenSeenStreet4,
                    wonAtSD,
                    raiseFirstInChance,
                    raisedFirstIn,
                    foldBbToStealChance,
                    foldedBbToSteal,
                    foldSbToStealChance,
                    foldedSbToSteal,
                    street1CBChance,
                    street1CBDone,
                    street2CBChance,
                    street2CBDone,
                    street3CBChance,
                    street3CBDone,
                    street4CBChance,
                    street4CBDone,
                    foldToStreet1CBChance,
                    foldToStreet1CBDone,
                    foldToStreet2CBChance,
                    foldToStreet2CBDone,
                    foldToStreet3CBChance,
                    foldToStreet3CBDone,
                    foldToStreet4CBChance,
                    foldToStreet4CBDone,
                    common,
                    committed,
                    winnings,
                    rake,
                    rakeDealt,
                    rakeContributed,
                    rakeWeighted,
                    totalProfit,
                    allInEV,
                    showdownWinnings,
                    nonShowdownWinnings,
                    street1CheckCallRaiseChance,
                    street1CheckCallDone,
                    street1CheckRaiseDone,
                    street2CheckCallRaiseChance,
                    street2CheckCallDone,
                    street2CheckRaiseDone,
                    street3CheckCallRaiseChance,
                    street3CheckCallDone,
                    street3CheckRaiseDone,
                    street4CheckCallRaiseChance,
                    street4CheckCallDone,
                    street4CheckRaiseDone,
                    street0Calls,
                    street1Calls,
                    street2Calls,
                    street3Calls,
                    street4Calls,
                    street0Bets,
                    street1Bets,
                    street2Bets,
                    street3Bets,
                    street4Bets,
                    street0Raises,
                    street1Raises,
                    street2Raises,
                    street3Raises,
                    street4Raises,
                    street1Discards,
                    street2Discards,
                    street3Discards
                    )
                    values (%s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s)"""
                    
        ####################################
        # update
        ####################################
        
        self.query['update_WM_S'] = """
                    UPDATE Sessions SET
                    weekId=%s,
                    monthId=%s
                    WHERE id=%s"""
                    
        self.query['update_S'] = """
                    UPDATE Sessions SET 
                    weekId=%s,
                    monthId=%s,
                    sessionStart=%s,
                    sessionEnd=%s
                    WHERE id=%s"""
                    
        self.query['update_SC'] = """
                    UPDATE SessionsCache SET
                    startTime=%s,
                    endTime=%s,
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
                    WHERE id=%s"""
                    
        self.query['update_TC'] = """
                    UPDATE TourneysCache SET
                    <UPDATE>
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
                    WHERE tourneyId=%s
                    AND playerId=%s"""
                    
        ####################################
        # delete
        ####################################
                    
        self.query['delete_S'] = """
                    DELETE FROM Sessions
                    WHERE id=%s"""
                    
        self.query['delete_SC'] = """
                    DELETE FROM SessionsCache
                    WHERE id=%s"""
                    
        ####################################
        # update SessionsCache, Hands, Tourneys
        ####################################
                    
        self.query['update_S_SC'] = """
                    UPDATE SessionsCache SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        self.query['update_S_TC'] = """
                    UPDATE TourneysCache SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        self.query['update_S_T'] = """
                    UPDATE Tourneys SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                            
        self.query['update_S_H'] = """
                    UPDATE Hands SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        ####################################
        # update Tourneys w. sessionIds, hands, start/end
        ####################################
                    
        self.query['updateTourneysSessions'] = """
                    UPDATE Tourneys SET
                    sessionId=%s
                    WHERE id=%s"""
        
        ####################################
        # Database management queries
        ####################################

        if db_server == 'mysql':
            self.query['analyze'] = """
            analyze table Actions, Autorates, Backings, Boards, Files, Gametypes, Hands, HandsActions, HandsPlayers, 
                          HandsStove, HudCache, Players, RawHands, RawTourneys, Sessions, Settings, Sites,
                          Tourneys, TourneysPlayers, TourneyTypes
            """
        elif db_server == 'postgresql':
            self.query['analyze'] = "analyze"
        elif db_server == 'sqlite':
            self.query['analyze'] = "analyze"
            

        if db_server == 'mysql':
            self.query['vacuum'] = """
            optimize table Actions, Autorates, Backings, Boards, Files, Gametypes, Hands, HandsActions, HandsPlayers, 
                           HandsStove, HudCache, Players, RawHands, RawTourneys, Sessions, Settings, Sites,
                           Tourneys, TourneysPlayers, TourneyTypes
            """
        elif db_server == 'postgresql':
            self.query['vacuum'] = """ vacuum """
        elif db_server == 'sqlite':
            self.query['vacuum'] = """ vacuum """
            
        if db_server == 'mysql':
            self.query['switchLockOn'] = """
                        UPDATE InsertLock k1, 
                        (SELECT count(locked) as locks FROM InsertLock WHERE locked=True) as k2 SET
                        k1.locked=%s
                        WHERE k1.id=%s
                        AND k2.locks = 0"""
                        
        if db_server == 'mysql':
            self.query['switchLockOff'] = """
                        UPDATE InsertLock SET
                        locked=%s
                        WHERE id=%s"""

        if db_server == 'mysql':
            self.query['lockForInsert'] = """
                lock tables Hands write, HandsPlayers write, HandsActions write, Players write
                          , HudCache write, Gametypes write, Sites write, Tourneys write
                          , TourneysPlayers write, TourneyTypes write, Autorates write
                """
        elif db_server == 'postgresql':
            self.query['lockForInsert'] = ""
        elif db_server == 'sqlite':
            self.query['lockForInsert'] = ""

        self.query['getGametypeFL'] = """SELECT id
                                           FROM Gametypes
                                           WHERE siteId=%s
                                           AND   type=%s
                                           AND   category=%s
                                           AND   limitType=%s
                                           AND   smallBet=%s
                                           AND   bigBet=%s
                                           AND   maxSeats=%s
                                           AND   ante=%s
        """ #TODO: seems odd to have limitType variable in this query

        self.query['getGametypeNL'] = """SELECT id
                                           FROM Gametypes
                                           WHERE siteId=%s
                                           AND   type=%s
                                           AND   category=%s
                                           AND   limitType=%s
                                           AND   currency=%s
                                           AND   mix=%s
                                           AND   smallBlind=%s
                                           AND   bigBlind=%s
                                           AND   maxSeats=%s
                                           AND   ante=%s
                                           AND   buyinType=%s
                                           AND   fast=%s
                                           AND   newToGame=%s
                                           AND   homeGame=%s
                                           AND   split=%s
        """ #TODO: seems odd to have limitType variable in this query

        self.query['insertGameTypes'] = """insert into Gametypes (siteId, currency, type, base, category, limitType, hiLo, mix, 
                                               smallBlind, bigBlind, smallBet, bigBet, maxSeats, ante, buyinType, fast, newToGame, homeGame, split)
                                           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        self.query['isAlreadyInDB'] = """SELECT H.id FROM Hands H
                                         INNER JOIN Gametypes G ON (H.gametypeId = G.id)
                                         WHERE siteHandNo=%s AND G.siteId=%s<heroSeat>
        """
        
        self.query['getTourneyTypeIdByTourneyNo'] = """SELECT tt.id,
                                                              tt.siteId,
                                                              tt.currency,
                                                              tt.buyin,
                                                              tt.fee,
                                                              tt.category,
                                                              tt.limitType,
                                                              tt.maxSeats,
                                                              tt.sng,
                                                              tt.knockout,
                                                              tt.koBounty,
                                                              tt.progressive,
                                                              tt.rebuy,
                                                              tt.rebuyCost,
                                                              tt.addOn,
                                                              tt.addOnCost,
                                                              tt.speed,
                                                              tt.shootout,
                                                              tt.matrix,
                                                              tt.fast,
                                                              tt.stack, 
                                                              tt.step,
                                                              tt.stepNo,
                                                              tt.chance,
                                                              tt.chanceCount,
                                                              tt.multiEntry,
                                                              tt.reEntry,
                                                              tt.homeGame,
                                                              tt.newToGame,
                                                              tt.split,
                                                              tt.fifty50,
                                                              tt.time,
                                                              tt.timeAmt,
                                                              tt.satellite,
                                                              tt.doubleOrNothing,
                                                              tt.cashOut,
                                                              tt.onDemand,
                                                              tt.flighted,
                                                              tt.guarantee,
                                                              tt.guaranteeAmt
                                                    FROM TourneyTypes tt 
                                                    INNER JOIN Tourneys t ON (t.tourneyTypeId = tt.id) 
                                                    WHERE t.siteTourneyNo=%s AND tt.siteId=%s
        """
        
        self.query['getTourneyTypeId'] = """SELECT  id
                                            FROM TourneyTypes
                                            WHERE siteId=%s
                                            AND currency=%s
                                            AND buyin=%s
                                            AND fee=%s
                                            AND category=%s
                                            AND limitType=%s
                                            AND maxSeats=%s
                                            AND sng=%s
                                            AND knockout=%s
                                            AND koBounty=%s
                                            AND progressive=%s
                                            AND rebuy=%s
                                            AND rebuyCost=%s
                                            AND addOn=%s
                                            AND addOnCost=%s
                                            AND speed=%s
                                            AND shootout=%s
                                            AND matrix=%s
                                            AND fast=%s
                                            AND stack=%s
                                            AND step=%s
                                            AND stepNo=%s
                                            AND chance=%s
                                            AND chanceCount=%s
                                            AND multiEntry=%s
                                            AND reEntry=%s
                                            AND homeGame=%s
                                            AND newToGame=%s
                                            AND split=%s
                                            AND fifty50=%s
                                            AND time=%s
                                            AND timeAmt=%s
                                            AND satellite=%s
                                            AND doubleOrNothing=%s
                                            AND cashOut=%s
                                            AND onDemand=%s
                                            AND flighted=%s
                                            AND guarantee=%s
                                            AND guaranteeAmt=%s
        """

        self.query['insertTourneyType'] = """insert into TourneyTypes (
                                                   siteId, currency, buyin, fee, category, limitType, maxSeats, sng, knockout, koBounty, progressive,
                                                   rebuy, rebuyCost, addOn, addOnCost, speed, shootout, matrix, fast,
                                                   stack, step, stepNo, chance, chanceCount, multiEntry, reEntry, homeGame, newToGame, split,
                                                   fifty50, time, timeAmt, satellite, doubleOrNothing, cashOut, onDemand, flighted, guarantee, guaranteeAmt
                                                   )
                                              values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        if db_server == 'sqlite':  
            self.query['updateTourneyTypeId'] = """UPDATE Tourneys
                                                SET tourneyTypeId = %s
                                                WHERE tourneyTypeId in (SELECT id FROM TourneyTypes WHERE siteId=%s)
                                                AND siteTourneyNo=%s
            """
        elif db_server == 'postgresql':
            self.query['updateTourneyTypeId'] = """UPDATE Tourneys t 
                                                SET tourneyTypeId = %s
                                                FROM TourneyTypes tt 
                                                WHERE t.tourneyTypeId = tt.id
                                                AND tt.siteId=%s 
                                                AND t.siteTourneyNo=%s
            """       
        else:
            self.query['updateTourneyTypeId'] = """UPDATE Tourneys t INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                                SET tourneyTypeId = %s
                                                WHERE tt.siteId=%s AND t.siteTourneyNo=%s
            """
        
        self.query['selectTourneyWithTypeId'] = """SELECT id 
                                                FROM Tourneys
                                                WHERE tourneyTypeId = %s
        """
        
        self.query['deleteTourneyTypeId'] = """DELETE FROM TourneyTypes WHERE id = %s
        """

        self.query['getTourneyByTourneyNo'] = """SELECT t.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        WHERE tt.siteId=%s AND t.siteTourneyNo=%s
        """

        self.query['getTourneyInfo'] = """SELECT tt.*, t.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        WHERE s.name=%s AND t.siteTourneyNo=%s
        """

        self.query['getSiteTourneyNos'] = """SELECT t.siteTourneyNo
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        WHERE tt.siteId=%s
        """

        self.query['getTourneyPlayerInfo'] = """SELECT tp.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        INNER JOIN TourneysPlayers tp ON (tp.tourneyId = t.id)
                                        INNER JOIN Players p ON (p.id = tp.playerId)
                                        WHERE s.name=%s AND t.siteTourneyNo=%s AND p.name=%s
        """
        
        self.query['insertTourney'] = """insert into Tourneys (
                                             tourneyTypeId, sessionId, siteTourneyNo, entries, prizepool,
                                             startTime, endTime, tourneyName, totalRebuyCount, totalAddOnCount,
                                             comment, commentTs, added, addedCurrency)
                                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.query['updateTourney'] = """UPDATE Tourneys
                                             SET entries = %s,
                                                 prizepool = %s,
                                                 startTime = %s,
                                                 endTime = %s,
                                                 tourneyName = %s,
                                                 totalRebuyCount = %s,
                                                 totalAddOnCount = %s,
                                                 comment = %s,
                                                 commentTs = %s,
                                                 added = %s,
                                                 addedCurrency = %s
                                        WHERE id=%s
        """
        
        self.query['updateTourneyStart'] = """UPDATE Tourneys
                                             SET startTime = %s
                                        WHERE id=%s
        """
        
        self.query['updateTourneyEnd'] = """UPDATE Tourneys
                                             SET endTime = %s
                                        WHERE id=%s
        """
        
        self.query['getTourneysPlayersByIds'] = """SELECT *
                                                FROM TourneysPlayers
                                                WHERE tourneyId=%s AND playerId=%s AND entryId=%s
        """
        
        self.query['getTourneysPlayersByTourney'] = """SELECT playerId, entryId
                                                       FROM TourneysPlayers
                                                       WHERE tourneyId=%s
        """

        self.query['updateTourneysPlayer'] = """UPDATE TourneysPlayers
                                                 SET rank = %s,
                                                     winnings = %s,
                                                     winningsCurrency = %s,
                                                     rebuyCount = %s,
                                                     addOnCount = %s,
                                                     koCount = %s
                                                 WHERE id=%s
        """

        self.query['updateTourneysPlayerBounties'] = """UPDATE TourneysPlayers
                                                 SET koCount = case when koCount is null then %s else koCount+%s end
                                                 WHERE id=%s
        """

        self.query['insertTourneysPlayer'] = """insert into TourneysPlayers (
                                                    tourneyId,
                                                    playerId,
                                                    entryId,
                                                    rank,
                                                    winnings,
                                                    winningsCurrency,
                                                    rebuyCount,
                                                    addOnCount,
                                                    koCount
                                                )
                                                values (%s, %s, %s, %s, %s, 
                                                        %s, %s, %s, %s)
        """

        self.query['selectHandsPlayersWithWrongTTypeId'] = """SELECT id
                                                              FROM HandsPlayers 
                                                              WHERE tourneyTypeId <> %s AND (TourneysPlayersId+0=%s)
        """

#            self.query['updateHandsPlayersForTTypeId2'] = """UPDATE HandsPlayers 
#                                                            SET tourneyTypeId= %s
#                                                            WHERE (TourneysPlayersId+0=%s)
#            """

        self.query['updateHandsPlayersForTTypeId'] = """UPDATE HandsPlayers 
                                                         SET tourneyTypeId= %s
                                                         WHERE (id=%s)
        """


        self.query['handsPlayersTTypeId_joiner'] = " OR TourneysPlayersId+0="
        self.query['handsPlayersTTypeId_joiner_id'] = " OR id="

        self.query['store_hand'] = """insert into Hands (
                                            tablename,
                                            sitehandno,
                                            tourneyId,
                                            gametypeid,
                                            sessionId,
                                            fileId,
                                            startTime,
                                            importtime,
                                            seats,
                                            heroSeat,
                                            maxPosition,
                                            texture,
                                            playersVpi,
                                            boardcard1,
                                            boardcard2,
                                            boardcard3,
                                            boardcard4,
                                            boardcard5,
                                            runItTwice,
                                            playersAtStreet1,
                                            playersAtStreet2,
                                            playersAtStreet3,
                                            playersAtStreet4,
                                            playersAtShowdown,
                                            street0Raises,
                                            street1Raises,
                                            street2Raises,
                                            street3Raises,
                                            street4Raises,
                                            street0Pot,
                                            street1Pot,
                                            street2Pot,
                                            street3Pot,
                                            street4Pot,
                                            finalPot
                                             )
                                             values
                                              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s)"""


        self.query['store_hands_players'] = """insert into HandsPlayers (
                handId,
                playerId,
                startCash,
                effStack,
                startBounty,
                endBounty,
                seatNo,
                sitout,
                card1,
                card2,
                card3,
                card4,
                card5,
                card6,
                card7,
                card8,
                card9,
                card10,
                card11,
                card12,
                card13,
                card14,
                card15,
                card16,
                card17,
                card18,
                card19,
                card20,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                street0VPIChance,
                street0VPI,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                showed,
                street0AllIn,
                street1AllIn,
                street2AllIn,
                street3AllIn,
                street4AllIn,
                wentAllIn,
                street0AggrChance,
                street0Aggr,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                street1CBChance,
                street2CBChance,
                street3CBChance,
                street4CBChance,
                street1CBDone,
                street2CBDone,
                street3CBDone,
                street4CBDone,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                position,
                street0InPosition,
                street1InPosition,
                street2InPosition,
                street3InPosition,
                street4InPosition,
                street0FirstToAct,
                street1FirstToAct,
                street2FirstToAct,
                street3FirstToAct,
                street4FirstToAct,
                tourneysPlayersId,
                startCards,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_2BChance,
                street0_2BDone,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards,
                handString
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s
                )"""

        self.query['store_hands_actions'] = """insert into HandsActions (
                        handId,
                        playerId,
                        street,
                        actionNo,
                        streetActionNo,
                        actionId,
                        amount,
                        raiseTo,
                        amountCalled,
                        numDiscarded,
                        cardsDiscarded,
                        allIn
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""

        self.query['store_hands_stove'] = """insert into HandsStove (
                        handId,
                        playerId,
                        streetId,
                        boardId,
                        hiLo,
                        rankId,
                        value,
                        cards,
                        ev
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
               )"""
                
        self.query['store_boards'] = """insert into Boards (
                        handId,
                        boardId,
                        boardcard1,
                        boardcard2,
                        boardcard3,
                        boardcard4,
                        boardcard5
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""
                
        self.query['store_hands_pots'] = """insert into HandsPots (
                        handId,
                        potId,
                        boardId,
                        hiLo,
                        playerId,
                        pot,
                        collected,
                        rake
               )
               values (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
               )"""

        ################################
        # queries for Files Table
        ################################
        
        self.query['get_id'] = """
                        SELECT id
                        FROM Files
                        WHERE file=%s"""
        
        self.query['store_file'] = """  insert into Files (
                        file,
                        site,
                        startTime,
                        lastUpdate,
                        hands,
                        stored,
                        dups,
                        partial,
                        skipped,
                        errs,
                        ttime100,
                        finished)
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""
        
        self.query['update_file'] = """
                    UPDATE Files SET
                    type=%s,
                    lastUpdate=%s,
                    endTime=%s,
                    hands=hands+%s,
                    stored=stored+%s,
                    dups=dups+%s,
                    partial=partial+%s,
                    skipped=skipped+%s,
                    errs=errs+%s,
                    ttime100=ttime100+%s,
                    finished=%s
                    WHERE id=%s"""
        
        ################################
        # Counts for DB stats window
        ################################
        self.query['getHandCount'] = "SELECT COUNT(*) FROM Hands"
        self.query['getTourneyCount'] = "SELECT COUNT(*) FROM Tourneys"
        self.query['getTourneyTypeCount'] = "SELECT COUNT(*) FROM TourneyTypes"
        
        ################################
        # queries for dumpDatabase
        ################################
        for table in (u'Autorates', u'Backings', u'Gametypes', u'Hands', u'HandsActions', u'HandsPlayers', u'HudCache', u'Players', u'RawHands', u'RawTourneys', u'Settings', u'Sites', u'TourneyTypes', u'Tourneys', u'TourneysPlayers'):
            self.query['get' + table] = u"SELECT * FROM " + table
        
        ################################
        # placeholders and substitution stuff
        ################################
        if db_server == 'mysql':
            self.query['placeholder'] = u'%s'
        elif db_server == 'postgresql':
            self.query['placeholder'] = u'%s'
        elif db_server == 'sqlite':
            self.query['placeholder'] = u'?'


        # If using sqlite, use the ? placeholder instead of %s
        if db_server == 'sqlite':
            for k, q in self.query.iteritems():
                self.query[k] = re.sub('%s', '?', q)

if __name__ == "__main__":
#    just print the default queries and exit
    s = Sql()
    for key in s.query:
        print "For query " + key + ", sql ="
        print s.query[key]
