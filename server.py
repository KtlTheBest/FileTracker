import argparse
import socket
import threading
import re

PORT = 1234
available_files = {}

connected_users = set()

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
    global PORT

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default = 1234)

    args = parser.parse_args()

    PORT = args.port

def getData(s):
    result = ""

    while True:
        data = s.recv(1024)

        if not data:
            break

        result += data

    return result.decode('utf-8')

def prepareResponse(fname):
    fname = fname.rstrip()

    r = ""

    if fname in available_files:
        for f in available[fname]:
            r += "<{},{},{},{},{}>\n".format(f)

    return r.encode('utf-8')

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
    typePat = re.compile(r'^[a-z/]{3,70}$')
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
    global available_files

    countPat = re.compile(r'<(.+?)>')
    matches = countPat.finditer(data)

    count = 0

    for match in matches:
        count += 1

    if not (count > 0 and count < 6):
        raise ParseError

    connect_user = False

    for match in matches:
        items = match.group(1).split(',')

        try:
            items = checkItems(items)
            connect_user = True
            if items[0] in available_files:
                available_files[items[0]].append(items[1:])
            else:
                available_files[items[0]] = [items[1:]]
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

    if connect_user == True:
        connected_users.add(items[4])

def acceptClient(s, addr):
    global connected_users

    s.send(b'HI')

    data = getData(s)

    try:
        parseFileListData(s, data, addr)
    except ParseError:
        pass

def removeClient(addr):
    global connected_users
    global available_files

    for fname, v in available_files.items():
        if v is None:
            continue

        to_remove = []

        for user in available_files[fname]:
            if (user[4], user[5]) == addr:
                to_remove.append(user)

        for r in to_remove:
            available_files[fname].remove(r)

    connected_users.discard(addr[0])

def searchFiles(s, fname):
    r = prepareResponse(fname)
    s.send(r)
    pass

def parseRequest(s, addr):
    data = getData(s)

    if data == "HELLO":
        acceptClient(s, addr)
    elif data == "BYE":
        removeClient(addr)
    elif data[:8] == "SEARCH: ":
        searchFiles(s, data[8:])
    else:
        pass

def listenForClients(s):
    while True:
        print("Listening for connections")
        sock, addr = s.accept()
        parseRequest(sock)

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ("", PORT)

    serverSocket.bind(addr)
    serverSocket.listen()

    listen_thread = threading.Thread(target=listenForClients, args=(serverSocket,))
    listen_thread.start()

if __name__ == "__main__":
    main()
