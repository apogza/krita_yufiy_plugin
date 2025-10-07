from krita import *

from wacom_yuify.login_form import LoginForm
from wacom_yuify.yuifinder_form import YuifinderForm
from wacom_yuify.logout_form import LogoutForm
from wacom_yuify.network_helper import NetworkHelper

class WacomYuify(Extension):

    def __init__(self, parent):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)
        self.network_helper = NetworkHelper(self)

    def setup(self):
        #This runs only once when app is installed
        pass

    def login(self):
        if self.network_helper.is_authenticated():
            self.logoutForm = LogoutForm(self.network_helper, None)
            self.logoutForm.exec()
        else:
            self.loginForm = LoginForm(self.network_helper, None)
            self.loginForm.exec()

    def export(self):
        pass

    def yufinder(self):
        self.yufinderForm = YuifinderForm(self.network_helper, None)
        self.yufinderForm.exec()

    def createActions(self, window):
        action = window.createAction("WacomYuify", "Wacom Yuify", "tools/scripts")

        self.menu = QMenu("WacomYuify", window.qwindow())
        action.setMenu(self.menu)

        login_action = self.menu.addAction("Authentication")
        login_action.triggered.connect(self.login)

        export_action = self.menu.addAction("Export")
        export_action.triggered.connect(self.export)

        yuifinder_action = self.menu.addAction("Yuifinder")
        yuifinder_action.triggered.connect(self.yufinder)

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(WacomYuify(Krita.instance())) 
