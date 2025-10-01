from krita import *
from PyQt5.QtWidgets import QWidget, QAction, QMessageBox


class wacom_yuify(Extension):

    def __init__(self, parent):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        #This runs only once when app is installed
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def export(self):
        pass

    def yufinder(self):
        pass

    def createActions(self, window):
        action = window.createAction("WacomYuify", "Wacom Yuify", "tools/scripts")

        self.menu = QMenu("WacomYuify", window.qwindow())
        action.setMenu(self.menu)

        login_action = self.menu.addAction("Login")
        login_action.triggered.connect(self.login)

        logout_action = self.menu.addAction("Logout")
        logout_action.triggered.connect(self.logout)

        export_action = self.menu.addAction("Export")
        export_action.triggered.connect(self.export)

        yuifinder_action = self.menu.addAction("Yuifinder")
        yuifinder_action.triggered.connect(self.yufinder)

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(wacom_yuify(Krita.instance())) 
