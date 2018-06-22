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
>>> [book.title for book in sfpl.getCheckouts()]
['On Intelligence', 'Money', 'Deep Learning', 'Make your Own Neural Network']
```

## Book Class

Returned by other classes, or can be created independently.

### Attributes

```title``` - Title of the book.

```author``` - Author of the book as a Author object.

```subtitle``` - The book's subtitle.

```ID``` - The SFPL's id for the book. (used for holding / looking up details)

```status``` - Status of the book, if applicable. (duedate, hold position, etc.)

### Methods

```getDescription()``` - Returns the SFPL's description of the book.

```getDetails()``` - Returns details on the book. (ISBN, Call Number, etc.)

### Example

Returned by SFPL / Author class methods:

```
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
>>> checkedOutBooks = sfpl.getCheckouts() # Get all checked out books
>>> book = checkedOutBooks[0] # Get the first book in the list
>>> book.title
'Basics of Web Design'
>>> book.subtitle
'HTML5 & CSS3'
>>> book.status
'Due Jun 28, 2018'
```

Created independently:

```
>>> from sfpl import Book
>>> book = Book('Learning Python')
>>> book.getDescription()
"Get a comprehensive, in-depth introduction to the core Python language with this hands-on book. Based on author Mark Lutz's popular training course..."
>>> book.getDetails()
{'Publisher': "Sebastopol, CA :, O'Reilly,, 2013", 'Edition': '5th ed', 'ISBN': ['9781449355739', '1449355730'], 'Call Number': '005.133 P999L2 2013', 'Characteristics': 'l, 1540 pages : illustrations ; 24 cm', 'Alternative Title': 'Python'}
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

Better Status Messages
