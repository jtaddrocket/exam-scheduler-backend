# Bước tiếp theo sau khi tạo EC2 Instance

## Thông tin EC2 của bạn:
- **Public IP**: 52.207.251.97
- **Public DNS**: ec2-52-207-251-97.compute-1.amazonaws.com
- **Instance Type**: t2.micro
- **State**: Running

## Bước 1: Kết nối SSH vào EC2

### Trên Windows (PowerShell):

1. **Tìm file key (.pem)** mà bạn đã tải khi tạo EC2 instance
   - Thường ở thư mục Downloads
   - Tên file có thể là: `my-key.pem`, `exam-scheduler-key.pem`, v.v.

2. **Di chuyển file key vào thư mục dự án** (tùy chọn, nhưng khuyến nghị):
   ```powershell
   # Copy file .pem vào thư mục exam-scheduler
   Copy-Item "C:\Users\YourName\Downloads\your-key.pem" "E:\exam-scheduler\ec2-key.pem"
   ```

3. **Thiết lập quyền cho file key** (quan trọng):
   ```powershell
   # Trong PowerShell
   icacls "E:\exam-scheduler\ec2-key.pem" /inheritance:r
   icacls "E:\exam-scheduler\ec2-key.pem" /grant:r "$($env:USERNAME):(R)"
   ```

4. **Kết nối SSH**:
   ```powershell
   ssh -i "E:\exam-scheduler\ec2-key.pem" ubuntu@52.207.251.97
   ```
   
   **Lưu ý**: 
   - Nếu dùng Amazon Linux, thay `ubuntu` bằng `ec2-user`
   - Nếu lần đầu kết nối, gõ `yes` khi được hỏi

### Nếu gặp lỗi "Permission denied":
- Đảm bảo file .pem có quyền đọc đúng
- Kiểm tra username: `ubuntu` (Ubuntu) hoặc `ec2-user` (Amazon Linux)

## Bước 2: Cài đặt môi trường trên EC2

Sau khi kết nối SSH thành công, chạy các lệnh sau:

```bash
# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt Python và các công cụ cần thiết
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# 3. Kiểm tra phiên bản Python
python3 --version
```

## Bước 3: Cấu hình PostgreSQL

```bash
# Tạo database và user
sudo -u postgres psql

# Trong PostgreSQL shell, chạy các lệnh sau:
CREATE DATABASE exam_scheduler;
CREATE USER exam_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE exam_user SET client_encoding TO 'utf8';
ALTER ROLE exam_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE exam_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE exam_scheduler TO exam_user;
\q
```

**Lưu lại password** để dùng trong file `.env` sau này!

## Bước 4: Upload code lên EC2

### Cách 1: Sử dụng Git (Khuyến nghị)

Nếu code đã có trên GitHub:

```bash
# Trên EC2
cd /home/ubuntu
git clone https://github.com/your-username/exam-scheduler.git
cd exam-scheduler/project
```

### Cách 2: Sử dụng SCP từ máy local

Từ **PowerShell trên máy Windows** của bạn:

```powershell
# Upload toàn bộ thư mục project
scp -i "E:\exam-scheduler\ec2-key.pem" -r "E:\exam-scheduler\project" ubuntu@52.207.251.97:/home/ubuntu/exam-scheduler/
```

Hoặc nếu muốn upload từng file:

```powershell
# Tạo thư mục trên EC2 trước
ssh -i "E:\exam-scheduler\ec2-key.pem" ubuntu@52.207.251.97 "mkdir -p /home/ubuntu/exam-scheduler/project"

# Upload các file cần thiết
scp -i "E:\exam-scheduler\ec2-key.pem" -r "E:\exam-scheduler\project\*" ubuntu@52.207.251.97:/home/ubuntu/exam-scheduler/project/
```

## Bước 5: Cấu hình Django trên EC2

Sau khi code đã được upload, quay lại SSH và chạy:

```bash
# Di chuyển vào thư mục project
cd /home/ubuntu/exam-scheduler/project

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Bước 6: Tạo file .env

```bash
# Tạo file .env từ template
nano .env
```

Dán nội dung sau và **cập nhật các giá trị**:

```env
SECRET_KEY=your-new-secret-key-here-generate-random-string
DEBUG=False
ALLOWED_HOSTS=52.207.251.97,ec2-52-207-251-97.compute-1.amazonaws.com,localhost

DB_NAME=exam_scheduler
DB_USER=exam_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://your-username.github.io,http://localhost:3000
```

**Tạo SECRET_KEY mới**:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Lưu file: `Ctrl+O`, Enter, `Ctrl+X`

## Bước 7: Cập nhật settings.py để dùng .env

Bạn cần cập nhật `settings.py` để đọc từ file `.env`. 

**Tùy chọn nhanh**: Copy `settings_production.py.example` và chỉnh sửa, hoặc cập nhật `settings.py` hiện tại.

Tôi sẽ tạo script để tự động cập nhật settings.py cho bạn.

## Bước 8: Chạy migrations và collect static

```bash
# Đảm bảo đang trong virtual environment
source venv/bin/activate

# Chạy migrations
python manage.py migrate

# Tạo superuser (tùy chọn)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Bước 9: Test chạy Django (tạm thời)

```bash
# Chạy development server để test
python manage.py runserver 0.0.0.0:8000
```

**Quan trọng**: Trước khi test, cần mở port 8000 trong Security Group:
1. Vào AWS Console → EC2 → Security Groups
2. Chọn Security Group của instance
3. Inbound rules → Edit
4. Thêm rule: Custom TCP, Port 8000, Source: My IP
5. Save

Sau đó truy cập: `http://52.207.251.97:8000`

Nếu thấy trang Django, tắt server (`Ctrl+C`) và tiếp tục bước 10.

## Bước 10: Cấu hình Gunicorn

```bash
# Tạo thư mục log
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:www-data /var/log/gunicorn

# Tạo file service
sudo nano /etc/systemd/system/exam-scheduler.service
```

Dán nội dung:

```ini
[Unit]
Description=Exam Scheduler Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/exam-scheduler/project
ExecStart=/home/ubuntu/exam-scheduler/project/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/ubuntu/exam-scheduler/project/exam_scheduler.sock \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    project.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Lưu và khởi động:

```bash
sudo systemctl daemon-reload
sudo systemctl start exam-scheduler
sudo systemctl enable exam-scheduler
sudo systemctl status exam-scheduler
```

## Bước 11: Cấu hình Nginx

```bash
sudo nano /etc/nginx/sites-available/exam-scheduler
```

Dán nội dung:

```nginx
server {
    listen 80;
    server_name 52.207.251.97 ec2-52-207-251-97.compute-1.amazonaws.com;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /home/ubuntu/exam-scheduler/project/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/exam-scheduler/project/exam_scheduler.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Kích hoạt:

```bash
sudo ln -s /etc/nginx/sites-available/exam-scheduler /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Xóa default nếu có
sudo nginx -t  # Kiểm tra cấu hình
sudo systemctl restart nginx
```

## Bước 12: Kiểm tra kết quả

Truy cập: `http://52.207.251.97`

Nếu thấy trang web của bạn, **thành công!** 🎉

## Troubleshooting

### Nếu không truy cập được:

1. **Kiểm tra Security Group**:
   - Port 80 (HTTP) phải mở cho 0.0.0.0/0

2. **Kiểm tra logs**:
   ```bash
   # Gunicorn logs
   sudo journalctl -u exam-scheduler -f
   
   # Nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Kiểm tra services**:
   ```bash
   sudo systemctl status exam-scheduler
   sudo systemctl status nginx
   ```

4. **Kiểm tra permissions**:
   ```bash
   sudo chown -R ubuntu:www-data /home/ubuntu/exam-scheduler/project
   sudo chmod -R 755 /home/ubuntu/exam-scheduler/project
   ```

## Bước tiếp theo

Sau khi backend đã chạy, bạn có thể:
1. Deploy frontend lên GitHub Pages (xem `GITHUB_PAGES_SETUP.md`)
2. Cấu hình domain name (nếu có)
3. Cài đặt SSL với Let's Encrypt (xem `DEPLOY_GUIDE.md`)
