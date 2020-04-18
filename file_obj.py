import os
import datetime
from mimetypes import guess_type
# from datetime import fromtimestamp


class File():
    def __init__(self, name):
        self.fname = name
        stat = os.stat(name)
        self.last_mod = datetime.datetime.fromtimestamp(
            stat.st_mtime).strftime("%d/%m/%Y")
        self.size = stat.st_size
        self.MIMEtype = guess_type(self.fname)[0]

    def form_str(self, ip, port):
        return "<{},{},{},{},{},{}>".format(
            self.fname, self.MIMEtype, self.size, self.last_mod, ip, port)

    def __repr__(self):
        return "<{}, Size:{}, Last modified:{}, Type:{}>".format(
            self.fname, self.size, self.last_mod, self.MIMEtype)
