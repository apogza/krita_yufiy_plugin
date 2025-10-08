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
        self.file_path = QFileDialog.getOpenFileName(None, "Open File", "/home", "Images (*.png *.jpg)")[0]
        
        if not self.file_path:
            return

        pixmap = QPixmap(self.file_path)
        scaled_pixmap = pixmap.scaled(400, 300, QtCore.Qt.KeepAspectRatio)
        self.centralWidget.imageLabel.setPixmap(scaled_pixmap)

        self.search()

    def slot_yuifinder_search_result(self, is_success, result):
        if is_success:
            search_object = result[0]
                        
            self.centralWidget.artistLabel.setText(search_object["container"]["creator"]["profile"]["artistName"])
            self.centralWidget.didLabel.setText(search_object["container"]["did"])
            self.centralWidget.providerLabel.setText(search_object["container"]["provider"])

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
