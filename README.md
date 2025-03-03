# 會員系統 Member System

這是一個使用 Flask 和 MongoDB 建立的會員系統，支持本地註冊和 Google OAuth 登入。

## 功能特點

- 用戶註冊與登入
  - 本地帳號註冊
  - Google 帳號登入
  - 密碼強度驗證
  - 驗證碼功能
- 會員管理
  - 會員資料儲存
  - 會員狀態追蹤
- 安全性
  - HTTPS 支援
  - Session 管理
  - 密碼驗證
  - 驗證碼防護

## 技術棧

- **後端框架**: Flask 2.0.1
- **資料庫**: MongoDB
- **認證**: Google OAuth 2.0
- **部署**: Heroku
- **其他工具**:
  - Gunicorn (WSGI HTTP Server)
  - python-dotenv (環境變數管理)
  - Pillow (驗證碼生成)

## 安裝指南

1. 克隆專案：
```bash
git clone https://github.com/your-username/member_system.git
cd member_system
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 設置環境變數：
   - 複製 `.env.example` 到 `.env`
   - 填入你的環境變數
   - 複製 `client_secret.example.json` 到 `client_secret.json`
   - 填入你的 Google OAuth 憑證

4. 運行應用：
```bash
python app.py
```

## 專案結構

```
member_system/
├── app.py                 # 主應用程式
├── public/               # 靜態文件
│   ├── js/              # JavaScript 文件
│   ├── images/          # 圖片文件
│   └── style.css        # CSS 樣式
├── templates/           # HTML 模板
│   ├── index.html      # 首頁
│   ├── login.html      # 登入頁面
│   ├── register.html   # 註冊頁面
│   ├── member.html     # 會員頁面
│   └── error.html      # 錯誤頁面
└── requirements.txt     # Python 依賴
```

## 環境要求

- Python 3.11.11
- MongoDB
- Google OAuth 2.0 憑證

## 環境變數

在 `.env` 文件中設置以下環境變數：

```
MONGODB_URI=your_mongodb_uri
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FLASK_SECRET_KEY=your_secret_key
OAUTH_REDIRECT_URI=your_oauth_redirect_uri
```

## 部署

### Heroku 部署

1. 安裝 Heroku CLI
2. 登入 Heroku
```bash
heroku login
```

3. 創建 Heroku 應用
```bash
heroku create your-app-name
```

4. 設置環境變數
```bash
heroku config:set MONGODB_URI="your_mongodb_uri"
heroku config:set GOOGLE_CLIENT_ID="your_google_client_id"
heroku config:set GOOGLE_CLIENT_SECRET="your_google_client_secret"
heroku config:set FLASK_SECRET_KEY="your_secret_key"
heroku config:set OAUTH_REDIRECT_URI="your_oauth_redirect_uri"
```

5. 部署
```bash
git push heroku main
```

## 開發者

- [Your Name](https://github.com/your-username)

## 授權

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 注意事項

- 請勿將敏感資訊（如 `.env` 和 `client_secret.json`）提交到版本控制系統
- 在生產環境中請確保啟用 HTTPS
- 定期更新依賴包以修補安全漏洞

