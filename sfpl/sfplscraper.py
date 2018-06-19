from robobrowser import RoboBrowser


class SFPL:
    def __init__(self, barcode, pin):
        """The SFPL scraper object
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
        """Gets the user's checked out items
        Returns:
            A list containing dictionaries with basic information on the book and due date
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/checkedout/index/out')

        return self.parseCheckouts(self.browser.parsed)

    def getHolds(self):
        """Gets the user's held items
        Returns:
            A list containing dictionaries with basic information on the book and hold status
        """
        self.browser.open('https://sfpl.bibliocommons.com/holds')

        return self.parseHolds(self.browser.parsed)

    def getForLater(self):
        """Get's user's for later shelf
        Returns:
            A list containing dictionaries with basic information on each book
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/collection/show/my/library/for_later')
        return self.parseShelf(self.browser.parsed)

    def getInProgress(self):
        """Get's user's in progress shelf
        Returns:
            A list containing dictionaries with basic information on each book
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/collection/show/my/library/in_progress')
        return self.parseShelf(self.browser.parsed)

    def getCompleted(self):
        """Get's user's completed shelf
        Returns:
            A list containing dictionaries with basic information on each book
        """
        self.browser.open(
            'https://sfpl.bibliocommons.com/collection/show/my/library/completed')
        return self.parseShelf(self.browser.parsed)

    def parseShelf(self, response):
        # Internal function to reduce duplicate code.
        books = response.find_all(
            'div', lambda value: value and value.startswith('listItem clearfix'))

        book_data = []

        for book in books:
            this_book_data = {
                'title': book.find(testid='bib_link').text,
                'author': book.find(testid='author_search').text,
                'medium': book.find(class_='format').find('strong').text,
                'publication year': int(book.find(class_='format').text.split('\n')[2].strip().replace('-', ''))
            }

            if book.find(class_='subTitle'):
                this_book_data['subtitle'] = book.find(class_='subTitle').text

            else:
                this_book_data['subtitle'] = None

            book_data.append(this_book_data)

        return book_data

    def parseCheckouts(self, response):
        books = response.find_all(
            'div', class_='listItem col-sm-offset-1 col-sm-10 col-xs-12 out bg_white')

        book_data = []

        for book in books:
            this_book_data = {
                'title': book.find(class_='title title_extended').text,
                'author': book.find(testid='author_search').text,
                'medium': book.find(class_='format').text.split('\n')[1].strip(),
                'publication year': int(book.find(class_='format').text.split('\n')[2].strip().replace('-', '')),
                'duedate': book.find_all(class_='checkedout_status out')[1].text.replace('\xa0', ''),
            }

            if book.find(class_='subTitle'):
                this_book_data['subtitle'] = book.find(class_='subTitle').text
            else:
                this_book_data['subtitle'] = None

            book_data.append(this_book_data)

        return book_data

    def parseHolds(self, response):
        books = response.find_all('div', {'class': [
            'listItem col-sm-offset-1 col-sm-10 col-xs-12 in_transit bg_white', 'listItem col-sm-offset-1 col-sm-10 col-xs-12 not_yet_available bg_white', 'listItem col-sm-offset-1 col-sm-10 col-xs-12 ready_for_pickup bg_white']})

        book_data = []

        for book in books:
            this_book_data = {
                'title': book.find(testid='bib_link').text,
                'author': book.find(testid='author_search').text,
                'medium': book.find(class_='format').text.split('\n')[1].strip(),
                'publication year': int(book.find(class_='format').text.split('\n')[2].strip().replace('-', '')),
            }

            if book.find(class_='hold_status in_transit'):
                location = book.find(class_='pick_up_location')
                location.span.clear()
                this_book_data['status'] = 'In Transit to {}'.format(
                    location.text.strip())

            elif book.find(class_='pick_up_date'):
                this_book_data['status'] = book.find(
                    class_='pick_up_date').text.strip()

            else:
                this_book_data['status'] = book.find(
                    class_='hold_position').text.strip()

            if book.find(class_='subTitle'):
                this_book_data['subtitle'] = book.find(class_='subTitle').text

            else:
                this_book_data['subtitle'] = None

            book_data.append(this_book_data)

        return book_data
