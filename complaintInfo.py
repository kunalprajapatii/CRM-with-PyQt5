from PyQt5.QtWidgets import QApplication, QLineEdit, QCalendarWidget, QVBoxLayout, QDialog, QMessageBox, QLabel, QComboBox,QPushButton
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
import sys
from datetime import datetime, timezone
import mydb_connection

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        # Load UI file and set it to the window
        uic.loadUi('GUI_files/layout2.ui', self)
        self.setWindowTitle('FSE Data Collection Form')
        QApplication.processEvents()
        self.EscalationTime.hide()
        self.EscalationTime_label_26.hide()

        self.connection = mydb_connection.create_connection()
        self.cursor = self.connection.cursor()

        self.Save_button.clicked.connect(self.on_SerialNumberChanged)
        
        # self.status_bar = self.findChild(QLabel, 'status_bar')
        self.status_bar = self.status_bar
        # self.calender = self.findChild(QLineEdit, 'calender')
        self.calender = self.calender
        self.calender.setText(QDate.currentDate().toString("dd/MM/yyyy"))

        self.EscalationTime = self.EscalationTime
        self.EscalationTime.setText(QDate.currentDate().toString("dd/MM/yyyy"))

        # Connect the QLineEdit click event to show the calendar
        self.calender.mousePressEvent = self.showCalendar
        self.EscalationTime.mousePressEvent = self.ShowCalendar
        self.inputPyqtObjects = [self.serial_number]

        '''Application type'''
        self.application_type = self.application_type
        self.cursor.execute("SELECT ApplicationType FROM fse_option")
        self.application_option = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.application_option.insert(0, '-None-')  # Add '-None-' as the first option
        self.application_type.addItems(self.application_option)
        self.application_type.currentIndexChanged.connect(self.on_combobox_changed)

        '''Complaint registered by'''
        self.complaint_register_by = self.complaint_register_by
        self.cursor.execute("SELECT ComplaintRegisterBy FROM fse_option")
        self.complaintregisterby_option = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.complaintregisterby_option.insert(0, '-None-')
        self.complaint_register_by.addItems(self.complaintregisterby_option)
        self.complaint_register_by.currentIndexChanged.connect(self.on_complaint_changed)

        '''Case Status'''
        # self.case_status = self.findChild(QtWidgets.QComboBox, 'case_status')
        self.case_status = self.case_status
        self.case_status_option = ['-None-', 'Open', 'Closed']
        # self.cursor.execute("SELECT CaseStatus FROM fse_option")
        # self.case_status_option = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.case_status_option.insert(0, '-None-')
        self.case_status.addItems(self.case_status_option)
        self.case_status.currentIndexChanged.connect(self.on_casestatus_changed)

        '''specification'''
        self.specification = self.specification
        self.cursor.execute("SELECT Specification FROM fse_option")
        self.specification_option = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.specification_option.insert(0, '-None-')
        self.specification.addItems(self.specification_option)
        self.specification.currentIndexChanged.connect(self.on_specification_changed)

        '''O.E.M'''
        self.oem = self.oem
        self.cursor.execute("SELECT OEM FROM fse_option")
        self.oem_option = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.oem_option.insert(0, '-None-')
        self.oem.addItems(self.oem_option)
        self.oem.currentIndexChanged.connect(self.on_oem_changed)

        '''Register By'''
        self.register_by = self.register_by
        self.cursor.execute("SELECT RegisterBy FROM fse_option")
        self.register_by_option = [row[0] for row in self.cursor.fetchall() if row[0] is not None]
        self.register_by_option.insert(0, '-None-')
        self.register_by.addItems(self.register_by_option)
        self.register_by.currentIndexChanged.connect(self.on_register_by_changed)


        #Checkboxes
        self.dispatch.toggled.connect(self.on_dispatch_toggled)
        self.no_barcode_case.toggled.connect(self.on_noBarcodeCase_toggled)
        self.standby_battery.toggled.connect(self.on_standbyBattery_toggled)
        self.admin_closure.toggled.connect(self.on_adminClosure_toggled)
        self.warrenty_void.toggled.connect(self.on_warrentyVoid_toggled)
        self.escalation.toggled.connect(self.on_escalation_toggled)   
        
    
    def insert_into_database(self, table_name, data_dict):
        try:
            # Check if data is empty
            if not data_dict:
                print("No data provided for insertion")
                print(data_dict)
                QMessageBox.warning(self, 'Warning', 'No data provided for insertion')
                return False

            # Construct the SQL query dynamically
            columns = ', '.join(data_dict.keys())
            placeholders = ', '.join(['%s'] * len(data_dict))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Execute the query
            self.cursor.execute(query, tuple(data_dict.values()))
            self.connection.commit()  # Commit the transaction

            # Show success message
            QMessageBox.information(self, 'Information', f'Data saved successfully in {table_name}!')
            print(f"Data inserted into {table_name}: {data_dict}")
            return True

        except Exception as e:
            # Handle exceptions and show error message
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            print(e)
            return False

    def on_SerialNumberChanged(self):
        try:
            # Get the serial number from the input field
            serial_number = self.serial_number.text().upper().strip()
            updateLineEdit = self.calender.text().strip()
            Specification = self.specification.currentText().strip()
            UpdateLineEdit = self.EscalationTime.text().strip()
            oem = self.oem.currentText().strip()
            
            mandatory_fields = {
                "Serial Number":serial_number,
                "OEM":oem,
                "Specification":Specification,
                "Register Date":updateLineEdit,
                "Escalation Time":UpdateLineEdit,
                # "Complaint By":
            }
            
            empty_fields = [key for key, value in mandatory_fields.items() if not value or value == "-None-"]

            if empty_fields:
                QMessageBox.warning(self, 'Warning', f'Please fill in the following fields: {", ".join(empty_fields)}')
                return
                
            # First, determine the Escalation and EscalationTime values based on the condition
            escalation = "True" if self.escalation.isChecked() else "False"
            escalation_time = UpdateLineEdit if self.EscalationTime.text() else None

            # If Escalation is False, set EscalationTime to None
            if escalation == "False":
                escalation_time = "Null"
                
            # Prepare data for insertion
            data_dict = {
                "SerialNo": serial_number,  # Column name: SerialNo
                "Dispatch": "Dispatched" if self.dispatch.isChecked() else "Not Dispatch",  # Column name: Dispatch
                "RegisterDate": updateLineEdit if self.calender.text() else None,  # Column name: RegisterDate
                "Specification": Specification if Specification != '--None--' else None,  # Column name: Specification
                "ComplaintRegisterBy": self.complaint_raised_by.currentText(),  # Column name: ComplaintRegisterBy
                "OEM": self.oem.currentText(),  # Column name: OEM
                "Application": self.application_type.currentText(),  # Column name: Application
                "NoBarcodeOnTheCase": "True" if self.no_barcode_case.isChecked() else "False",  # Column name: NoBarcodeOnTheCase
                "RegisterBy": self.register_by.currentText(),  # Column name: RegisterBy
                "StandByBattery": "True" if self.standby_battery.isChecked() else "False",  # Column name: StandByBattery
                "WarrentyVoid": "True" if self.warrenty_void.isChecked() else "False",  # Column name: WarrentyVoid
                "AdminClosure": "True" if self.admin_closure.isChecked() else "False",  # Column name: AdminClosure
                # "Escalation": "True" if self.escalation.isChecked() else "False",  # Column name: Escalation
                # "EscalationTime": UpdateLineEdit if self.EscalationTime.text() else None  # Column name: EscalationTime
                "Escalation": escalation,  # Column name: Escalation
                "EscalationTime": escalation_time  # Column name: EscalationTime
            }
            
            # Insert data into the database
            self.insert_into_database(table_name="ComplaintInformation", data_dict=data_dict)
        
        except Exception as e:
            # Handle any exceptions and show an error message
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            print(e)

    def on_oem_changed(self):
        try:
            oem = self.oem.currentText()
            if oem == '--None--':
                self.status_bar.hide()
            else:
                self.status_bar.show()
                self.status_bar.setText("Selected O.E.M: " + oem)
                print(oem)
        except Exception as e:
            print(e)

    def on_register_by_changed(self):
        try:
            register_by = self.register_by.currentText()
            if register_by == '--None--':
                self.status_bar.hide()
            else:
                self.status_bar.show()
                self.status_bar.setText("Selected register by: " + register_by)
                print(register_by)
        except Exception as e:
            print(e)

    def on_complaint_changed(self):
        try:
            complaint_register_by = self.complaint_register_by.currentText()
            if complaint_register_by == '--None--':
                self.status_bar.hide()
            elif complaint_register_by == '':
                QMessageBox.warning(self, 'Warning', 'Please select complaint registered by')
            else:
                self.status_bar.show()
                self.status_bar.setText("Complaint registered by: " + complaint_register_by)
                print(complaint_register_by)
        except Exception as e:
            print(e)

    def on_specification_changed(self):
        try:
            specification = self.specification.currentText()
            if specification == '--None--':
                self.status_bar.hide()
            else:
                self.status_bar.show()
                self.status_bar.setText("Selected specification: " + specification)
                print(specification)
        except Exception as e:
            print(e)

    def on_serial_number_changed(self):
        try:
            battery_code_input = self.serial_number.text().upper()
            # QMessageBox.information(self, 'Information', 'Battery code is: ' + battery_code_input)
        except Exception as e:
            print(e)

    def on_combobox_changed(self):
        try:
            selected_text = self.application_type.currentText()
            if selected_text == '--None--':
                self.status_bar.hide()
            else:
                self.status_bar.show()
                self.status_bar.setText("Selected application type: " + selected_text)
                print(selected_text)
        except Exception as e:
            print(e)

    def on_casestatus_changed(self):
        try:
            selected_txt = self.case_status.currentText()
            if selected_txt == '--None--'or'Open':
                pass
            elif selected_txt == 'Closed':
                pass
        except Exception as e:
            print(e)

    def showCalendar(self, event):
        # Create a dialog with a calendar widget
        calendar_dialog = QDialog(self)
        calendar_layout = QVBoxLayout(calendar_dialog)

        # Create the calendar widget and set the selected date as the current one
        calendar = QCalendarWidget(calendar_dialog)
        calendar.setSelectedDate(QDate.currentDate())
        calendar_layout.addWidget(calendar)

        # Set up the dialog layout
        calendar_dialog.setLayout(calendar_layout)
        calendar_dialog.setWindowTitle("Select Date")

        # Connect the calendar's clicked signal to update the QLineEdit
        calendar.clicked.connect(lambda date: self.updateLineEdit(date, calendar_dialog))

        # Show the dialog
        calendar_dialog.exec_()

    def ShowCalendar(self, event):
        # Create a dialog with a calendar widget
        calendar_dialog = QDialog(self)
        calendar_layout = QVBoxLayout(calendar_dialog)

        # Create the calendar widget and set the selected date as the current one
        EscalationTime = QCalendarWidget(calendar_dialog)
        EscalationTime.setSelectedDate(QDate.currentDate())
        calendar_layout.addWidget(EscalationTime)

        # Set up the dialog layout
        calendar_dialog.setLayout(calendar_layout)
        calendar_dialog.setWindowTitle("Select Date")

        # Connect the calendar's clicked signal to update the QLineEdit
        EscalationTime.clicked.connect(lambda date: self.UpdateLineEdit(date, calendar_dialog))

        # Show the dialog
        calendar_dialog.exec_()

    def updateLineEdit(self, date, calendar_dialog):
        # Update the QLineEdit text with the selected date in the format "dd/MM/yyyy"
        self.calender.setText(date.toString("dd/MM/yyyy"))
        # Close the calendar dialog
        calendar_dialog.accept()
        print(date.toString("dd/MM/yyyy"))

    def UpdateLineEdit(self, date, calendar_dialog):
        # Update the QLineEdit text with the selected date in the format "dd/MM/yyyy"
        self.EscalationTime.setText(date.toString("dd/MM/yyyy"))
        # Close the calendar dialog
        calendar_dialog.accept()
        print(date.toString("dd/MM/yyyy"))

    def on_dispatch_toggled(self):
        if self.dispatch.isChecked():
            pass

    def on_noBarcodeCase_toggled(self):
        if self.no_barcode_case.isChecked():
            print('No Barcode Case')

    def on_standbyBattery_toggled(self):
        if self.standby_battery.isChecked():
            print('Standby Battery')
    
    def on_adminClosure_toggled(self):
        if self.admin_closure.isChecked():
            print('Admin Closure')
    
    def on_warrentyVoid_toggled(self):
        if self.warrenty_void.isChecked():
            print('Warrenty Void')
        
    def on_escalation_toggled(self):
        if self.escalation.isChecked():
            print('Escalation')
            self.EscalationTime.show()
            self.EscalationTime_label_26.show()
        else:
            self.EscalationTime.hide()
            self.EscalationTime_label_26.hide()

    # def on_EscalationTimeChanged(self):


    def closeEvent(self, event):
        # Close the connection when the window is closed
        mydb_connection.close_connection(self.connection)
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
