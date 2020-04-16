from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QListWidget,
                             QMessageBox, QWidget,
                             QVBoxLayout, QGridLayout)


class ConnectWindow(QWidget):
    switch_window = pyqtSignal(object)

    def __init__(self, main):
        super().__init__()
        self.Main = main
        self.initUI()

    def initUI(self):

        # Create textbox
        server_ip = QLineEdit(self)
        server_ip.setText("IP of FT - <IP>:<PORT>")

        client_port = QLineEdit(self)
        client_port.setText("Listening port")

        # Create a button in the window
        button = QPushButton('Connect', self)
        # connect button to function on_click
        button.clicked.connect(self.on_click)

        self.server_ip = server_ip
        self.client_port = client_port
        self.button = button

        box = QVBoxLayout()
        box.addWidget(server_ip)
        box.addWidget(client_port)
        box.addWidget(button)

        self.setLayout(box)
        self.show()

    @pyqtSlot()
    def on_click(self):
        try:
            ip_address = self.server_ip.text()
            client_port = self.client_port.text()
            print(ip_address)
            print(client_port)
            self.Main.connect(ip_address, client_port)
            self.switch_window.emit(self.Main)
        except Exception as ex:
            err = Error(str(ex))
            err.exec_()
        self.close()


class LoadWindow(QWidget):
    def __init__(self, main):
        super().__init__()
        self.Main = main
        self.initUI()
        print(self.Main)

    def initUI(self):
        self.status = QLabel("Connected to server")
        grid = QGridLayout()
        self.search_line = QLineEdit("Search for file")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_click)
        self.search_results = QListWidget()
        self.search_results.itemClicked.connect(self.on_item_click)
        grid.addWidget(self.search_line, 1, 0)
        grid.addWidget(self.search_button, 1, 1)
        grid.addWidget(self.search_results, 2, 0)
        grid.addWidget(self.status, 3, 0)
        self.setLayout(grid)
        self.show()

    def on_item_click(self, item):
        self.status.setText(item.text())

    @pyqtSlot()
    def on_click(self):
        results = self.Main.search(self.search_line.text())
        # results = self.Main.search("")
        print("res:", results)
        if results:
            self.search_results.addItems(results)
        else:
            Error("Nothing found").exec_()


class Controller():
    def show_connect_window(self, main):
        self.connect = ConnectWindow(main)
        self.connect.switch_window.connect(self.show_load_window)
        self.connect.show()

    def show_load_window(self, main):
        self.main = LoadWindow(main)
        self.main.show()


class Error(QMessageBox):
    def __init__(self, msg):
        super().__init__(QMessageBox.Critical, "Error", msg)
