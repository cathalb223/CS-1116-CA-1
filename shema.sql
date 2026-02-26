DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS owns_character;

CREATE TABLE owns_character
(
    user_id TEXT FOREIGN KEY REFERENCES users(user_id),
    character_id TEXT FOREIGN KEY REFERENCES characters(character_id)
);

DROP TABLE IF EXISTS characters;

CREATE TABLE characters
(
  character_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  species TEXT NOT NULL
  level INT NOT NULL
  class TEXT NOT NULL
);

CREATE TABLE friends
(
    user_id TEXT FOREIGN KEY REFERENCES users(user_id),
    friend_id TEXT FOREIGN KEY REFERENCES users(user_id)
);

SELECT *
FROM users