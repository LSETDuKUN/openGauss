class Staff:
    def __init__(self, db):
        self.db = db

    def get_info(self, staff_id):
        query = "SELECT * FROM staffs WHERE staff_id = %s"
        return self.db.execute_query(query, (staff_id,))

    def update_phone(self, staff_id, new_phone):
        query = "UPDATE staffs SET phone_number = %s WHERE staff_id = %s"
        return self.db.execute_query(query, (new_phone, staff_id))


class Manager(Staff):
    def get_department_staff(self, dept_id, order_by="staff_id"):
        order = "ASC" if order_by == "staff_id" else "DESC"
        query = f"""
        SELECT * FROM staffs 
        WHERE department_id = %s 
        ORDER BY {order_by} {order}
        """
        return self.db.execute_query(query, (dept_id,))

    def get_salary_stats(self, dept_id):
        query = """
        SELECT 
            MAX(salary) as max_salary,
            MIN(salary) as min_salary,
            AVG(salary) as avg_salary
        FROM staffs 
        WHERE department_id = %s
        """
        return self.db.execute_query(query, (dept_id,))


class HRManager(Manager):
    def get_all_staff(self, order_by="staff_id"):
        order = "ASC" if order_by == "staff_id" else "DESC"
        query = f"SELECT * FROM staffs ORDER BY {order_by} {order}"
        return self.db.execute_query(query)

    def update_department(self, dept_id, new_name):
        query = "UPDATE departments SET department_name = %s WHERE department_id = %s"
        return self.db.execute_query(query, (new_name, dept_id))

    def add_location(self, location_data):
        query = """
        INSERT INTO locations (location_id, address, postal_code, city, state)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, location_data)