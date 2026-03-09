DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);


DROP TABLE IF EXISTS characters;

CREATE TABLE characters
(
  character_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  species TEXT NOT NULL,
  level INTEGER NOT NULL,
  class TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);


DROP TABLE IF EXISTS friends;

CREATE TABLE friends
(
    user_id TEXT ,
    friend_id TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    FOREIGN KEY (friend_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS campaigns;

CREATE TABLE campaigns
(
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dm_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (dm_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS in_campaign;

CREATE TABLE in_campaign
(
    user_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

