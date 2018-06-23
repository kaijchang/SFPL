import requests
from bs4 import BeautifulSoup


class SFPL:
    """The SFPL account class.

    Attributes:
        session (requests.Session): the requests Session with the login cookies."""

    def __init__(self, barcode, pin):
        """
        Args:
            barcode (str): The library card barcode.
            pin (str): PIN/ password for library account.
        """
        self.session = requests.Session()
        self.session.post(
            'https://sfpl.bibliocommons.com/user/login?destination=https%3A%2F%2Fsfpl.org%2F',
            data={'name': barcode, 'user_pin': pin})

    def hold(self, book):
        """Holds the book.

        Args:
            book (Book): Book object to hold.
        """
        self.session.get(
            'https://sfpl.bibliocommons.com/holds/place_single_click_hold/{}'.format(book.ID))

    def getCheckouts(self):
        """Gets the user's checked out items.

        Returns:
            A list of Book objects.
        """
        return self.parseCheckouts(BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/checkedout/index/out').text, 'html.parser'))

    def getHolds(self):
        """Gets the user's held items.

        Returns:
            A list of Book objects.
        """
        return self.parseHolds(BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/holds').text, 'html.parser'))

    def getForLater(self):
        """Get's user's for later shelf.

        Returns:
            A list of Book objects.
        """
        return self.parseShelf(BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/collection/show/my/library/for_later').text, 'html.parser'))

    def getInProgress(self):
        """Get's user's in progress shelf.

        Returns:
            A list of Book objects.
        """
        return self.parseShelf(BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/collection/show/my/library/in_progress').text, 'html.parser'))

    def getCompleted(self):
        """Get's user's completed shelf.

        Returns:
            A list of Book objects.
        """
        return self.parseShelf(BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/collection/show/my/library/completed').text, 'html.parser'))

    @classmethod
    def parseShelf(cls, response):
        return [Book(data_dict={'title': book.find(testid='bib_link').text, 'author': book.find(testid='author_search').text if book.find(testid='author_search') else None, 'subtitle': book.find(
            class_='subTitle').text if book.find(class_='subTitle') else None, 'ID': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))}) for book in response.find_all('div', lambda value: value and value.startswith('listItem clearfix'))]

    @classmethod
    def parseCheckouts(cls, response):
        return [Book(data_dict={'title': book.find(class_='title title_extended').text, 'author': book.find(testid='author_search').text if book.find(testid='author_search') else None, 'subtitle': book.find(
            class_='subTitle').text if book.find(class_='subTitle') else None, 'ID': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))}, status='Due {}'.format(book.find_all(class_='checkedout_status out')[1].text.replace('\xa0', ''))) for book in response.find_all(
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

            book_data.append(Book(data_dict={'title': book.find(testid='bib_link').text, 'author': book.find(testid='author_search').text if book.find(testid='author_search') else None, 'subtitle': book.find(
                class_='subTitle').text if book.find(class_='subTitle') else None, 'ID': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))}, status=status))

        return book_data


class Book:
    """A book from the San Francisco Public Library

    Attributes:
        title (str): The title of the book.
        author (Author): The author of the book as an Author object.
        version (dict): Dictionary mapping different mediums (str) to their publication years (int).
        subtitle (str): The subtitle of the book.
        ID (int): SFPL's ID for the book.
        status (str): The book's status, if applicable. (e.g. duedate, hold position)"""

    def __init__(self, search=None, data_dict=None, status=None):
        if data_dict:
            self.title = data_dict['title']
            self.author = Author(data_dict['author'])
            self.subtitle = data_dict['subtitle']
            self.ID = data_dict['ID']

        elif search:
            book = BeautifulSoup(requests.get('https://sfpl.bibliocommons.com/v2/search?query={}&searchType=smart'.format(
                '+'.join(search.split()))).text, 'html.parser').find(class_='cp-search-result-item-content')

            self.title = book.find('span').text
            self.author = Author(book.find(
                'a', class_='author-link').text if book.find(class_='author-link') else None)
            self.subtitle = book.find(
                'span', class_='cp-subtitle').text if book.find('span', class_='cp-subtitle') else None
            self.ID = int(
                ''.join(s for s in book.find('a')['href'] if s.isdigit()))

        self.status = status

    def getDescription(self):
        """Get the book's description.

        Returns:
            Book description."""
        return BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self.ID)).text, 'html.parser').find(class_='bib_description').text.strip()

    def getDetails(self):
        """Get's the book's details.

        Returns:
            A dictionary with additional data like Publisher, Edition and ISBN.
        """
        book_page = BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self.ID)).text, 'html.parser')
        return {k: v for (k, v) in zip([d.text.replace(':', '') for d in book_page.find_all(class_='label')], [d.text.strip(
        ).split() if book_page.find_all(class_='label')[book_page.find_all(class_='value').index(d)].text == 'ISBN:' else (
            [t.strip() for t in d.text.split('\n') if t] if book_page.find_all(class_='label')[book_page.find_all(class_='value').index(
                d)].text == 'Additional Contributors:' else d.text.replace('\n', '').strip()) for d in book_page.find_all(class_='value')])}

    def __str__(self):
        return '{} by {}'.format(self.title, self.author.name)

    def __eq__(self, other):
        return self.ID == other.ID

    def __ne__(self, other):
        return self.ID != other.ID


class Author:
    """An author of a book from the San Francisco Public Library.

    Attributes:
        name (str): The name of the author."""

    def __init__(self, name):
        """
        Args:

            name (str): Name of tha author
        """
        self.name = name

    def getBooks(self, pages=1):
        """Get's the first page of book written by the author.

        Returns:
            A list of 5 Book objects.
        """
        return [Book(data_dict={'title': book.find('span').text, 'author': book.find('a', class_='author-link').text, 'subtitle': book.find('span', class_='cp-subtitle').text if book.find(
            'span', class_='cp-subtitle') else None, 'ID': int(''.join(s for s in book.find('a')['href'] if s.isdigit()))}) for x in range(1, pages + 1) for book in BeautifulSoup(requests.get(
                'https://sfpl.bibliocommons.com/v2/search?pagination_page={}&query={}&searchType=author'.format(x, '+'.join(self.name.split()))).text, 'html.parser').find_all(class_='cp-search-result-item-content')]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name
