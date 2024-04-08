import sqlite3

# Kết nối đến cơ sở dữ liệu (nếu không tồn tại, sẽ tạo một cơ sở dữ liệu mới)
conn = sqlite3.connect('sinhVien.db')

# Tạo một con trỏ để thực hiện các truy vấn SQL
cursor = conn.cursor()

# Tạo một bảng

cursor.execute('''CREATE TABLE IF NOT EXISTS Class (
                    id INTEGER PRIMARY KEY,
                    tenLop TEXT NOT NULL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Courses (
                    id INTEGER PRIMARY KEY,
                    tenMonHoc TEXT NOT NULL,
                    lopID INT NOT NULL,
                    thoiGianDiemDanh TEXT NOT NULL,
                    IDgiangVien INTEGER NOT NULL,
                    FOREIGN KEY (lopID) REFERENCES Class(id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                    MSSV INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    lopID INTEGER,
                    vaiTro TEXT NOT NULL,
                     FOREIGN KEY (lopID) REFERENCES Class(id)
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Attendance (
                    id INTEGER PRIMARY KEY,
                    MSSV INTEGER NOT NULL,
                    courseID INTEGER NOT NULL,
                    ngayDiemDanh TEXT NOT NULL,
                    status  INTEGER DEFAULT 0,
                    FOREIGN KEY (MSSV) REFERENCES User(MSSV),
                    FOREIGN KEY (courseID) REFERENCES Courses(id)
                )''')

# Thêm dữ liệu vào bảng

cursor.execute("INSERT INTO Class (tenLop) VALUES ('IT01')")
cursor.execute("INSERT INTO Class (tenLop) VALUES ('IT02')")

cursor.execute("INSERT INTO Users (MSSV,name,password,lopID,vaiTro) VALUES (2051050342,'Phat','123',1,'sinhVien')")
cursor.execute("INSERT INTO Users (MSSV,name,password,lopID,vaiTro) VALUES (2051050360,'Phuc','123',1,'sinhVien')")
cursor.execute("INSERT INTO Users (MSSV,name,password,lopID,vaiTro) VALUES (2051050333,'Loc','123',2,'sinhVien')")
cursor.execute("INSERT INTO Users (MSSV,name,password,lopID,vaiTro) VALUES (2051050444,'Luong','123',2,'sinhVien')")


cursor.execute("INSERT INTO Users (MSSV,name,password,vaiTro) VALUES(101202303,'giaovien','123','giaoVien')")
cursor.execute("INSERT INTO Users (MSSV,name,password,vaiTro) VALUES(001122,'giaovien2','123','giaoVien')")

cursor.execute("INSERT INTO Courses (tenMonHoc,lopID,thoiGianDiemDanh,IDgiangVien) VALUES ('Mã nguồn mở',1,'07:45',"
               "101202303)")
cursor.execute("INSERT INTO Courses (tenMonHoc,lopID,thoiGianDiemDanh,IDgiangVien) VALUES ('Lập trình mobile',1,"
               "'07:45',101202303)")
cursor.execute("INSERT INTO Courses (tenMonHoc,lopID,thoiGianDiemDanh,IDgiangVien) VALUES ('Mã nguồn mở',2,'07:45',"
               "001122)")
cursor.execute("INSERT INTO Courses (tenMonHoc,lopID,thoiGianDiemDanh,IDgiangVien) VALUES ('Lập trình mobile',2,"
               "'07:45',001122)")
cursor.execute("INSERT INTO Courses (tenMonHoc,lopID,thoiGianDiemDanh,IDgiangVien) VALUES ('Lập trình Java',2,"
               "'10:45',101202303)")

cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050342,5,'2024-04-01',0)")
cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050342,1,'2024-04-01',0)")
cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050342,2,'2024-04-01',0)")

cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050360,1,'2024-04-01',0)")
cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050360,2,'2024-04-01',0)")

cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050333,3,'2024-04-01',0)")
cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050333,4,'2024-04-01',0)")

cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050444,3,'2024-04-01',0)")
cursor.execute("INSERT INTO Attendance (MSSV,courseID,ngayDiemDanh,status) VALUES (2051050444,4,'2024-04-01',0)")

# Thêm dữ liệu sinh viên khác vào bảng

# Lưu các thay đổi
conn.commit()

# Đóng kết nối
conn.close()
