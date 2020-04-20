from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QListWidget,
                             QMessageBox, QWidget, QListWidgetItem,
                             QVBoxLayout, QGridLayout, QHBoxLayout)


class ConnectWindow(QWidget):
    # window switch flag
    switch_window = pyqtSignal(object)

    def __init__(self, main_client):
        super().__init__()
        self.main_client = main_client
        self.initUI()

    def initUI(self):

        # create textbox for ip and port
        server_ip = QLineEdit(self)
        server_ip.setText("IP of FT - <IP>:<PORT>")

        client_port = QLineEdit(self)
        client_port.setText("Listening port")

        # create and connect a button
        button = QPushButton('Connect', self)
        button.clicked.connect(self.on_click)

        # saving GUI items as class attributes
        self.server_ip = server_ip
        self.client_port = client_port
        self.button = button

        # creating layout and inserting GUI
        # elements into the layout
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
            # connecting to server
            self.main_client.connect(ip_address, client_port)
            # show next window if successfully connected
            self.switch_window.emit(self.main_client)
        except Exception as ex:
            err = Error(str(ex))
            err.exec_()
        self.close()


class LoadWindow(QWidget):
    def __init__(self, main_client):
        super().__init__()
        self.main_client = main_client
        self.initUI()

    def initUI(self):
        # initializing GUI elements
        self.status = QLabel("Connected to server")
        self.search_line = QLineEdit("Search for file")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_click)
        self.search_results = QListWidget()
        # attaching listener on double click to list item
        self.search_results.itemDoubleClicked.connect(self.on_item_click)

        # creating layout and inserting GUI
        # elements into the layout
        grid = QGridLayout()
        grid.addWidget(self.search_line, 1, 0)
        grid.addWidget(self.search_button, 1, 1)
        grid.addWidget(self.search_results, 2, 0)
        grid.addWidget(self.status, 3, 0)

        self.setLayout(grid)
        self.show()

    def on_item_click(self, item):
        try:
            # getting QWidget object binded to QListWidgetItem
            widget = self.search_results.itemWidget(item)
            fname = widget.name_label.text()
            self.main_client.download(widget.ip, widget.port,
                                      fname, widget.prepare_download())
            self.status.setText("File downloaded successfully")
            QMessageBox(QMessageBox.Information, "Success",
                        "File {} was downloaded".format(fname)).exec_()
        except Exception as ex:
            Error(str(ex)).exec_()

    @pyqtSlot()
    def on_click(self):
        try:
            # empty previous search results
            self.search_results.clear()
            search_term = self.search_line.text()
            self.status.setText(
                "Searching {} on server".format(search_term))
            # getting results from server
            results = self.main_client.search(search_term)
            # if we have any results...
            if results:
                # removing < , >  and splitting each result by ','
                results = [x[1:len(x) - 1].split(",") for x in results]
                # lists for QWidget and QListWidgetItem
                results_widget = []
                results_obj = []
                for item in results:
                    obj = FileWidget(
                        search_term, item[1], item[0],
                        item[2], item[3], item[4])
                    results_obj.append(obj)
                    widget = QListWidgetItem(self.search_results)
                    results_widget.append(widget)
                    # setting size for QListWidgetItem
                    widget.setSizeHint(obj.sizeHint())
                for widget, item in zip(results_widget, results_obj):
                    # adding QListWidgetItem objects and binding to QWidget
                    self.search_results.addItem(widget)
                    self.search_results.setItemWidget(widget, item)
                self.status.setText("Search results")
        except Exception as ex:
            Error(str(ex)).exec_()


class FileWidget(QWidget):
    def __init__(self, fname, size, MIMEtype, date, ip, port):
        super().__init__()

        self.ip = ip
        self.port = int(port)
        self.size = size

        # setting labels for widget
        self.name_label = QLabel()
        self.name_label.setText(fname)

        self.type_label = QLabel()
        self.type_label.setText(MIMEtype)

        self.size_label = QLabel()
        self.size_label.setText(self.humansize(size))

        self.date_label = QLabel()
        self.date_label.setText(date)

        # initializing layout and adding to widget
        widgetLayout = QHBoxLayout()
        widgetLayout.addWidget(self.name_label, 1)
        widgetLayout.addWidget(self.type_label, 1)
        widgetLayout.addWidget(self.size_label, 1)
        widgetLayout.addWidget(self.date_label, 1)
        widgetLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(widgetLayout)

    # converting bytes to human readable format
    def humansize(self, nbytes):
        nbytes = int(nbytes)
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        i = 0
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])

    def prepare_download(self):
        return "DOWNLOAD:{},{},{}".format(self.name_label.text(),
                                          self.type_label.text(),
                                          self.size)

    def __repr__(self):
        return self.__str__(self)

    def __str__(self):
        return "n:{} s:{} t:{} d:{} i:{} p:{}".format(
            self.name_label.text(), self.size_label.text(),
            self.type_label.text(), self.date_label.text(),
            self.ip, self.port)


class Controller():
    def show_connect_window(self, main_client):
        self.connect = ConnectWindow(main_client)
        self.connect.switch_window.connect(self.show_load_window)
        self.connect.show()

    def show_load_window(self, main_client):
        self.load = LoadWindow(main_client)
        self.load.show()


class Error(QMessageBox):
    def __init__(self, msg):
        super().__init__(QMessageBox.Critical, "Error", msg)
