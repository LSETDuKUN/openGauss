import sys
from PyQt5.QtWidgets import QApplication
from database import Database
from views.login import LoginWindow


def main():
    app = QApplication(sys.argv)

    # 初始化数据库连接
    db = Database()

    # 显示登录窗口
    login = LoginWindow(db)
    login.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
