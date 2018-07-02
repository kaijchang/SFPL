class NotOnHold(Exception):
    def __init__(self, book):
        self.book = book

    def __str__(self):
        return '{} is not on hold.'.format(self.book)


class InvalidSearchType(Exception):
    def __init__(self, _type):
        self._type = _type

    def __str__(self):
        return "{} is not a valid search type. Valid search types are 'keyword', 'title', 'author', 'subject', 'tag' and 'list'.".format(self._type)


class NoBranchFound(Exception):
    def __init__(self, branch):
        self.branch = branch

    def __str__(self):
        return 'No matches found for {}.'.format(self.branch)


class NoUserFound(Exception):
    def __init__(self, user):
        self.user = user

    def __str__(self):
        return 'No match found for {}'.format(self.name)


class NotLoggedIn(Exception):
    pass


class LoginError(Exception):
    pass
