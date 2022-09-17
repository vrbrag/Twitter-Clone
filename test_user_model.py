"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup(
            username="testu1",
            email="u1@test.com",
            password="HASHED_PASSWORD",
            image_url=None
        )
        u1id = 111
        u1.id = u1id

        u2 = User.signup(
            username="testu2",
            email="u2@test.com",
            password="HASHED_PASSWORD",
            image_url=None
        )
        u2id = 222
        u2.id = u2id

        db.session.commit()

        self.u1 = u1
        self.u1id = u1id
        self.u2 = u2
        self.u2id = u2id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


###### Test User Follows ######

    def test_user_follows(self):
        # u1 is following u2
        self.u1.following.append(self.u2)
        db.session.commit()

        # Test list of following/followers
        self.assertEqual(len(self.u1.following), 1) # u1 is following u2
        self.assertEqual(len(self.u2.followers), 1) # u2 is being following by u1
        self.assertEqual(len(self.u1.followers), 0) # u1 is being following by no one
        self.assertEqual(len(self.u2.following), 0) # u2 is following no one
        
        # Test if correct user is following/follower
        self.assertEqual(self.u1.following[0], self.u2) # u1 is following u2    
        self.assertEqual(self.u2.followers[0], self.u1) # u2 is being following by u1


    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))


###### Test User Signup ######
    def test_user_signup(self):
        user_test = User.signup("testUser", "testuser@test.com", "password", None)
        user_testid = 333
        user_test.id = user_testid
        
        db.session.commit()

        user_test = User.query.get(user_testid)

        self.assertEqual(user_test.username, "testUser")
        self.assertEqual(user_test.email, "testuser@test.com")
        # password is not saved as "password", its hashed!!
        self.assertNotEqual(user_test.password, "password")
        self.assertIsNotNone(user_test)

    # Username is a required field, should raise 'IntegrityError'
    def test_invalid_username_signup(self):
        invalid_user = User.signup(None, "testuser@test.com", "password", None)
        invalid_userid = 333
        invalid_user.id = invalid_userid

        with self.assertRaises(exc.IntegrityError): 
            db.session.commit()

    # Invalid Email
    def test_invalid_email_signup(self):
        invalid_user = User.signup("invalidUser", None, "password", None)
        invalid_userid = 444
        invalid_user.id = invalid_userid

        with self.assertRaises(exc.IntegrityError): 
            db.session.commit()

    # Invalid Password
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError):
            invalid_user = User.signup("invalidUser", "invalid@test.com", None, None)
            invalid_userid = 444
            invalid_user.id = invalid_userid

        with self.assertRaises(ValueError):
            invalid_user = User.signup("invalidUser", "invalid@test.com", "", None)
            invalid_userid = 444
            invalid_user.id = invalid_userid


###### Test Authenitcation ######
    def test_valid_authentication(self):
        u1 = User.authenticate(self.u1.username, "HASHED_PASSWORD")

        # self.assertTrue(self.u1.username, "testu1")
        # self.assertEqual(u1.id, self.u1id)
        self.assertIsNotNone(u1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("invalidUsername", "HASHED_PASSWORD"))
        
    def test_invalid_password(self):
        self.assertFalse(User.authenticate("self.u1.username", "invalidpassword"))