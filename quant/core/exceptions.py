import logging

logger = logging.getLogger(__name__)

__all__ = ['DATETIMENOTEXIST', 'SYMBOLNOTFOUND', 'CREATESNAPSHOTERROR']


class DATETIMENOTEXIST(Exception):
    def __init__(self, msg):
        super(DATETIMENOTEXIST, self).__init__()
        self.errorinfo = msg

    def __str__(self):
        return self.errorinfo


class SYMBOLNOTFOUND(Exception):
    def __init__(self, msg):
        super(SYMBOLNOTFOUND, self).__init__()
        self.errorinfo = msg

    def __str__(self):
        return self.errorinfo


class CREATESNAPSHOTERROR(Exception):
    def __init__(self, msg):
        super(CREATESNAPSHOTERROR, self).__init__()
        self.errorinfo = msg

    def __str__(self):
        return self.errorinfo
