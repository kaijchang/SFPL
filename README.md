# SFPL Scraper
![travis](https://travis-ci.org/kajchang/sfpl-scraper.svg?branch=master)
![pypi](https://badge.fury.io/py/sfpl.svg)

Python Package for accessing account, book, and author data from the SFPL Website.

# Usage

```pip install sfpl``` or clone / download this repository and ```python setup.py install```.

The package has 3 classes: SFPL, Book and Author.

## SFPL Class

The SFPL class is allows you to access SFPL accounts and all their holds, checkouts, and shelves.

### Methods

#### Read Methods

```getHolds()``` - Returns a list containing Book objects for each book in your holds.

```getCheckouts()``` - Returns a list containing Book objects for each book you've checked out.

```getForLater()```, ```getInProgress()``` and ```getCompleted()``` - Return a list containing Book objects for each book in the respective shelves.

#### Write Methods

```hold(book)``` - Takes a Book object as a parameter and holds the book.

TODO:
Holding errors

### Example

```
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
>>> sfpl.getCheckouts()
[<__main__.Book object at 0x114b284e0>, <__main__.Book object at 0x114b41c88>, <__main__.Book object at 0x114b41d30>, <__main__.Book object at 0x114b41dd8>]
>>> [book.title for book in sfpl.getCheckouts()]
['On Intelligence', 'Money', 'Deep Learning', 'Make your Own Neural Network']
```

## Book Class

Returned by other classes.

### Attributes

```title``` - Title of the book.

```author``` - Author of the book as a Author object.

```version``` - Dictionary mapping mediums to their publication years.

```subtitle``` - The book's subtitle.

```id``` - The SFPL's id for the book. (used for holding / looking up details)

```status``` - Status of the book, if applicable. (duedate, hold position, etc.)

### Methods

```getDescription()``` - Returns the SFPL's description of the book.

```getDetails()``` - Returns details on the book. (ISBN, Call Number, etc.)

### Example

```
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
>>> checkedOutBooks = sfpl.getCheckouts() # Get all checked out books
>>> book = checkedOutBooks[0] # Get the first book in the list
>>> book.title
'Basics of Web Design'
>>> book.version
{'Book': 2012}
>>> book.subtitle
'HTML5 & CSS3'
>>> book.status
'Due Jun 28, 2018'
>>> book.getDescription()
Basics of Web Design: HTML, XHTML, and CSS is intended for use in a beginning web design or web development course. The text covers the basics ....
>>> book.getDetails()
{'Publisher': 'Boston : Addison-Wesley, c2012', 'ISBN': ['9780137003389', '0137003382'], 'Call Number': '006.74 H8599mo2', 'Characteristics': 'xi, 352 p. : col. ill. ; 26 cm', 'Alternative Title': 'Web design'}
```

## Author Class

Returned in Book objects from SFPL class methods, or can be created independently.

### Attributes

```name``` - Name of the author

### Methods

```getBooks()``` - Get top 5 books written by the author

TODO:
Support pagination

### Examples

Returned by SFPL class methods:

```
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
>>> checkedOutBooks = sfpl.getCheckouts() # Get all checked out books
>>> book = checkedOutBooks[0] # Get the first book in the list
>>> book.author.name
'Felke-Morris, Terry'
```

Created independently:

```
>>> from sfpl import Author
>>> author = Author('J.K. Rowling')
>>> books = author.getBooks() # Get top 5 books written by J.K. Rowling
>>> book = books[0] # Get the first book in the list
>>> book.title
"Harry Potter and the Sorcerer's Stone"
```

## TODO:

Calendars

Events

Searches

Better Status Messages
