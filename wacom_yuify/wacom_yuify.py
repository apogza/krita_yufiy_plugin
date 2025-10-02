from krita import *
import os
import json

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
    from PyQt6 import QtNetwork
except:
    from PyQt5 import uic
    from PyQt5 import QtNetwork

base_url = "https://stage-cri-e485850d.wacom.com"

class LoginForm(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

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
        pass

    def open_signup_page(self):
        QDesktopServices.openUrl(QUrl("%s/registration" % (base_url)))

class YuifinderForm(QDialog):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setWindowTitle("Wacom Yuifinder")
        self.centralWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'YuifinderForm.ui'))
        self.centralWidget.selectFileButton.clicked.connect(self.selectFile)
        self.centralWidget.searchButton.clicked.connect(self.search)

        logo = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'yuify-icon.png'))
        self.centralWidget.yuifyLogo.setPixmap(logo)

        layout = QVBoxLayout()
        layout.addWidget(self.centralWidget)
        self.setLayout(layout)

        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handleSearchResponse)

    def selectFile(self):
        self.filePath = QFileDialog.getOpenFileName(None, "Open File", "/home", "Images (*.png *jpg)")[0]

        if not self.filePath:
            return

        print(self.filePath)

        pixmap = QPixmap(self.filePath)
        pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.centralWidget.imageLabel.setPixmap(pixmap)

    def search(self):
        url = "%s/api/public/watermark/extract-from-file" % base_url
        print(url)
        req = QtNetwork.QNetworkRequest(QUrl(url))
        
        multipart_form = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
        file_part = QtNetwork.QHttpPart();
        file_info = QFileInfo(self.filePath)

        file_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader, "form-data; name=\"file\"; filename=\"%s\"" % file_info.fileName())
        file_part.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "image/png")

        file = QFile(self.filePath)        
        file.open(QIODevice.ReadOnly)
        
        file_bytes = file.readAll();

        print(len(file_bytes))
        file.close()

        file_part.setBody(file_bytes)
        multipart_form.append(file_part)
        
        self.reply = self.nam.post(req, multipart_form)
        multipart_form.setParent(self.reply)
        
        self.reply.finished.connect(self.handleSearchResponse)

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

class WacomYuify(Extension):

    def __init__(self, parent):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        #This runs only once when app is installed
        pass

    def login(self):
        self.loginForm = LoginForm(None)
        self.loginForm.exec()

    def logout(self):
        pass

    def export(self):
        pass

    def yufinder(self):
        self.yufinderForm = YuifinderForm(None)
        self.yufinderForm.exec()

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
Krita.instance().addExtension(WacomYuify(Krita.instance())) 
