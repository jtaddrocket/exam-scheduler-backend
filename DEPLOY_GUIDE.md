# Hướng dẫn Deploy Exam Scheduler

## Phần 1: Deploy Backend Django lên EC2

### Bước 1: Chuẩn bị EC2 Instance

1. **Tạo EC2 Instance trên AWS:**
   - Đăng nhập vào AWS Console
   - Chọn EC2 → Launch Instance
   - Chọn Ubuntu 22.04 LTS (hoặc Amazon Linux 2023)
   - Chọn instance type: t2.micro (free tier) hoặc t3.small
   - Tạo hoặc chọn Key Pair (lưu file .pem)
   - Cấu hình Security Group:
     - SSH (22): Your IP
     - HTTP (80): 0.0.0.0/0
     - HTTPS (443): 0.0.0.0/0
     - Custom TCP (8000): 0.0.0.0/0 (tạm thời cho testing)

2. **Kết nối vào EC2:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

### Bước 2: Cài đặt môi trường trên EC2

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Python và pip
sudo apt install python3 python3-pip python3-venv -y

# Cài đặt PostgreSQL (thay vì SQLite cho production)
sudo apt install postgresql postgresql-contrib -y

# Cài đặt Nginx
sudo apt install nginx -y

# Cài đặt Git
sudo apt install git -y
```

### Bước 3: Cấu hình PostgreSQL

```bash
# Chuyển sang user postgres
sudo -u postgres psql

# Trong PostgreSQL shell:
CREATE DATABASE exam_scheduler;
CREATE USER exam_user WITH PASSWORD 'your_secure_password';
ALTER ROLE exam_user SET client_encoding TO 'utf8';
ALTER ROLE exam_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE exam_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE exam_scheduler TO exam_user;
\q
```

### Bước 4: Upload code lên EC2

**Cách 1: Sử dụng Git (Khuyến nghị)**

```bash
# Trên EC2
cd /home/ubuntu
git clone https://github.com/your-username/exam-scheduler.git
cd exam-scheduler/project
```

**Cách 2: Sử dụng SCP (từ máy local)**

```bash
# Từ máy local Windows PowerShell
scp -i your-key.pem -r project ubuntu@your-ec2-ip:/home/ubuntu/exam-scheduler/
```

### Bước 5: Cấu hình Django cho Production

1. **Cập nhật settings.py:**

Cần cập nhật file `project/settings.py` với các cấu hình production:
- DEBUG = False
- ALLOWED_HOSTS bao gồm domain/IP của EC2
- Database PostgreSQL
- Static files configuration
- Security settings

2. **Tạo file .env cho biến môi trường:**

```bash
# Trên EC2
cd /home/ubuntu/exam-scheduler/project
nano .env
```

Nội dung file .env:
```
SECRET_KEY=your-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com
DB_NAME=exam_scheduler
DB_USER=exam_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Bước 6: Cài đặt dependencies và migrate database

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
pip install psycopg2-binary  # Thêm vào requirements.txt

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Bước 7: Cấu hình Gunicorn

```bash
# Gunicorn đã có trong requirements.txt
# Tạo file systemd service
sudo nano /etc/systemd/system/exam-scheduler.service
```

Nội dung file service:
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
    project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Khởi động service:
```bash
sudo systemctl daemon-reload
sudo systemctl start exam-scheduler
sudo systemctl enable exam-scheduler
sudo systemctl status exam-scheduler
```

### Bước 8: Cấu hình Nginx

```bash
sudo nano /etc/nginx/sites-available/exam-scheduler
```

Nội dung:
```nginx
server {
    listen 80;
    server_name your-ec2-ip your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/exam-scheduler/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/exam-scheduler/project/exam_scheduler.sock;
    }
}
```

Kích hoạt site:
```bash
sudo ln -s /etc/nginx/sites-available/exam-scheduler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Bước 9: Cấu hình SSL với Let's Encrypt (Tùy chọn nhưng khuyến nghị)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Phần 2: Deploy Frontend lên GitHub Pages

### Bước 1: Tạo repository GitHub cho Frontend

1. Tạo repository mới trên GitHub (ví dụ: `exam-scheduler-frontend`)
2. Clone repository về máy local

### Bước 2: Tách Frontend từ Django Templates

Nếu bạn muốn tách frontend thành một ứng dụng riêng:

**Option A: Static HTML/CSS/JS (Đơn giản)**

1. Tạo thư mục frontend:
```bash
mkdir exam-scheduler-frontend
cd exam-scheduler-frontend
```

2. Copy các file HTML từ `templates/` và tạo cấu trúc:
```
exam-scheduler-frontend/
├── index.html
├── login.html
├── registrations.html
├── css/
│   └── style.css
├── js/
│   └── app.js
└── assets/
```

3. Cập nhật các file HTML để gọi API từ backend EC2:
```javascript
// Thay đổi base URL
const API_BASE_URL = 'http://your-ec2-ip';
// hoặc
const API_BASE_URL = 'https://your-domain.com';
```

**Option B: React/Vue/Angular (Nếu muốn framework)**

1. Tạo React app:
```bash
npx create-react-app exam-scheduler-frontend
cd exam-scheduler-frontend
```

2. Cấu hình API endpoint trong `.env`:
```
REACT_APP_API_URL=http://your-ec2-ip
```

3. Build và deploy:
```bash
npm run build
```

### Bước 3: Cấu hình GitHub Pages

1. **Tạo file `index.html`** (nếu dùng static files)

2. **Tạo file `.github/workflows/deploy.yml`** cho GitHub Actions:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build
        run: npm run build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
          # hoặc ./dist nếu dùng Vite
```

3. **Cấu hình GitHub Pages:**
   - Vào Settings → Pages
   - Source: Deploy from a branch → chọn `gh-pages`
   - Hoặc: GitHub Actions

### Bước 4: Cấu hình CORS trên Django Backend

Cần cấu hình CORS để frontend trên GitHub Pages có thể gọi API:

1. Cài đặt django-cors-headers:
```bash
pip install django-cors-headers
```

2. Thêm vào `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "https://your-username.github.io",
    "http://localhost:3000",  # Cho development
]

CORS_ALLOW_CREDENTIALS = True
```

### Bước 5: Deploy

```bash
# Commit và push code
git add .
git commit -m "Initial frontend deployment"
git push origin main
```

GitHub Actions sẽ tự động build và deploy lên GitHub Pages.

## Phần 3: Cấu hình Domain và DNS (Tùy chọn)

1. **Mua domain** (nếu có)
2. **Cấu hình DNS:**
   - A record: `@` → EC2 Public IP
   - CNAME: `www` → domain chính
   - CNAME: `frontend` → `your-username.github.io`

## Troubleshooting

### Backend không chạy:
```bash
# Kiểm tra logs
sudo journalctl -u exam-scheduler -f
sudo tail -f /var/log/nginx/error.log
```

### Frontend không kết nối được API:
- Kiểm tra CORS settings
- Kiểm tra Security Group trên EC2
- Kiểm tra firewall rules

### Static files không load:
```bash
# Kiểm tra permissions
sudo chown -R ubuntu:www-data /home/ubuntu/exam-scheduler/project/static
sudo chmod -R 755 /home/ubuntu/exam-scheduler/project/static
```

## Lưu ý bảo mật

1. **Không commit file .env lên Git**
2. **Sử dụng environment variables**
3. **Bật HTTPS với Let's Encrypt**
4. **Cập nhật Django và dependencies thường xuyên**
5. **Sử dụng strong SECRET_KEY**
6. **Cấu hình firewall đúng cách**
