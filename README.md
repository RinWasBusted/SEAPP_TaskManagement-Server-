# 📌 TỔNG QUAN VỀ DỰ ÁN --- SEAPP Task Management Server

## 1. 🚀 Hướng dẫn chạy dự án

### **B1. Clone dự án & tạo môi trường ảo**

``` bash
python -m env env/
```

### **B2. Kích hoạt môi trường ảo**

-   **Linux/MacOS:**\

``` bash
source venv/bin/activate
```

-   **Windows:**\

``` bash
venv/Script/activate
```

### **B3. Cài đặt thư viện**

``` bash
pip install -r requirements.txt
```

### **B4. Chạy dự án**

``` bash
python main.py
```

### **B5. Lưu lại thư viện đã cài**

``` bash
pip freeze > requirements.txt
```

------------------------------------------------------------------------

## 2. 🧩 Tổng quan cấu trúc dự án

    project/
    │── main.py              # File chạy chính
    │── .env                 # Biến môi trường
    │── template.py          # Script tạo cấu trúc folder
    │── template.sh          # Script tạo cấu trúc folder
    │
    └── src/
        │── __init__.py      # Khởi tạo Flask app + config
        │── api.py           # Đăng ký các blueprint
        │
        ├── config/          # File cấu hình
        ├── controllers/     # Khai báo API (Blueprints)
        ├── models/          # Tương tác DB
        ├── middlewares/     # Middleware xử lý request
        └── services/        # Logic nghiệp vụ

------------------------------------------------------------------------

## 3. 🗄️ Khởi động & thiết lập Database

### **Cấu hình trong file `.env`**

-   Sửa username\
-   Sửa password\
-   Sửa tên database\
-   Sửa địa chỉ kết nối nếu cần

### **Khai báo models**

Viết các class ORM trong:

    src/schemas/Models.py

### **Chạy migrations**

``` bash
flask -A main.py db init
flask -A main.py db migrate
flask -A main.py db upgrade
```

🔹 `db init` → chạy **1 lần duy nhất**\
🔹 `db migrate` → chạy khi thay đổi Models\
🔹 `db upgrade` → cập nhật DB thật

Nếu lỗi hoặc không update → xóa folder `migrations/` và làm lại.

Sau khi ORM đã setup xong:\
➡️ Bạn chỉ cần chạy code, SQLAlchemy sẽ tự động map dữ liệu, không cần
chạy lại `db upgrade` mỗi lần.

------------------------------------------------------------------------

## 4. 📚 Lưu ý quan trọng --- Import Modules

### **Import trong package**

Nếu đang import file trong **cùng một package**, phải có dấu `.`

**Ví dụ (đúng):**

``` python
from .api import configure_api_bp
```

**Sai:**

``` python
from api import configure_api_bp
```

### **Import tuyệt đối**

Khi import từ thư mục gốc `src/`:

**Ví dụ:**

``` python
from src.schemas.Models import User, Blog
```

Không dùng relative import kiểu:

``` python
from ....src.schemas.Models import User
```

→ Vì sẽ gây lỗi *"attempted relative import beyond top-level package"*

------------------------------------------------------------------------

## 5. 📝 Ghi chú thêm

-   Đảm bảo mọi thư mục đều có `__init__.py`
-   Dùng import tuyệt đối khi làm việc với Flask + cấu trúc module
-   Luôn đặt project root và chạy bằng:

``` bash
python main.py
```

hoặc

``` bash
python -m src.main
```

------------------------------------------------------------------------

✨ **Tài liệu này dành cho Dev khởi động dự án nhanh, rõ ràng và
modern.**
