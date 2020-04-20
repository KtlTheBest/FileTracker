import socket
import sys
import threading
import atexit
from os import listdir
from os.path import isfile, join
from gui import Error, Controller
from file_obj import File
from PyQt5.QtWidgets import QApplication


class Client():
    def __init__(self):
        # finding my IP address in local network
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip_client = s.getsockname()[0]
        print("My ip:", self.ip_client)
        s.close()

        # attributes init
        self.get_files()
        self.port_client = None
        self.ip_server = None
        self.port_server = None
        self.server_connect = False

        # execute at exit
        atexit.register(self.exit_handler)

    def exit_handler(self):
        if hasattr(self, "socket_client"):
            self.socket_client.close()

        if hasattr(self, "socket_server"):
            self.socket_server.close()

        if self.server_connect:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip_server, self.port_server))
            s.sendall(b'BYE')
            s.close()

            print("Exitting...")

    def get_files(self):
        self.files = [File(f)
                      for f in listdir("./") if isfile(join("./", f))][:5]

    def find_file(self, fname, MIMEtype, size):
        for f in self.files:
            if f.equals(str(fname), str(MIMEtype), int(size)):
                print("found:", f)
                return f

    def prepare_files_list(self):
        result = ""
        for f in self.files:
            result += f.form_str(self.ip_client, self.port_client)
        return result

    def get_data(self, s):
        result = b""
        while True:
            data = s.recv(1024)
            if not data:
                break
            result += data
        return result.decode('utf-8')

    def listen_for_clients(self, sock):
        while True:
            # accept new client and read
            s, addr = sock.accept()
            req = self.get_data(s)
            print("accepted new client!:", req)

            # if client wants to download...
            if req[:9] == "DOWNLOAD:":
                req = req[9:]
                req_parsed = req.split(",")
                print(req_parsed)

            # get requested file properties
                fname = req_parsed[0]
                MIMEtype = req_parsed[1]
                size = int(req_parsed[2])

                requested_file = self.find_file(fname, MIMEtype, size)

                print("requested file", requested_file)

            # open and send file

                f = open(requested_file.fname, "rb")
                filebytes = f.read(1024)

                s.send(b"FILE:")

                while filebytes:
                    s.send(filebytes)
                    filebytes = f.read(1024)

                print("file sent")

                s.shutdown(socket.SHUT_RDWR)
                s.close()
                f.close()

    def download(self, ip, port, fname, request):
        # requesting download from client

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.settimeout(10)
        s.send(bytearray(request, "utf-8"))
        s.shutdown(socket.SHUT_WR)

        print("sent download request")

        # receiving server responce
        cmd = s.recv(5)
        if cmd == b"FILE:":
            print("receiving file")

            with open(fname, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
            f.close()

            print("file write success!")
        s.close()

    def connect(self, ip_address, port_client):
        # initializing socket for connection to server
        self.ip_server = ip_address.split(":")[0]
        self.port_server = int(ip_address.split(":")[1])
        self.port_client = int(port_client)
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client.settimeout(5)
        self.socket_client.connect((self.ip_server, self.port_server))

        # first handshake with server
        self.socket_client.sendall(bytearray("HELLO", "utf-8"))
        resp = self.socket_client.recv(1024)
        print(resp)
        resp = resp.decode("utf-8")
        if resp[:5] == "ERROR":
            error_text = "".join(resp.split()[1:])
            raise Exception(error_text)
        elif resp[:2] != "HI":
            raise Exception("Invalid responce from server")

        # sending filelist to server
        filelist = bytearray(self.prepare_files_list(), "utf-8")
        self.socket_client.sendall(filelist)
        print("connected to server")
        self.socket_client.close()

        # checking if sockets were initialized and
        # needed to be closed afterwards
        self.server_connect = True

        # initializing listener for other clients
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.bind(("0.0.0.0", self.port_client))
        self.socket_server.listen()
        listen_thread = threading.Thread(
            target=self.listen_for_clients, args=(self.socket_server,))
        listen_thread.start()

    def search(self, keyword):
        # initializing socket for server connection
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client.connect((self.ip_server, self.port_server))

        self.socket_client.sendall(bytearray("SEARCH: "+keyword, "utf-8"))

        # getting and parsing responce
        data_str = self.get_data(self.socket_client)
        print("responce", data_str)
        if data_str[:10] == "NOT FOUND":
            err = Error("Nothing found")
            err.exec_()
            self.socket_client.close()
            return []
        elif data_str[:6] == "FOUND:":
            data_str = data_str[6:]
            self.socket_client.close()
            print("Found:", data_str)
            result = []
            # removing empty string after last \n
            for item in data_str.split("\n"):
                if item:
                    result.append(item.strip())
            return result
        # show error if any
        elif data_str[:5] == "ERROR":
            error_text = "".join(data_str.split()[1:])
            err = Error(error_text)
            err.exec_()
            self.socket_client.close()
            return []

    def __repr__(self):
        return "".join(str(x)+"\n" for x in self.files)

    def __str__(self):
        return "".join(str(x)+"\n" for x in self.files)


def main():
    app = QApplication(sys.argv)
    try:
        main_client = Client()
    except Exception as ex:
        err = Error("Could not initialize app, "+str(ex))
        err.exec_()
        app.exit()

    # initializing window controller
    controller = Controller()
    controller.show_connect_window(main_client)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
