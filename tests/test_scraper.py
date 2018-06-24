import unittest
import os
import codecs

from bs4 import BeautifulSoup
import sfpl


class TestScraper(unittest.TestCase):
    def test_holds(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mockups/holds.html'), encoding='utf-8') as mockup:
            result = sfpl.SFPL.parseHolds(
                BeautifulSoup(mockup.read(), 'html.parser'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Fundamentals of Deep Learning')
        self.assertEqual(result[0].author.name, 'Buduma, Nikhil')
        self.assertEqual(result[0].status, 'Pickup by:  Jun 18, 2018')
        self.assertEqual(
            result[0].subtitle, 'Designing Next-generation Machine Intelligence Algorithms')
        self.assertEqual(result[0].ID, 3388519093)

    def test_checkouts(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mockups/checkouts.html'), encoding='utf-8') as mockup:
            result = sfpl.SFPL.parseCheckouts(
                BeautifulSoup(mockup.read(), 'html.parser'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Basics of Web Design')
        self.assertEqual(result[0].author.name, 'Felke-Morris, Terry')
        self.assertEqual(result[0].status, 'Due Jun 28, 2018')
        self.assertEqual(result[0].subtitle, 'HTML5 & CSS3')
        self.assertEqual(result[0].ID, 2423174093)

    def test_shelf(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mockups/shelf.html'), encoding='utf-8') as mockup:
            result = sfpl.SFPL.parseShelf(
                BeautifulSoup(mockup.read(), 'html.parser'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Bitcoin')
        self.assertEqual(result[0].author.name, 'United States')
        self.assertEqual(
            result[0].subtitle, 'Examining the Benefits and Risks for Small Business : Hearing Before the Committee on Small Business, United States House of Representatives, One Hundred Thirteenth Congress, Second Session, Hearing Held April 2, 2014')
        self.assertEqual(result[0].ID, 2776977093)

    def test_author(self):
        author = sfpl.Author('J.K. Rowling')
        result = author.getBooks()

        self.assertEqual(len(result), 5)
        self.assertEqual(
            result[0].title, "Harry Potter and the Sorcerer's Stone")
        self.assertEqual(result[0].author.name, 'Rowling, J. K.')

    def test_book(self):
        book = sfpl.Book('Python')

        self.assertEqual(book.getDetails(), {'Publisher': '[San Francisco, California] :, Peachpit Press,, [2014]',
                                             'Edition': 'Third edition', 'ISBN': ['9780321929556', '0321929551'],
                                             'Call Number': '005.133 P999do 2014', 'Characteristics': 'vii, 215 pages : illustrations ; 23 cm'})
        self.assertEqual(book.getDescription(), 'Python is a remarkably powerful dynamic programming language used in a wide variety of situations such as Web, database access, desktop GUIs, game and software development, and network programming. Fans of Python use the phrase "batteries included" to describe the standard library, which covers everything from asynchronous processing to zip files. The language itself is a flexible powerhouse that can handle practically any application domain.  This task-based tutorial on Python is for those new to the language and walks you through the fundamentals. You\'ll learn about arithmetic, strings, and variables; writing programs; flow of control, functions; strings; data structures; input and output; and exception handling. At the end of the book, a special section walks you through a longer, realistic application, tying the concepts of the book together.')
        self.assertEqual(book.getKeywords(), ['Introduction to programming', 'Arithmetic, strings, and variables', 'Writing programs', 'Flow of control', 'Functions', 'Strings', 'Data structures',
                                              'Input and output', 'Exception handling', 'Object-oriented programming', 'Case study: text statistics', 'Popular Python packages', 'Comparing Python 2 and Python 3'])
