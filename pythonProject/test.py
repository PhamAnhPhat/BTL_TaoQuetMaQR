import tkinter as tk
from tkinter import messagebox, ttk
import qrcode
from PIL import Image, ImageTk
import sqlite3
import pandas as pd
from datetime import datetime
import subprocess



def login():

    username = entry_username.get()
    password = entry_password.get()

    # Kiểm tra xem textbox có trống không
    if not username or not password:
        messagebox.showerror("Lỗi", f"Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
        return


    try:
        if check_credentials(username, password):

            role = get_role(username)

            if role == "giaoVien":

             change_teacher_page()
             label_class.pack()
             display_class_buttons_teacher(username)
             label_class_table.pack();
             display_class_buttons_table_teacher(username)



            else:
                # Hiển thị mã QR

                student_page(username)
                label_khoaHoc.pack()
                display_course_buttons(username)
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không chính xác.")
    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

def student_page(username):
    label_username.pack_forget()
    label_qr.pack()
    entry_username.pack_forget()
    label_password.pack_forget()
    entry_password.pack_forget()
    btn_logout_student.pack()
    btn_login.pack_forget()


def display_class_buttons_table_teacher(teacherID):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Truy vấn các lớp học mà giáo viên đang giảng dạy
        cursor.execute("SELECT Class.id, tenLop FROM Courses, Class WHERE Courses.lopID = Class.id AND Courses.IDgiangVien = ? GROUP BY tenLop", (teacherID,))
        classes = cursor.fetchall()

        # Tạo nút cho mỗi lớp học
        for class_info in classes:
            class_id, class_name = class_info
            button = tk.Button(root, text=class_name, command=lambda c=class_id: display_course_buttons_table_teacher(teacherID, c))
            button.pack()

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()

# Tạo biến để lưu trữ trạng thái của các nút môn học
course_buttons2 = {}

def display_course_buttons_table_teacher(teacher_id, class_id):
    global course_buttons2

    # Ẩn tất cả các nút môn học của các lớp khác
    for buttons in course_buttons2.values():
        for button in buttons:
            button.pack_forget()

    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        cursor.execute("SELECT Courses.id, Courses.tenMonHoc FROM Courses, Attendance, Class WHERE Courses.id = Attendance.courseID AND Courses.IDgiangVien = ? AND Courses.lopID = Class.id AND Class.id = ? GROUP BY Courses.tenMonHoc", (teacher_id, class_id))
        courses = cursor.fetchall()

        # Tạo nút cho mỗi môn học và lưu trữ chúng
        buttons = []
        for course_id, course_name in courses:
            button = tk.Button(root, text="Xem Excel "+course_name, command=lambda c=course_id: display_attendance_table(c), padx=25, pady=5, relief=tk.GROOVE)
            button.pack(pady=10, padx=10)
            buttons.append(button)

        course_buttons2[class_id] = buttons

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()

def display_attendance_table(courseID):
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Thực hiện truy vấn
        cursor.execute("SELECT MSSV, Courses.tenMonHoc, ngayDiemDanh, status FROM Attendance, Courses WHERE courseID =? AND ngayDiemDanh = ? AND Courses.id = Attendance.courseID", (courseID, current_date))
        attendance_data = cursor.fetchall()

        # Tạo cửa sổ mới
        window = tk.Toplevel()
        window.title("Attendance Information")

        # Tạo và hiển thị Treeview
        tree = ttk.Treeview(window)
        tree["columns"] = ( "MSSV", "Course", "Date", "Status")
        tree["show"] = "headings"
        tree.heading("MSSV", text="MSSV")
        tree.heading("Course", text="Môn học")
        tree.heading("Date", text="Ngày điểm danh")
        tree.heading("Status", text="Trạng thái")

        for row in attendance_data:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True)

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()
def change_teacher_page():
    btn_logout.pack(pady=10)

    label_khoaDay.pack()
    label_username.pack_forget()
    entry_username.pack_forget()
    label_password.pack_forget()
    entry_password.pack_forget()
    btn_login.pack_forget()


def logout_student():
    response = messagebox.askquestion("Xác nhận đăng xuất", "Bạn có chắc chắn muốn đăng xuất không?")

    if response == 'yes':
     for button in root.winfo_children():
      button.pack_forget()
     label_qr.config(image=None)
     label_qr.pack_forget()
     label_username.pack()
     entry_username.pack()

     label_password.pack()
     entry_password.pack()
     btn_logout_student.pack_forget()
     btn_login.pack();
     entry_username.delete(0, tk.END)
     entry_password.delete(0, tk.END)

def logout_teacher():
    response = messagebox.askquestion("Xác nhận đăng xuất", "Bạn có chắc chắn muốn đăng xuất không?")

    if response == 'yes':
     for button in root.winfo_children():
      button.pack_forget()
     btn_logout.pack_forget()

     label_khoaDay.pack_forget()
     label_username.pack()
     entry_username.pack()
     label_password.pack()
     entry_password.pack()
     btn_login.pack();
     entry_username.delete(0, tk.END)
     entry_password.delete(0, tk.END)
def export_to_excel(courseID):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect('sinhVien.db')
        df = pd.read_sql_query("SELECT Attendance.id, MSSV, Courses.tenMonHoc, ngayDiemDanh, status FROM Attendance, Courses WHERE courseID =? AND ngayDiemDanh = ? AND Courses.id = Attendance.courseID",  conn, params=(courseID, current_date))

        # Xuất dữ liệu vào một tệp Excel

        excel_filename = f"D:\\sinhVien_{current_date}_{get_course_name(courseID)}.xlsx"

        # Xuất dữ liệu vào một tệp Excel
        df.to_excel(excel_filename, index=False)

        messagebox.showinfo("Thông báo", "Xuất dữ liệu thành công vui lòng kiểm ổ đĩa D")


    except sqlite3.Error as e:
        messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi xuất dữ liệu ra file Excel: {e}")

    finally:
        if conn:
            conn.close()

def get_course_name(courseID):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()


        cursor.execute("SELECT tenMonHoc FROM Courses WHERE id = ?", (courseID,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            return "Unknown"

    except sqlite3.Error as e:
        print("Lỗi:", e)
        return "Unknown"

    finally:
        if conn:
            conn.close()

def get_class_name_teacher(classID):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()


        cursor.execute("SELECT tenLop FROM Class WHERE id = ?", (classID,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            return "Unknown"

    except sqlite3.Error as e:
        print("Lỗi:", e)
        return "Unknown"

    finally:
        if conn:
            conn.close()




def get_class_name_student(classID):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()


        cursor.execute("SELECT tenLop FROM Class WHERE id = ?", (classID,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            return "Unknown"

    except sqlite3.Error as e:
        print("Lỗi:", e)
        return "Unknown"

    finally:
        if conn:
            conn.close()





def get_role(username):
    try:

        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()


        cursor.execute("SELECT vaiTro FROM Users WHERE MSSV=?", (username,))
        row = cursor.fetchone()

        if row:
            return row[0]

    except sqlite3.Error as e:
        print("Lỗi kết nối đến cơ sở dữ liệu:", e)
        return None

    finally:
        # Đóng kết nối
        if conn:
            conn.close()



def check_credentials(username, password):
    try:

        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM Users WHERE MSSV=? AND password=?", (username, password))
        row = cursor.fetchone()

        return bool(row)

    except sqlite3.Error as e:
        print("Lỗi kết nối đến cơ sở dữ liệu:", e)
        return False

    finally:
        # Đóng kết nối
        if conn:
            conn.close()

def generate_qr(username,courseID):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = f"MSSV: {username}, course: {courseID}, NgayHienTai: {current_date}, ThoiGianHienTai:{current_time} "
            qr.add_data(data)
            qr.make(fit=True)
            # Tạo hình ảnh từ mã QR
            img = qr.make_image(fill_color="black", back_color="white")

            # Chuyển đổi hình ảnh thành đối tượng ImageTk
            img_tk = ImageTk.PhotoImage(img)

            # Hiển thị hình ảnh mã QR trên giao diện
            label_qr.config(image=img_tk)
            label_qr.image = img_tk

    except sqlite3.Error as e:
        print("Lỗi", e)
        messagebox.showerror("Lỗi", f"Lỗi ")
def display_class_buttons_teacher(teacherID):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Truy vấn các lớp học mà giáo viên đang giảng dạy
        cursor.execute("SELECT Class.id, tenLop FROM Courses, Class WHERE Courses.lopID = Class.id AND Courses.IDgiangVien = ? GROUP BY tenLop", (teacherID,))
        classes = cursor.fetchall()

        # Tạo nút cho mỗi lớp học
        for class_info in classes:
            class_id, class_name = class_info
            button = tk.Button(root, text=class_name, command=lambda c=class_id: display_course_buttons_teacher(teacherID, c))
            button.pack()

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()

# Tạo biến để lưu trữ trạng thái của các nút môn học
course_buttons = {}

def display_course_buttons_teacher(teacher_id, class_id):
    global course_buttons

    # Ẩn tất cả các nút môn học của các lớp khác
    for buttons in course_buttons.values():
        for button in buttons:
            button.pack_forget()

    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        cursor.execute("SELECT Courses.id, Courses.tenMonHoc FROM Courses, Attendance, Class WHERE Courses.id = Attendance.courseID AND Courses.IDgiangVien = ? AND Courses.lopID = Class.id AND Class.id = ? GROUP BY Courses.tenMonHoc", (teacher_id, class_id))
        courses = cursor.fetchall()

        # Tạo nút cho mỗi môn học và lưu trữ chúng
        buttons = []
        for course_id, course_name in courses:
            button = tk.Button(root, text=course_name, command=lambda c=course_id: export_to_excel(c), padx=25, pady=5, relief=tk.GROOVE)
            button.pack(pady=10, padx=10)
            buttons.append(button)

        course_buttons[class_id] = buttons

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()



def display_course_buttons(student_id):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()


        cursor.execute("SELECT Courses.id, tenMonHoc FROM Courses JOIN Attendance ON Courses.id = Attendance.courseID WHERE MSSV=? GROUP BY tenMonHoc", (student_id,))
        courses = cursor.fetchall()

        for course in courses:
            course_id, course_name = course
            button = tk.Button(root, text=course_name, command=lambda c=course_id: generate_qr(student_id, c))
            button.pack()

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()

def mark_attendance(username, course_id):
    print(f"Đánh dấu điểm danh cho sinh viên có MSSV {username} trong môn học có ID {course_id}")




def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
# Tạo cửa sổ giao diện
root = tk.Tk()
root.title("Ứng dụng đăng nhập và tạo mã QR")


# Tạo label và textbox đăng nhập và mật khẩu
label_class = tk.Label(root, text="Các lớp đang dạy hiện tại")
label_class_table = tk.Label(root, text="Xem danh sách trước khi xuất Excel")
label_username = tk.Label(root, text="Tên đăng nhập:")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()
label_khoaHoc = tk.Label(root, text="Các khoá học hiện tại")
label_khoaDay = tk.Label(root, text="Xuất Excel khoá học đang dạy hiện tại")
label_password = tk.Label(root, text="Mật khẩu:")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()
btn_logout = tk.Button(root, text="Đăng xuất",command=logout_teacher, padx=25, pady=5, relief=tk.GROOVE)
btn_logout_student = tk.Button(root, text="Đăng xuất",command=logout_student)
# Tạo nút "Đăng nhập" để kiểm tra và hiển thị mã QR
btn_login = tk.Button(root, text="Đăng nhập", command=login)
btn_login.pack()

btn_login.pack()
# Tạo label để hiển thị mã QR
label_qr = tk.Label(root)

label_qr.pack()

window_width = 600
window_height = 600
center_window(root, window_width, window_height)
# Chạy ứng dụng
root.mainloop()
