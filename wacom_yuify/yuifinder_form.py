from krita import *

import os

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic, QtCore
except:
    from PyQt5 import uic, QtCore

class YuifinderForm(QDialog):
    
    def __init__(self, network_helper, parent):
        super().__init__(parent)        
        
        self.setWindowTitle("Wacom Yuifinder")
        self.centralWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'YuifinderForm.ui'))
        self.centralWidget.yuifinderStackedWidget.setVisible(False)
        self.centralWidget.selectFileButton.clicked.connect(self.selectFile)
        self.centralWidget.cancelButton.clicked.connect(self.cancel_search)

        self.network_helper = network_helper
        self.network_helper.yuifinder_search_result.connect(self.slot_yuifinder_search_result)

        logo = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'yuify-icon.png'))
        self.centralWidget.yuifyLogo.setPixmap(logo)

        layout = QVBoxLayout()
        layout.addWidget(self.centralWidget)
        self.setLayout(layout)        

    def selectFile(self):
        self.file_path = QFileDialog.getOpenFileName(None, "Open File", QDir().homePath(), "Images (*.png *.jpg)")[0]
        
        if not self.file_path:
            return

        pixmap = QPixmap(self.file_path)
        scaled_pixmap = pixmap.scaled(400, 300, QtCore.Qt.KeepAspectRatio)
        self.centralWidget.imageLabel.setPixmap(scaled_pixmap)

        self.search()

    def slot_yuifinder_search_result(self, is_success, result):
        if is_success:
                       
            artwork_label = result["artworkContainer"]["title"]
            artist_name = ""

            if "artistName" in result["artworkContainer"]["creator"]["profile"]:
                artist_name = result["artworkContainer"]["creator"]["profile"]["artistName"]
            else:
                artist_name = result["artworkContainer"]["creator"]["profile"]["firstName"] + " " + result["artworkContainer"]["creator"]["profile"]["lastName"]

            artwork_did = result["artworkContainer"]["did"]

            self.centralWidget.artworkLabel.setText(artwork_label)
            self.centralWidget.artistLabel.setText(artist_name)
            self.centralWidget.didLabel.setText(artwork_did)

            self.centralWidget.yuifinderStackedWidget.setCurrentIndex(1)
        else:
            self.centralWidget.yuifinderStackedWidget.setCurrentIndex(2)

        self.centralWidget.selectFileButton.setEnabled(True)

    def search(self):
        self.centralWidget.selectFileButton.setEnabled(False)
        self.centralWidget.yuifinderStackedWidget.setCurrentIndex(0)
        self.centralWidget.yuifinderStackedWidget.setVisible(True)
        
        self.network_helper.yuifinder_search(self.file_path)
    
    def cancel_search(self):
        self.centralWidget.selectFileButton.setEnabled(True)
        self.centralWidget.yuifinderStackedWidget.setVisible(True)

        self.network_helper.cancel_yuifinder_search()
