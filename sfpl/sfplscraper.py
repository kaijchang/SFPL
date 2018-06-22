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

    def hold(self, book):
        """Holds the book.
        Args:
            book (Book): Book object to hold.
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/holds/place_single_click_hold/{}'.format(book.id))

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

    @classmethod
    def parseShelf(cls, response):
        return [Book(book.find(testid='bib_link').text, book.find(testid='author_search').text, {book.find(class_='format').find('strong').text: int(
                book.find(class_='format').text.split('\n')[2].strip().replace('-', ''))}, book.find(class_='subTitle').text if book.find(class_='subTitle') else None, int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))) for book in response.find_all('div', lambda value: value and value.startswith('listItem clearfix'))]

    @classmethod
    def parseCheckouts(cls, response):
        return [Book(book.find(class_='title title_extended').text, book.find(testid='author_search').text, {book.find(class_='format').text.split('\n')[1].strip(): int(book.find(class_='format').text.split(
                '\n')[2].strip().replace('-', ''))}, book.find(class_='subTitle').text if book.find(class_='subTitle') else None, int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit())), 'Due {}'.format(book.find_all(class_='checkedout_status out')[1].text.replace('\xa0', ''))) for book in response.find_all(
                    'div', class_='listItem col-sm-offset-1 col-sm-10 col-xs-12 out bg_white')]

    @classmethod
    def parseHolds(cls, response):
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

            book_data.append(Book(book.find(testid='bib_link').text, book.find(testid='author_search').text, {book.find(class_='format').text.split('\n')[1].strip(): int(
                book.find(class_='format').text.split('\n')[2].strip().replace('-', ''))}, book.find(class_='subTitle').text if book.find(class_='subTitle') else None, int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit())), status))

        return book_data


class Book:
    def __init__(self, title, author, version, subtitle, id, status=None):
        self.title = title
        self.author = Author(author)
        self.version = version
        self.subtitle = subtitle
        self.id = id
        self.status = status

    def getDescription(self):
        """Get the book's description.
        Returns:
            Book description."""
        return BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self.id)).text, 'html.parser').find(class_='bib_description').text.strip()

    def getDetails(self):
        """Get's the book's details.
        Returns:
            A dictionary with Publisher, Edition, ISBN, Call Number, Characteristics, and Additional Contributors.
        """
        book_page = BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self.id)).text, 'html.parser')
        return {k: v for (k, v) in zip([d.text.replace(':', '') for d in book_page.find_all(class_='label')], [d.text.strip() if book_page.find_all(class_='label')[book_page.find_all(class_='value').index(d)].text != 'ISBN:' else d.text.strip().split() for d in book_page.find_all(class_='value')])}


class Author:
    def __init__(self, name):
        self.name = name

    def getBooks(self):
        """Get's the first page of book written by the author.
        Returns:
            A list of 5 Book objects.
        """
        return [Book(book.find('span').text, book.find('a', class_='author-link').text, {k: v for (k, v) in zip([b.text.replace('\xa0', '') for version in book.find_all(class_='format-info-main-content') for b in version.find_all('span', class_='cp-format-indicator')], [int(b.text.strip().replace('-', '')) if version.find('span', class_='cp-publication-date') else None for version in book.find_all(class_='format-info-main-content') for b in version.find_all('span', class_='cp-publication-date')])}, book.find('span', class_='cp-subtitle').text if book.find('span', class_='cp-subtitle') else None, int(''.join(s for s in book.find('a')['href'] if s.isdigit()))) for book in BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/v2/search?query=%22{}%22&searchType=author'.format('+'.join(self.name.split()))).text, 'html.parser').find_all(class_='cp-search-result-item-content')]
