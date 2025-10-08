import os

from krita import *
from wacom_yuify.constants import base_url

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
except:
    from PyQt5 import uic

class ExportForm(QDialog):
    
    def __init__(self, network_helper, parent):
        super().__init__(parent)

        self.network_helper = network_helper

        self.setWindowTitle("Wacom Yuify")

        self.centralWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'ExportForm.ui'))
        self.centralWidget.fileButton.clicked.connect(self.open_save_file_dialog)
        self.centralWidget.exportButton.clicked.connect(self.export)

        logo = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'yuify-icon.png'))
        self.centralWidget.yuifyLogo.setPixmap(logo)

        layout = QVBoxLayout()
        layout.addWidget(self.centralWidget)
        self.setLayout(layout)

    def open_save_file_dialog(self):
        self.export_filepath = QFileDialog.getSaveFileName(self, "Save File", "/home", "PNG (*.png);;JPG/JPEG(*.jpg *.jpeg)")[0]
        print(self.export_filepath)
    
    def export(self):
        doc = Krita.instance().activeDocument()
        doc.exportImage(self.export_filepath, InfoObject())

        drawing_actions = doc.userActions()
        pass