from robobrowser import RoboBrowser
import requests
from bs4 import BeautifulSoup


class SFPL:
    def __init__(self, barcode, pin):
        """The SFPL account class.
        Args:
            barcode (str): The library card barcode
            pin (str): PIN/ password for library account
        """
        self.browser = RoboBrowser(parser='html.parser')
        self.browser.open('https://sfpl.bibliocommons.com/user/login')
        form = self.browser.get_form(class_='loginForm left')
        form['name'] = barcode
        form['user_pin'] = pin
        self.browser.submit_form(form)

    def getCheckouts(self):
        """Gets the user's checked out items.
        Returns:
            A list of Book objects.
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/checkedout/index/out')

        return self.parseCheckouts(self.browser.parsed)

    def getHolds(self):
        """Gets the user's held items.
        Returns:
            A list of Book objects.
        """
        self.browser.open('https://sfpl.bibliocommons.com/holds')

        return self.parseHolds(self.browser.parsed)

    def getForLater(self):
        """Get's user's for later shelf.
        Returns:
            A list of Book objects.
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/collection/show/my/library/for_later')
        return self.parseShelf(self.browser.parsed)

    def getInProgress(self):
        """Get's user's in progress shelf.
        Returns:
            A list of Book objects.
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/collection/show/my/library/in_progress')
        return self.parseShelf(self.browser.parsed)

    def getCompleted(self):
        """Get's user's completed shelf.
        Returns:
            A list of Book objects.
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/collection/show/my/library/completed')
        return self.parseShelf(self.browser.parsed)

    def parseShelf(self, response):
        return [Book(book.find(testid='bib_link').text, book.find(testid='author_search').text, book.find(class_='format').find('strong').text, int(
                book.find(class_='format').text.split('\n')[2].strip().replace('-', '')), book.find(class_='subTitle').text if book.find(class_='subTitle') else None) for book in response.find_all('div', lambda value: value and value.startswith('listItem clearfix'))]

    def parseCheckouts(self, response):
        return [Book(book.find(class_='title title_extended').text, book.find(testid='author_search').text, book.find(class_='format').text.split('\n')[1].strip(), int(book.find(class_='format').text.split(
                '\n')[2].strip().replace('-', '')), book.find(class_='subTitle').text if book.find(class_='subTitle') else None, 'Due {}'.format(book.find_all(class_='checkedout_status out')[1].text.replace('\xa0', ''))) for book in response.find_all(
                    'div', class_='listItem col-sm-offset-1 col-sm-10 col-xs-12 out bg_white')]

    def parseHolds(self, response):
        books = response.find_all('div', {'class': [
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 in_transit bg_white', 'listItem col-sm-offset-1 col-sm-10 col-xs-12 not_yet_available bg_white', 'listItem col-sm-offset-1 col-sm-10 col-xs-12 ready_for_pickup bg_white']})

        book_data = []

        for book in books:
            if book.find(class_='hold_status in_transit'):
                location = book.find(class_='pick_up_location')
                location.span.clear()
                status = 'In Transit to {}'.format(
                    location.text.strip())

            elif book.find(class_='pick_up_date'):
                status = book.find(
                    class_='pick_up_date').text.strip()

            else:
                status = book.find(
                    class_='hold_position').text.strip()

            book_data.append(Book(book.find(testid='bib_link').text, book.find(testid='author_search').text, book.find(class_='format').text.split('\n')[1].strip(), int(
                book.find(class_='format').text.split('\n')[2].strip().replace('-', '')), book.find(class_='subTitle').text if book.find(class_='subTitle') else None, status))

        return book_data


class Book:
    def __init__(self, title, author, medium, publication_year, subtitle, status=None):
        self.title = title
        self.author = Author(author)
        self.medium = medium
        self.publication_year = publication_year
        self.subtitle = subtitle
        self.status = status


class Author:
    def __init__(self, name):
        self.name = name

    def getBooks(self):
        return [Book(book.find('span').text, book.find('a', class_='author-link').text, [b.text.replace('\xa0', '') for b in book.find_all('span', class_='cp-format-indicator')],
                     int(book.find('span', class_='cp-publication-date').text.strip().replace('-', '')) if book.find('span', class_='cp-publication-date') else None, book.find('span', class_='cp-subtitle').text if book.find('span', class_='cp-subtitle') else None) for book in BeautifulSoup(requests.get(
                         'https://sfpl.bibliocommons.com/v2/search?query=%22{}%22&searchType=author'.format('+'.join(self.name.split()))).text, 'html.parser').find_all(class_='cp-search-result-item-content')]
