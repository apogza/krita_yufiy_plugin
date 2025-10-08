import os

from krita import *

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
except:
    from PyQt5 import uic

class LogoutForm(QDialog):
    def __init__(self, network_helper, parent):
        super().__init__(parent)
        self.network_helper = network_helper

        self.setWindowTitle("Wacom Yuify")
        self.centralWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'LogoutForm.ui'))
        self.centralWidget.emailLabel.setText(self.network_helper.get_email())
        self.centralWidget.logoutButton.clicked.connect(self.logout)

        logo = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'yuify-icon.png'))
        self.centralWidget.yuifyLogo.setPixmap(logo)

        layout = QVBoxLayout()
        layout.addWidget(self.centralWidget)
        self.setLayout(layout)

    def logout(self):
        self.network_helper.logout()
        self.close()





