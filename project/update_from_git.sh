#!/bin/bash
# Script để pull code từ GitHub và restart services
# Chạy: bash update_from_git.sh

set -e  # Dừng nếu có lỗi

echo "=== Updating code from GitHub ==="

# Đường dẫn đến project
PROJECT_DIR="/home/ubuntu/exam-scheduler-backend/project"
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Pull code mới nhất
echo "Pulling latest code..."
git pull origin main  # Hoặc master tùy branch của bạn

# Cài đặt dependencies mới (nếu có)
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Chạy migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn service
echo "Restarting Gunicorn service..."
sudo systemctl restart exam-scheduler

# Kiểm tra status
echo "Checking service status..."
sudo systemctl status exam-scheduler --no-pager -l

echo "=== Update completed! ==="
