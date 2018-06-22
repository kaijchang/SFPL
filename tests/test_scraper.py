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
        book = sfpl.Book('Learning Python')

        self.assertEqual(book.getDetails(), {'Publisher': "Sebastopol, CA :, O'Reilly,, 2013", 'Edition': '5th ed', 'ISBN': [
                         '9781449355739', '1449355730'], 'Call Number': '005.133 P999L2 2013', 'Characteristics': 'l, 1540 pages : illustrations ; 24 cm', 'Alternative Title': 'Python'})
        self.assertEqual(book.getDescription(), "Get a comprehensive, in-depth introduction to the core Python language with this hands-on book. Based on author Mark Lutz's popular training course, this updated fifth edition will help you quickly write efficient, high-quality code with Python. It's an ideal way to begin, whether you're new to programming or a professional developer versed in other languages. Complete with quizzes, exercises, and helpful illustrations, this easy-to-follow, self-paced tutorial gets you started with both Python 2.7 and 3.3-- the latest releases in the 3.X and 2.X lines--plus all other releases in common use today. You'll also learn some advanced language features that recently have become more common in Python code. Explore Python's major built-in object types such as numbers, lists, and dictionaries Create and process objects with Python statements, and learn Python's general syntax model Use functions to avoid code redundancy and package code for reuse Organize statements, functions, and other tools into larger components with modules Dive into classes: Python's object-oriented programming tool for structuring code Write large programs with Python's exception-handling model and development tools Learn advanced Python tools, including decorators, descriptors, metaclasses, and Unicode processing")
