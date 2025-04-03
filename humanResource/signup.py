import psycopg2

user = "pengyifei"
password = "pengyifei@123"
host = "113.44.150.42"
port = "26000"
database = "human_resource"
try:
    connection = psycopg2.connect(
            user = user,
            password = password,
            host = host,
            port = port,
            database = database
            )
    print("connection success! current database:"+database)
except(Exception, psycopg2.Error) as Error:
    print("connection error!")
cursor = connection.cursor()
query = "select * from staffs"
cursor.execute(query)
results = cursor.fetchall()

for row in results:
    print("-------------")
    print(f"主键：{row[0]}")
    print(f"content:{row[1]}")
cursor.close()
connection.close()