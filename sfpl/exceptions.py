# -*- coding: utf-8 -*-

"""Custom exception classes raised by the sfpl module."""


class NotOnHold(Exception):
    """Raised when a user tries to cancel a hold on a book they aren't holding."""
    def __init__(self, book):
        self.book = book

    def __str__(self):
        return '{} is not on hold.'.format(self.book)


class InvalidSearchType(Exception):
    """Raised when a user passes an invalid search type for the Search class."""
    def __init__(self, _type):
        self._type = _type

    def __str__(self):
        return "{} is not a valid search type. Valid search types are 'keyword', 'title', 'author', 'subject', 'tag' and 'list'.".format(self._type)


class NoBranchFound(Exception):
    """Raised when no matches are found for a user's branch search."""
    def __init__(self, branch):
        self.branch = branch

    def __str__(self):
        return 'No matches found for {}.'.format(self.branch)


class NoUserFound(Exception):
    """Raised when no matches are found for a user's user search."""
    def __init__(self, user):
        self.user = user

    def __str__(self):
        return 'No match found for {}'.format(self.name)


class NotLoggedIn(Exception):
    """Raised when an authentication token is rejected."""
    pass


class LoginError(Exception):
    """Raised when a user's barcode and pin are rejected."""
    pass
