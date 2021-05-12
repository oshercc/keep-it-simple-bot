
import os
import unittest
import sys
import mock
sys.modules['slack_bolt'] = mock.Mock()
sys.modules['slack_bolt.adapter.socket_mode'] = mock.Mock()
import keep_it_simple



class TestUtils(unittest.TestCase):

    def test_strip_links(self):
        text = 'text with single link: <http://foo.com|link>'
        expected = 'text with single link: link'
        self.assertEqual(keep_it_simple.strip_links(text), expected)

    def test_strip_multiple_links(self):
        text = 'text with multiple links: <http://foo.com|link1>, and another one <http://bar.com|link2>'
        expected = 'text with multiple links: link1, and another one link2'
        self.assertEqual(keep_it_simple.strip_links(text), expected)

    def test_strip_links_no_links(self):
        text = 'text without links'
        expected = 'text without links'
        self.assertEqual(keep_it_simple.strip_links(text), expected)

if __name__ == '__main__':
    unittest.main()