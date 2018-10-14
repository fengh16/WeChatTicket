# -*- coding: utf-8 -*-
#



__author__ = "Epsirom"


class BaseError(Exception):

    def __init__(self, code, msg):
        super(BaseError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __repr__(self):
        return '[ERRCODE=%d] %s' % (self.code, self.msg)


class InputError(BaseError):

    def __init__(self, msg):
        super(InputError, self).__init__(1, msg)


class LogicError(BaseError):

    def __init__(self, msg):
        super(LogicError, self).__init__(2, msg)


class ValidateError(BaseError):

    def __init__(self, msg):
        super(ValidateError, self).__init__(3, msg)


class AuthError(BaseError):
    def __init__(self, msg):
        super(AuthError, self).__init__(4, msg)


class DatabaseError(BaseError):
    def __init__(self, msg):
        super(DatabaseError, self).__init__(5, msg)

class FileError(BaseError):
    def __init__(self, msg):
        super(FileError, self).__init__(6, msg)

class TicketError(BaseError):
    def __init__(self, msg):
        super(TicketError, self).__init__(7, msg)
