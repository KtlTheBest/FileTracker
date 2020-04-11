import socket
import threading
import re

PORT = 1234
available_files = {}

###### EXCEPTIONS: BEGIN ######

class ParseError(Exception):
    def __init__(self):
        self.message = "You should send info about no less than 1 file and no more than 5 files!!"

class WrongFileNameError(Exception):
    def __init__(self):
        self.message = "The filename is in the wrong format!! The filename accepts only alphanumchars, -, . and _"

class WrongFileTypeError(Exception):
    def __init__(self):
        self.message = "The file type looks strange... Make sure everything is correct!"

class WrongFileSizeError(Exception):
    def __init__(self):
        self.message = "The filesize value is wrong! Make sure everything is correct!"

class WrongDateFormatError(Exception):
    def __init__(self):
        self.message = "The date is of the wrong format! Make sure everything is correct!"

class WrongDateValueError(Exception):
    def __init__(self):
        self.message = "The date contains strange values... make sure everything is correct!"

class WrongIPFormatError(Exception):
    def __init__(self):
        self.message = "Your IP Address is of the wrong format! Make sure everything is correct!"

class WrongIPValueError(Exception):
    def __init__(self):
        self.message = "Your IP Address has strange values in it, make sure everything is correct!"

class WrongPortNumberError(Exception):
    def __init__(self):
        self.message = "Your port number has a strange value! Make sure everything is correct!"

class WrongPortFormatError(Exception):
    def __init__(self):
        self.message = "It doesn't look like a port number! Make sure everything is correct!"

class WrongItemNumberError(Exception):
    def __init__(self):
        self.message = "There are wrong number of items in your list! Make sure everything is correct!"

###### EXCEPTIONS: END ######

def parseArgs():
    pass

def getData(s):
    result = ""

    while True:
        data = s.recv(1024)

        if not data:
            break

        result += data

    return result

def sendError(s, message):
    if message == "":
        return

    s.sendall(bytes("ERROR: ") + bytes(message))

def checkFileName(filename):
    valid_filename_pat = re.compile(r'^[\w,\s-_]+(\.([A-Za-z]{1, 6})?)?$')
    res = valid_filename_pat.search(filename)
    if not res:
        raise WrongFileNameError

def checkFileType(Type):
    typePat = re.compile(r'^[a-z]{3,20}$')
    res = typePat.search(Type)

    if res == None:
        raise WrongFileTypeError

def checkFileSize(size):
    sizePat = re.compile(r'^([1-9][0-9]*|0)$')
    res = sizePat.search(size)

    if res == None:
        raise WrongFileSizeError

def checkModDate(date):
    datePat = re.compile(r'^[0-9]{2}/[0-9]{2}/[0-9]{2}$')
    res = datePat.search(date)

    if res == None:
        raise WrongDateFormatError

    vals = date.split('/')
    day = int(vals[0])
    month = int(vals[1])
    if day > 31 or month > 12:
        raise WrongDateValueError

def checkIPAddr(ip):
    orig = ip
    ip += '.'
    ipPat = re.compile(r'^((0|[1-9][0-9]{0,2})\.){4}$')
    match = ipPat.serach(ip)

    if match == None:
        raise WrongIPFormatError

    ip = orig.split('.')

    for val in ip:
        if int(val) > 255:
            raise WrongIPValueError

def checkPort(port):
    if len(port) > 1 and port.startswith('0'):
        raise WrongPortNumberError

    try:
        if int(port) > 65535:
            raise WrongPortNumberError
    except ValueError:
        raise WrongPortFormatError

def checkItems(items):
    if len(items) != 6:
        raise WrongItemNumberError

    checkFileName(item[0])
    checkFileType(item[1])
    checkFileSize(item[2])
    checkModDate(item[3])
    checkIPAddr(item[4])
    checkPort(item[5])

    return items

def parseFileListData(s, data, addr):
    countPat = re.compile(r'<(.+?)>')
    matches = countPat.finditer(data)

    count = 0

    for match in matches:
        count += 1

    if not (count > 0 and count < 6):
        raise ParseError

    for match in matches:
        items = match.group(1).split(',')

        try:
            items = checkItems(items)

        except WrongFileNameError as e:
            message = e
        except WrongFileTypeError as e:
            message = e
        except WrongFileSizeError as e:
            message = e
        except WrongDateFormatError as e:
            message = e
        except WrongDateValueError as e:
            message = e
        except WrongIPFormatError as e:
            message = e
        except WrongIPValueError as e:
            message = e
        except WrongPortNumberError as e:
            message = e
        except WrongPortFormatError as e:
            message = e
        except WrongItemNumberError as e:
            message = e
        finally:
            sendError(s, message)

def acceptClient(s, addr):
    data = getData(s)

    try:
        parseFileListData(s, data, addr)
    except ParseError:
        pass

def parseRequest(s, addr):
    data = getData(s)

    if data == "HELLO":
        acceptClient(s, addr)
    else:
        pass

def listenForClients(s):
    while True:
        sock, addr = s.accept()
        parseRequest(sock)

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ("", PORT)

    s = socket.create_server(addr)

    listen_thread = threading.Thread(target=listenForClients, args=(s,))
    listen_thread.start()

if __name__ == "__main__":
    main()
