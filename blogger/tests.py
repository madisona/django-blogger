"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from xml.dom.minidom import parse
from StringIO import StringIO

from django.test import TestCase

from blogger import models

class GeneralModelTests(TestCase):

    def setUp(self):
        self.sample_xml = """<?xml version='1.0' encoding='UTF-8'?>

        <feed>
            <link rel='link1' href='http://googleblog.blogspot.com/' />
            <link rel='link2' href='http://google.com/' />
        </feed>
        """

    def test_get_links_returns_dictionary_of_links(self):
        xml = parse(StringIO(self.sample_xml))
        links = models.get_links(xml)
        self.assertEqual({
            'link1': 'http://googleblog.blogspot.com/',
            'link2': 'http://google.com/',
        }, links)
