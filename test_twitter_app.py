import sqlite3
import unittest
from unittest.mock import patch
from io import StringIO
from main import * 

class TestTwitterApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection, cls.cursor = connect_db()

        # Set up a test database
        cls.cursor.execute("DELETE FROM users")
        cls.cursor.execute("DELETE FROM follows")
        cls.cursor.execute("DELETE FROM tweets")
        cls.cursor.execute("DELETE FROM retweets")
        cls.cursor.execute("DELETE FROM hashtag_mentions")

        # Populate test data
        cls.cursor.execute("INSERT INTO users (usr, name, email, phone, pwd) VALUES (1, 'Alice', 'alice@example.com', '1234567890', 'password')")
        cls.cursor.execute("INSERT INTO users (usr, name, email, phone, pwd) VALUES (2, 'Bob', 'bob@example.com', '0987654321', 'password')")
        cls.cursor.execute("INSERT INTO follows (flwer, flwee, start_date) VALUES (1, 2, '2024-01-01')")
        cls.cursor.execute("INSERT INTO tweets (tid, writer_id, text, tdate, ttime) VALUES (1, 2, 'Hello World! #greeting', '2024-11-15', '10:00')")
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_register_user(self):
        with patch('builtins.input', side_effect=['Charlie', 'charlie@example.com', '1112223333', 'mypassword']):
            with patch('getpass.getpass', return_value='mypassword'):
                register_user(self.cursor, self.connection)
                self.cursor.execute("SELECT * FROM users WHERE name = 'Charlie'")
                user = self.cursor.fetchone()
                self.assertIsNotNone(user)

    def test_login_user(self):
        with patch('builtins.input', side_effect=['1', 'password']):
            with patch('getpass.getpass', return_value='password'):
                user_id = login_user(self.cursor)
                self.assertEqual(user_id, '1')

    def test_display_feed(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_feed(self.cursor, '1')
            output = fake_out.getvalue()
            self.assertIn("Hello World! #greeting", output)

    def test_compose_tweet(self):
        with patch('builtins.input', side_effect=['This is a test tweet #test']):
            compose_tweet(self.cursor, self.connection, '1')
            self.cursor.execute("SELECT * FROM tweets WHERE text LIKE '%test%'")
            tweet = self.cursor.fetchone()
            self.assertIsNotNone(tweet)

    def test_search_tweets(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            search_tweets(self.cursor, '#greeting')
            output = fake_out.getvalue()
            self.assertIn("Hello World! #greeting", output)

    def test_search_users(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            search_users(self.cursor, 'Bob')
            output = fake_out.getvalue()
            self.assertIn("Bob", output)

    def test_list_followers(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            list_followers(self.cursor, '2')
            output = fake_out.getvalue()
            self.assertIn("Alice", output)

    def test_follow_user(self):
        follow_user(self.cursor, self.connection, '2', '1')
        self.cursor.execute("SELECT * FROM follows WHERE flwer = 2 AND flwee = 1")
        follow = self.cursor.fetchone()
        self.assertIsNotNone(follow)

    def test_unfollow_user(self):
        unfollow_user(self.cursor, self.connection, '1', '2')
        self.cursor.execute("SELECT * FROM follows WHERE flwer = 1 AND flwee = 2")
        follow = self.cursor.fetchone()
        self.assertIsNone(follow)

    def test_invalid_login(self):
        with patch('builtins.input', side_effect=['999', 'wrongpassword']):
            with patch('getpass.getpass', return_value='wrongpassword'):
                user_id = login_user(self.cursor)
                self.assertIsNone(user_id)

    def test_tweet_statistics(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.cursor.execute("SELECT COUNT(*) FROM retweets WHERE tid = 1")
            retweet_count = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM tweets WHERE replyto_tid = 1")
            reply_count = self.cursor.fetchone()[0]

            self.assertEqual(retweet_count, 0)
            self.assertEqual(reply_count, 0)

if __name__ == "__main__":
    unittest.main()
