# Hướng dẫn Auto Deploy từ GitHub lên EC2

Có 3 cách chính để tự động deploy khi push code lên GitHub:

## Cách 1: GitHub Actions (Khuyến nghị - Tự động hoàn toàn)

### Bước 1: Tạo GitHub Secrets

1. Vào GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Thêm các secrets sau:
   - `EC2_HOST`: IP của EC2 (ví dụ: `52.207.251.97`)
   - `EC2_USER`: Username SSH (ví dụ: `ubuntu`)
   - `EC2_SSH_KEY`: Nội dung file `.pem` key (copy toàn bộ nội dung)

### Bước 2: File workflow đã được tạo

File `.github/workflows/deploy-ec2.yml` đã được tạo sẵn. Chỉ cần:

1. **Commit và push** file workflow lên GitHub
2. **Mỗi lần push vào branch `main`**, GitHub Actions sẽ tự động:
   - SSH vào EC2
   - Pull code mới nhất
   - Cài dependencies
   - Chạy migrations
   - Collect static files
   - Restart Gunicorn service

### Bước 3: Kiểm tra

- Vào tab **Actions** trên GitHub để xem logs
- Nếu có lỗi, sẽ hiển thị trong logs

## Cách 2: GitHub Webhook (Tự động với webhook)

### Bước 1: Setup webhook listener trên EC2

```bash
# Upload file setup_auto_deploy.sh lên EC2
scp -i your-key.pem setup_auto_deploy.sh ubuntu@your-ec2-ip:/home/ubuntu/

# SSH vào EC2 và chạy
ssh -i your-key.pem ubuntu@your-ec2-ip
bash setup_auto_deploy.sh
```

### Bước 2: Cấu hình webhook secret

```bash
nano /home/ubuntu/webhook_listener.py
# Thay đổi WEBHOOK_SECRET thành một chuỗi ngẫu nhiên
```

### Bước 3: Khởi động webhook listener

```bash
sudo systemctl start webhook-listener
sudo systemctl enable webhook-listener
```

### Bước 4: Mở port trong Security Group

- Vào AWS Console → EC2 → Security Groups
- Thêm rule: **Custom TCP**, Port **9000**, Source: **0.0.0.0/0** (hoặc chỉ GitHub IPs)

### Bước 5: Cấu hình GitHub Webhook

1. Vào GitHub repository → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `http://your-ec2-ip:9000`
3. **Content type**: `application/json`
4. **Secret**: Giống với WEBHOOK_SECRET trong webhook_listener.py
5. **Events**: Chọn **Just the push event**
6. **Active**: ✓
7. Click **Add webhook**

### Bước 6: Test

Push code lên GitHub và kiểm tra:
```bash
sudo journalctl -u webhook-listener -f
```

## Cách 3: Pull thủ công (Đơn giản nhất)

### Sử dụng script update

```bash
# Trên EC2
cd /home/ubuntu/exam-scheduler-backend/project
bash update_from_git.sh
```

Hoặc tạo alias để dễ nhớ:
```bash
echo 'alias deploy="cd /home/ubuntu/exam-scheduler-backend/project && bash update_from_git.sh"' >> ~/.bashrc
source ~/.bashrc

# Sau đó chỉ cần gõ:
deploy
```

### Pull thủ công từng bước

```bash
cd /home/ubuntu/exam-scheduler-backend/project
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart exam-scheduler
```

## Cách 4: Cron Job (Tự động check định kỳ)

Tự động pull code mỗi X phút:

```bash
# Chỉnh sửa crontab
crontab -e

# Thêm dòng này (check mỗi 5 phút):
*/5 * * * * cd /home/ubuntu/exam-scheduler-backend/project && git fetch && [ $(git rev-parse HEAD) != $(git rev-parse origin/main) ] && bash update_from_git.sh >> /var/log/auto-deploy.log 2>&1
```

## So sánh các cách

| Cách | Ưu điểm | Nhược điểm |
|------|---------|------------|
| **GitHub Actions** | ✅ Tự động hoàn toàn<br>✅ Logs trên GitHub<br>✅ Dễ debug | ⚠️ Cần setup secrets<br>⚠️ Tốn GitHub Actions minutes |
| **Webhook** | ✅ Tự động ngay lập tức<br>✅ Không tốn GitHub Actions | ⚠️ Cần mở port<br>⚠️ Cần setup webhook listener |
| **Pull thủ công** | ✅ Đơn giản<br>✅ Kiểm soát được | ❌ Phải SSH vào mỗi lần |
| **Cron Job** | ✅ Tự động<br>✅ Không cần setup phức tạp | ⚠️ Có độ trễ<br>⚠️ Tốn tài nguyên |

## Khuyến nghị

- **Development**: Dùng cách 3 (pull thủ công)
- **Production**: Dùng cách 1 (GitHub Actions) hoặc cách 2 (Webhook)

## Troubleshooting

### GitHub Actions không chạy
- Kiểm tra secrets đã đúng chưa
- Kiểm tra file workflow có syntax đúng không
- Xem logs trong tab Actions

### Webhook không hoạt động
- Kiểm tra port 9000 đã mở chưa
- Kiểm tra service: `sudo systemctl status webhook-listener`
- Xem logs: `sudo journalctl -u webhook-listener -f`

### Pull code bị conflict
- Backup trước khi pull: `git stash`
- Hoặc reset về remote: `git fetch && git reset --hard origin/main`
