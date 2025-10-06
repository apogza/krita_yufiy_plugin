import os
import json

from wacom_yuify.constants import base_url, auth_file

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import QtNetwork
    from PyQt6.QtCore import pyqtSignal, QObject, QUrl, QByteArray, QFileInfo, QFile, QIODevice
except:
    from PyQt5 import QtNetwork
    from PyQt5.QtCore import pyqtSignal, QObject, QUrl, QByteArray, QFileInfo, QFile, QIODevice

class NetworkHelper(QObject):
    login_success = pyqtSignal()
    profile_incomplete = pyqtSignal(object)
    yuifinder_search_result = pyqtSignal(bool, object)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.main_token = ""
        self.refresh_token = ""

        self.nam = QtNetwork.QNetworkAccessManager()
        self.load_tokens()

    def login(self, email, password):
        url = QUrl("%s/api/isv/krita/users/auth" % base_url)
        req = QtNetwork.QNetworkRequest(url)
        req.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")

        req_body = json.dumps({"username": email, "password": password})
        self.login_reply = self.nam.post(req, QByteArray(req_body.encode()))
        self.login_reply.finished.connect(self.handle_login_reply)

    def logout(self):
        self.main_token = ""
        self.refresh_token = ""

        if os.path.exists(auth_file):
            os.remove(auth_file)

    def is_authenticated(self):
        return self.main_token != ""

    def handle_login_reply(self):
        
        err = self.login_reply.error()
        
        if err == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = self.login_reply.readAll()
            json_reply = json.loads(str(bytes_string, 'utf-8'))

            self.main_token = json_reply["mainToken"]
            self.refresh_token = json_reply["refreshToken"]

            self.save_tokens(self.main_token, self.refresh_token)
            self.login_success.emit()
        else:
            status = int(self.login_reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute))
            if (status == 403):
                bytes_string = self.login_reply.readAll()
                error_reply = json.loads(str(bytes_string, 'utf-8'))
                self.profile_incomplete.emit(error_reply)
            else:
                bytes_string = self.login_reply.readAll()                
                self.logout()

    def load_tokens(self):
        if os.path.exists(auth_file):
            with open(auth_file, "r") as f:
                auth = json.load(f)                
                self.main_token = auth["mainToken"]
                self.refresh_token = auth["refreshToken"]
        
            self.refresh_tokens()          

    def save_tokens(self, main_token, refresh_token):
        auth = {}
        auth["mainToken"] = main_token
        auth["refreshToken"] = refresh_token        

        with open(auth_file, "w") as f:
            json.dump(auth, f)                        
        
    def refresh_tokens(self):
        url = QUrl("%s/api/isv/users/refresh-token" % base_url)
        
        request_body = json.dumps({"refreshToken": self.refresh_token})
        print(request_body)
        req = QtNetwork.QNetworkRequest(url)
        req.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")

        self.login_reply = self.nam.post(req, QByteArray(request_body.encode()))
        self.login_reply.finished.connect(self.handle_login_reply)

    def yuifinder_search(self, file_path):
        url = QUrl("%s/api/public/watermark/extract-from-file" % base_url)
        print(url)
        req = QtNetwork.QNetworkRequest(url)
        
        multipart_form = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
        file_part = QtNetwork.QHttpPart();
        file_info = QFileInfo(file_path)

        file_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader, "form-data; name=\"file\"; filename=\"%s\"" % file_info.fileName())
        file_part.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "image/png")

        file = QFile(file_path)        
        file.open(QIODevice.ReadOnly)
        file_bytes = file.readAll();
        file.close()

        file_part.setBody(file_bytes)
        multipart_form.append(file_part)
        
        self.yuifinder_search_reply = self.nam.post(req, multipart_form)
        multipart_form.setParent(self.yuifinder_search_reply)
        
        self.yuifinder_search_reply.finished.connect(self.handle_yuifinder_search_reply)        

    def handle_yuifinder_search_reply(self):
        print("received yuifinder response")
        err = self.yuifinder_search_reply.error()

        is_success = err == QtNetwork.QNetworkReply.NetworkError.NoError
        bytes_string = self.yuifinder_search_reply.readAll()
        yuifinder = json.loads(str(bytes_string, 'utf-8'))
        self.yuifinder_search_result.emit(is_success, yuifinder)