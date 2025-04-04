from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QComboBox, QMessageBox
)


class ManagerWindow(QWidget):
    def __init__(self, db, staff_id):
        super().__init__()
        self.db = db
        self.staff_id = staff_id
        self.department_id = self.get_department()
        self.init_ui()
        self.load_staff()

    def get_department(self):
        query = "SELECT department_id FROM staffs WHERE staff_id = %s"
        result = self.db.execute_query(query, (self.staff_id,))
        return result[0][0] if result else None

    def init_ui(self):
        self.setWindowTitle('部门经理主页')
        self.setFixedSize(800, 600)

        main_layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_type = QComboBox()
        self.search_type.addItems(['按编号', '按姓名'])
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search_staff)

        search_layout.addWidget(QLabel('搜索:'))
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(search_btn)

        # 排序选项
        sort_layout = QHBoxLayout()
        self.sort_by = QComboBox()
        self.sort_by.addItems(['员工编号升序', '工资降序'])
        sort_btn = QPushButton('排序')
        sort_btn.clicked.connect(self.load_staff)

        sort_layout.addWidget(QLabel('排序方式:'))
        sort_layout.addWidget(self.sort_by)
        sort_layout.addWidget(sort_btn)

        # 统计按钮
        stats_btn = QPushButton('查看部门工资统计')
        stats_btn.clicked.connect(self.show_stats)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ['员工ID', '姓名', '邮箱', '电话', '工资', '职位']
        )

        main_layout.addLayout(search_layout)
        main_layout.addLayout(sort_layout)
        main_layout.addWidget(stats_btn)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def load_staff(self):
        order_by = "staff_id ASC" if self.sort_by.currentIndex() == 0 else "salary DESC"
        query = f"""
        SELECT staff_id, name, email, phone_number, salary, position
        FROM staffs 
        WHERE department_id = %s
        ORDER BY {order_by}
        """
        results = self.db.execute_query(query, (self.department_id,))

        self.populate_table(results)

    def search_staff(self):
        search_text = self.search_field.text()
        if not search_text:
            self.load_staff()
            return

        if self.search_type.currentIndex() == 0:  # 按编号
            query = """
            SELECT staff_id, name, email, phone_number, salary, position
            FROM staffs 
            WHERE department_id = %s AND staff_id = %s
            """
            params = (self.department_id, search_text)
        else:  # 按姓名
            query = """
            SELECT staff_id, name, email, phone_number, salary, position
            FROM staffs 
            WHERE department_id = %s AND name LIKE %s
            """
            params = (self.department_id, f"%{search_text}%")

        results = self.db.execute_query(query, params)
        self.populate_table(results)

    def populate_table(self, data):
        self.table.setRowCount(0)
        if not data:
            return

        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(
                    row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def show_stats(self):
        query = """
        SELECT 
            MAX(salary) as max_salary,
            MIN(salary) as min_salary,
            AVG(salary) as avg_salary
        FROM staffs 
        WHERE department_id = %s
        """
        result = self.db.execute_query(query, (self.department_id,))

        if result:
            max_sal, min_sal, avg_sal = result[0]
            msg = f"最高工资: {max_sal}\n最低工资: {min_sal}\n平均工资: {avg_sal:.2f}"
            QMessageBox.information(self, '部门工资统计', msg)