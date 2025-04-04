from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QMessageBox
)


class StaffWindow(QWidget):
    def __init__(self, db, staff_id):
        super().__init__()
        self.db = db
        self.staff_id = staff_id
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle('员工主页')
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.labels = {}
        self.fields = {}

        fields = ['staff_id', 'name', 'email', 'phone_number', 'salary']
        for field in fields:
            self.labels[field] = QLabel(field.replace('_', ' ').title())
            self.fields[field] = QLineEdit()
            self.fields[field].setReadOnly(True)
            form.addRow(self.labels[field], self.fields[field])

        self.fields['phone_number'].setReadOnly(False)
        self.btn_update = QPushButton('更新电话号码')
        self.btn_update.clicked.connect(self.update_phone)

        layout.addLayout(form)
        layout.addWidget(self.btn_update)
        self.setLayout(layout)

    def load_data(self):
        query = "SELECT * FROM staffs WHERE staff_id = %s"
        result = self.db.execute_query(query, (self.staff_id,))

        if result:
            data = result[0]
            self.fields['staff_id'].setText(str(data[0]))
            self.fields['name'].setText(data[1])
            self.fields['email'].setText(data[2])
            self.fields['phone_number'].setText(data[3])
            self.fields['salary'].setText(str(data[4]))

    def update_phone(self):
        new_phone = self.fields['phone_number'].text()
        query = "UPDATE staffs SET phone_number = %s WHERE staff_id = %s"
        result = self.db.execute_query(query, (new_phone, self.staff_id))

        if result:
            QMessageBox.information(self, '成功', '电话号码更新成功')
        else:
            QMessageBox.warning(self, '错误', '电话号码更新失败')