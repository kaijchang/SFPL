# SFPL Scraper
Python Package for Scraping SFPL Website

#Usage

```pip install sfpl```

```
from sfpl import SFPL
sfpl = SFPL('barcode', 'pin')
```

The current methods are ```getHolds()```, ```getCheckouts()```, ```getForLater()```, ```getInProgress()``` and ```getCompleted()```.

```getCheckouts()``` returns a list of dictionaries with basic information on books the user has checked out, along with a due date:

```
[
    {
        "title": "Blockchain and the Law",
        "author": "De Filippi, Primavera",
        "medium": "Book",
        "publication year": 2018,
        "duedate": "Jun 13, 2018",
        "subtitle": "The Rule of Code"
    }, ...
```

```getHolds()``` returns a list of dictionaries with basic information on books the user has requested, along with the request status:
```
[
    {
        "title": "Fundamentals of Deep Learning",
        "author": "Buduma, Nikhil",
        "medium": "Book",
        "publication year": 2017,
        "status": "In Transit to WEST PORTAL BRANCH",
        "subtitle": "Designing Next-generation Machine Intelligence Algorithms"
    }, ...
```

```getForLater()``` returns a list of dictionaries with basic information on the books on your For Later shelf:
```
[
    {
        "title": "Cryptocurrency",
        "author": "Goleman, Travis",
        "medium": "Downloadable Audiobook",
        "publication year": 2018,
        "subtitle": "Mining, Investing and Trading in Blockchain for Beginners"
    }, ...
]
```

```getInProgress()```, ```getCompleted()``` are identical as ```getForLater()``` for their respective shelves.

## TODO:

Calendars, Events, and Searches.
