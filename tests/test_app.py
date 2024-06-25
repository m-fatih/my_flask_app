import unittest
from unittest.mock import patch, MagicMock
from app import app, db, User
# import app

class BasicTests(unittest.TestCase):

    # Executed prior to each test
    def setUp(self):
        pass
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()

    # Executed after each test
    def tearDown(self):
        pass

    # Test home page
    def test_index(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # Test form submission
    @patch('app.db.session.add')
    @patch('app.db.session.commit')
    def test_submit(self, mock_commit, mock_add):
        # Create a sample POST request
        response = self.app.post('/submit', data={
            'name': 'Test User',
            'email': 'test@example.com'
        })

        # Check if the redirection happens as expected
        self.assertEqual(response.status_code, 302)

        # Verify that db.session.add was called with the correct parameters
        mock_add.assert_called_once()
        added_user = mock_add.call_args[0][0]
        self.assertEqual(added_user.name, 'Test User')
        self.assertEqual(added_user.email, 'test@example.com')

        # Verify that db.session.commit was called once
        mock_commit.assert_called_once()

    # # Test analysis page
    @patch('app.User')
    def test_analysis(self, mock_query):
        # Create mock user data
        mock_users = [
            User(id=1, name='User One', email='user1@example.com'),
            User(id=2, name='User Two', email='user2@example.com'),
            User(id=3, name='User Three', email='user1@sample.com'),
        ]
        
        # Configure the mock to return the mock user data
        mock_query.query.all.return_value = mock_users

        # Simulate a GET request to the /analysis route
        response = self.app.get('/analysis')

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct number of users is in the context
        self.assertIn(b'Total Users: 3', response.data)

        # Check if the email domain counts are correct
        self.assertIn(b'example.com: 2', response.data)
        self.assertIn(b'sample.com: 1', response.data)

if __name__ == "__main__":
    unittest.main()
