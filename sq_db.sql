CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);


CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
title text unique NOT NULL,
category not null,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL,
author NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL unique,
email text NOT NULL,
psw text NOT NULL,
time integer NOT NULL,
avatar BLOB DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS Category (
category text NOT NULL unique
);

