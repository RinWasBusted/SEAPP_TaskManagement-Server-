# TỔNG QUAN VỀ DỰ ÁN --- SEAPP Task Management Server

## 1. Hướng dẫn chạy dự án

### **B1. Clone dự án & tạo môi trường ảo**

`python -m env env/`

### **B2. Kích hoạt môi trường ảo**

-   Linux/MacOS: `source venv/bin/activate`\
-   Windows: `venv/Script/activate`

### **B3. Cài đặt thư viện**

`pip install -r requirements.txt`

### **B4. Chạy dự án**

`python main.py`

### **B5. Lưu lại thư viện đã cài**

`pip freeze > requirements.txt`

------------------------------------------------------------------------

## 2. 🧩 Tổng quan cấu trúc dự án

-   **main.py** -- File chính chạy app\
-   **src** -- Chứa toàn bộ mã nguồn
    -   **config** -- File cấu hình\
    -   **controllers** -- Các route API\
    -   **models** -- Làm việc với database\
    -   **middlewares** -- Xử lý request trung gian\
    -   **services** -- Logic xử lý\
    -   **api.py** -- Đăng ký Blueprint\
    -   **\_\_init\_\_.py** -- Tạo Flask app
-   **.env** -- Biến môi trường\
-   **template.py / template.sh** -- Script tạo cấu trúc thư mục

------------------------------------------------------------------------

## 4. 🗄️ Khởi động database

Trong file `.env`, chỉnh lại:

-   đường dẫn DB\
-   username\
-   password\
-   tên database

Khai báo các model trong file **Models.py** của thư mục **schema**.

### **Các lệnh migration**

    flask -A main.py db init
    flask -A main.py db migrate
    flask -A main.py db upgrade

Sau khi chạy, nếu hiện **Done** → mở MariaDB kiểm tra các bảng.

Nếu lỗi → xoá thư mục `migrations/` và chạy lại từ đầu.

Sau khi ORM thiết lập xong → chỉ cần chạy code, **không cần chạy lại
`db upgrade`**.

------------------------------------------------------------------------

## 5. 📚 Ghi chú dự án

### **5.1. Vấn đề import file**

Nếu import module trong **cùng package**, phải thêm dấu `.`:

-   **Đúng**:\
    `from .api import configure_api_bp`

-   **Sai**:\
    `from api import configure_api_bp`

Nếu import từ **ngoài package**, dùng tuyệt đối:

    from src.schemas.Models import User, Blog

Tránh kiểu:

    from ....src.schemas.Models import User , Blog

→ lỗi *attempted relative import beyond top-level package*.

------------------------------------------------------------------------
