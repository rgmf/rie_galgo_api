DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  username varchar(255) NOT NULL,
  email varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  created_at timestamp NULL DEFAULT NULL,
  updated_at timestamp NULL DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY users_email_unique (email)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS medias;
CREATE TABLE medias (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(128) NOT NULL,
  hash varchar(172) DEFAULT NULL,
  data text NOT NULL, -- Path to the file
  thumbnail text NOT NULL, -- Path to the thumbnail
  size int(11) NOT NULL,
  media_type varchar(255) DEFAULT NULL,
  mime_type varchar(255) DEFAULT NULL,
  latitude varchar(50) DEFAULT NULL,
  longitude varchar(50) DEFAULT NULL,
  created_at int(11) NOT NULL,
  updated_at int(11) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY hash (hash)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS albums;
CREATE TABLE albums (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  description text DEFAULT NULL,
  user_id int(10) unsigned NOT NULL,
  public int(1) DEFAULT 0,
  created_at int(11) NOT NULL,
  updated_at int(11) NOT NULL,
  PRIMARY KEY (id),
  KEY user_id (user_id),
  FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS album_media;
CREATE TABLE album_media (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  album_id int(10) unsigned NOT NULL,
  media_id int(10) unsigned NOT NULL,
  created_at int(11) NOT NULL,
  updated_at int(11) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY album_id (album_id,media_id),
  KEY media_id (media_id),
  FOREIGN KEY (album_id) REFERENCES albums (id),
  FOREIGN KEY (media_id) REFERENCES medias (id)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS trash;
CREATE TABLE trash (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(128) NOT NULL,
  hash varchar(172) DEFAULT NULL,
  data text NOT NULL,
  size int(11) NOT NULL,
  date_created int(11) NOT NULL,
  created_at int(11) NOT NULL,
  updated_at int(11) NOT NULL,
  media_type varchar(255) DEFAULT NULL,
  mime_type varchar(255) DEFAULT NULL,
  longitude varchar(50) DEFAULT NULL,
  latitude varchar(50) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY hash (hash)
) ENGINE=InnoDB;
