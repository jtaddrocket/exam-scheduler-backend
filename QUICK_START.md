# Quick Start - Deploy Exam Scheduler

## Tóm tắt nhanh

### Backend trên EC2 (Django)

1. **Tạo EC2 Instance** (Ubuntu 22.04, t2.micro)
2. **SSH vào EC2**: `ssh -i key.pem ubuntu@ec2-ip`
3. **Chạy script tự động** (tùy chọn):
   ```bash
   chmod +x deploy_scripts.sh
   ./deploy_scripts.sh
   ```
4. **Hoặc làm thủ công**:
   - Cài đặt: Python, PostgreSQL, Nginx, Git
   - Clone code: `git clone your-repo`
   - Tạo `.env` từ `.env.example`
   - Cài đặt dependencies: `pip install -r requirements.txt`
   - Migrate: `python manage.py migrate`
   - Collect static: `python manage.py collectstatic`
   - Cấu hình Gunicorn (xem `gunicorn.service.example`)
   - Cấu hình Nginx (xem `nginx.conf.example`)
   - Khởi động services

### Frontend trên GitHub Pages

1. **Tạo repository mới** trên GitHub
2. **Chọn một trong các cách**:
   - **Static HTML**: Copy templates, tạo API client
   - **React**: `npx create-react-app`, cấu hình GitHub Actions
   - **Vue**: `vue create`, cấu hình tương tự
3. **Enable GitHub Pages** trong Settings
4. **Cập nhật API endpoint** trong frontend code

## File quan trọng

- `DEPLOY_GUIDE.md` - Hướng dẫn chi tiết đầy đủ
- `GITHUB_PAGES_SETUP.md` - Hướng dẫn setup frontend
- `project/.env.example` - Template cho biến môi trường
- `project/nginx.conf.example` - Cấu hình Nginx
- `project/gunicorn.service.example` - Cấu hình Gunicorn service
- `project/settings_production.py.example` - Settings cho production

## Checklist

### Backend EC2
- [ ] EC2 instance đã tạo và có Security Group đúng
- [ ] PostgreSQL đã cài và cấu hình database
- [ ] File `.env` đã tạo với các giá trị đúng
- [ ] Dependencies đã cài đặt
- [ ] Database migrations đã chạy
- [ ] Static files đã collect
- [ ] Gunicorn service đã cấu hình và chạy
- [ ] Nginx đã cấu hình và chạy
- [ ] SSL certificate đã cài (Let's Encrypt) - Tùy chọn

### Frontend GitHub Pages
- [ ] Repository đã tạo
- [ ] Code frontend đã upload
- [ ] API endpoint đã cấu hình đúng
- [ ] GitHub Pages đã enable
- [ ] CORS đã cấu hình trên backend

### Bảo mật
- [ ] SECRET_KEY đã thay đổi
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS đã cấu hình đúng
- [ ] File `.env` không commit lên Git
- [ ] HTTPS đã bật (nếu có domain)

## Liên kết hữu ích

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Let's Encrypt](https://letsencrypt.org/)
