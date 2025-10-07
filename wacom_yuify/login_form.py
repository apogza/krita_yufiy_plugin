import os

from krita import *
from wacom_yuify.constants import base_url

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
except:
    from PyQt5 import uic

class LoginForm(QDialog):

    def __init__(self, network_helper, parent):
        super().__init__(parent)

        self.network_helper = network_helper
        self.network_helper.login_success.connect(self.slot_login_success)
        self.network_helper.profile_incomplete.connect(self.slot_profile_incomplete)
        self.network_helper.login_fail.connect(self.slot_login_fail)

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
        self.centralWidget.infoLabel.setText("Please wait...")

        self.email = self.centralWidget.emailLineEdit.text()
        password = self.centralWidget.passwordLineEdit.text()

        if len(self.email) > 0 and len(password) > 0:            
            self.enable_buttons(False)
            self.network_helper.login(self.email, password)
        else:
            self.centralWidget.infoLabel.setText("Please supply valid email and password")

    def slot_login_success(self):
        self.close()
    
    def slot_login_fail(self, error_reply):
        if error_reply["errorKey"] and error_reply["errorKey"] == "invalid_login_id_or_password" :
            self.centralWidget.infoLabel.setText("Please supply valid email and password")
            self.enable_buttons(True)

    def slot_profile_incomplete(self, error_reply):
        if error_reply["errorKey"] and error_reply["errorKey"] == "invalid_login_id_or_password" :
            self.centralWidget.infoLabel.setText("Please supply valid email and password")
            self.enable_buttons(True)

    def open_signup_page(self):
        QDesktopServices.openUrl(QUrl("%s/registration" % (base_url)))
    
    def enable_buttons(self, enable):
        self.centralWidget.loginButton.setEnabled(enable)
        self.centralWidget.signupButton.setEnabled(enable)
