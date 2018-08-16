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

* Better Book Status Messages

## How to Use

Searching for books on Python:

```python
>>> from sfpl import Search
>>> python_search = Search('Python')
>>> results = python_search.getResults(pages=2) # .getResults is a generator that yields / streams pages of results
>>> for page in results:
		print(page)
[Python by Donaldson, Toby, Python by Johansen, Andrew, Python! by Moses, Brian, Python by McGrath, Mike, Python by Vo. T. H, Phuong]
[Python by Romano, Fabrizio, Python by Phillips, Dusty, Python by Joshi, Prateek, Python by Lassoff, Mark, Python by Wayani, Rafiq]
```

Searching for books by J.K. Rowling:

```python
>>> from sfpl import Search
>>> jk_search = Search('J.K. Rowling', _type='author')
>>> results = jk_search.getResults()
>>> first_page = next(results)
>>> first_page[0].title
"Harry Potter and the Sorcerer's Stone"
>>> first_page[0].getDescription()
"For the first time, J. K. Rowling's beloved Harry Potter ..."
```

Searching for book lists related to San Francisco:

```python
>>> from sfpl import Search
>>> list_search = Search('San Francisco', _type='list')
>>> results = list_search.getResults()
>>> first_page = next(results)
>>> first_page[0].title
'Made in SF - San Francisco love for young readers'
>>> for book in first_page[0].getBooks():
		print(book)
Al Capone Does My Shirts by Choldenko, Gennifer
Book Scavenger by Bertman, Jennifer Chambliss
...
```

Getting all your books on hold:

```python
>>> from sfpl import Account
>>> my_account = Account('barcode', 'pin') # Replace with your barcode and pin.
>>> my_holds = my_account.getHolds()
>>> for book in my_holds:
		print(book.title)
'Python for Data Analysis'
'Automate the Boring Stuff With Python'
>>> for book in my_holds:
		print(book.status)
'#4 on 6 copies'
'#7 on 3 copies'
>>> for book in my_holds:
		print(book.author)
'McKinney, Wes'
'Sweigart, Al'
```

Searching for books by J.K. Rowling but not about Harry Potter:

```python
>>> from sfpl import AdvancedSearch
>>> search = AdvancedSearch(includeauthor='J.K. Rowling', excludekeyword='Harry Potter') # Search for books by J.K. Rowling but don't include 'Harry Potter'
>>> results = search.getResults()
>>> for book in results:
		print(book.title)
'Fantastic Beasts and Where to Find Them'
'Fantastic Beasts and Where to Find Them : The Original Screenplay'
'The Casual Vacancy'
'Very Good Lives'
'Una vacante imprevista'
```

Getting hours for a library branch:

```python
>>> from sfpl import Branch
>>> branch = Branch('anza')
>>> branch.getHours()
{'Sun': '1 - 5', 'Mon': '12 - 6', 'Tue': '10 - 9', 'Wed': '1 - 9', 'Thu': '10 - 6', 'Fri': '1 - 6', 'Sat': '10 - 6'}
```
