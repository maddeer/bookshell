PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE user_role(
	role_id integer PRIMARY KEY asc, 
	role_name varchar(50)
);
INSERT INTO 'user_role' VALUES(1,'user');
INSERT INTO 'user_role' VALUES(2,'autor');
CREATE TABLE users ( 
	user_id  integer PRIMARY KEY asc, 
	user_name varchar(255) unique not null, 
	password varchar(255) not null, 
	full_name varchar(255), 
	role integer not null,
	FOREIGN KEY (role) REFERENCES user_role(role_id)
);
CREATE UNIQUE INDEX users_idx ON users(user_name); 
INSERT INTO "users" VALUES(1,'maddeer','pass','Mad Deer',1);
INSERT INTO "users" VALUES(2,'mad-deer','longpass','Mad Deer',2);
INSERT INTO "users" VALUES(3,'mad.deer','longpass','TOLSTOY',2);
CREATE TABLE books ( 
	book_id  integer PRIMARY KEY asc, 
	book_name varchar(255) not null , 
	book_description text
);
CREATE INDEX books_idx ON books(book_name); 
INSERT INTO "books" VALUES(1,'War and Peace','Everybody fightes after Napoleon and dances with Natasha Rostova');
CREATE TABLE genre ( 
	genre_id integer PRIMARY KEY asc, 
	genre_name varchar(255)
);
INSERT INTO "genre" VALUES(1,'history roman');
CREATE TABLE genre_book ( 
	id integer PRIMARY KEY asc,
	book_id integer, 
	genre_id integer,
	FOREIGN KEY (book_id) REFERENCES books(book_id),
	FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);
INSERT INTO "genre_book" VALUES(1,1,1);
create table autors ( 
	id integer PRIMARY KEY asc,
	user_id integer, 
	book_id integer,
	foreign key (book_id) references books(book_id),
	foreign key (user_id) references users(user_id)
);
INSERT INTO "autors" VALUES(1,3,1);
CREATE TABLE chapters ( 
	chapter_id integer PRIMARY KEY asc, 
	book_id integer not null, 
	chapter_number integer not null, 
	chapter_title varchar(255), 
	date_to_open date, 
	chapter_text text,
	FOREIGN KEY (book_id) REFERENCES books(book_id)
);
CREATE INDEX chapters_idx ON chapters(book_id); 
INSERT INTO "chapters" VALUES(1,1,1,'peace','2017-09-22 11:00:00.222','Everybody fights. Somebody dances. War is coming');
INSERT INTO "chapters" VALUES(2,1,2,'war','2017-09-22 11:00:00.222','Everybody fights. Somebody dies. War is going');
CREATE TABLE chapter_grants_allowed ( 
	id integer PRIMARY KEY asc,
	user_id integer, 
	allowed_chapter_id integer,
	FOREIGN KEY (user_id) REFERENCES users(user_id),
	FOREIGN KEY (allowed_chapter_id) REFERENCES chapters(chapter_id)
);
INSERT INTO "chapter_grants_allowed" VALUES(1,1,1);
INSERT INTO "chapter_grants_allowed" VALUES(2,2,1);
INSERT INTO "chapter_grants_allowed" VALUES(3,3,1);
INSERT INTO "chapter_grants_allowed" VALUES(4,1,2);
INSERT INTO "chapter_grants_allowed" VALUES(5,2,2);
INSERT INTO "chapter_grants_allowed" VALUES(6,3,2);
COMMIT;
