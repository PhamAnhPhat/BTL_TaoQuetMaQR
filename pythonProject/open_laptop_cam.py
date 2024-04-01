from datetime import datetime

import cv2
from pyzbar.pyzbar import decode
import sqlite3
from PIL import ImageGrab
import numpy as np
def check_student_id(student_id):
    try:
        # Kết nối đến cơ sở dữ liệu SQLite
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Thực hiện truy vấn để kiểm tra mã sinh viên trong cơ sở dữ liệu
        cursor.execute("SELECT * FROM Users WHERE MSSV=?", (student_id,))
        row = cursor.fetchone()

        if row:
            return True
        else:
            return False

    except sqlite3.Error as e:
        print("Lỗi kết nối đến cơ sở dữ liệu:", e)
        return False

    finally:
        # Đóng kết nối
        if conn:
            conn.close()

def update_student_status(student_id,courseID):
    try:
        # Kết nối đến cơ sở dữ liệu SQLite
        conn = sqlite3.connect('sinhVien.db')
        cursor = conn.cursor()

        # Lấy ngày hiện tại
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Kiểm tra xem có dữ liệu trùng lặp hay không
        cursor.execute("SELECT * FROM Attendance WHERE MSSV=? AND courseID=? AND ngayDiemDanh=?",
                       (student_id, courseID, current_date))
        existing_data = cursor.fetchone()

        if existing_data:
            # Nếu đã có dữ liệu, thực hiện cập nhật
            cursor.execute("UPDATE Attendance SET status=? WHERE MSSV=? AND courseID=? AND ngayDiemDanh=?",
                           (1, student_id, courseID, current_date))
        else:
            # Nếu chưa có dữ liệu, thực hiện chèn mới
            cursor.execute(
                "INSERT INTO Attendance (MSSV, courseID, ngayDiemDanh, status) VALUES (?, ?, ?, ?)",
                (student_id, courseID, current_date, 1))

        conn.commit()

    except sqlite3.Error as e:
        print("Lỗi cập nhật cơ sở dữ liệu:", e)

    finally:
        # Đóng kết nối
        if conn:
            conn.close()

def extract_mssv_from_qr_data(qr_data):
    # Split dữ liệu từ mã QR bằng dấu phẩy
    qr_parts = qr_data.split(", ")

    # Lặp qua từng phần tử trong qr_parts để tìm và lấy ra MSSV và courseID
    mssv = None
    courseID = None
    for part in qr_parts:
        # Nếu phần tử bắt đầu bằng "MSSV: ", lấy MSSV bằng cách loại bỏ phần "MSSV: "
        if part.startswith("MSSV: "):
            mssv = part.split(": ")[1]
        # Nếu phần tử bắt đầu bằng "course: ", lấy courseID bằng cách loại bỏ phần "course: "
        elif part.startswith("course: "):
            courseID = part.split(": ")[1]

    return mssv, courseID

# Kết nối đến webcam
cap = cv2.VideoCapture(0)

# while True:
#     # Đọc frame từ webcam
#     ret, frame = cap.read()
#
#     # Tìm mã QR trong frame
#     qr_codes = decode(frame)
#
#     # Hiển thị frame
#     cv2.imshow('QR Code Scanner', frame)
#
#     # Kiểm tra dữ liệu quét với cơ sở dữ liệu
#     if qr_codes:
#         for qr_code in qr_codes:
#             qr_data = qr_code.data.decode('utf-8')
#             mssv = extract_mssv_from_qr_data(qr_data)
#             if check_student_id(mssv):
#                 update_student_status(mssv)
#                 print("True")
#             else:
#                 print("False")
#
#     # Thoát khỏi vòng lặp khi nhấn phím 'q'
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Giải phóng webcam và đóng cửa sổ
# cap.release()
# cv2.destroyAllWindows()

while True:
    # Chụp màn hình
    screen = np.array(ImageGrab.grab(bbox=(0, 0, 800, 600)))
    qr_codes = decode(screen)

    # Tìm mã QR trong màn hình đã chụp
    qr_codes = decode(screen)

    # Hiển thị màn hình
    cv2.imshow('Screen', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))

    # Thực hiện xử lý cho mã QR nếu có
    if qr_codes:
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8')
            mssv, courseID = extract_mssv_from_qr_data(qr_data)
            print("MSSV:", mssv)
            print("courseID:", courseID)
            if check_student_id(mssv):
                update_student_status(mssv,courseID)
                print("True")
            else:
                print("False")

    # Thoát khỏi vòng lặp khi nhấn phím 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Đóng cửa sổ
cv2.destroyAllWindows()