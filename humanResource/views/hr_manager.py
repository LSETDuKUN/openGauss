from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QComboBox, QMessageBox
)
from psycopg2 import sql


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
        self.place_tab = QWidget()
        self.init_place_tab()

        self.tabs.addTab(self.staff_tab, "员工管理")
        self.tabs.addTab(self.dept_tab, "部门管理")
        self.tabs.addTab(self.place_tab, "工作地点")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # 添加查询工作历史按钮和输入框
        history_layout = QHBoxLayout()
        self.history_staff_id = QLineEdit()
        history_btn = QPushButton('查询工作历史')
        history_btn.clicked.connect(self.show_employment_history)

        history_layout.addWidget(QLabel('员工ID:'))
        history_layout.addWidget(self.history_staff_id)
        history_layout.addWidget(history_btn)

        # 将新布局添加到主布局中
        main_layout.addLayout(history_layout)

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



    def init_place_tab(self):
        layout = QVBoxLayout()

        # 地点表格
        self.loc_table = QTableWidget()
        self.loc_table.setColumnCount(6)
        self.loc_table.setHorizontalHeaderLabels(
            ['地点ID', '地址', '邮编', '城市', '国家', '地区']
        )

        # 添加新地点区域
        add_layout = QFormLayout()
        self.loc_id = QLineEdit()
        self.loc_address = QLineEdit()
        self.loc_postal = QLineEdit()
        self.loc_city = QLineEdit()
        self.state_combobox = QComboBox()  # 国家下拉框
        self.area_combobox = QComboBox()  # 地区下拉框

        # 加载国家和地区数据到下拉框
        self.load_states_and_areas()

        add_btn = QPushButton('添加新地点')
        add_btn.clicked.connect(self.add_place)

        add_layout.addRow('地点ID:', self.loc_id)
        add_layout.addRow('地址:', self.loc_address)
        add_layout.addRow('邮编:', self.loc_postal)
        add_layout.addRow('城市:', self.loc_city)
        add_layout.addRow('国家:', self.state_combobox)
        add_layout.addRow('地区:', self.area_combobox)
        add_layout.addRow(add_btn)

        layout.addWidget(self.loc_table)
        layout.addLayout(add_layout)
        self.place_tab.setLayout(layout)

        self.load_places()



    def load_all_staff(self):
        try:
            order_by = "s.staff_id ASC" if self.staff_sort.currentIndex() == 0 else "s.salary DESC"
            query = f"""
            SELECT 
                s.staff_id, 
                s.first_name || ' ' || s.last_name AS full_name,
                s.email, 
                s.phone_number, 
                s.salary, 
                s.employment_id,
                sec.section_name,
                a.area_name,
                st.state_name,
                s.role
            FROM staffs s
            LEFT JOIN sections sec ON s.section_id = sec.section_id
            LEFT JOIN places l ON sec.place_id = l.place_id
            LEFT JOIN states st ON l.state_id = st.state_id
            LEFT JOIN areas a ON st.area_id = a.area_id
            ORDER BY {order_by}
            """

            results = self.db.safe_execute(query)
            if results is None:
                QMessageBox.warning(self, "错误", "员工数据加载失败")
                return

            # 更新表头（新增地区和州字段）
            self.staff_table.setColumnCount(10)
            self.staff_table.setHorizontalHeaderLabels(
                ['员工ID', '姓名', '邮箱', '电话', '工资', '职位', '部门', '地区', '州', '角色']
            )
            self.populate_staff_table(results)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"系统错误: {str(e)}")

    def populate_staff_table(self, data):
        self.staff_table.setRowCount(0)
        if not data:
            return

        self.staff_table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                self.staff_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def search_staff(self):
        search_text = self.staff_search.text()
        if not search_text:
            self.load_all_staff()
            return

        try:
            if self.staff_search_type.currentIndex() == 0:  # 按编号
                query = """
                SELECT 
                    s.staff_id,
                    s.first_name || ' ' || s.last_name AS full_name,
                    s.email,
                    s.phone_number,
                    s.salary,
                    s.employment_id,
                    sec.section_name,
                    a.area_name,
                    st.state_name,
                    s.role
                FROM staffs s
                LEFT JOIN sections sec ON s.section_id = sec.section_id
                LEFT JOIN places l ON sec.place_id = l.place_id
                LEFT JOIN states st ON l.state_id = st.state_id
                LEFT JOIN areas a ON st.area_id = a.area_id
                WHERE s.staff_id = %s
                """
                params = (search_text,)
                # 在 search_staff 方法中,将按姓名搜索的 else 分支修改如下
            else:  # 按姓名
                query = """
                    SELECT
                        s.staff_id,
                        s.first_name || ' ' || s.last_name AS full_name,
                        s.email,
                        s.phone_number,
                        s.salary,
                        s.employment_id,
                        sec.section_name,
                        a.area_name,
                        st.state_name,
                        s.role
                    FROM staffs s
                    LEFT JOIN sections sec ON s.section_id = sec.section_id
                    LEFT JOIN places l ON sec.place_id = l.place_id
                    LEFT JOIN states st ON l.state_id = st.state_id
                    LEFT JOIN areas a ON st.area_id = a.area_id
                    WHERE (s.first_name || ' ' || s.last_name) ILIKE %s
                    """
                search_pattern = f"%{search_text}%"
                params = (search_pattern,)

            results = self.db.safe_execute(query, params)
            if results is None:
                QMessageBox.warning(self, "错误", "搜索失败")
                return

            self.populate_staff_table(results)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索出错: {str(e)}")




    def show_dept_stats(self):
        query = """
        SELECT 
            sec.section_name,
            a.area_name,
            MAX(s.salary) as max_salary,
            MIN(s.salary) as min_salary,
            AVG(s.salary) as avg_salary,
            COUNT(s.staff_id) as staff_count
        FROM staffs s
        JOIN sections sec ON s.section_id = sec.section_id
        JOIN places l ON sec.place_id = l.place_id
        JOIN states st ON l.state_id = st.state_id
        JOIN areas a ON st.area_id = a.area_id
        GROUP BY sec.section_name, a.area_name
        ORDER BY a.area_name, sec.section_name
        """

        results = self.db.safe_execute(query)
        if not results:
            QMessageBox.warning(self, "警告", "未获取到统计数据")
            return

        msg = "部门和地区工资统计:\n\n"
        for section, area, max_sal, min_sal, avg_sal, count in results:
            msg += (
                f"{area} - {section}:\n"
                f"  人数: {count}\n"
                f"  最高工资: {max_sal}\n"
                f"  最低工资: {min_sal}\n"
                f"  平均工资: {avg_sal:.2f}\n\n"
            )

        QMessageBox.information(self, "统计结果", msg)
    def load_depts(self):
        query = """
        SELECT 
            sec.section_id,
            sec.section_name,
            sec.manager_id,
            l.place_id,
            l.city,
            st.state_name,
            a.area_name
        FROM sections sec
        LEFT JOIN places l ON sec.place_id = l.place_id
        LEFT JOIN states st ON l.state_id = st.state_id
        LEFT JOIN areas a ON st.area_id = a.area_id
        """
        results = self.db.safe_execute(query)

        self.dept_table.setRowCount(0)
        if not results:
            return

        self.dept_table.setColumnCount(7)
        self.dept_table.setHorizontalHeaderLabels(
            ['部门ID', '部门名称', '经理ID', '地点ID', '城市', '州', '地区']
        )

        self.dept_table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            for col_idx, value in enumerate(row):
                self.dept_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def update_dept(self):
        dept_id = self.dept_id.text()
        new_name = self.new_dept_name.text()

        if not dept_id or not new_name:
            QMessageBox.warning(self, '错误', '请输入部门ID和新名称')
            return

        query = "UPDATE sections SET section_name = %s WHERE section_id = %s"
        result = self.db.execute_query(query, (new_name, dept_id))

        if result:
            QMessageBox.information(self, '成功', '部门名称更新成功')
            self.load_depts()
        else:
            QMessageBox.warning(self, '错误', '部门名称更新失败')

    def load_places(self):

            query = """
            SELECT
                l.place_id,
                l.street_address,
                l.postal_code,
                l.city,
                st.state_name,
                a.area_name
            FROM places l
            JOIN states st ON l.state_id = st.state_id
            JOIN areas a ON st.area_id = a.area_id
            """
            results = self.db.safe_execute(query)

            self.loc_table.setRowCount(0)
            if not results:
                return

            self.loc_table.setColumnCount(6)
            self.loc_table.setHorizontalHeaderLabels(
                ['地点ID', '地址', '邮编', '城市', '州', '地区']
            )

            self.loc_table.setRowCount(len(results))
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    self.loc_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def load_states_and_areas(self):
        """加载国家和地区数据到下拉框"""
        # 加载地区数据
        area_query = "SELECT area_id, area_name FROM areas ORDER BY area_name"
        area_results = self.db.safe_execute(area_query)

        self.area_combobox.clear()
        self.area_combobox.addItem("请选择地区", None)
        if area_results:
            for area_id, area_name in area_results:
                self.area_combobox.addItem(area_name, area_id)

        # 加载国家数据
        state_query = "SELECT state_id, state_name FROM states ORDER BY state_name"
        state_results = self.db.safe_execute(state_query)

        self.state_combobox.clear()
        self.state_combobox.addItem("请选择国家", None)
        if state_results:
            for state_id, state_name in state_results:
                self.state_combobox.addItem(state_name, state_id)


    def add_place(self):
        # 获取输入数据
        loc_id = self.loc_id.text().strip()
        address = self.loc_address.text().strip()
        postal = self.loc_postal.text().strip()
        city = self.loc_city.text().strip()
        state_id = self.state_combobox.currentData()

        # 验证所有必填字段
        if not all([loc_id, address, postal, city, state_id]):
            QMessageBox.warning(self, '错误', '请填写所有必填字段')
            return

        # 插入新地点
        query = """
        INSERT INTO places 
            (place_id, street_address, postal_code, city, state_id)
        VALUES 
            (%s, %s, %s, %s, %s)
        """
        result = self.db.safe_execute(query, (loc_id, address, postal, city, state_id))

        if result:
            QMessageBox.information(self, '成功', '工作地点添加成功')
            self.load_states_and_areas()
            # 清空输入框
            self.loc_id.clear()
            self.loc_address.clear()
            self.loc_postal.clear()
            self.loc_city.clear()
            self.state_combobox.setCurrentIndex(0)
            self.area_combobox.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, '错误', '工作地点添加失败')

    # 在 hr_manager.py 中添加新方法
    def show_employment_history(self):
        staff_id = self.history_staff_id.text().strip()
        if not staff_id:
            QMessageBox.warning(self, "警告", "请输入员工ID")
            return

        query = """
        SELECT
            eh.staff_id,
            eh.employment_id,
            eh.section_id,
            eh.start_date,
            eh.end_date,
            sec.section_name
        FROM employment_history eh
        LEFT JOIN sections sec ON eh.section_id = sec.section_id
        WHERE eh.staff_id = %s
        ORDER BY eh.start_date DESC
        """

        results = self.db.safe_execute(query, (staff_id,))
        if not results:
            QMessageBox.information(self, "提示", "未找到该员工的工作历史记录")
            return

        msg = f"员工 {staff_id} 的工作历史:\n\n"
        for row in results:
            # 正确处理datetime对象
            start_date = row[3].strftime('%Y-%m-%d') if row[3] else ''
            end_date = "至今" if row[4] is None else row[4].strftime('%Y-%m-%d')

            msg += (
                f"时间: {start_date} - {end_date}\n"
                f"职位编号: {row[1]}\n"
                f"部门: {row[5]} (ID: {row[2]})\n"
                f"------------------------\n"
            )

        QMessageBox.information(self, "工作历史", msg)