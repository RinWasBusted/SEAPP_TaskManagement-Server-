# TỔNG QUAN VỀ DỰ ÁN

## 1. Hướng dẫn chạy dự án

### Bước 1 --- Clone dự án & tạo môi trường ảo

``` bash
python -m venv env/
```

### Bước 2 --- Kích hoạt môi trường ảo

-   **Linux/MacOS**

    ``` bash
    source env/bin/activate
    ```

-   **Windows**

    ``` bash
    env\Scripts\activate
    ```

### Bước 3 --- Cài đặt thư viện

``` bash
pip install -r requirements.txt
```

### Bước 4 --- Chạy dự án

-   Chạy database:

    ``` bash
    docker compose up -d
    ```

-   Chạy server:

    ``` bash
    python main.py
    ```

### Bước 5 --- Cập nhật gói đã cài

``` bash
pip freeze > requirements.txt
```

------------------------------------------------------------------------

## 2. Cấu trúc dự án (Tree View)

    SEAPP_TaskManagement-Server-
    │── main.py: File chạy chính của chương trình 
    │── requirements.txt
    │── .env                 
    │── template.py
    │── template.sh
    │
    └── src/
        │── api.py
        │── __init__.py
        │
        ├── config/
        │     └── Chứa các cấu hinfhc ho hệ thống 
        │
        ├── controllers/
        │     └── ...
        │
        ├── models/
        │     └── Nơi khai báo các Model cũng như biến db 
        │
        ├── middlewares/
        │     └── ...
        │
        └── services/
              └── Các hàm hỗ trợ logic 

------------------------------------------------------------------------

## 3. Hướng dẫn phát triển

### 3.1. Cập nhật cấu trúc dữ liệu (migrations)

``` bash
flask -A main.py db init
flask -A main.py db migrate
flask -A main.py db upgrade
```

### 3.2. Bật gợi ý trong Python (VSCode)

`Ctrl + Shift + P` → **Select Python Interpreter** → chọn `env/`

### 3.3. Gửi dữ liệu JSON trong Flask

``` python
return data, status_code
```

### 3.4. Tạo bảng không dùng class

``` python
team_member_association = db.Table('team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.team_id'), primary_key=True)
)
```

### 3.4. Caching và cache invalidation
-   Format key khi caching: `{resource}:{id}:{attribute}:{filter}` 
-   Ví dụ:
``` python
user:123                          // User entity
user:123:posts                    // User's posts
user:123:posts:published          // User's published posts only
user:123:profile                  // User profile
post:456                          // Post entity
post:456:comments                 // Post's comments
post:456:comments:approved        // Approved comments only
category:789:products             // Products in category
category:789:products:featured    // Featured products in category
```

------------------------------------------------------------------------

## 4. Xác thực đăng nhập

### 4.1. Luồng hoạt động

-   FE mở popup đăng nhập Google
-   OAuth xác thực
-   Google trả về: `id_token`, `access_token`, `code`
-   FE gửi dữ liệu xuống BE
-   BE verify token hoặc dùng `code` lấy token mới từ Google

------------------------------------------------------------------------

## Hướng 1: Xác thực qua JWT Token

-   BE nhận **id_token**
-   Verify JWT
-   Giải mã lấy thông tin người dùng

------------------------------------------------------------------------

## Hướng 2: Authorization Code (đang sử dụng)

### FE gọi login qua Google OAuth

``` js
const login = useGoogleLogin({
  onSuccess: (tokenResponse) => loginGoogleSuccess(tokenResponse),
  onError: (error) => loginGoogleFailed(error),
  flow: "auth-code",
  scope: "openid email profile",
});
```

### BE đổi code lấy access_token & id_token

``` python
def getToken(code):
    url = "https://oauth2.googleapis.com/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "code": code,
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_PUBLIC_KEY",
        "redirect_uri": "http://localhost:5173",
        "grant_type": "authorization_code"
    }
    r = requests.post(url, data=data, headers=headers)
    if r.status_code == 200:
        return r.json()
    return None
```

### BE đổi toke lấy thông tin người dùng 

```py
def getUserInfoFromToken(code): 
    print(code) 
    response_token_data = getToken(code) 
    print('Response token la: ' , response_token_data) 
    if response_token_data: 
        access_token = response_token_data.get('access_token') 
        if access_token: 
            headers = {"Authorization": f"Bearer {access_token}"}
            r = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
            if r.status_code == 200:
                return r.json()
            return None
        else: return None 
    else: 
        return None  
```

---
### Các endpoint quan trọng: 
/login: Khi người dùng đăng nhập thông qua email - password đã đăng kí   
/login-google: Khi người dùng đăng nhập qua cơ chế google, dùng cách xác thực trên   
/register: Dùng để đăng kí => Trả về 1 token cho FE   
/verify: FE dùng nó để tiếp tục verify cái đã đăng kí   

------------------------------------------------------------------------

## Lưu ý khi cấu hình OAuth Google

-   **CLIENT_ID** -- đăng ký trên Google Cloud
-   **CLIENT_SECRET** -- đăng ký trên Google Cloud
-   **REDIRECT_URI**
    -   Nếu **SPA** → URI của Frontend
    -   Nếu **SSR / Backend** → URI của Backend
-   Phải đăng ký Redirect URI trên Google Cloud Console

------------------------------------------------------------------------
Qua trinh xac thuc: 
Login by google: Verify -> FE 
Login by user name and email => Login 
Register by user name and email => Register => Gui 1 duong link de dan toi 1 trang FE Veirify, tren url co cai token => Nguoi dung mo trang nay ra => Trang Verify FE mo ra va luc nay ta se lum cai token o ben tren url => Gui request ve endpoint Verify => Tao tai khoan nguoi dung 

## 5. Một số mã lỗi 
308: Đường link tự động redirect sang dạng mới. Ví dụ: user thì tự biến thành user/ 
422: Thông tin cung cấp không đúng dạng hoặc không đầy đủ