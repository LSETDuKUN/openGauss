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
        self.section_id = self.get_manager_section()
        self.init_ui()
        self.load_department_staff()

    def get_manager_section(self):
        """获取当前经理管理的部门ID"""
        query = """
        SELECT section_id FROM staffs 
        WHERE staff_id = %s AND role = 'manager'
        """
        result = self.db.safe_execute(query, (self.staff_id,))
        return result[0][0] if result else None

    def init_ui(self):
        self.setWindowTitle('部门经理主页')
        self.setFixedSize(900, 600)

        main_layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_type = QComboBox()
        self.search_type.addItems(['按员工ID', '按员工姓名'])
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search_staff)

        search_layout.addWidget(QLabel('搜索:'))
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(search_btn)

        # 排序选项
        sort_layout = QHBoxLayout()
        self.sort_by = QComboBox()
        self.sort_by.addItems(['员工ID升序', '工资降序', '入职日期降序'])
        sort_btn = QPushButton('排序')
        sort_btn.clicked.connect(self.load_department_staff)

        sort_layout.addWidget(QLabel('排序方式:'))
        sort_layout.addWidget(self.sort_by)
        sort_layout.addWidget(sort_btn)

        # 统计按钮
        stats_btn = QPushButton('部门工资统计')
        stats_btn.clicked.connect(self.show_salary_stats)

        # 员工表格
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(8)
        self.staff_table.setHorizontalHeaderLabels(
            ['员工ID', '姓名', '职位', '邮箱', '电话', '工资', '入职日期', '角色']
        )

        main_layout.addLayout(search_layout)
        main_layout.addLayout(sort_layout)
        main_layout.addWidget(stats_btn)
        main_layout.addWidget(self.staff_table)
        self.setLayout(main_layout)

    def load_department_staff(self):
        try:
            order_mapping = {
                0: "s.staff_id ASC",
                1: "s.salary DESC",
                2: "s.hire_date DESC"
            }
            order_by = order_mapping.get(self.sort_by.currentIndex(), "s.staff_id ASC")

            query = f"""
            SELECT 
                s.staff_id,
                s.first_name || ' ' || s.last_name AS full_name,
                s.employment_id,
                s.email,
                s.phone_number,
                s.salary,
                s.hire_date,
                s.role
            FROM staffs s
            WHERE s.section_id = %s
            ORDER BY {order_by}
            """
            results = self.db.safe_execute(query, (self.section_id,))

            self.populate_table(results if results else [])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据加载失败: {str(e)}")

    def search_staff(self):
        search_text = self.search_field.text().strip()
        if not search_text:
            self.load_department_staff()
            return

        if self.search_type.currentIndex() == 0:  # 按员工ID
            query = """
            SELECT
                s.staff_id,
                s.first_name || ' ' || s.last_name AS full_name,
                s.employment_id,
                s.email,
                s.phone_number,
                s.salary,
                s.hire_date,
                s.role
            FROM staffs s
            WHERE s.section_id = %s AND s.staff_id = %s
            """
            params = (self.section_id, search_text)
        else:  # 按员工姓名
            query = """
            SELECT
                s.staff_id,
                s.first_name || ' ' || s.last_name AS full_name,
                s.employment_id,
                s.email,
                s.phone_number,
                s.salary,
                s.hire_date,
                s.role
            FROM staffs s
            WHERE s.section_id = %s
              AND (
                  s.first_name ILIKE %s 
                  OR s.last_name ILIKE %s
                  OR (s.first_name || ' ' || s.last_name) ILIKE %s
              )
            """
            search_pattern = f"%{search_text}%"
            params = (self.section_id, search_pattern, search_pattern, search_pattern)

        results = self.db.safe_execute(query, params)
        self.populate_table(results if results else [])

    def populate_table(self, data):
        self.staff_table.setRowCount(0)
        if not data:
            return

        self.staff_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data if col_data is not None else ""))

                # 特殊格式化
                if col_idx == 5:  # 工资列
                    item.setText(f"{float(col_data):,.2f}")
                elif col_idx == 6:  # 日期列
                    item.setText(str(col_data).split()[0])  # 只显示日期部分

                self.staff_table.setItem(row_idx, col_idx, item)

    def show_salary_stats(self):
        query = """
        SELECT 
            COUNT(*) as staff_count,
            MAX(salary) as max_salary,
            MIN(salary) as min_salary,
            AVG(salary) as avg_salary
        FROM staffs
        WHERE section_id = %s
        """
        result = self.db.safe_execute(query, (self.section_id,))

        if result and result[0]:
            count, max_sal, min_sal, avg_sal = result[0]
            msg = (
                f"部门员工数: {count}\n"
                f"最高工资: {max_sal:,.2f}\n"
                f"最低工资: {min_sal:,.2f}\n"
                f"平均工资: {avg_sal:,.2f}"
            )
            QMessageBox.information(self, "部门统计", msg)
        else:
            QMessageBox.warning(self, "错误", "获取统计信息失败")