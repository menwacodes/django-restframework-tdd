from unittest.mock import patch
from django.core.management import call_command

from django.db.utils import OperationalError
from django.test import TestCase

class CommandTests(TestCase):
    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')  # name of management command
            self.assertEqual(gi.call_count, 1)  # called one

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            # add side effect to raise Op Error 5 times then don't raise to complete call
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEquals(gi.call_count, 6)
