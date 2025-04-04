from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QTextEdit, QDialog, QHBoxLayout, QLabel, \
    QComboBox, QWidget


class UserInterface(QWidget):
    def __init__(self):
        super().__init__()

        #定义登录信息输入框

        self.user_box = None
        self.pwd_box = None
        self.host_box = None
        self.database_box = None

        # 定义界面
        self.init_ui()

        #主布局
        self.mainLayout = None

        self.configure_btn = None

    def init_ui(self):

        # 布局
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        #界面名称
        self.setWindowTitle("用户登录界面")
        self.setGeometry(500,500,500,500)

        self.user_box = self.my_input("用户名：")
        self.pwd_box = self.my_input("密码：")
        self.host_box = self.my_input("host：")
        self.database_box = self.my_input("数据库名称：")
        self.configure_btn = QPushButton("确认")
        self.mainLayout.addWidget(self.configure_btn)

    def my_input(self,label):



        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        input_box = QLineEdit()
        layout.addWidget(input_box)
        self.mainLayout.addLayout(layout)

        return input_box


