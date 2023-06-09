# -*- coding: utf-8 -*-


import requests

import re
import math
import json

from bs4 import BeautifulSoup
from . import exceptions

# Regex Patterns

id_regex = 'https://sfpl.bibliocommons.com/.+/(\d+)'
book_page_regex = '[\d,]+ to [\d,]+ of ([\d,]+) results?'
list_page_regex = '[\d,]+ - [\d,]+ of ([\d,]+) items?'


class User:
    """A library user account.

    Attributes:
        name (str): the account's username.
        _id (str): the account's id.
    """

    def __init__(self, name, _id=None):
        """
        Args:
            name (str): The account's username.

        Raises:
            NoUserFound: If the search doesn't return any users.
        """
        if not _id:
            self.name = name

            resp = requests.get(
                'https://sfpl.bibliocommons.com/search?t=user&search_category=user&q={}'.format(self.name))

            match = re.match(
                id_regex, resp.url)

            if not match:
                raise exceptions.NoUserFound(name)

            self._id = match.group(1)

        else:
            self.name = name
            self._id = _id

    def getFollowing(self):
        """Gets all the users the account follows.

        Returns:
            list: A list of User objects.
        """
        return [User(user.find('a').text,
                     re.match(id_regex, user.find('a')['href']).group(1)) for user in BeautifulSoup(requests.get(
                         'https://sfpl.bibliocommons.com/user_profile/{}/following'.format(self._id)).text, 'lxml')(class_='col-xs-12 col-md-4')]

    def getFollowers(self):
        """Gets all the account's followers.

        Returns:
            list: A list of User objects.
        """
        return [User(user.find('a').text,
                     re.match(id_regex, user.find('a')['href']).group(1)) for user in BeautifulSoup(requests.get(
                         'https://sfpl.bibliocommons.com/user_profile/{}/followers'.format(self._id)).text, 'lxml')(class_='col-xs-12 col-md-4')]

    def getLists(self):
        """Gets all the lists the user has created.

        Returns:
            list: A list of List objects.
        """
        return [List({'type': _list('td')[1].text.strip(),
                      'title': _list.find('a').text,
                      'user': self,
                      'createdon': _list('td')[2].text.strip(),
                      'itemcount': int(_list('td')[3].text),
                      'description': None,
                      'id': _list.find('a')['href'].split('/')[4]
                      }) for _list in BeautifulSoup(requests.get(
                          'https://sfpl.bibliocommons.com/lists/show/{}'.format(self._id)).text, 'lxml').find('tbody')('tr')]

    def getForLater(self):
        """Get's user's for later shelf.

        Returns:
            list: A list of Book objects.
        """
        return self.parseShelf(BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/collection/show/{}/library/for_later'.format(self._id)).text, 'lxml'))

    def getInProgress(self):
        """Get's user's in progress shelf.

        Returns:
            list: A list of Book objects.
        """
        return self.parseShelf(BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/collection/{}/my/library/in_progress'.format(self._id)).text, 'lxml'))

    def getCompleted(self):
        """Get's user's completed shelf.

        Returns:
            list: A list of Book objects.
        """
        return self.parseShelf(BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/collection/show/{}/library/completed'.format(self._id)).text, 'lxml'))

    @staticmethod
    def parseShelf(response):
        return [Book({'title': book.find(testid='bib_link').text,
                      'author': book.find(testid='author_search').text if book.find(testid='author_search') else None,
                      'subtitle': book.find(class_='subTitle').text if book.find(class_='subTitle') else None,
                      '_id': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))})
                for book in response('div', lambda value: value and value.startswith('listItem clearfix'))]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self._id == other._id

    def __ne__(self, other):
        return self._id != other._id


class Account(User):
    """The SFPL account class.

    Attributes:
        session (requests.Session): The requests session with cookies.
        name (str): the account's username.
        _id (str): the account's id.
    """

    def __init__(self, barcode, pin):
        """
        Args:
            barcode (str): The library card barcode.
            pin (str): PIN/ password for library account.

        Raises:
            LoginError: If we aren't redirected to the main page after login.
        """
        self.session = requests.Session()

        resp = self.session.post(
            'https://sfpl.bibliocommons.com/user/login',
            data={'name': barcode, 'user_pin': pin}, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            })

        if not resp.json()['logged_in']:
            raise exceptions.LoginError(resp.json()['messages'][0]['key'])

        main = BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/user_dashboard').text, 'lxml')

        super().__init__(main.find(class_='cp_user_card')[
            'data-name'], main.find(class_='cp_user_card')['data-id'])

    def hold(self, book, branch):
        """Holds the book.

        Args:
            book (Book): Book object to hold.
            branch (Branch): Branch to have book delivered to.

        Raises:
            HoldError: If the hold request is denied.
            NotLoggedIn: If the server doesn't accept the token.
        """
        resp = self.session.post(
            'https://sfpl.bibliocommons.com/holds/place_single_click_hold/{}'.format(book._id), data={
                'authenticity_token': BeautifulSoup(self.session.get('https://sfpl.bibliocommons.com/item/show/{}'.format(book._id)).text, 'lxml').find('input', {'name': 'authenticity_token'})['value'],
                'bib': book._id,
                'branch': branch._id
            }, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            })

        if not resp.json()['logged_in']:
            raise exceptions.NotLoggedIn

        if not resp.json()['success']:
            raise exceptions.HoldError(resp.json()['messages'][0]['key'])

    def cancelHold(self, book):
        """Cancels the hold on the book.

        Args:
            book (Book): Book to cancel the hold for.

        Raises:
            NotOnHold: If the book isn't being held.
            NotLoggedIn: If the server doesn't accept the token.
        """
        resp = self.session.get(
            'https://sfpl.bibliocommons.com/holds/index/not_yet_available')

        if resp.history:
            raise exceptions.NotLoggedIn

        holds = BeautifulSoup(resp.text, 'lxml')

        for hold in holds('div', lambda class_: class_ and class_.startswith('listItem col-sm-offset-1 col-sm-10 col-xs-12')):
            if hold.find(testid='bib_link').text == book.title:
                resp = self.session.post('https://sfpl.bibliocommons.com/holds/delete.json', data={
                    'authenticity_token': holds.find('input', {'name': 'authenticity_token'})['value'],
                    'confirm_hold_delete': True,
                    'items[]': hold.find(class_='btn btn-link single_circ_action')['href'].split('/')[3],
                    'bib_status': 'future',
                    'is_private': True
                }, headers={
                    'X-Requested-With': 'XMLHttpRequest'
                })

                if not resp.json()['logged_in']:
                    raise exceptions.NotLoggedIn

                break

        else:
            raise exceptions.NotOnHold(book.title)

    def renew(self, book):
        """Renews the hold on the book.

        Args:
            book (Book): Book to renew.

        Raises:
            NotCheckedOut: If the user is trying to renew a book that they haven't checked out.
            RenewError: If the renew request is denied.
            NotLoggedIn: If the server doesn't accept the token.
        """
        resp = self.session.get(
            'https://sfpl.bibliocommons.com/checkedout')

        if resp.history:
            raise exceptions.NotLoggedIn

        checkouts = BeautifulSoup(resp.text, 'lxml')

        for checkout in checkouts('div', lambda class_: class_ and class_.startswith('listItem')):
            if checkout.find(class_='title title_extended').text == book.title:
                confirmation = self.session.get('https://sfpl.bibliocommons.com/{}'.format(
                    checkout.find(class_='btn btn-link single_circ_action')['href']), headers={
                    'X-CSRF-Token': checkouts.find('input', {'name': 'authenticity_token'})['value']}).json()

                if not confirmation['logged_in']:
                    raise exceptions.NotLoggedIn

                resp = self.session.post('https://sfpl.bibliocommons.com/checkedout/renew', data={
                    'authenticity_token': BeautifulSoup(confirmation['html'], 'lxml').find('input', {'name': 'authenticity_token'})['value'],
                    'items[]': BeautifulSoup(confirmation['html'], 'lxml').find('input', id='items_')['value']
                }, headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                    'Referer': 'https://sfpl.bibliocommons.com/checkedout'
                })

                if not resp.json()['logged_in']:
                    raise exceptions.NotLoggedIn

                if not resp.json()['success']:
                    raise exceptions.RenewError(
                        resp.json()['messages'][0]['key'])

                break

        else:
            raise exceptions.NotCheckedOut(book.title)

    def follow(self, user):
        """Follows the user.

        Args:
            user (User): User to follow.

        Raises:
            NotLoggedIn: If the server doesn't accept the token.
        """
        resp = self.session.put(
            'https://sfpl.bibliocommons.com/user_profile/{}?type=follow&value={}'.format(self._id, user._id), headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': BeautifulSoup(self.session.get('https://sfpl.bibliocommons.com/user_profile/{}'.format(user._id)).text, 'lxml').find('meta', {'name': 'csrf-token'})['content']
            })

        if not resp.json()['logged_in']:
            raise exceptions.NotLoggedIn

    def unfollow(self, user):
        """Unfollows the user.

        Args:
            user (User): User to unfollow.

        Raises:
            NotLoggedIn: If the server doesn't accept the token.
        """
        resp = self.session.put(
            'https://sfpl.bibliocommons.com/user_profile/{}?type=unfollow&value={}'.format(self._id, user._id), headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': BeautifulSoup(self.session.get('https://sfpl.bibliocommons.com/user_profile/{}'.format(user._id)).text, 'lxml').find('meta', {'name': 'csrf-token'})['content']
            })

        if not resp.json()['logged_in']:
            raise exceptions.NotLoggedIn

    def getCheckouts(self):
        """Gets the user's checked out items.

        Returns:
            list: A list of Book objects.
        """
        resp = self.session.get(
            'https://sfpl.bibliocommons.com/checkedout')

        if resp.history:
            raise exceptions.NotLoggedIn

        return self.parseCheckouts(BeautifulSoup(resp.text, 'lxml'))

    def getHolds(self):
        """Gets the user's held items.

        Returns:
            list: A list of Book objects.
        """
        resp = self.session.get(
            'https://sfpl.bibliocommons.com/holds/index/not_yet_available')

        if resp.history:
            raise exceptions.NotLoggedIn

        return self.parseHolds(BeautifulSoup(resp.text, 'lxml'))

    @staticmethod
    def parseCheckouts(response):
        return [Book({'title': book.find(class_='title title_extended').text,
                      'author': book.find(testid='author_search').text if book.find(testid='author_search') else None,
                      'subtitle': book.find(class_='subTitle').text if book.find(class_='subTitle') else None,
                      '_id': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))},
                     status="Due {}".format(book(class_='checkedout_status out')[1].text.replace('\xa0', '')) if len(book(class_='checkedout_status out')) == 2 else (book.find(class_='checkedout_status overdue').text.strip() if book.find(class_='checkedout_status overdue') else book.find(class_='checkedout_status coming_due').text.strip()))
                for book in response('div', lambda class_: class_ and class_.startswith('listItem'))]

    @staticmethod
    def parseHolds(response):
        books = response(
            'div', lambda class_: class_ and class_.startswith('listItem'))

        book_data = []

        for book in books:
            if book.find(class_='hold_status in_transit'):
                location = book.find(class_='pick_up_location')
                location.span.clear()
                status = 'In Transit to {}'.format(location.text.strip())

            elif book.find(class_='pick_up_date'):
                status = book.find(
                    class_='pick_up_date').text.strip()

            else:
                status = book.find(
                    class_='hold_position').text.strip()

            book_data.append(Book({'title': book.find(testid='bib_link').text,
                                   'author': book.find(testid='author_search').text if book.find(testid='author_search') else None,
                                   'subtitle': book.find(class_='subTitle').text if book.find(class_='subTitle') else None,
                                   '_id': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))}, status=status))
        return book_data

    def loggedIn(self):
        return not bool(self.session.get('https://sfpl.bibliocommons.com/user_dashboard').history)

    def logout(self):
        """Logs out of the account."""
        self.session.get('https://sfpl.bibliocommons.com/user/logout')


class Book:
    """A book from the San Francisco Public Library

    Attributes:
        title (str): The title of the book.
        author (sre): The book's author's name.
        subtitle (str): The subtitle of the book.
        _id (int): SFPL's _id for the book.
        status (str): The book's status, if applicable. (e.g. duedate, hold position)
    """

    def __init__(self, data_dict, status=None):
        self.title = data_dict['title']
        self.author = data_dict['author']
        self.subtitle = data_dict['subtitle']
        self._id = data_dict['_id']

        self.status = status

    def getDescription(self):
        """Get the book's description.

        Returns:
            str: Book description.
        """
        return BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self._id)).text, 'lxml').find(class_='bib_description').text.strip()

    def getDetails(self):
        """Get's the book's details.

        Returns:
            dict: A dictionary with additional data like Publisher, Edition and ISBN.
        """
        book_page = BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self._id)).text, 'lxml')

        return {k: v for (k, v) in zip(
            [d.text.replace(':', '')
             for d in book_page(class_='label')],
            [d.text.strip().split() if book_page(class_='label')[book_page(class_='value').index(d)].text == 'ISBN:' else (
                [t.strip() for t in d.text.split('\n') if t] if book_page(class_='label')[book_page(class_='value').index(
                    d)].text == 'Additional Contributors:' else ' '.join(d.text.split())) for d in book_page(class_='value')])}

    def getKeywords(self):
        """Get the book's keywords.

        Returns:
            list: A list of terms contained in the book.
        """
        book_page = BeautifulSoup(requests.get('https://sfpl.bibliocommons.com/item/show/{}?active_tab=bib_info'.format(self._id)).text,
                                  'lxml')

        return book_page.find(class_='dataPair clearfix contents').find(
            class_='value').get_text('\n').split('\n') if book_page.find(class_='dataPair clearfix contents') else []

    def downloadJacket(self, filename):
        """Downloads the book's jacket image.

        Args:
            filename (str): The name of the file to save the image to.
        """
        with open('{}.png'.format(filename), 'wb') as jacket:
            image_url = BeautifulSoup(requests.get('https://sfpl.bibliocommons.com/item/show/{}'.format(
                self._id)).text, 'lxml').find(class_='jacketCover bib_detail')['src']
            jacket.write(requests.get(image_url if image_url.startswith(
                'http') else 'https:{}'.format(image_url)).content)

    @staticmethod
    def metaDataIdToId(metaDataId):
        """Converts a metadata ID to an ID contained in urls

        Args:
            metaDataId (str): The metadataId to convert.

        Returns:
            str: The ID contained in urls.
        """

        # var _id = id.split(/[SC]/g),
        metaDataID = re.split('[SC]', metaDataId)

        # sourceLibId = _id[1]
        sourceLibId = metaDataID[1]

        # var paddedSourceLibId = sourceLibId.padStart(3, '0');
        paddedSourceLibId = (3 - len(sourceLibId)) * '0' + \
            sourceLibId if len(sourceLibId) < 3 else sourceLibId

        # bibId = _id[2];
        bibId = metaDataID[2]

        return bibId + paddedSourceLibId

    def __str__(self):
        return '{} by {}'.format(self.title, self.author) if self.author else self.title

    def __repr__(self):
        return '{} by {}'.format(self.title, self.author) if self.author else self.title

    def __eq__(self, other):
        return self._id == other._id

    def __ne__(self, other):
        return self._id != other._id


class Search:
    """A search for books or user-created lists.

    Attributes:
        term (str): Search term.
        _type(str): The type of search.
    """

    def __init__(self, term, _type='keyword'):
        """
        Args:
            term (str): Search term.
            _type(str, optional): The type of search.

        Raises:
            InvalidSearchType: If the search type is not valid.
        """
        if _type.lower() in ['keyword', 'title', 'author', 'subject', 'tag', 'list']:
            self.term = term
            self._type = _type.lower()

        else:
            raise exceptions.InvalidSearchType(_type.lower())

    def getResults(self, pages=1):
        """Gets the results of the search.

        Args:
            pages(int): Number of pages to get.

        Yields:
            list: A list of books or lists on the page.
        """
        if self._type in ['keyword', 'title', 'author', 'subject', 'tag']:
            for x in range(1, pages + 1):
                query = '+'.join(self.term.split())
                url = f'https://sfpl.bibliocommons.com/v2/search?page={x}&query={query}&searchType={self._type}'
                resp = requests.get(url)
                soup = BeautifulSoup(resp.text, 'lxml')
                pages_element = soup.find(string=re.compile(book_page_regex))

                if not pages_element:
                    raise StopIteration

                pages = re.match(book_page_regex, pages_element).group(1).replace(',', '')

                if math.ceil(int(pages) / 10) < x:
                    raise StopIteration

                bib_data = json.loads(
                    soup.find(type='application/json').text)['entities']['bibs']

                books = []

                for book in bib_data:
                    authors = bib_data[book]['briefInfo']['authors']
                    b = Book({
                        'title': bib_data[book]['briefInfo']['title'],
                        'author': authors[0] if authors else None,
                        'subtitle': bib_data[book]['briefInfo']['subtitle'],
                        '_id': Book.metaDataIdToId(book),
                    })
                    books.append(b)

                yield books

        elif self._type == 'list':
            for x in range(1, pages + 1):
                resp = requests.get(
                    'https://sfpl.bibliocommons.com/search?page={}&q={}&search_category=userlist&t=userlist'.format(x, self.term))

                soup = BeautifulSoup(resp.text, 'lxml')

                if math.ceil(int(re.match(list_page_regex, str(soup.find(string=re.compile(list_page_regex))).strip()).group(1).replace(',', '')) / 25) < x:
                    raise StopIteration

                yield [List({'type': _list.find(class_='list_type small').text.strip(),
                             'title': _list.find(class_='title').text,
                             'user': User(_list.find(class_='username').text, _list.find(class_='username')['href'].split('/')[4]) if not _list.find(class_='username muted') else _list.find(class_='username muted').text.strip(),
                             'createdon': _list.find(class_='dataPair clearfix small list_created_date').find(class_='value').text,
                             'itemcount': int(_list.find(class_='list_item_count').text.replace('items', '')),
                             'description': _list.find(class_='description').text.replace('\n', ''),
                             'id': _list.find(class_='title').find('a')['href'].split('/')[4]
                             }) for _list in soup(class_='col-xs-12 col-sm-4 cp_user_list_item')]

    def __str__(self):
        return 'Search Type: {} Search Term {}'.format(self._type, self.term)

    def __repr__(self):
        return 'Search Type: {} Search Term {}'.format(self._type, self.term)

    def __eq__(self, other):
        return self._type == other._type and self.term == other.term

    def __ne__(self, other):
        return self._type != other._type or self.term != other.term


class AdvancedSearch:
    """An advanced, multi-term search.

    Attributes:
        query(str): The formatted query.
    """

    def __init__(self, exclusive=True, **kwargs):
        """
        Args:
            exclusive (bool): Whether or not to include all results that match or any that match.
            **kwargs: Search terms including one of 'include' or 'exclude' and one type such as 'keyword' or 'author'.
                      An example kwarg would be: includeauthor='J.K Rowling' or excludekeyword='Chamber'.
                      You can include multiple of the same type with includekeyword1='Chamber' and includekeyword2='Secrets'.

        Raises:
            MissingFilterTerm: If the term is missing a required part.
        """
        term_map = {'keyword': 'anywhere',
                    'author': 'contributor',
                    'title': 'title',
                    'subject': 'subject',
                    'series': 'series',
                    'award': 'award',
                    'identifier': 'identifier',
                    'region': 'region',
                    'genre': 'genre',
                    'publisher': 'publisher',
                    'callnumber': 'callnumber'}

        for term in kwargs:
            if not any(term.lower() in '{}{}'.format(t, s) for t in ['include', 'exclude'] for s in term_map):
                raise exceptions.MissingFilterTerm

        include = ['{}:({})'.format(
            ''.join(term_map[t] for t in term_map if t in term.lower()), kwargs[term]) for term in kwargs if 'include' in term.lower()]

        exclude = ['{}:({})'.format(
            ''.join(term_map[t] for t in term_map if t in term.lower()), kwargs[term]) for term in kwargs if 'exclude' in term.lower()]

        self.query = '({}){}'.format(
            (' AND ' if exclusive else ' OR ').join(include), ' -' + '-'.join(exclude) if exclude else '')

    def getResults(self, pages=1):
        """Generator that yields a stream of results.

        Args:
            pages(int): Number of pages to get.

        Yields:
            list: A list of books on the page.

        Examples:
            >>> search = sfpl.AdvancedSearch(includeauthor='J. K. Rowling', excludekeyword='Harry Potter')
            >>> stream = search.getResults(pages=2)
            >>> next(stream)
            [Fantastic Beasts and Where to Find Them by Rowling, J. K., Fantastic Beasts and Where to Find Them : The Original Screenplay by Rowling, J. K., The Casual Vacancy by Rowling, J. K., Very Good Lives by Rowling, J. K., Animales fantásticos y dónde encontrarlos by Rowling, J. K.]
        """
        for x in range(1, pages + 1):
            resp = requests.get(
                "https://sfpl.bibliocommons.com/v2/search?page={}&query={}&searchType=bl".format(x, self.query))

            soup = BeautifulSoup(resp.text, 'lxml')
            pages_element = soup.find(string=re.compile(book_page_regex))

            if not pages_element:
                raise StopIteration

            pages = re.match(book_page_regex, pages_element).group(1).replace(',', '')

            if math.ceil(int(pages) / 10) < x:
                raise StopIteration

            bib_data = json.loads(
                    soup.find(type='application/json').text)['entities']['bibs']

            books = []

            for book in bib_data:
                authors = bib_data[book]['briefInfo']['authors']
                b = Book({
                    'title': bib_data[book]['briefInfo']['title'],
                    'author': authors[0] if authors else None,
                    'subtitle': bib_data[book]['briefInfo']['subtitle'],
                    '_id': Book.metaDataIdToId(book),
                })
                books.append(b)

            yield books

    def __str__(self):
        return self.query

    def __repr__(self):
        return self.query

    def __eq__(self, other):
        return self.query == other.query

    def __ne__(self, other):
        return self.query != other.query


class List:
    """A user-created list of books.

    Atrributes:
        _type (str): type of list.
        title (str): title of the list.
        user (User): creator of the list.
        createdOn (str): the day the list was created.
        itemcount (int): the number of books in the list.
        description (str): a description of the list.
        _id (str): SFPL's id for the list.
    """

    def __init__(self, data_dict):
        self._type = data_dict['type']
        self.title = data_dict['title']
        self.user = data_dict['user']
        self.createdOn = data_dict['createdon']
        self.itemcount = data_dict['itemcount']
        self.description = data_dict['description']
        self._id = data_dict['id']

    def getBooks(self):
        return [Book({'title': book.find(class_='list_item_title').text.strip(),
                      'author': book.find(testid='author_search').text,
                      'subtitle': book.find(class_='list_item_subtitle').text.strip() if book.find(class_='list_item_subtitle') else None,
                      '_id': int(''.join(s for s in book.find('a')['href'] if s.isdigit()))
                      }) for book in BeautifulSoup(requests.get('https://sfpl.bibliocommons.com/list/share/{}_{}/{}'.format(self.user._id, self.user.name, self._id)
                                                                ).text, 'lxml')(class_='listItem bg_white col-xs-12')]

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    def __eq__(self, other):
        return self._id == other._id

    def __ne__(self, other):
        return self._id != other._id


class Branch:
    """A library branch.

    Attributes:
        name (str): The name of the library branch.
        _id (str): SFPL's ID for the library branch.
    """
    BRANCHES = {
        'anza': '44563120',
        'bayview': '44563121',
        'bernal heights': '44563122',
        'chinatown': '44563123',
        "chinatown children's": '44563124',
        'eureka valley': '44563125',
        'excelsior': '44563126',
        'glen park': '44563127',
        'golden gate valley': '44563128',
        'ingleside': '44563130',
        'main library': '44563151',
        'marina': '44563131',
        'merced': '44563132',
        'mission': '44563133',
        'mission bay': '44563134',
        'noe valley': '44563135',
        'north beach': '44563136',
        'ocean view': '44563137',
        'ortega': '44563138',
        'park': '44563139',
        'parkside': '44563140',
        'portola': '44563141',
        'potrero': '44563142',
        'presidio': '44563143',
        'richmond': '44563144',
        "richmond children's": '44563145',
        'sunset': '44563146',
        "sunset children's": '44563147',
        'visitacion valley': '44563148',
        'west portal': '44563149',
        'western addition': '44563150',
    }

    def __init__(self, name):
        """
        Args:
            name (str): Name of library branch to match.

        Raises:
            NoBranchFound: No matches for the given name were found.
        """
        for branch in Branch.BRANCHES:
            if name.lower() in branch.lower():
                self.name = branch
                self._id = Branch.BRANCHES[self.name]
                break

        else:
            raise exceptions.NoBranchFound(name)

    def getHours(self):
        """Get the operating hours of the library.

        Returns:
            dict: A dictionary mapping days of the week to operating hours.
        """
        branch = (
            self.name
                .replace(" children's", '')
                .replace(' ', '-')
                .lower()
        )
        response = requests.get(f'https://sfpl.org/locations/{branch}')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        result = {}

        for day in soup.select('.office-hours__item'):
            day_of_week = day.select_one('.office-hours__item-label').text.strip()
            hours = day.select_one('.office-hours__item-slots').text.strip()
            result[day_of_week] = hours

        return result

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name
