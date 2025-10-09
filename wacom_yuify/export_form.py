import os
import json
from datetime import datetime

from krita import *

try:
    if int(qVersion().split('.')[0]) == 5:
        raise
    from PyQt6 import uic
except:
    from PyQt5 import uic, QtXml

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
        self.export_filepath = QFileDialog.getSaveFileName(self, "Save File", "/home", "PNG (*.png);;JPG (*.jpg)")[0]
        print(self.export_filepath)
    
    def export(self):

        self.title = self.centralWidget.titleEdit.text()
        self.description = self.centralWidget.descriptionEdit.text()
        self.type = "PNG" if self.centralWidget.pngRadioButton.checked() else "JPEG"

        self.network_helper.create_artwork_container(self.title)

    def slot_artwork_container_success(self, result):

        self.container_id = result["id"]
        
        doc = Krita.instance().activeDocument()
        doc.exportImage(self.export_filepath, InfoObject())
        self.actions_object = {}
        self.actions_object["actions"] = self.create_c2pa_actions(doc)        
        self.c2pa_json = json.dumps(self.actions_object, cls=C2PaActionEncoder)

        self.network_helper.add_artwork_to_container(
            self.container_id, 
            self.export_filepath, 
            self.c2pa_json, 
            self.description)

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
        pass
    
    def slot_add_artwork_success(self, result):
        self.task_id = result["taskId"]
        self.network_helper.start_poll_task_status(self.task_id)

    def slot_add_artwork_fail(self, status, result):
        pass

    def slot_task_status_success(self):
        pass
    
    def slot_task_status_fail(self, status, result):
        pass
