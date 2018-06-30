import requests
from bs4 import BeautifulSoup
import sfpl.exceptions


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
        """
        if not _id:
            self.name = name
            r = requests.get(
                'https://sfpl.bibliocommons.com/search?t=user&search_category=user&q={}'.format(self.name))

            if r.url == 'https://sfpl.bibliocommons.com/search?t=user&search_category=user&q={}'.format(self.name):
                raise Exception('No user found.')

            else:
                self._id = r.url.split('/')[4]

        else:
            self.name = name
            self._id = _id

    def getFollowing(self):
        """Gets all the users the account follows.

        Returns:
            A list of User objects.
        """
        return [User(user.find('a').text,
                     user.find('a')['href'].split('/')[4]) for user in BeautifulSoup(requests.get(
                         'https://sfpl.bibliocommons.com/user_profile/{}/following'.format(self._id)).text, 'html.parser').find_all(class_='col-xs-12 col-md-4')]

    def getFollowers(self):
        """Gets all the account's followers.

        Returns:
            A list of User objects.
        """
        return [User(user.find('a').text,
                     user.find('a')['href'].split('/')[4]) for user in BeautifulSoup(requests.get(
                         'https://sfpl.bibliocommons.com/user_profile/{}/followers'.format(self._id)).text, 'html.parser').find_all(class_='col-xs-12 col-md-4')]

    def getLists(self):
        """Gets all the lists the user has created.

        Returns:
            A list of List objects.
        """
        return [List({'type': _list.find_all('td')[1].text.strip(),
                      'title': _list.find('a').text,
                      'user': self,
                      'createdon': _list.find_all('td')[2].text.strip(),
                      'itemcount': int(_list.find_all('td')[3].text),
                      'description': None,
                      'id': _list.find('a')['href'].split('/')[4]
                      }) for _list in BeautifulSoup(requests.get(
                          'https://sfpl.bibliocommons.com/lists/show/{}'.format(self._id)).text, 'html.parser').find('tbody').find_all('tr')]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self._id == other._id

    def __ne__(self, other):
        return self._id != other._id


class SFPL(User):
    """The SFPL account class.

    Attributes:
        session (requests.Session): the requests Session with the login cookies.
        name (str): the account's username.
        _id (str): the account's id.
    """

    session = requests.Session()

    def __init__(self, barcode, pin):
        """
        Args:
            barcode (str): The library card barcode.
            pin (str): PIN/ password for library account.

        Raises:
            LoginError: If we aren't redirected to the main page after login.
        """
        r = self.session.post(
            'https://sfpl.bibliocommons.com/user/login?destination=https%3A%2F%2Fsfpl.org%2F',
            data={'name': barcode, 'user_pin': pin, 'remember_me': True})

        if r.url != 'https://sfpl.org/':
            raise sfpl.exceptions.LoginError

        main = BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/user_dashboard').text, 'html.parser')

        self.name = main.find(class_='cp_user_card')['data-name']
        self._id = main.find(class_='cp_user_card')['data-id']

    def hold(self, book, branch):
        """Holds the book.

        Args:
            book (Book): Book object to hold.
            branch (Branch): Branch to have book delivered to.
        """
        self.session.post(
            'https://sfpl.bibliocommons.com/holds/place_single_click_hold/{}'.format(book._id), data={
                'authenticity_token': BeautifulSoup(self.session.get('https://sfpl.bibliocommons.com/item/show/{}'.format(book._id)).text, 'html.parser').find('input', {'name': 'authenticity_token'})['value'],
                'bib': book._id,
                'branch': branch._id
            }, headers={
                'X-Requested-With': 'XMLHttpRequest'
            })

    def cancelHold(self, book):
        """Cancels the hold on the book.

        Args:
            book (Book): Book object to cancel the hold for.

        Raises:
            NotOnHold: If the book isn't being held.
            NotLoggedIn: If the server doesn't accept the token.
        """
        holds = BeautifulSoup(self.session.get(
            'https://sfpl.bibliocommons.com/holds').text, 'html.parser')

        for hold in holds.find_all('div', {'class': [
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 in_transit bg_white',
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 not_yet_available bg_white',
                'listItem col-sm-offset-1 col-sm-10 col-xs-12 ready_for_pickup bg_white']}):

            if hold.find(testid='bib_link').text == book.title:
                r = self.session.post('https://sfpl.bibliocommons.com/holds/delete.json', data={
                    'authenticity_token': holds.find('input', {'name': 'authenticity_token'})['value'],
                    'confirm_hold_delete': True,
                    'items[]': hold.find(class_='btn btn-link single_circ_action')['href'].split('/')[3],
                    'bib_status': 'future',
                    'is_private': True
                }, headers={
                    'X-Requested-With': 'XMLHttpRequest'
                }).json()

                if not r['logged_in']:
                    raise sfpl.exceptions.NotLoggedIn

                return

        raise sfpl.exceptions.NotOnHold(book.title)

    def follow(self, user):
        """Follows the user.

        Args:
            user (User): User to follow.

        Raises:
            NotLoggedIn: If the server doesn't accept the token.
        """
        r = self.session.put(
            'https://sfpl.bibliocommons.com/user_profile/{}?type=follow&value={}'.format(self._id, user._id), headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': BeautifulSoup(self.session.get('https://sfpl.bibliocommons.com/user_profile/{}'.format(user._id)).text, 'html.parser').find('meta', {'name': 'csrf-token'})['content']
            }).json()

        if not r['logged_in']:
            raise sfpl.exceptions.NotLoggedIn

    def unfollow(self, user):
        """Unfollows the user.

        Args:
            user (User): User to unfollow.

        Raises:
            NotLoggedIn: If the server doesn't accept the token.
        """
        r = self.session.put(
            'https://sfpl.bibliocommons.com/user_profile/{}?type=unfollow&value={}'.format(self._id, user._id), headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': BeautifulSoup(self.session.get('https://sfpl.bibliocommons.com/user_profile/{}'.format(user._id)).text, 'html.parser').find('meta', {'name': 'csrf-token'})['content']
            }).json()

        if not r['logged_in']:
            raise sfpl.exceptions.NotLoggedIn

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
        return [Book({'title': book.find(testid='bib_link').text,
                      'author': book.find(testid='author_search').text if book.find(testid='author_search') else None,
                      'subtitle': book.find(class_='subTitle').text if book.find(class_='subTitle') else None,
                      '_id': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))})
                for book in response.find_all('div', lambda value: value and value.startswith('listItem clearfix'))]

    @classmethod
    def parseCheckouts(cls, response):
        return [Book({'title': book.find(class_='title title_extended').text,
                      'author': book.find(testid='author_search').text if book.find(testid='author_search') else None,
                      'subtitle': book.find(class_='subTitle').text if book.find(class_='subTitle') else None,
                      '_id': int(''.join(s for s in book.find(testid='bib_link')['href'] if s.isdigit()))},
                     status="Due {}".format(book.find_all(class_='checkedout_status out')[1].text.replace('\xa0', '')))
                for book in response.find_all('div', class_='listItem col-sm-offset-1 col-sm-10 col-xs-12 out bg_white')]

    @classmethod
    def parseHolds(cls, response):
        books = response.find_all('div', {'class': [
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 in_transit bg_white',
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 not_yet_available bg_white',
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 ready_for_pickup bg_white']})

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
            Book description.
        """
        return BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self._id)).text, 'html.parser').find(class_='bib_description').text.strip()

    def getDetails(self):
        """Get's the book's details.

        Returns:
            A dictionary with additional data like Publisher, Edition and ISBN.
        """
        book_page = BeautifulSoup(requests.get(
            'https://sfpl.bibliocommons.com/item/show/{}'.format(self._id)).text, 'html.parser')

        return {k: v for (k, v) in zip(
            [d.text.replace(':', '')
             for d in book_page.find_all(class_='label')],
            [d.text.strip().split() if book_page.find_all(class_='label')[book_page.find_all(class_='value').index(d)].text == 'ISBN:' else (
                [t.strip() for t in d.text.split('\n') if t] if book_page.find_all(class_='label')[book_page.find_all(class_='value').index(
                    d)].text == 'Additional Contributors:' else ' '.join(d.text.split())) for d in book_page.find_all(class_='value')])}

    def getKeywords(self):
        """Get the book's keywords.

        Returns:
            A list of terms contained in the book.
        """
        book_page = BeautifulSoup(requests.get('https://sfpl.bibliocommons.com/item/show/{}?active_tab=bib_info'.format(self._id)).text,
                                  'html.parser')

        return book_page.find(class_='dataPair clearfix contents').find(
            class_='value').get_text('\n').split('\n') if book_page.find(class_='dataPair clearfix contents') else []

    def __str__(self):
        return '{} by {}'.format(self.title, self.author.name)

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
            raise sfpl.exceptions.InvalidSearchType(_type.lower())

    def getResults(self, pages=1):
        if self._type in ['keyword', 'title', 'author', 'subject', 'tag']:
            return [Book({'title': book.find('span').text,
                          'author': book.find(class_='author-link').text,
                          'subtitle': book.find(class_='cp-subtitle').text if book.find(class_='cp-subtitle') else None,
                          '_id': int(''.join(s for s in book.find('a')['href'] if s.isdigit()))})
                    for x in range(1, pages + 1) for book in BeautifulSoup(requests.get(
                        "https://sfpl.bibliocommons.com/v2/search?pagination_page={}&query={}&searchType={}".format(x, '+'.join(self.term.split()), self._type)).text,
                'html.parser').find_all(class_='cp-search-result-item-content')]

        elif self._type == 'list':
            return [List({'type': _list.find(class_='list_type small').text.strip(),
                          'title': _list.find(class_='title').text,
                          'user': User(_list.find(class_='username').text, _list.find(class_='username')['href'].split('/')[4]) if not _list.find(class_='username muted') else _list.find(class_='username muted').text.strip(),
                          'createdon': _list.find(class_='dataPair clearfix small list_created_date').find(class_='value').text,
                          'itemcount': int(_list.find(class_='list_item_count').text.replace('items', '')),
                          'description': _list.find(class_='description').text.replace('\n', ''),
                          'id': _list.find(class_='title').find('a')['href'].split('/')[4]
                          }
                         ) for x in range(1, pages + 1) for _list in BeautifulSoup(requests.get(
                             'https://sfpl.bibliocommons.com/search?page={}&q={}&search_category=userlist&t=userlist'.format(x, self.term)).text,
                'html.parser').find_all(class_='col-xs-12 col-sm-4 cp_user_list_item')]

    def __eq__(self, other):
        return self._type == other._type and self.term == other.term

    def __ne__(self, other):
        return self._type != other._type or self.term != other.term


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
                                                                ).text, 'html.parser').find_all(class_='listItem bg_white col-xs-12')]

    def __str__(self):
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

    def __init__(self, name):
        """
        Args:
            name (str): Name of library branch to match.

        Raises:
            NoBranchFound: No matches for the given name were found.
        """
        branches = {'ANZA BRANCH': '44563120',
                    'BAYVIEW BRANCH': '44563121',
                    'BERNAL HEIGHTS BRANCH': '44563122',
                    'CHINATOWN BRANCH': '44563123',
                    "CHINATOWN CHILDREN'S": '44563124',
                    'EUREKA VALLEY BRANCH': '44563125',
                    'EXCELSIOR BRANCH': '44563126',
                    'Friends for Life': '44563152',
                    'GLEN PARK BRANCH': '44563127',
                    'GOLDEN GATE VALLEY BRANCH': '44563128',
                    'Green Bookmobile': '44563155',
                    'INGLESIDE BRANCH': '44563130',
                    'LIBRARY FOR THE BLIND': '983427677',
                    'LIBRARY ON WHEELS': '44563158',
                    'MAIN': '44563151',
                    'MARINA BRANCH': '44563131',
                    'MERCED BRANCH': '44563132',
                    'MISSION': '44563133',
                    'MISSION BAY BRANCH': '44563134',
                    'NOE VALLEY': '44563135',
                    'NORTH BEACH BRANCH': '44563136',
                    'OCEAN VIEW BRANCH': '44563137',
                    'ORTEGA BRANCH': '44563138',
                    'PARK BRANCH': '44563139',
                    'PARKSIDE BRANCH': '44563140',
                    'PORTOLA BRANCH': '44563141',
                    'POTRERO BRANCH': '44563142',
                    'PRESIDIO BRANCH': '44563143',
                    'RICHMOND BRANCH': '44563144',
                    "RICHMOND CHILDREN'S": '44563145',
                    'SUNSET BRANCH': '44563146',
                    "SUNSET CHILDREN'S": '44563147',
                    'TREASURE ISLAND BOOKMOBILE': '44563154',
                    'VISITACION VALLEY BRANCH': '44563148',
                    'WESTERN ADDITION BRANCH': '44563150',
                    'WEST PORTAL BRANCH': '44563149'}

        for branch in branches:
            if name.lower() in branch.lower():
                self.name = branch
                self._id = branches[self.name]
                return

        raise sfpl.exceptions.NoBranchFound(name)
