-- user tables
drop table if exists Users;
create table Users (
        USER_ID INTEGER PRIMARY KEY,
        USER_NAME TEXT NOT NULL,
        PASSWORD TEXT NOT NULL, -- this needs to be taken care off later for n
        COMMENT TEXT, -- this needs to be taken care off later
        DATE_JOINED TEXT DEFAULT CURRENT_TIMESTAMP -- this needs to be taken care off later
);

-- playlist tables
drop table if exists Playlists;
create table Playlists (
        PLAYLIST_ID INTEGER PRIMARY KEY,
        PLAYLIST_NAME TEXT NOT NULL,
        USER_ID TEXT NOT NULL,
        Tags TEXT NOT NULL, -- this will be limited by the size limit of mysql text fields
        DATE_ADDED TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        COMMENT TEXT, -- is case users wanna add a comment
        LINK TEXT NOT NULL, -- this will be limited by the size limit of mysql text fields
        FOREIGN KEY(USER_ID) REFERENCES Users(USER_ID) -- who posted the playlist
);

-- playlist tags this is for searching purposes,
-- we might need some data cleanup to get rid off 
-- tags like #music #awesome #pokemongo (this is for later)
drop table if exists Tags;
create table Tags (
        TAG_ID INTEGER PRIMARY KEY, --just id
        TAG_NAME TEXT NOT NULL,
        PLAYLISTS_LIST TEXT NOT NULL, -- this will be limited by the size limit of mysql text fields
        DATE_ADDED TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);