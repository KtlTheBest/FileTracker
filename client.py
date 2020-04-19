import socket
import sys
from os import listdir
from os.path import isfile, join
from gui import Error, Controller
from file_obj import File
from PyQt5.QtWidgets import QApplication


class Main():
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip_client = s.getsockname()[0]
        print(self.ip_client)
        s.close()
        self.get_files()
        self.port_client = None
        self.ip_server = None
        self.port_server = None

    def get_files(self):
        self.files = [File(f)
                      for f in listdir("./") if isfile(join("./", f))][:5]

    def connect(self, ip_address, port):
        self.ip_server = ip_address.split(":")[0]
        self.port_server = int(ip_address.split(":")[1])
        self.port_client = int(port)
        self.socket_client = socket.create_connection(
            (self.ip_server, self.port_server), timeout=10)
        self.socket_client.sendall(b"HELLO")
        data = self.socket_client.recv(1024)
        print(data)
        if(data != b'HI'):
            raise Exception("Invalid response")
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.bind(("0.0.0.0", self.port_client))

        self.get_files()

        fileList = ""
        for f in self.files:
            fileList += f.form_str(self.ip_client, self.port_client)

        self.socket_client.sendall(bytes(fileList, 'utf-8'))

    def search(self, keyword):
        self.socket_client.sendall(bytearray("SEARCH: "+keyword, "utf-8"))
        data = self.socket_client.recv(4048)
        data_str = data.decode("utf-8")
        if data_str == "NOT FOUND":
            return list()
        return data_str.split("\r\n")

    def __repr__(self):
        return "".join(str(x)+"\n" for x in self.files)

    def __str__(self):
        return "".join(str(x)+"\n" for x in self.files)


def main():
    app = QApplication(sys.argv)
    try:
        main = Main()
    except Exception as ex:
        err = Error("Could not initialize app, "+str(ex))
        err.exec_()
        app.exit()

    print(main.files)
    controller = Controller()
    controller.show_connect_window(main)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
