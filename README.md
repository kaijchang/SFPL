# SFPL Scraper
![travis](https://travis-ci.org/kajchang/sfpl-scraper.svg?branch=master)
![pypi](https://badge.fury.io/py/sfpl.svg)

Python Package for accessing data on the SFPL Website in a Python program.

# Usage

```pip install sfpl``` or clone / download this repository and ```python setup.py install```.

The package has 3 classes: SFPL, Book and Author.

The SFPL class is allows you to access SFPL account and all its holds, checkouts, and shelves

## SFPL Class

### Methods

The current methods are ```getHolds()```, ```getCheckouts()```, ```getForLater()```, ```getInProgress()``` and ```getCompleted()```.

The ```getHolds()``` method returns a Book object for each book in your holds.
The ```getCheckouts()``` method returns a Book object for each book you've checked out.
The ```getForLater()```, ```getInProgress()``` and ```getCompleted()``` methods return Book objects for each book in the respective shelf.

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
