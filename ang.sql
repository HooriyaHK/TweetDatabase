-- SQLite

--1. Login Query:
--Find out if userID and pwd exists in table, by searching through it
SELECT * FROM users WHERE usr = ? AND pwd = ?;

--2. Registration Query:
--If a user does not exist, register them
INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?);

--4. Search for tweets by keywords:
SELECT tid, writer_id, text, tdate, ttime 
FROM tweets 
WHERE text LIKE '%' || ? || '%' 
   OR tid IN (
       SELECT tid FROM hashtag_mentions WHERE term = ?
   )
ORDER BY tdate DESC
LIMIT 5 OFFSET ?;


--6: Compose a tweet:
-- if a tweet contains a hashtag, insert # into hashtag_mentions table
INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) 
VALUES (?, ?, ?, DATE('now'), TIME('now'), ?);
INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?);



--display all tables
--SELECT * FROM tweets;
--SELECT * FROM hashtag_mentions;
