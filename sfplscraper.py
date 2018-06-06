from robobrowser import RoboBrowser


class SFPL:
    def __init__(self, barcode, pin):
        self.browser = RoboBrowser(parser='html5lib')
        self.browser.open('https://sfpl.bibliocommons.com/user/login')
        form = self.browser.get_form(class_='loginForm left')
        form['name'] = barcode
        form['user_pin'] = pin
        self.browser.submit_form(form)

    def getCheckedOut(self):
        self.browser.open(
            'https://sfpl.bibliocommons.com/checkedout/index/out')
        books = self.browser.parsed.find_all(
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
