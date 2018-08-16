# -*- coding: utf-8 -*-


import unittest
import os
import codecs

from bs4 import BeautifulSoup
import sfpl


class TestScraper(unittest.TestCase):
    def test_holds(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets/holds.html'), encoding='utf-8') as mockup:
            result = sfpl.Account.parseHolds(
                BeautifulSoup(mockup.read(), 'lxml'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Fundamentals of Deep Learning')
        self.assertEqual(result[0].author, 'Buduma, Nikhil')
        self.assertEqual(result[0].status, 'Pickup by:  Jun 18, 2018')
        self.assertEqual(
            result[0].subtitle, 'Designing Next-generation Machine Intelligence Algorithms')
        self.assertEqual(result[0]._id, 3388519093)

    def test_checkouts(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets/checkouts.html'), encoding='utf-8') as mockup:
            result = sfpl.Account.parseCheckouts(
                BeautifulSoup(mockup.read(), 'lxml'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Basics of Web Design')
        self.assertEqual(result[0].author, 'Felke-Morris, Terry')
        self.assertEqual(result[0].status, 'Due Jun 28, 2018')
        self.assertEqual(result[0].subtitle, 'HTML5 & CSS3')
        self.assertEqual(result[0]._id, 2423174093)

    def test_shelf(self):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets/shelf.html'), encoding='utf-8') as mockup:
            result = sfpl.Account.parseShelf(
                BeautifulSoup(mockup.read(), 'lxml'))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, 'Bitcoin')
        self.assertEqual(result[0].author, 'United States')
        self.assertEqual(
            result[0].subtitle, 'Examining the Benefits and Risks for Small Business : Hearing Before the Committee on Small Business, United States House of Representatives, One Hundred Thirteenth Congress, Second Session, Hearing Held April 2, 2014')
        self.assertEqual(result[0]._id, 2776977093)

    def test_author_search(self):
        author = sfpl.Search('J.K. Rowling', _type='author')
        results = author.getResults()

        for result in results:
            self.assertEqual(result.author, 'Rowling, J. K.')

    def test_pagination(self):
        author = sfpl.Search('J.K. Rowling', _type='author')
        results = author.getResults(pages=2)

        self.assertEqual(len(results), 10)

    def test_book_search(self):
        search = sfpl.Search('Python')

        results = search.getResults()

        for result in results:
            self.assertTrue('python' in result.title.lower())

    def test_list_search(self):
        search = sfpl.Search('red', _type='list')

        lists = search.getResults()

        for list_ in lists:
            self.assertTrue('red' in list_.title.lower())

    def test_user_search(self):
        user = sfpl.User('Sublurbanite')

        self.assertListEqual([u.name for u in user.getFollowers()], [
            'Loriel_2', 'jac523', 'WritingDeskRaven', 'Stephenson1'])
        self.assertListEqual([u.name for u in user.getFollowing()], ['monkeymind', 'Pickeringnonfiction', 'ogopogo', ' NVDPL Librarians',
                                                                     'wplstaffpicks', 'Loriel_2', 'Mighty_Info_Ninja', 'jac523', 'WPL_Reference', 'bxrlover', 'AdamPeltier'])
        self.assertListEqual([l.title for l in user.getLists()], ["I Can't Believe this Book Exists", "The [Insert Profession Here]'s [Insert Family Member Here]",
                                                                  'Funny Skeleton/Skull Covers', 'Black Strap for the Soul', 'My Favourite Biographies and Memoirs', 'Tales from Iran', 'Jewels of India', 'Sewing Fun'])

    def test_user_error(self):
        with self.assertRaises(sfpl.exceptions.NoUserFound):
            sfpl.User('eopghpeghip')

    def test_branch(self):
        branch = sfpl.Branch('west portal')
        self.assertEqual(branch.name, 'WEST PORTAL BRANCH')
        self.assertEqual(branch._id, '44563149')
        self.assertDictEqual(branch.getHours(), {'Sun': '1 - 5', 'Mon': '1 - 6', 'Tue': '10 - 9',
                                                 'Wed': '10 - 9', 'Thu': '10 - 9', 'Fri': '1 - 6', 'Sat': '10 - 6'})

    def test_branch_error(self):
        with self.assertRaises(sfpl.exceptions.NoBranchFound):
            sfpl.Branch('eighhegiohi;eg')

    def test_account_error(self):
        with self.assertRaises(sfpl.exceptions.LoginError):
            sfpl.Account('flbknnklvd', 'uhoegwohi')

    def test_advanced_search(self):
        search = sfpl.AdvancedSearch(
            includeauthor='J. K. Rowling', excludekeyword='Harry Potter')

        results = search.getResults()

        for result in results:
            self.assertTrue('harry potter' not in result.title.lower())

    def test_advanced_search_error(self):
        with self.assertRaises(sfpl.exceptions.MissingFilterTerm):
            sfpl.AdvancedSearch(soemthingkeyword='Harry Potter')

        with self.assertRaises(sfpl.exceptions.MissingFilterTerm):
            sfpl.AdvancedSearch(excludesomething='Harry Potter')


if __name__ == '__main__':
    unittest.main()
