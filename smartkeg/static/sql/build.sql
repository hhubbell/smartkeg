-- ---------------------------------------------------------------------------
-- Filename:    build.sql
-- Author:      Harrison Hubbell
-- Created:     03/10/2014
-- Updated:     09/02/2014
-- Description: Create tables for the smart kegerator that tracks temperature 
--              and consumption using a raspberry pi.  Data will be pushed to 
--              the the database from the main process in communication with 
--              local sensors, as well as through the web.  Data will mostly 
--              be pulled via the web, however there may be instances where 
--              debugging is done locally, as well as physical displays that
--              also required data.
--              
--              This script covers the creation of the Kegerator Schema, which
--              handles facets of the beer portion of the Smartkeg - this 
--              also includes users who may drink or purchase the beer.  
--              
--              Because the smartkeg DB user does not have permissions to 
--              CREATE and DROP schemas - for data security concerns - this 
--              script must be run as root.
-- ---------------------------------------------------------------------------

DROP SCHEMA IF EXISTS Kegerator;
CREATE SCHEMA Kegerator;
GRANT ALL PRIVILEGES ON Kegerator.* TO smartkeg;
USE Kegerator;

-- --------------------
-- BEER TYPE TABLE
-- --------------------
CREATE TABLE BeerType (
    id              INTEGER     NOT NULL AUTO_INCREMENT,
    type            VARCHAR(16) NOT NULL CHECK(type IN ('Ale', 'Lager')),
    subtype         VARCHAR(32), /* IPA, STOUT, ETC.. */
    PRIMARY KEY(id)
);

-- --------------------
-- BREWER TABLE
-- --------------------
CREATE TABLE Brewer (
    id              INTEGER     NOT NULL AUTO_INCREMENT,
    name            VARCHAR(64),
    city            VARCHAR(64),
    state           VARCHAR(64),
    country         VARCHAR(64),
    PRIMARY KEY(id)
)

-- --------------------
-- BEER TABLE
-- -------------------- 
CREATE TABLE Beer (
    id              INTEGER     NOT NULL AUTO_INCREMENT,
    brewer_id       INTEGER
    type_id         INTEGER
    name            VARCHAR(50) NOT NULL,
    brewer          VARCHAR(50) NOT NULL,  
    ABV             FLOAT(3,1),
    IBU             INTEGER(3),
    color_primary   CHAR(7),
    color_secondary CHAR(7),
    FOREIGN KEY(brewer_id) REFERENCES Brewer(id),
    FOREIGN KEY(type_id) REFERENCES BeerType(id),
    PRIMARY KEY(id)
);

-- --------------------
-- FRIDGE TABLE
-- --------------------
CREATE TABLE Fridge (
    id          INTEGER     NOT NULL AUTO_INCREMENT,
    name        VARCHAR(20),
    PRIMARY KEY(id)
);

-- --------------------
-- SENSOR TABLE
-- --------------------
CREATE TABLE Sensor (
    id              INTEGER     NOT NULL AUTO_INCREMENT,
    name            CHAR(15)    NOT NULL,
    type            VARCHAR(6)  NOT NULL CHECK(type IN ('Fridge', 'Keg')),
    PRIMARY KEY(id)
);

-- --------------------
-- KEG TABLE
-- --------------------
CREATE TABLE Keg (
    id              INTEGER     NOT NULL AUTO_INCREMENT,
    fridge_id       INTEGER     NOT NULL, 
    beer_id         INTEGER     NOT NULL,
    volume          FLOAT(5,2)  NOT NULL,
    date_started    DATE        NOT NULL,
    cost            FLOAT(5,2),
    deposit         FLOAT(5,2),
    now_serving     TINYINT(1)  DEFAULT 0,
    FOREIGN KEY(fridge_id) REFERENCES Fridge(id),
    FOREIGN KEY(beer_id) REFERENCES Beer(id),
    PRIMARY KEY(id)
);

-- --------------------
-- FRIDGE TEMP TABLE
-- --------------------
CREATE TABLE FridgeTemp (
    id          INTEGER     NOT NULL AUTO_INCREMENT,  
    fridge_id   INTEGER     NOT NULL,
    sensor_id   INTEGER     NOT NULL,
    read_time   TIMESTAMP   NOT NULL,
    temperature FLOAT(5,2),
    FOREIGN KEY(fridge_id) REFERENCES Fridge(id),
    FOREIGN KEY(sensor_id) REFERENCES Sensor(id),
    PRIMARY KEY(id)
);

-- --------------------
-- KEG TEMP TABLE
-- --------------------
CREATE TABLE KegTemp (
    id          INTEGER     NOT NULL AUTO_INCREMENT,
    keg_id      INTEGER     NOT NULL,
    sensor_id   INTEGER     NOT NULL,    
    read_time   TIMESTAMP   NOT NULL,
    temperature FLOAT(5,2),
    FOREIGN KEY(keg_id) REFERENCES Keg(id),
    FOREIGN KEY(sensor_id) REFERENCES Sensor(id),
    PRIMARY KEY(id)
);

-- --------------------
-- PERSON TABLE
-- --------------------
CREATE TABLE Person (
    id          INTEGER     NOT NULL AUTO_INCREMENT,
    first_name  VARCHAR(30),
    last_name   VARCHAR(30),
    email       VARCHAR(40),
    PRIMARY KEY(id)
);

-- --------------------
-- POUR TABLE
-- --------------------
CREATE TABLE Pour (
    id          INTEGER     NOT NULL AUTO_INCREMENT,
    keg_id      INTEGER     NOT NULL,
    person_id   INTEGER,
    pour_time   TIMESTAMP   NOT NULL,
    volume      FLOAT(4,2)  NOT NULL,
    FOREIGN KEY(keg_id) REFERENCES Keg(id),
    FOREIGN KEY(person_id) REFERENCES Person(id),
    PRIMARY KEY(id)
    );

-- --------------------
-- BEER RATING TABLE
-- --------------------
CREATE TABLE BeerRating (
    id          INTEGER     NOT NULL,
    person_id   INTEGER     NOT NULL,
    beer_id     INTEGER     NOT NULL,
    rating      TINYINT(1),
    comments    TEXT,
    FOREIGN KEY(person_id) REFERENCES Person(id),
    FOREIGN KEY(beer_id) REFERENCES Beer(id),
    PRIMARY KEY(id)
);

-- --------------------
-- PURCHASE CONTRIBUTION TABLE
-- --------------------
CREATE TABLE PurchaseContribution (
    id          INTEGER     NOT NULL,
    person_id   INTEGER     NOT NULL,
    keg_id      INTEGER     NOT NULL,
    amount      FLOAT(5,2)  NOT NULL,
    FOREIGN KEY(person_id) REFERENCES Person(id),
    FOREIGN KEY(keg_id) REFERENCES Keg(id),
    PRIMARY KEY(id)
);
