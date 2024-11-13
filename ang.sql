-- SQLite

--1. Login Query:
--Find out if userID and pwd exists in table, by searching through it
SELECT * FROM users WHERE usr = ? AND pwd = ?;

--2. Registration Query:
--If a user does not exist, register them
INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?);


--3. List all tweets and retweets:
--List tweets
SELECT T.tid, T.writer_id, T.text, T.tdate, T.ttime
FROM tweets T, follows F
WHERE T.writer_id = F.flwer AND F.flwee = 2
Limit 5 OFFSET ?;
--List retweets
SELECT RT.tid, RT.retweeter_id, RT.writer_id, RT.spam, RT.rdate
FROM retweets RT, follows F
WHERE RT.retweeter_id = F.flwer AND F.flwee = 2
Limit 5 OFFSET ?;

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
--List of user by keywords
SELECT U.usr, U.name, U.email, U.phone
FROM users U
Where U.name LIKE '%' || ? || '%' 
ORDER BY LENGTH(U.name) ASC
Limit 5 OFFSET ?;
--Detail information of user
SELECT COUNT(distinct T.writer_id = U.usr) AS num_tweets, 
COUNT(distinct F.flwer = U.usr) AS num_flwee, 
COUNT(distinct F.flwee = U.usr) AS num_flwer
FROM users U, follows F, tweets T,
WHERE U.usr = ?;
--Give 3 most recent tweets
SELECT T.tid, T.writer_id, T.text, T.tdate, T.ttime
FROM tweets T, users U
WHERE U.usr = T.writer_id AND U.usr = ?
Limit 3 OFFSET 0;


/*
Test part

SELECT DISTINCT *
FROM users U, tweets T
WHERE T.writer_id = U.usr AND U.usr = 1;

SELECT COUNT(distinct T.writer_id = U.usr) AS num_tweets
FROM users U, tweets T
WHERE U.usr = 1;
*/


--6: Compose a tweet:
-- if a tweet contains a hashtag, insert # into hashtag_mentions table
INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) 
VALUES (?, ?, ?, DATE('now'), TIME('now'), ?);
INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?);


--display all tables
--SELECT *FROM users;
--SELECT *FROM follows;
--SELECT * FROM tweets;
--SELECT *FROM retweets;
--SELECT * FROM hashtag_mentions;