import os
import json

from krita import *
from wacom_yuify.constants import base_url

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
    from PyQt6 import QtNetwork
except:
    from PyQt5 import uic
    from PyQt5 import QtNetwork


class LoginForm(QDialog):

    def __init__(self, network_helper, parent):
        super().__init__(parent)

        self.network_helper = network_helper
        self.network_helper.login_success.connect(self.handle_login_success)

        self.setWindowTitle("Wacom Yuify")
        self.centralWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'LoginForm.ui'))
        self.centralWidget.loginButton.clicked.connect(self.login)
        self.centralWidget.signupButton.clicked.connect(self.open_signup_page)        

        logo = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'yuify-icon.png'))
        self.centralWidget.yuifyLogo.setPixmap(logo)

        layout = QVBoxLayout()
        layout.addWidget(self.centralWidget)
        self.setLayout(layout)

    def login(self):        
        email = self.centralWidget.emailLineEdit.text()
        password = self.centralWidget.passwordLineEdit.text()
        self.network_helper.login(email, password)

    def handle_login_success(self):        
        self.close()

    def open_signup_page(self):
        QDesktopServices.openUrl(QUrl("%s/registration" % (base_url)))