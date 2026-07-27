# SFPL

Python Package for accessing account, book, and author data from the SFPL Website.

## Status
[![python-test](https://github.com/kaijchang/SFPL/actions/workflows/python-package.yml/badge.svg)](https://github.com/kaijchang/SFPL/actions/workflows/python-package.yml)
[![static-analysis](https://github.com/kaijchang/SFPL/actions/workflows/static-analysis.yaml/badge.svg)](https://github.com/kaijchang/SFPL/actions/workflows/static-analysis.yaml)
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
>>> first_page = next(results).getBooks()
>>> first_page[0].title
"Harry Potter and the Deathly Hallows"
>>> first_page[0].getDetails()["brief"]["description"]
"Harry discovers what fate truly has in store for him as he inevitably makes his way to the final meeting with Voldemort. Book #7"
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

## Command-Line Interface

Installing the package provides an `sfpl` command. You can also run it directly
with `pipx run sfpl` or `uvx sfpl`. The same interface is available through
`python -m sfpl`:

```console
$ sfpl --help
```

### Search

Search books or media by keyword, title, author, subject, or tag:

```console
$ sfpl search "J.K. Rowling" --type author --pages 2
$ sfpl search "climate fiction" --type subject
$ sfpl search "music" --format LP --sort newly_acquired --on-order
$ sfpl search "music" --format LP --no-on-order
```

Use `--type list` to search user-created lists:

```console
$ sfpl search "San Francisco" --type list
```

Advanced search accepts repeatable `--include FIELD=TERM` and
`--exclude FIELD=TERM` filters, as well as `--format` and `--sort` options.
At least one `--include` filter is required. Included filters match all terms
by default; use `--match any` to match any included term. The same field cannot
be repeated within `--include` or `--exclude`.

```console
$ sfpl advanced-search \
    --include "author=J. K. Rowling" \
    --include "keyword=magic" \
    --exclude "title=Harry Potter" \
    --format BK \
    --sort relevance \
    --match all \
    --pages 2
```

Valid advanced-search fields are `keyword`, `author`, `title`, `subject`,
`series`, `award`, `identifier`, `region`, `genre`, `publisher`, and
`callnumber`.

Pass `--details` to `sfpl search` or `sfpl advanced-search` to include full metadata (format, publication date, description, etc.) for each result item:

```console
$ sfpl search "vegan" --sort newly_acquired --no-on-order --details
```

### Book Details

Look up detailed metadata for a specific item by catalog ID:

```console
$ sfpl details 4564247093
```

### Branch Hours

```console
$ sfpl branch-hours west portal
$ sfpl branch-hours "main library"
```

### Account Holds and Checkouts

```console
$ sfpl account holds --barcode "your library card barcode"
$ sfpl account checkouts --barcode "your library card barcode"
```

The command prompts for your PIN without displaying it.

Alternatively, provide both credentials through environment variables:

```console
$ export SFPL_BARCODE="your library card barcode"
$ export SFPL_PIN="your library account PIN"
$ sfpl account holds
```
