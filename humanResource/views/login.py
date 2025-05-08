from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('人力资源管理系统 - 登录')
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.lbl_user = QLabel('员工ID:')
        self.txt_user = QLineEdit()

        self.lbl_pass = QLabel('密码:')
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton('登录')
        self.btn_login.clicked.connect(self.authenticate)

        layout.addWidget(self.lbl_user)
        layout.addWidget(self.txt_user)
        layout.addWidget(self.lbl_pass)
        layout.addWidget(self.txt_pass)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def authenticate(self):
        user_id = self.txt_user.text()
        password = self.txt_pass.text()

        if not user_id or not password:
            QMessageBox.warning(self, '错误', '请输入用户名和密码')
            return

        query = "SELECT role FROM staffs WHERE staff_id = %s AND password = %s"
        result = self.db.execute_query(query, (user_id, password))

        if not result:
            QMessageBox.warning(self, '错误', '用户名或密码错误')
            return

        role = result[0][0]
        self.hide()

        if role == 'staff':
            from views.staff import StaffWindow
            self.staff_window = StaffWindow(self.db, user_id)
            self.staff_window.show()
        elif role == 'manager':
            from views.manager import ManagerWindow
            self.manager_window = ManagerWindow(self.db, user_id)
            self.manager_window.show()
        elif role == 'hr_manager':
            from views.hr_manager import HRManagerWindow
            self.hr_window = HRManagerWindow(self.db, user_id)
            self.hr_window.show()