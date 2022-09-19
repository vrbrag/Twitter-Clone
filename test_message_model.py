"""Message model tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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


class MessageModelTestCase(TestCase):
   """Test views for messages."""

   def setUp(self):
      """Create test client, add sample data."""
      db.drop_all()
      db.create_all()

      u1 = User.signup("testu1", "u1@test.com", "password", None)
      uid1 = 10101
      u1.id = uid1
      
      u2 = User.signup("testu2", "u2@test.com", "password", None)
      uid2 = 20202
      u2.id = uid2

      db.session.commit()

      u1 = User.query.get(uid1)
      u2 = User.query.get(uid2)

      self.u1 = u1
      self.u2 = u2
      self.uid1 = uid1
      self.uid2 = uid2

      self.client = app.test_client()


   def tearDown(self):
      res = super().tearDown()
      db.session.rollback()
      return res

   
   def test_message_model(self):
      """Does basic model work?"""

      msg = Message(text="Hello")
      self.u1.messages.append(msg)

      db.session.commit()

      self.assertEqual(len(self.u1.messages), 1)
      self.assertEqual(msg.text, "Hello")
      self.assertEqual(self.u1.messages[0].text, "Hello")
      self.assertIsNotNone(msg.timestamp)
      self.assertIsNotNone(msg.user_id, self.uid1)

   
   def test_message_likes(self):
      m1 = Message(
         text="Hello",
         user_id=self.uid1
      )
      
      m2 = Message(
         text="Warble",
         user_id=self.uid1
      )

      u = User.signup("usertest", "user@test.com", "password", None)
      uid = 30303
      u.id = uid
      db.session.add_all([m1, m2, u])
      db.session.commit()

      # user u likes message m1
      u.likes.append(m1)
      db.session.commit()

      l = Likes.query.all()
      self.assertEqual(len(l), 1)

      u_likes = Likes.query.filter(Likes.user_id==uid).all()
      self.assertEqual(len(u_likes), 1)
      self.assertEqual(u_likes[0].message_id, m1.id)