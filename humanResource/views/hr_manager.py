from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QComboBox, QMessageBox
)


class HRManagerWindow(QWidget):
    def __init__(self, db, staff_id):
        super().__init__()
        self.db = db
        self.staff_id = staff_id
        self.init_ui()
        self.load_all_staff()

    def init_ui(self):
        self.setWindowTitle('人事经理主页')
        self.setFixedSize(1000, 800)

        self.tabs = QTabWidget()

        # 员工管理标签页
        self.staff_tab = QWidget()
        self.init_staff_tab()

        # 部门管理标签页
        self.dept_tab = QWidget()
        self.init_dept_tab()

        # 工作地点标签页
        self.location_tab = QWidget()
        self.init_location_tab()

        self.tabs.addTab(self.staff_tab, "员工管理")
        self.tabs.addTab(self.dept_tab, "部门管理")
        self.tabs.addTab(self.location_tab, "工作地点")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def init_staff_tab(self):
        layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.staff_search = QLineEdit()
        self.staff_search_type = QComboBox()
        self.staff_search_type.addItems(['按编号', '按姓名'])
        search_btn = QPushButton('搜索员工')
        search_btn.clicked.connect(self.search_staff)

        search_layout.addWidget(QLabel('搜索:'))
        search_layout.addWidget(self.staff_search)
        search_layout.addWidget(self.staff_search_type)
        search_layout.addWidget(search_btn)

        # 排序选项
        sort_layout = QHBoxLayout()
        self.staff_sort = QComboBox()
        self.staff_sort.addItems(['员工编号升序', '工资降序'])
        sort_btn = QPushButton('排序')
        sort_btn.clicked.connect(self.load_all_staff)

        sort_layout.addWidget(QLabel('排序方式:'))
        sort_layout.addWidget(self.staff_sort)
        sort_layout.addWidget(sort_btn)

        # 统计按钮
        stats_btn = QPushButton('查看部门工资统计')
        stats_btn.clicked.connect(self.show_dept_stats)

        # 表格
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(7)
        self.staff_table.setHorizontalHeaderLabels(
            ['员工ID', '姓名', '邮箱', '电话', '工资', '职位', '部门']
        )

        layout.addLayout(search_layout)
        layout.addLayout(sort_layout)
        layout.addWidget(stats_btn)
        layout.addWidget(self.staff_table)
        self.staff_tab.setLayout(layout)

    def init_dept_tab(self):
        layout = QVBoxLayout()

        # 部门表格
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(3)
        self.dept_table.setHorizontalHeaderLabels(
            ['部门ID', '部门名称', '经理ID']
        )

        # 部门编辑区域
        edit_layout = QFormLayout()
        self.dept_id = QLineEdit()
        self.dept_id.setPlaceholderText("输入要修改的部门ID")
        self.new_dept_name = QLineEdit()
        self.new_dept_name.setPlaceholderText("输入新部门名称")
        update_btn = QPushButton('更新部门名称')
        update_btn.clicked.connect(self.update_dept)

        edit_layout.addRow('部门ID:', self.dept_id)
        edit_layout.addRow('新名称:', self.new_dept_name)
        edit_layout.addRow(update_btn)

        layout.addWidget(self.dept_table)
        layout.addLayout(edit_layout)
        self.dept_tab.setLayout(layout)

        self.load_depts()

    def init_location_tab(self):
        layout = QVBoxLayout()

        # 地点表格
        self.loc_table = QTableWidget()
        self.loc_table.setColumnCount(5)
        self.loc_table.setHorizontalHeaderLabels(
            ['地点ID', '地址', '邮编', '城市', '州']
        )

        # 添加新地点区域
        add_layout = QFormLayout()
        self.loc_id = QLineEdit()
        self.loc_address = QLineEdit()
        self.loc_postal = QLineEdit()
        self.loc_city = QLineEdit()
        self.loc_state = QLineEdit()
        add_btn = QPushButton('添加新地点')
        add_btn.clicked.connect(self.add_location)

        add_layout.addRow('地点ID:', self.loc_id)
        add_layout.addRow('地址:', self.loc_address)
        add_layout.addRow('邮编:', self.loc_postal)
        add_layout.addRow('城市:', self.loc_city)
        add_layout.addRow('州:', self.loc_state)
        add_layout.addRow(add_btn)

        layout.addWidget(self.loc_table)
        layout.addLayout(add_layout)
        self.location_tab.setLayout(layout)

        self.load_locations()

    def load_all_staff(self):
        order_by = "staff_id ASC" if self.staff_sort.currentIndex() == 0 else "salary DESC"
        query = f"""
        SELECT s.staff_id, s.name, s.email, s.phone_number, s.salary, s.position, d.department_name
        FROM staffs s
        JOIN departments d ON s.department_id = d.department_id
        ORDER BY {order_by}
        """
        results = self.db.execute_query(query)
        self.populate_staff_table(results)

    def search_staff(self):
        search_text = self.staff_search.text()
        if not search_text:
            self.load_all_staff()
            return

        if self.staff_search_type.currentIndex() == 0:  # 按编号
            query = """
            SELECT s.staff_id, s.name, s.email, s.phone_number, s.salary, s.position, d.department_name
            FROM staffs s
            JOIN departments d ON s.department_id = d.department_id
            WHERE s.staff_id = %s
            """
            params = (search_text,)
        else:  # 按姓名
            query = """
            SELECT s.staff_id, s.name, s.email, s.phone_number, s.salary, s.position, d.department_name
            FROM staffs s
            JOIN departments d ON s.department_id = d.department_id
            WHERE s.name LIKE %s
            """
            params = (f"%{search_text}%",)

        results = self.db.execute_query(query, params)
        self.populate_staff_table(results)

    def populate_staff_table(self, data):
        self.staff_table.setRowCount(0)
        if not data:
            return

        self.staff_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                self.staff_table.setItem(
                    row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def show_dept_stats(self):
        query = """
        SELECT 
            d.department_name,
            MAX(s.salary) as max_salary,
            MIN(s.salary) as min_salary,
            AVG(s.salary) as avg_salary
        FROM staffs s
        JOIN departments d ON s.department_id = d.department_id
        GROUP BY d.department_name
        """
        results = self.db.execute_query(query)

        if results:
            msg = "各部门工资统计:\n\n"
            for dept, max_sal, min_sal, avg_sal in results:
                msg += f"{dept}:\n  最高: {max_sal}\n  最低: {min_sal}\n  平均: {avg_sal:.2f}\n\n"

            QMessageBox.information(self, '部门工资统计', msg)

    def load_depts(self):
        query = "SELECT * FROM departments"
        results = self.db.execute_query(query)

        self.dept_table.setRowCount(0)
        if not results:
            return

        self.dept_table.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                self.dept_table.setItem(
                    row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def update_dept(self):
        dept_id = self.dept_id.text()
        new_name = self.new_dept_name.text()

        if not dept_id or not new_name:
            QMessageBox.warning(self, '错误', '请输入部门ID和新名称')
            return

        query = "UPDATE departments SET department_name = %s WHERE department_id = %s"
        result = self.db.execute_query(query, (new_name, dept_id))

        if result:
            QMessageBox.information(self, '成功', '部门名称更新成功')
            self.load_depts()
        else:
            QMessageBox.warning(self, '错误', '部门名称更新失败')

    def load_locations(self):
        query = "SELECT * FROM locations"
        results = self.db.execute_query(query)

        self.loc_table.setRowCount(0)
        if not results:
            return

        self.loc_table.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                self.loc_table.setItem(
                    row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def add_location(self):
        loc_id = self.loc_id.text()
        address = self.loc_address.text()
        postal = self.loc_postal.text()
        city = self.loc_city.text()
        state = self.loc_state.text()

        if not all([loc_id, address, postal, city, state]):
            QMessageBox.warning(self, '错误', '请填写所有字段')
            return

        query = """
        INSERT INTO locations (location_id, address, postal_code, city, state)
        VALUES (%s, %s, %s, %s, %s)
        """
        result = self.db.execute_query(query, (loc_id, address, postal, city, state))

        if result:
            QMessageBox.information(self, '成功', '工作地点添加成功')
            self.load_locations()
            # 清空输入框
            self.loc_id.clear()
            self.loc_address.clear()
            self.loc_postal.clear()
            self.loc_city.clear()
            self.loc_state.clear()
        else:
            QMessageBox.warning(self, '错误', '工作地点添加失败')