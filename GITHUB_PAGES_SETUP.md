# Hướng dẫn Setup Frontend trên GitHub Pages

## Tùy chọn 1: Static HTML/CSS/JS (Đơn giản nhất)

### Bước 1: Tạo repository mới trên GitHub

1. Tạo repository mới: `exam-scheduler-frontend`
2. Clone về máy local:
```bash
git clone https://github.com/your-username/exam-scheduler-frontend.git
cd exam-scheduler-frontend
```

### Bước 2: Tạo cấu trúc thư mục

```
exam-scheduler-frontend/
├── index.html
├── login.html
├── registrations.html
├── css/
│   └── style.css
├── js/
│   └── api.js
└── README.md
```

### Bước 3: Tạo file `js/api.js`

```javascript
// Cấu hình API endpoint
const API_BASE_URL = 'http://your-ec2-ip'; // Hoặc domain của bạn
// const API_BASE_URL = 'https://your-domain.com';

// Helper function để gọi API
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Để gửi cookies nếu cần
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Export các hàm API
const API = {
    // Authentication
    login: (username, password) => {
        return apiCall('/login/', 'POST', { username, password });
    },
    
    logout: () => {
        return apiCall('/logout/', 'POST');
    },
    
    // Registrations
    getRegistrations: () => {
        return apiCall('/registrations/');
    },
    
    register: (sid) => {
        return apiCall(`/register/${sid}/`, 'POST');
    },
    
    unregister: (sid) => {
        return apiCall(`/unregister/${sid}/`, 'POST');
    },
    
    // Generate schedule
    generate: (data) => {
        return apiCall('/generate/', 'POST', data);
    }
};

// Export để sử dụng trong các file HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
```

### Bước 4: Cập nhật HTML để sử dụng API

Ví dụ trong `index.html`:

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exam Scheduler</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="app">
        <!-- Nội dung của bạn -->
    </div>
    
    <script src="js/api.js"></script>
    <script>
        // Sử dụng API
        API.getRegistrations()
            .then(data => {
                console.log('Registrations:', data);
                // Cập nhật UI
            })
            .catch(error => {
                console.error('Error:', error);
            });
    </script>
</body>
</html>
```

### Bước 5: Enable GitHub Pages

1. Vào Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` (hoặc `master`)
4. Folder: `/ (root)`
5. Save

Frontend sẽ có sẵn tại: `https://your-username.github.io/exam-scheduler-frontend/`

## Tùy chọn 2: React App (Nếu muốn dùng framework)

### Bước 1: Tạo React App

```bash
npx create-react-app exam-scheduler-frontend
cd exam-scheduler-frontend
```

### Bước 2: Cài đặt dependencies

```bash
npm install axios  # Hoặc fetch API
```

### Bước 3: Tạo file `.env`

```
REACT_APP_API_URL=http://your-ec2-ip
```

### Bước 4: Tạo API service

`src/services/api.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true, // Để gửi cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;
```

### Bước 5: Cấu hình GitHub Actions

Tạo file `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          REACT_APP_API_URL: ${{ secrets.REACT_APP_API_URL }}
      
      - name: Setup Pages
        uses: actions/configure-pages@v3
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: './build'
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

### Bước 6: Cấu hình package.json

Thêm vào `package.json`:

```json
{
  "homepage": "https://your-username.github.io/exam-scheduler-frontend",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

### Bước 7: Deploy

```bash
git add .
git commit -m "Initial React app setup"
git push origin main
```

GitHub Actions sẽ tự động build và deploy.

## Tùy chọn 3: Vue.js App

Tương tự như React, nhưng sử dụng Vue CLI:

```bash
npm install -g @vue/cli
vue create exam-scheduler-frontend
cd exam-scheduler-frontend
```

Cấu hình tương tự như React, nhưng build output sẽ là `dist/` thay vì `build/`.

## Lưu ý quan trọng

1. **CORS Configuration**: Đảm bảo backend Django đã cấu hình CORS đúng cách
2. **HTTPS**: GitHub Pages sử dụng HTTPS, nên backend cũng nên có HTTPS
3. **API Endpoint**: Cập nhật API_BASE_URL trong frontend code
4. **Environment Variables**: Sử dụng GitHub Secrets cho sensitive data

## Troubleshooting

### CORS Error
- Kiểm tra CORS_ALLOWED_ORIGINS trong Django settings
- Đảm bảo đã cài django-cors-headers
- Kiểm tra middleware order

### API không kết nối được
- Kiểm tra Security Group trên EC2
- Kiểm tra firewall rules
- Kiểm tra domain/IP có đúng không
