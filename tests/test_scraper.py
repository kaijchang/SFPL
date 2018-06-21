import unittest
import os
import codecs

from bs4 import BeautifulSoup
import sfpl


class TestScraper(unittest.TestCase):
    def setUp(self):
        self.SFPL = sfpl.SFPL('PLACEHOLDER', 'PLACEHOLDER')

    def test_holds(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mockups/holds.html'), encoding='utf-8') as mockup:
            result = self.SFPL.parseHolds(
                BeautifulSoup(mockup.read(), 'html.parser'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Fundamentals of Deep Learning')
        self.assertEqual(result[0].author.name, 'Buduma, Nikhil')
        self.assertEqual(result[0].medium, 'Book')
        self.assertEqual(result[0].publication_year, 2017)
        self.assertEqual(result[0].status, 'Pickup by:  Jun 18, 2018')
        self.assertEqual(
            result[0].subtitle, 'Designing Next-generation Machine Intelligence Algorithms')

    def test_checkouts(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mockups/checkouts.html'), encoding='utf-8') as mockup:
            result = self.SFPL.parseCheckouts(
                BeautifulSoup(mockup.read(), 'html.parser'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Basics of Web Design')
        self.assertEqual(result[0].author.name, 'Felke-Morris, Terry')
        self.assertEqual(result[0].medium, 'Book')
        self.assertEqual(result[0].publication_year, 2012)
        self.assertEqual(result[0].status, 'Due Jun 28, 2018')
        self.assertEqual(result[0].subtitle, 'HTML5 & CSS3')

    def test_shelf(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mockups/shelf.html'), encoding='utf-8') as mockup:
            result = self.SFPL.parseShelf(
                BeautifulSoup(mockup.read(), 'html.parser'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Bitcoin')
        self.assertEqual(result[0].author.name, 'United States')
        self.assertEqual(result[0].medium, 'Website or Online Data')
        self.assertEqual(result[0].publication_year, 2014)
        self.assertEqual(
            result[0].subtitle, 'Examining the Benefits and Risks for Small Business : Hearing Before the Committee on Small Business, United States House of Representatives, One Hundred Thirteenth Congress, Second Session, Hearing Held April 2, 2014')

    def test_author(self):
        author = sfpl.Author('J.K. Rowling')
        result = author.getBooks()

        self.assertEqual(len(result), 5)
        self.assertEqual(
            result[0].title, "Harry Potter and the Sorcerer's Stone")
        self.assertEqual(result[0].author.name, 'Rowling, J. K.')
        self.assertEqual(set(result[0].medium), set([
                         'Audiobook CD', 'eBook', 'Book', 'Downloadable Audiobook', 'Large Print']))
        self.assertEqual(result[0].publication_year, 1997)
