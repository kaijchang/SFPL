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

        for result in next(results):
            self.assertTrue('Rowling, J. K' in result.author)

    def test_pagination(self):
        'test pagination'
        author = sfpl.Search('J.K. Rowling', _type='author')
        results = author.getResults(pages=2)

        page_one = next(results)
        page_two = next(results)
        self.assertNotEqual(page_one, page_two)

    def test_book_search(self):
        search = sfpl.Search('Python')

        results = search.getResults()

        for result in next(results):
            self.assertTrue('python' in result.title.lower())

    def test_book_search_with_zero_results(self):
        'test book search with zero results'
        search = sfpl.Search('qwteyut_does_not_exist')
        self.assertRaises(RuntimeError, lambda: next(search.getResults()))

    def test_book_search_with_one_result(self):
        'test book search with one result'
        search = sfpl.Search('Everything Keeps Dissolving')
        self.assertEqual(len(list(search.getResults())), 1)

    def test_list_search(self):
        search = sfpl.Search('red', _type='list')

        lists = search.getResults()

        for list_ in next(lists):
            self.assertTrue('red' in list_.title.lower())

    def test_user_search(self):
        user = sfpl.User('Sublurbanite')

        user.getFollowers()
        user.getFollowing()
        user.getLists()

    def test_user_error(self):
        with self.assertRaises(sfpl.exceptions.NoUserFound):
            sfpl.User('eopghpeghip')

    def test_branch_hours(self):
        'test branch hours'
        branch = sfpl.Branch('west portal')
        actual_hours = branch.getHours()
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.assertIn(day, actual_hours)
            self.assertRegex(actual_hours[day], r'\d+ - \d+')

    def test_branch_hours_all(self):
        'test branch hours on all branches approximately'
        for branch_name in sfpl.Branch.BRANCHES:
            branch = sfpl.Branch(branch_name)
            actual_hours = branch.getHours()
            expected_hours = '12 - 6' if branch_name == 'main library' else '1 - 5'
            err_msg = f'Sun hours were incorrect for {branch_name}'
            self.assertEqual(actual_hours['Sun'], expected_hours, err_msg)

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

        for result in next(results):
            self.assertTrue('harry potter' not in result.title.lower())

    def test_advanced_search_with_zero_results(self):
        'test advanced search with zero results'
        search = sfpl.AdvancedSearch(includeauthor='asdafa_does_not_exist')
        self.assertRaises(RuntimeError, lambda: next(search.getResults()))

    def test_advanced_search_error(self):
        with self.assertRaises(sfpl.exceptions.MissingFilterTerm):
            sfpl.AdvancedSearch(soemthingkeyword='Harry Potter')

        with self.assertRaises(sfpl.exceptions.MissingFilterTerm):
            sfpl.AdvancedSearch(excludesomething='Harry Potter')

if __name__ == '__main__':
    unittest.main(verbosity=2)
