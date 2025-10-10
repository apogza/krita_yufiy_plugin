import os
import json
from datetime import datetime

from krita import *

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
except:
    from PyQt5 import uic

class C2PaActionEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

class C2PaAction():
    def __init__(self):
        self.softwareAgent = {}
        self.softwareAgent["name"] = "Krita"
        self.parameters = {}

class ExportForm(QDialog):
    
    def __init__(self, network_helper, parent):
        super().__init__(parent)

        self.network_helper = network_helper
        self.network_helper.artwork_container_success.connect(self.slot_artwork_container_success)
        self.network_helper.artwork_container_fail.connect(self.slot_artwork_container_fail)
        self.network_helper.add_artwork_success.connect(self.slot_add_artwork_success)
        self.network_helper.add_artwork_fail.connect(self.slot_add_artwork_fail)
        self.network_helper.task_status_success.connect(self.slot_task_status_success)
        self.network_helper.task_status_fail.connect(self.slot_task_status_fail)
        self.network_helper.export_download_success.connect(self.slot_export_download_success)
        self.network_helper.export_download_fail.connect(self.slot_export_download_fail)
        self.network_helper.login_success.connect(self.slot_login_success)
        self.network_helper.login_fail.connect(self.slot_login_fail)

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
        self.type = "png" if self.centralWidget.pngRadioButton.isChecked() else "jpeg"

        file_filter = "PNG (*.png)" if self.type == "png" else "JPEG (*.jpeg)"        
        self.export_filepath = QFileDialog.getSaveFileName(self, "Save File", QDir().homePath(), file_filter)[0]

        if not self.export_filepath:
            return

        if not self.export_filepath.endswith(self.type):
            self.export_filepath = "%s.%s" % (self.export_filepath, self.type)

        file_info = QFileInfo(self.export_filepath)
        self.centralWidget.filenameLabel.setText(file_info.fileName())
    
    def export(self):
        self.title = self.centralWidget.titleEdit.text()
        self.description = self.centralWidget.descriptionEdit.toPlainText()

        self.change_status("Beginning export...")

        self.network_helper.create_artwork_container(self.title)       

    def slot_artwork_container_success(self, result):
        self.container_id = result["id"]

        doc = Krita.instance().activeDocument()
        doc.exportImage(self.export_filepath, InfoObject())
        self.actions_object = {}
        self.actions_object["actions"] = self.create_c2pa_actions(doc)        
        self.c2pa_json = json.dumps(self.actions_object, cls=C2PaActionEncoder)

        self.change_status("Uploading artwork...")
        self.network_helper.add_artwork_to_container(
            self.container_id, 
            self.export_filepath, 
            self.c2pa_json, 
            self.description,
            self.type)

    def create_c2pa_actions(self, doc):
        c2pa_actions = []

        creation_date = doc.creationDate()
        created_action = C2PaAction()
        created_action.action = "c2pa.created"
        created_action.parameters["type"] = "blank_canvas"
        created_action.when = creation_date

        c2pa_actions.append(created_action)

        drawing_actions = doc.userActions()

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        for key, value in drawing_actions.items():
            current_action = C2PaAction()
            current_action.action = "c2pa.drawing"
            current_action.parameters["type"] = key
            current_action.parameters["count"] = value
            current_action.when = now
            
            c2pa_actions.append(current_action)
        
        return c2pa_actions
    
    def slot_artwork_container_fail(self, status, result):
        if status == 401:
            self.continue_with = "create_artwork_container"
            self.network_helper.refresh_tokens()
        else:
            self.change_status("")
        
    def slot_add_artwork_success(self, result):
        self.task_id = result["taskId"]

        self.change_status("Waiting for export task to complete...")
        self.network_helper.start_poll_task_status(self.task_id)

    def slot_add_artwork_fail(self, status, result):
        if status == 401:
            self.continue_with = "add_artwork_to_container"
            self.network_helper.refresh_tokens()
        else:            
            self.change_status("")
            
            print("Error uploading artwork")
            print(result)

            error_key = result["errorKey"]

            if error_key == "c2pa_data_insufficient":
                msg_box = self.create_critical_error_dialog("No C2PA data found")
                msg_box.exec()
            elif error_key == "":
                msg_box = self.create_critical_error_dialog("Insufficient C2PA data")
                msg_box.exec()

    def slot_task_status_success(self, result):
        url = result["downloadURL"]

        self.change_status("Downloading exported file...")
        self.network_helper.download_export(url)
    
    def slot_task_status_fail(self, status, result):
        if status == 401:
            self.continue_with = "start_poll_task_status"
            self.network_helper.refresh_tokens()
        else:
            self.change_status("")

    def slot_export_download_success(self):
        self.close()

    def slot_export_download_fail(self, status, result):
        if status == 401:
            self.continue_with = "download_export"
            self.network_helper.refresh_tokens()
        else:
            self.change_status("")

    def slot_login_success(self):
        if not self.continue_with:
            return
        
        if self.continue_with == "create_artwork_container":            
            self.network_helper.create_artwork_container(self.title)
            self.change_status("Beginning export...")

        if self.continue_with == "add_artwork_to_container":
            self.network_helper.add_artwork_to_container(
                self.container_id, 
                self.export_filepath, 
                self.c2pa_json, 
                self.description)
            self.change_status("Uploading artwork...")
            
        if self.continue_with == "start_poll_task_status":
            self.network_helper.start_poll_task_status
            self.change_status("Waiting for export task to complete...")
        
        self.continue_with = None

    def change_status(self, status):
        self.centralWidget.statusLabel.setText(status)

    def create_critical_error_dialog(self, error_msg):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(error_msg)

        return msg_box

    def slot_login_fail(self, result):
        msg_box = self.create_critical_error_dialog("Please authenticate before exporting a document")
        msg_box.exec()
        self.close()