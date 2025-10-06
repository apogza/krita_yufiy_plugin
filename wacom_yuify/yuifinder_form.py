from krita import *

import os

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic, QtCore
    from PyQt6 import QtNetwork
except:
    from PyQt5 import uic, QtCore
    from PyQt5 import QtNetwork


class YuifinderForm(QDialog):
    
    def __init__(self, network_helper, parent):
        super().__init__(parent)
        
        
        self.setWindowTitle("Wacom Yuifinder")
        self.centralWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'YuifinderForm.ui'))
        self.centralWidget.selectFileButton.clicked.connect(self.selectFile)
        self.centralWidget.searchButton.clicked.connect(self.search)
        self.network_helper = network_helper
        self.network_helper.yuifinder_search_result.connect(self.slot_yuifinder_search_result)

        logo = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'yuify-icon.png'))
        self.centralWidget.yuifyLogo.setPixmap(logo)

        layout = QVBoxLayout()
        layout.addWidget(self.centralWidget)
        self.setLayout(layout)        

    def selectFile(self):
        self.file_path = QFileDialog.getOpenFileName(None, "Open File", "/home", "Images (*.png *jpg)")[0]

        if not self.file_path:
            return

        pixmap = QPixmap(self.file_path)
        scaled_pixmap = pixmap.scaled(400, 300, QtCore.Qt.KeepAspectRatio)
        self.centralWidget.imageLabel.setPixmap(scaled_pixmap)

    def slot_yuifinder_search_result(self, is_success, result):
        print(result)

    def search(self):
        self.network_helper.yuifinder_search(self.file_path)

    def handleSearchResponse(self):
        print("received response")
        err = self.reply.error()

        if err == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = self.reply.readAll()
            print(str(bytes_string, 'utf-8'))
            print("OK")
        else:
            print("An error has occurred")
            bytes_string = self.reply.readAll()
            print(str(bytes_string, 'utf-8'))

