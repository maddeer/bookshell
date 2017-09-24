PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE users ( 
	user_ID  integer PRIMARY KEY asc, 
	Username varchar(255) unique not null, 
	password varchar(255) not null, 
	FullName varchar(255), 
	role varchar(255) not null
);
CREATE UNIQUE INDEX users_idx ON users(Username); 
INSERT INTO "users" VALUES(1,'maddeer','pass','Mad Deer','user');
INSERT INTO "users" VALUES(2,'mad-deer','longpass','Mad Deer','autor');
INSERT INTO "users" VALUES(3,'mad.deer','longpass','TOLSTOY','autor');
CREATE TABLE books ( 
	book_ID  integer PRIMARY KEY asc, 
	BookName varchar(255) not null , 
	BookDescription text
);
CREATE UNIQUE INDEX books_idx ON books(BookName); 
INSERT INTO "books" VALUES(1,'War and Peace','Everybody fightes after Napoleon and dances with Natasha Rostova');
CREATE TABLE ganr ( 
	ganr_ID integer PRIMARY KEY asc, 
	ganr varchar(255)
);
INSERT INTO "ganr" VALUES(1,'history roman');
CREATE TABLE book_ganr ( 
	book_ID integer, 
	ganr_ID integer,
	FOREIGN KEY (book_ID) REFERENCES books(book_ID),
	FOREIGN KEY (ganr_ID) REFERENCES ganr(ganr_ID)
);
INSERT INTO "book_ganr" VALUES(1,1);
CREATE TABLE autors ( 
	user_ID integer, 
	book_ID integer,
	FOREIGN KEY (book_ID) REFERENCES books(book_ID),
	FOREIGN KEY (user_ID) REFERENCES users(user_ID)
);
INSERT INTO "autors" VALUES(3,1);
CREATE TABLE chapters ( 
	chapter_ID integer PRIMARY KEY asc, 
	book_ID integer not null, 
	chapter_number integer not null, 
	chapter_title varchar(255), 
	date_to_open date, 
	chapter_text text,
	FOREIGN KEY (book_ID) REFERENCES books(book_ID)
);
CREATE INDEX chapters_idx ON chapters(book_ID); 
INSERT INTO "chapters" VALUES(1,1,1,'peace','2017-09-22','Everybody fights. Somebody dances. War is coming');
INSERT INTO "chapters" VALUES(2,1,2,'war','2017-09-22','Everybody fights. Somebody dies. War is going');
CREATE TABLE chapter_grants_allowed ( 
	user_ID integer, 
	allowed_chapter_ID integer,
	FOREIGN KEY (user_ID) REFERENCES users(user_ID),
	FOREIGN KEY (allowed_chapter_ID) REFERENCES chapters(chapter_ID)
);
INSERT INTO "chapter_grants_allowed" VALUES(1,1);
INSERT INTO "chapter_grants_allowed" VALUES(2,1);
INSERT INTO "chapter_grants_allowed" VALUES(3,1);
INSERT INTO "chapter_grants_allowed" VALUES(1,2);
INSERT INTO "chapter_grants_allowed" VALUES(2,2);
INSERT INTO "chapter_grants_allowed" VALUES(3,2);
COMMIT;
