# TỔNG QUAN VỀ DỰ ÁN 
## 1. Hướng dẫn chạy dự án 
B1. Clone dự án về máy và khởi tạo môi trường ảo mới 
`python -m env env/` 

B2. Khởi tạo môi trường ảo 
- Linux/MacOS: `source venv/bin/activate`
- Windows: `venv/Script/activate`

B3. Cài đặt các gói cần thiết: 
`pip install -r requirements.txt`

B4. Chạy dự án 
- Chạy database: `docker compose up -d` (Đã cài docker)
- Chạy server: `python main.py`

B5. Sau khi code và chỉnh sử dự án, nhớ lưu lại các gói đã cài thêm vào file requirements.txt 
`pip freeze > requirements.txt`

## 2. Tổng quan về dự án 
- main.py: File chính để chạy app  
- src: Thư mục chứa mã nguồn 
    + config: Chứa các file cấu hình dự án 
    + controllers: Chứa các đường dẫn api 
    + models: Thao tác với database 
    + middlewares: Các hàm xử lí middleware (nếu có) 
    + serives: Các hàm hỗ trợ logic 
    + api.py: Đăng kí cho tất cả blueprints
    + __init__.py: Khai báo biến app, chạy các cấu hình cần thiết 
- .env: Biến môi trường 
- template.py: Tạo folder structure
- template.sh: Tạo folder structure # SEAPP_TaskManagement-Server-


## 3. Chú ý khi phát triển

### 1. Cập nhật cấu trúc bảng trong database

Khi thay đổi cấu trúc các models của database thì cần lưu các thay đổi vào folder migrations và cập nhật lên database

```
flask -A main.py db init	Tạo hệ thống migration (làm 1 lần)
flask -A main.py db migrate	Tạo file migration khi model thay đổi (Các lần sau có chạy lại cũng không bị mất dữ liệu)
flask -A main.py db upgrade: Cập nhật dữ liệu xuống database theo file migration 
```