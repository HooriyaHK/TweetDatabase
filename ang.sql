-- SQLite

--1. Login Query:
--Find out if userID and pwd exists in table, by searching through it
SELECT * FROM users WHERE usr = ? AND pwd = ?;

--2. Registration Query:
--If a user does not exist, register them
INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?);

--3. List Tweets:
--List all tweets and retweets after user login
SELECT T.tid, T.writer_id, T.text, T.tdate, T.ttime
FROM tweets T
WHERE T.writer_id = F.flower
UNION ALL
SELECT RT.tid, RT.writer_id, RT.text, RT.tdate, T.ttime
FROM retweets RT
WHERE RT.writer_id = F.flower
ORDER By T.tdate, RT.tdate DESC
LIMIT 5

--4. Search for tweets by keywords:
SELECT tid, writer_id, text, tdate, ttime 
FROM tweets 
WHERE text LIKE '%' || ? || '%' 
   OR tid IN (
       SELECT tid FROM hashtag_mentions WHERE term = ?
   )
ORDER BY tdate DESC
LIMIT 5 OFFSET ?;

--5. Search for users by keywords:
SELECT U.usr, U.name, U.
FROM users U
Where U.name LIKE '%' || ? || '%' 


--6: Compose a tweet:
-- if a tweet contains a hashtag, insert # into hashtag_mentions table
INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) 
VALUES (?, ?, ?, DATE('now'), TIME('now'), ?);
INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?);



--display all tables
--SELECT * FROM tweets;
--SELECT * FROM hashtag_mentions;
