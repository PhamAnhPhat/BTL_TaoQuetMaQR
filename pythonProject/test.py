import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk
import sqlite3
import pandas as pd
from datetime import datetime

def login():
    # Lấy dữ liệu từ textbox đăng nhập và mật khẩu
    username = entry_username.get()
    password = entry_password.get()

    # Kiểm tra xem textbox có trống không
    if not username or not password:
        messagebox.showerror("Lỗi", f"Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
        return

    # Kiểm tra tên đăng nhập và mật khẩu từ cơ sở dữ liệu
    try:
        if check_credentials(username, password):
            # Lấy role từ database
            role = get_role(username)

            if role == "giaoVien":

             change_teacher_page()
             label_class.pack()
             display_class_buttons_teacher(username)
                # Hiển thị nút "Đăng xuất" và "Xuất excel"


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


def change_teacher_page():
    btn_logout.pack(pady=10)
    btn_reset_attendances.pack(pady=10)
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
     btn_reset_attendances.pack_forget()
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
        # Kết nối đến cơ sở dữ liệu SQLite và truy vấn dữ liệu từ các bảng
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

        # Truy vấn tên của môn học từ cơ sở dữ liệu
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

        # Truy vấn tên của môn học từ cơ sở dữ liệu
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

        # Truy vấn tên của môn học từ cơ sở dữ liệu
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




def get_role(username):
    try:
        # Kết nối đến cơ sở dữ liệu SQLite
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Truy vấn role của sinh viên
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

def reset_attendance():
    # Hiển thị hộp thoại xác nhận
    response = messagebox.askquestion("Xác nhận", "Bạn đã lưu dữ liệu của ngày hôm qua chưa?")

    # Nếu người dùng xác nhận
    if response=="yes":
        try:
            # Kết nối đến cơ sở dữ liệu SQLite và thực hiện cập nhật
            conn = sqlite3.connect('sinhVien.db')
            cursor = conn.cursor()

            cursor.execute("UPDATE Students SET attendance=?", (0,))
            conn.commit()

            messagebox.showinfo("Thông báo", "Đã đặt lại điểm danh thành công!.")

        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

        finally:
            if conn:
                conn.close()

def check_credentials(username, password):
    try:
        # Kết nối đến cơ sở dữ liệu SQLite
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Thực hiện truy vấn để kiểm tra tên đăng nhập và mật khẩu
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
    try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = f"MSSV: {username}, course: {courseID}, NgayHienTai: {current_date}"
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

def display_course_buttons_teacher(teacher_id, lopID):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Truy vấn các môn học mà giáo viên đang giảng dạy trong một lớp cụ thể
        cursor.execute("SELECT Courses.id, Courses.tenMonHoc FROM Courses, Attendance, Class WHERE Courses.id = Attendance.courseID AND Courses.IDgiangVien = ? AND Courses.lopID = Class.id AND Class.id=? GROUP BY Courses.tenMonHoc", (teacher_id, lopID))
        courses = cursor.fetchall()

        # Tạo nút cho mỗi môn học
        for course in courses:
            course_id, course_name = course
            button = tk.Button(root, text=course_name, command=lambda c=course_id: export_to_excel(c), padx=25, pady=5, relief=tk.GROOVE)
            button.pack(pady=10, padx=10)

    except sqlite3.Error as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()



def display_course_buttons(student_id):
    try:
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Truy vấn các môn học mà sinh viên đang tham gia
        cursor.execute("SELECT Courses.id, tenMonHoc FROM Courses JOIN Attendance ON Courses.id = Attendance.courseID WHERE MSSV=? GROUP BY tenMonHoc", (student_id,))
        courses = cursor.fetchall()

        # Tạo nút cho mỗi môn học
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
btn_reset_attendances = tk.Button(root, text="Reset ngày mới ", command=reset_attendance, padx=10, pady=5, relief=tk.GROOVE)
btn_login.pack()
# Tạo label để hiển thị mã QR
label_qr = tk.Label(root)

label_qr.pack()

window_width = 600
window_height = 600
center_window(root, window_width, window_height)
# Chạy ứng dụng
root.mainloop()
