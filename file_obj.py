import os
import datetime
from mimetypes import guess_type


class File():
    def __init__(self, name):
        self.fname = name
        stat = os.stat(name)
        self.last_mod = datetime.datetime.fromtimestamp(
            stat.st_mtime).strftime("%d/%m/%y")
        self.size = stat.st_size
        guess = guess_type(self.fname)
        self.MIMEtype = guess[0] if guess[0] else 'data'

    def form_str(self, ip, port):
        return "<{},{},{},{},{},{}>\n".format(
            self.fname, self.MIMEtype, self.size, self.last_mod, ip, port)

    def equals(self, fname, MIMEtype, size):
        return self.fname == fname and self.size == size\
            and self.MIMEtype == MIMEtype

    def __repr__(self):
        return "<{}, Size:{}, Last modified:{}, Type:{}>".format(
            self.fname, self.size, self.last_mod, self.MIMEtype)
