from krita import *

from wacom_yuify.login_form import LoginForm
from wacom_yuify.yuifinder_form import YuifinderForm
from wacom_yuify.logout_form import LogoutForm
from wacom_yuify.export_form import ExportForm
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
            logout_form = LogoutForm(self.network_helper, None)
            logout_form.exec()
        else:
            login_form = LoginForm(self.network_helper, None)
            login_form.exec()

    def export(self):
        krita = Krita.instance()

        active_document = krita.activeDocument()

        if not active_document:
            msg_box = QMessageBox()
            msg_box.setText("Please open a document")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.exec()
            return

        if self.network_helper.is_authenticated():
            export_form = ExportForm(self.network_helper, None)
            export_form.exec()
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setText("Please authenticate before exporting a document")
            msg_box.exec()


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
