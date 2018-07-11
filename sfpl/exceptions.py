# -*- coding: utf-8 -*-

"""Custom exception classes raised by the sfpl module."""


class NotOnHold(Exception):
    """Raised when a user tries to cancel a hold on a book they aren't holding."""

    def __init__(self, book):
        Exception.__init__(self, '{} is not on hold.'.format(book))


class NotCheckedOut(Exception):
    """Raised when a user tries to renew a book they haven't checked out."""

    def __init__(self, book):
        Exception.__init__(self, '{} is not checked out.'.format(book))


class InvalidSearchType(Exception):
    """Raised when a user passes an invalid search type for the Search class."""

    def __init__(self, _type):
        Exception.__init__(
            self, "{} is not a valid search type. Valid search types are 'keyword', 'title', 'author', 'subject', 'tag' and 'list'.".format(_type))


class NoBranchFound(Exception):
    """Raised when no matches are found for a user's branch search."""

    def __init__(self, branch):
        Exception.__init__(self, 'No matches found for {}.'.format(branch))


class NoUserFound(Exception):
    """Raised when no matches are found for a user's user search."""

    def __init__(self, user):
        Exception.__init__(self, 'No match found for {}'.format(user))


class LoginError(Exception):
    """Raised when a user's barcode and pin are rejected."""

    def __init__(self, msg):
        Exception.__init__(self, msg)


class HoldError(Exception):
    """Raised when a user's hold request is denied."""

    def __init__(self, msg):
        Exception.__init__(self, msg)


class RenewError(Exception):
    """Raised when a user's renew request is denied."""

    def __init__(self, msg):
        Exception.__init__(self, msg)


class MissingFilterTerm(Exception):
    """Raised when a search term doesn't have include or exclude in it."""

    def __init__(self):
        Exception.__init__(self,
            "Each search term needs to include 'exclude' or 'include' and a valid term type such as 'keyword', 'author', 'title', 'subject', 'series', 'award', 'identifier', 'region', 'genre', 'publisher' or 'callnumber'")


class NotLoggedIn(Exception):
    """Raised when an authentication token is rejected."""
    pass
