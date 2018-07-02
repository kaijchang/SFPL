# SFPL
![travis](https://travis-ci.org/kajchang/SFPL.svg?branch=master)
![pypi](https://badge.fury.io/py/sfpl.svg)

Python Package for accessing account, book, and author data from the SFPL Website.

# Usage

Install the package:

```$ pip install sfpl```

Clone / download this repository and ```$ python setup.py install``` or ```$ pip install .```

# Table of Contents

The package has 6 classes: SFPL, Search, Book, List, Branch and User.

[Book Class](https://github.com/kajchang/SFPL#book-class)

[Search Class](https://github.com/kajchang/SFPL#search-class)

[List Class](https://github.com/kajchang/SFPL#list-class)

[Branch Class](https://github.com/kajchang/SFPL#branch-class)

[User Class](https://github.com/kajchang/SFPL#user-class)

[SFPL Class](https://github.com/kajchang/SFPL#sfpl-class)

# Book Class

[Top](https://github.com/kajchang/SFPL#sfpl)

A book in the SFPL database.

## Attributes

```title``` - Title of the book.

```author``` - The name of the book's author.

```subtitle``` - The book's subtitle.

```ID``` - The SFPL's id for the book. (used for holding / looking up details)

```status``` - Status of the book, if applicable. (duedate, hold position, etc.)

## Methods

```Book.getDescription()``` - Returns the SFPL's description of the book.

```Book.getDetails()``` - Returns details on the book. (ISBN, Call Number, etc.)

```Book.getKeywords()``` - Returns a list of terms from the book.

## Example

```python
>>> from sfpl import SFPL
>>> sfpl = SFPL('barcode', 'pin')
>>> checkedOutBooks = sfpl.getCheckouts()  # Get all checked out books
>>> book = checkedOutBooks[0]  # Get the first book in the list
>>> book.title
'Basics of Web Design'
>>> book.subtitle
'HTML5 & CSS3'
>>> book.status
'Due Jun 28, 2018'
>>> book.author
'Felke-Morris, Terry'
```

# Search Class

[Top](https://github.com/kajchang/SFPL#sfpl)

Searches for books or for user-created lists.

## Attributes

```term``` - Name of the author.

```_type``` - Type of search (author, keyword, tag, list). Defaults to keyword.

## Methods

```Search.getResults(pages)``` - Get specified number of pages of books (5 / page) by the author. Defaults to 1 page.

## Examples

Searches for books by a specific author:

```python
>>> from sfpl import Search
>>> author = Search('J.K. Rowling', _type='author')
>>> books = author.getResults()  # Get first page of books written by J.K. Rowling
>>> book = books[0]  # Get the first book in the list
>>> book.title
"Harry Potter and the Sorcerer's Stone"
```

Searches for books with a certain keyword:

```python
>>> from sfpl import Search
>>> search = Search('Python') # Defaults to keyword search
>>> books = search.getResults() # Get the first page of books with keyword 'Python'
>>> book = books[0]  # Get the first book in the list
>>> book.getDescription()
'Python is a remarkably powerful dynamic programming language used in a wide variety of situations such as Web, database access ...'
>>> book.getDetails()
{'Publisher': '[San Francisco, California] :, Peachpit Press,, [2014]', 'Edition': 'Third edition', 'ISBN': ['9780321929556', '0321929551'], ...}
>>> book.getKeywords()
['Introduction to programming', 'Arithmetic, strings, and variables', 'Writing programs', 'Flow of control', 'Functions', ...]
```

# List Class

[Top](https://github.com/kajchang/SFPL#sfpl)

User-created lists of books.

## Attributes

```_type``` - Type of list.

```title``` - Title of the list.

```user``` - The creator of the list as an User object.

```createdOn``` - The date the list was created on.

```itemCount``` - The number of books in the list.

```description``` - A description of the list.

```_id``` - SFPL's id for the list.

## Methods

```List.getBooks()``` - Returns a list of Book objects with all the books in the list.

## Example

```python
>>> from sfpl import Search
>>> search = Search('Python', _type='list')
>>> lists = search.getResults() # Get the first page of results for user-created lists named 'Python'
>>> _list = lists[0] # Get the first list in the list
>>> _list._type
'Topic Guide'
>>> _list.title
'python'
>>> [book.title for book in _list.getBooks()] # Get a list of the titles of all the books in the 'Python' list.
['Data Structures and Algorithms in Python', 'Python for Secret Agents', 'Python Forensics', 'Raspberry Pi Cookbook for Python Programmers', ...]
```

# Branch Class

[Top](https://github.com/kajchang/SFPL#sfpl)

## Attributes

```name``` - The branches name.

```_id``` - SFPL's id for the library branch.

## Methods

```Branch.getHours()``` - Returns a dictionary mapping days of the week to opening times.

## Example

```python
>>> from sfpl import Branch
>>> branch = Branch('anza')
>>> branch.name
'ANZA BRANCH'
>>> branch._id
'44563120'
>>> branch.getHours()
{'Sun': '1 - 5', 'Mon': '12 - 6', 'Tue': '10 - 9', 'Wed': '1 - 9', 'Thu': '10 - 6', 'Fri': '1 - 6', 'Sat': '10 - 6'}
```


# User Class

[Top](https://github.com/kajchang/SFPL#sfpl)

A SFPL account with all of lists, shelves, and activity.

## Attributes 

```name``` - The user's username.

```_id``` - SFPL's id for the user.

## Methods

```User.getFollowing()``` - Returns a list with a User object for each account that the account follows.

```User.getFollowers()``` - Returns a list with a User object for each account that the account is followed by.

```User.getLists()``` - Returns a list with a List object for each list the account has created.

## Example

```python
>>> from sfpl import User
>>> user = User('Sublurbanite')
>>> [u.name for u in user.getFollowers()]
['Loriel_2', 'jac523', 'WritingDeskRaven', 'Stephenson1']
>>> [u.name for u in user.getFollowing()]
['monkeymind', 'Pickeringnonfiction', 'ogopogo', ...]
>>> [l.title for l in user.getLists()]
["I Can't Believe this Book Exists", "The [Insert Profession Here]'s [Insert Family Member Here]", ...]
```

# SFPL Class

[Top](https://github.com/kajchang/SFPL#sfpl)

The SFPL class is allows you to access SFPL accounts and all their holds, checkouts, and shelves. The SFPL class inherits from the User class, so it also has access to all User class methods.

## Attributes

```name``` - Your username.

```_id``` - SFPL's id for your account.

```session``` - The requests Session.

## Methods

### Read Methods

```SFPL.getHolds()``` - Returns a list containing Book objects for each book in your holds.

```SFPL.getCheckouts()``` - Returns a list containing Book objects for each book you've checked out.

```SFPL.getForLater()```, ```SFPL.getInProgress()``` and ```SFPL.getCompleted()``` - Return a list containing Book objects for each book in the respective shelves.

### Write Methods

```SFPL.hold(book, branch)``` - Holds the book at the given branch.

```SFPL.cancelHold(book)``` - Cancels any holds on the book.

```SFPL.follow(user)``` - Follow the given user.

```SFPL.unfollow(user)``` - Unfollow the given user.

## Example

```python
>>> from sfpl import SFPL, Branch
>>> sfpl = SFPL('barcode', 'pin')
>>> [book.title for book in sfpl.getHolds()]
['Coding Games in Python', 'Python for Data Analysis', 'Automate the Boring Stuff With Python']
>>> book = sfpl.getHolds()[0]
>>> sfpl.cancelHold(book)
>>> [book.title for book in sfpl.getHolds()]
['Python for Data Analysis', 'Automate the Boring Stuff With Python']
>>> sfpl.hold(book, Branch('anza'))
>>> [book.title for book in sfpl.getHolds()]
['Coding Games in Python', 'Python for Data Analysis', 'Automate the Boring Stuff With Python']
```


# TODO:

Boolean Search Filters

Better Status Messages

Full Cross-Library Bibliocommons Support
