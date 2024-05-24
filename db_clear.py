import sqlite3

# Mở kết nối đến cơ sở dữ liệu
conn = sqlite3.connect('face_recognition.db')
c = conn.cursor()

# Xóa tất cả dữ liệu từ các bảng
c.execute("DELETE FROM users")
c.execute("DELETE FROM face_images")
c.execute("DELETE FROM registration_times")
c.execute("DELETE FROM login_attempts")

# Commit các thay đổi
conn.commit()

# Đóng kết nối với cơ sở dữ liệu
conn.close()