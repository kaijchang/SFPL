# SFPL

Python Package for accessing account, book, and author data from the SFPL Website.

## Status
![travis](https://travis-ci.org/kajchang/SFPL.svg?branch=master)
[![pypi](https://badge.fury.io/py/sfpl.svg)](https://pypi.org/project/sfpl/)

## Installation

From `pip`:

`$ pip install sfpl`

From source:

`$ pip install git+git://github.com/kajchang/SFPL.git`

Or clone / download this repository and `$ python setup.py install` or `$ pip install .`

## Frameworks Used

`requests` - Used for getting data from the SFPL website and managing login cookies.

`bs4 + lxml` - Used for parsing information from HTML.

## Features

* Managing current checkouts and holds for your SFPL library account.

* Searching for books by keyword, title, author, subject, and tag and searching for user-created book lists.

* Following other library users and viewing their book lists.

* Getting libary branch hours.

### TODO

* Boolean Search Filters

* Better Book Status Messages

## How to Use

Searching for books on Python:

```python
>>> from sfpl import Search # Import the Search class, used for finding useful books or book lists.
>>> python_search = Search('Python')
>>> results = python_search.getResults(pages=2) # You can specify how many pages of results to get (defaults to 1) 
>>> book = results[1] # Let's take a closer look at one of the books.
>>> print(book.getDetails()) # Get some more details on the book.
{
	'Publisher': '[Place of publication not identified] :, Mercury Learning, , 2017', 
	'ISBN': ['9781944534653'], 
	'Call Number': 'EBOOK BOOKS24x7', 
	'Characteristics': '1 online resource (549 pages) : illustrations'
}
>>> print(book.getDescription()) # Get a description of the book.
'Following a practical, just-in-time presentation which gives students material as they need it ...'
```

Searching for books by J.K. Rowling:

```python
>>> from sfpl import Search # Import the Search class, used for finding useful books or book lists.
>>> jk_search = Search('J.K. Rowling', _type='author') # You can specify a search type (defaults to keyword)
>>> results = jk_search.getResults()
>>> for book in results: # Print the titles for each book.
		print(book.title)
"Harry Potter and the Sorcerer's Stone"
'Harry Potter and the Prisoner of Azkaban'
'Harry Potter and the Chamber of Secrets'
'Harry Potter and the Cursed Child Parts One and Two'
'Fantastic Beasts and Where to Find Them'
```

Searching for book lists related to San Francisco:

```python
>>> from sfpl import Search # Import the Search class, used for finding useful books or book lists.
>>> list_search = Search('San Francisco', _type='list')
>>> results = list_search.getResults()
>>> _list = results[0] # Let's take a close look at one of these lists.
>>> print(_list.name, _list._type, _list.createdOn, _list.itemcount) # Print some of the list's attributes.
'Made in SF - San Francisco love for young readers'   'Topic Guide'   'Oct 20, 2016'   18
>>> print(_list.user.name) # Print the name of the list creator.
'SFPL_Kids'
>>> for book in _list.getBooks(): # Print the titles of all the books in the list.
		print(book.title)
'Al Capone Does My Shirts'
'Book Scavenger'
'Discovering Mission San Francisco De Asis'
'Larry Gets Lost in San Francisco'
'Levi Strauss Gets A Bright Idea'
'Me, Frida'
...
```

Getting all your books on hold:

```python
>>> from sfpl import Account # Import the Account class, used for interacting with your library account.
>>> my_account = Account('barcode', 'pin') # Login with your barcode and pin.
>>> my_holds = my_account.getHolds()
>>> for book in my_holds: # Print the title for each book
		print(book.title)
'Python for Data Analysis'
'Automate the Boring Stuff With Python'
>>> for book in my_holds: # Print the hold status for each book
		print(book.status)
'#4 on 6 copies'
'#7 on 3 copies'
>>> for book in my_holds: # Print the author for each book
		print(book.author)
'McKinney, Wes'
'Sweigart, Al'
```

Getting hours for a library branch:

```python
>>> from sfpl import Branch # Import the Branch class, used for interacting with library branches.
>>> branch = Branch('anza')
>>> branch.getHours()
{'Sun': '1 - 5', 'Mon': '12 - 6', 'Tue': '10 - 9', 'Wed': '1 - 9', 'Thu': '10 - 6', 'Fri': '1 - 6', 'Sat': '10 - 6'}
```
