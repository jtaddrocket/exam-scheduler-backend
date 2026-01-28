#!/usr/bin/env python3
"""
Script để tạo file .env từ .env.example
Chạy: python create_env.py
"""

import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_EXAMPLE = BASE_DIR / '.env.example'
ENV_FILE = BASE_DIR / '.env'

def generate_secret_key():
    """Tạo Django secret key mới"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

def main():
    if ENV_FILE.exists():
        response = input(f"File .env đã tồn tại. Bạn có muốn ghi đè? (y/N): ")
        if response.lower() != 'y':
            print("Hủy bỏ.")
            return
    
    # Đọc template
    if ENV_EXAMPLE.exists():
        with open(ENV_EXAMPLE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # Tạo template mặc định nếu không có .env.example
        content = """# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com,localhost

# Database Configuration (PostgreSQL)
DB_NAME=exam_scheduler
DB_USER=exam_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# CORS Settings (for frontend on GitHub Pages)
CORS_ALLOWED_ORIGINS=https://your-username.github.io,http://localhost:3000
"""
    
    # Thay thế SECRET_KEY
    if '{secret_key}' in content:
        secret_key = generate_secret_key()
        content = content.replace('{secret_key}', secret_key)
    elif 'SECRET_KEY=your-secret-key-here' in content:
        secret_key = generate_secret_key()
        content = content.replace('SECRET_KEY=your-secret-key-here', f'SECRET_KEY={secret_key}')
    
    # Ghi file
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã tạo file .env tại: {ENV_FILE}")
    print("\n⚠️  QUAN TRỌNG: Vui lòng chỉnh sửa file .env và cập nhật:")
    print("   - ALLOWED_HOSTS: Thêm IP/domain của EC2")
    print("   - DB_PASSWORD: Đặt password cho database")
    print("   - CORS_ALLOWED_ORIGINS: Thêm URL frontend GitHub Pages")
    print(f"\nChạy lệnh để chỉnh sửa: nano {ENV_FILE}")

if __name__ == '__main__':
    main()
