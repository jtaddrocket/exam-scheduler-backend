#!/bin/bash
# Script tự động hóa một số bước deploy lên EC2

echo "=== Exam Scheduler Deployment Script ==="

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kiểm tra xem đang chạy với quyền root hay không
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}Warning: Đang chạy với quyền root. Một số lệnh sẽ cần quyền sudo.${NC}"
fi

# 1. Cập nhật hệ thống
echo -e "${GREEN}[1/8] Cập nhật hệ thống...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt dependencies
echo -e "${GREEN}[2/8] Cài đặt Python và các công cụ cần thiết...${NC}"
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# 3. Cấu hình PostgreSQL
echo -e "${GREEN}[3/8] Cấu hình PostgreSQL...${NC}"
echo "Vui lòng nhập password cho database user:"
read -s DB_PASSWORD

sudo -u postgres psql <<EOF
CREATE DATABASE exam_scheduler;
CREATE USER exam_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE exam_user SET client_encoding TO 'utf8';
ALTER ROLE exam_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE exam_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE exam_scheduler TO exam_user;
\q
EOF

# 4. Tạo virtual environment
echo -e "${GREEN}[4/8] Tạo virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# 5. Cài đặt Python packages
echo -e "${GREEN}[5/8] Cài đặt Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 6. Cấu hình .env
echo -e "${GREEN}[6/8] Cấu hình file .env...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Vui lòng chỉnh sửa file .env với các giá trị phù hợp!"
    echo "Đặc biệt là SECRET_KEY và DB_PASSWORD"
    nano .env
else
    echo "File .env đã tồn tại, bỏ qua..."
fi

# 7. Chạy migrations
echo -e "${GREEN}[7/8] Chạy database migrations...${NC}"
python manage.py migrate

# 8. Collect static files
echo -e "${GREEN}[8/8] Thu thập static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}=== Hoàn thành! ===${NC}"
echo "Các bước tiếp theo:"
echo "1. Tạo superuser: python manage.py createsuperuser"
echo "2. Cấu hình Gunicorn service (xem gunicorn.service.example)"
echo "3. Cấu hình Nginx (xem nginx.conf.example)"
echo "4. Khởi động services:"
echo "   sudo systemctl start exam-scheduler"
echo "   sudo systemctl enable exam-scheduler"
echo "   sudo systemctl restart nginx"
