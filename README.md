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

```getHolds()``` - Returns a list containing Book objects for each book in your holds.

```getCheckouts()``` - Returns a list containing Book objects for each book you've checked out.

```getForLater()```, ```getInProgress()``` and ```getCompleted()``` methods return a list containing Book objects for each book in the respective shelf.

### Example

```
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
```

## Book Class

Returned by other classes.

### Attributes

```title``` - Title of the book.

```author``` - Author of the book as a Author object.

```medium``` - Medium of the resource. (Audiobook, Book, Website)

```publication_year``` - The year the book was published.

```subtitle``` - The book's subtitle.

```status``` - Status of the book, if applicable. (duedate, hold position, etc.)

### Example

```
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
>>> checkedOutBooks = sfpl.getCheckouts() # Get all checked out books
>>> book = checkedOutBooks[0] # Get the first book in the list
>>> book.title
'Basics of Web Design'
>>> book.medium
'Book'
>>> book.publication_year
2012
>>> book.subtitle
'HTML5 & CSS3'
>>> book.status
'Due Jun 28, 2018'
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

Tests for Author
