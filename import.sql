CREATE DATABASE IF NOT EXISTS geofilm;
USE geofilm;


CREATE TABLE IF NOT EXISTS FilmingType(
   id_filming_type INT AUTO_INCREMENT,
   type VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_filming_type),
   UNIQUE(type)
);

CREATE TABLE IF NOT EXISTS WorkTitle(
   id_title INT AUTO_INCREMENT,
   title VARCHAR(255) NOT NULL,
   PRIMARY KEY(id_title),
   UNIQUE(title)
);

CREATE TABLE IF NOT EXISTS Realisator(
   id_realisator INT AUTO_INCREMENT,
   realisator VARCHAR(255) NOT NULL,
   PRIMARY KEY(id_realisator),
   UNIQUE(realisator)
);

CREATE TABLE IF NOT EXISTS Productor(
   id_productor INT AUTO_INCREMENT,
   productor VARCHAR(255) NOT NULL,
   PRIMARY KEY(id_productor),
   UNIQUE(productor)
);

CREATE TABLE IF NOT EXISTS Location(
   id_location INT AUTO_INCREMENT,
   geopoint_2d JSON NOT NULL,
   PRIMARY KEY(id_location)
);

CREATE TABLE IF NOT EXISTS Adress(
   id_adress INT AUTO_INCREMENT,
   adress VARCHAR(255),
   postal_code VARCHAR(50),
   PRIMARY KEY(id_adress),
   UNIQUE(adress, postal_code)
);

CREATE TABLE IF NOT EXISTS Scene(
   id_scene VARCHAR(50) NOT NULL,
   startDate DATE NOT NULL,
   endDate DATE NOT NULL,
   yearFilming INT NOT NULL,
   id_location INT NOT NULL,
   id_filming_type INT NOT NULL,
   id_title INT NOT NULL,
   PRIMARY KEY(id_scene),
   FOREIGN KEY(id_location) REFERENCES Location(id_location),
   FOREIGN KEY(id_filming_type) REFERENCES FilmingType(id_filming_type),
   FOREIGN KEY(id_title) REFERENCES WorkTitle(id_title)
);

CREATE TABLE IF NOT EXISTS Adress_Scene(
   id_scene VARCHAR(50),
   id_adress INT,
   PRIMARY KEY(id_scene, id_adress),
   FOREIGN KEY(id_scene) REFERENCES Scene(id_scene),
   FOREIGN KEY(id_adress) REFERENCES Adress(id_adress)
);

CREATE TABLE IF NOT EXISTS Scene_Realisator(
   id_scene VARCHAR(50),
   id_realisator INT,
   PRIMARY KEY(id_scene, id_realisator),
   FOREIGN KEY(id_scene) REFERENCES Scene(id_scene),
   FOREIGN KEY(id_realisator) REFERENCES Realisator(id_realisator)
);

CREATE TABLE IF NOT EXISTS Scene_Productor(
   id_scene VARCHAR(50),
   id_productor INT,
   PRIMARY KEY(id_scene, id_productor),
   FOREIGN KEY(id_scene) REFERENCES Scene(id_scene),
   FOREIGN KEY(id_productor) REFERENCES Productor(id_productor)
);