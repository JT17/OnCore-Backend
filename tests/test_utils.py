from speranza.util import email_messaging
import unittest


# TODO implement these in a useful way...I'm not going to do it now it seems like it works well enough and these are very simple functions...
class TestEmailUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_send_email(self):
        pass

    def test_send_formatted_email(self):
        pass

    def test_create_message(self):
        text = "test message"
        subj = "test_subj"
        dest = "test_dest"
        src = "test_src"
        message = email_messaging.create_message(text, subj, dest, src)
        assert message == "From: test_src\r\nTo: test_dest\r\nSubject: test_subj\r\n\r\ntest message"

    def test_login_to_server(self):
        server = email_messaging.login_to_server()
        assert server is not None

if __name__ == '__main__':
    unittest.main()
