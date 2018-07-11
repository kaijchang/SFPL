# -*- coding: utf-8 -*-

"""
This module is an unofficial Python API for the San Francisco Public Library's Website that uses requests and BeautifulSoup, with lxml as the HTML parser.

The module uses a combination of using requests to simulate AJAX requests sent by the webpage to the SFPL's internal "API" and using requests in conjuction with BeautifulSoup and lxml to scrape data from the HTML of the website.
With this module, you can check your holds and checked out books, as well as request and cancel holds and renew books. You can also search for books and user-created book lists using a variety of different filters.
Additionally, you can get the operating times of different SFPL library branches.
"""


from .sfpl import Account, Search, User, Branch, AdvancedSearch
