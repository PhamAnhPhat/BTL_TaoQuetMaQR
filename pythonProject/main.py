import base64
import io
from datetime import datetime
import qrcode
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Route và view function cho trang đăng nhập
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_credentials(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        role = get_role(username)
        if role == 'sinhVien':
            # Truy vấn danh sách các khóa học của sinh viên và render template student.html
            conn = sqlite3.connect('sinhVien.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Courses.id, tenMonHoc FROM Courses JOIN Attendance ON Courses.id = Attendance.courseID WHERE MSSV=? GROUP BY tenMonHoc", (username,))
            courses = cursor.fetchall()
            conn.close()

            # Tạo danh sách các URL dữ liệu của các ảnh QR
            qr_code_urls = [generate_qr_code(username, course[0]) for course in courses]

            # Ghép cặp danh sách courses và qr_code_urls
            course_qr_pairs = zip(courses, qr_code_urls)

            return render_template('student.html', username=username, course_qr_pairs=course_qr_pairs)
        elif role == 'giaoVien':
            return render_template('teacher.html')
    return redirect(url_for('login'))



def generate_qr_code(username, course_id):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    # Tạo nội dung chuỗi cho mã QR
    qr_content =  f"MSSV: {username}, course: {course_id}, NgayHienTai: {current_date}, ThoiGianHienTai:{current_time} "

    # Tạo mã QR
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(qr_content)
    qr.make(fit=True)

    # Tạo ảnh từ mã QR dưới dạng io.BytesIO
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img_bytes = io.BytesIO()
    qr_img.save(qr_img_bytes, format='PNG')

    # Chuyển đổi ảnh QR thành URL dữ liệu
    qr_img_data = base64.b64encode(qr_img_bytes.getvalue()).decode()
    qr_img_url = f"data:image/png;base64,{qr_img_data}"

    # Trả về URL dữ liệu của ảnh QR
    return qr_img_url


def check_credentials(username, password):
    conn = sqlite3.connect('sinhVien.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE MSSV=? AND password=?", (username, password))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# Hàm lấy vai trò của người dùng dựa trên tên đăng nhập
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

if __name__ == '__main__':
    app.run(host='192.168.1.21', port=5000, debug=True)
