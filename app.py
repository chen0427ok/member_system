from flask import *
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json
from datetime import datetime
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
from dotenv import load_dotenv
#push to github
# 在文件開頭添加這行
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # 允許在本地使用 HTTP
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'   # 添加這行，放寬 token scope 限制

# 修改 Google OAuth 設置部分
GOOGLE_CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile']

# 添加這些設置
CLIENT_SECRETS_FILE = "client_secret.json"

# 載入環境變數
load_dotenv()

# 使用環境變數
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
MONGODB_URI = os.getenv('MONGODB_URI')
OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI')

# Flask app setup
app = Flask(__name__, 
    static_url_path='',  # 修改這裡
    static_folder='public'  # 確保這個路徑正確
)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = True  # 只在 HTTPS 下發送 cookie
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 JavaScript 訪問 cookie
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # session 過期時間（秒）

# 設置日誌
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# MongoDB setup
client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi('1'),
    tls=True,
    tlsAllowInvalidCertificates=True
)

try:
    # 測試連接
    client.admin.command('ping')
    print("MongoDB 連接成功！")
    
    # 設置資料庫和集合
    db = client.get_database('member_system')
    collection = db.get_collection('members')
    
    # 檢查是否需要創建索引
    existing_indexes = collection.list_indexes()
    has_username_index = False
    
    for index in existing_indexes:
        if 'username_1' in index['name']:
            has_username_index = True
            break
    
    if not has_username_index:
        collection.create_index([("username", 1)], unique=True)
        
except Exception as e:
    print(f"MongoDB 連接錯誤: {str(e)}")

# 添加安全相關設置
if os.environ.get('FLASK_ENV') == 'production':
    from flask_talisman import Talisman
    Talisman(app, force_https=True)

# Google OAuth route
@app.route('/google_login')
def google_login():
    try:
        session.clear()
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=OAUTH_REDIRECT_URI
        )
        
        # 確保使用 HTTPS
        if not request.is_secure and not app.debug:
            return redirect(request.url.replace('http://', 'https://', 1))
            
        # 生成 state 並儲存到 session
        state = os.urandom(16).hex()
        session['oauth_state'] = state
        
        authorization_url, flow_state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=state  # 使用我們生成的 state
        )
        
        print(f"Generated state: {state}")  # 調試用
        return redirect(authorization_url)
    except Exception as e:
        print(f"Google 登入錯誤: {str(e)}")
        return redirect('/error?message=無法啟動 Google 登入，請稍後再試')

@app.route('/oauth2callback')
def oauth2callback():
    try:
        # 驗證 state
        received_state = request.args.get('state')
        stored_state = session.get('oauth_state')
        
        print(f"Received state: {received_state}")  # 調試用
        print(f"Stored state: {stored_state}")      # 調試用
        
        if not received_state or not stored_state or received_state != stored_state:
            print("State 驗證失敗")  # 調試用
            session.clear()
            return redirect('/error?message=安全驗證失敗，請重新登入')
        
        # 清除已使用的 state
        session.pop('oauth_state', None)
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=received_state
        )
        flow.redirect_uri = OAUTH_REDIRECT_URI
        
        # 確保使用 HTTPS
        authorization_response = request.url
        if request.url.startswith('http:'):
            authorization_response = 'https://' + request.url[7:]
        
        try:
            flow.fetch_token(authorization_response=authorization_response)
        except Exception as e:
            print(f"Token 獲取錯誤: {str(e)}")
            session.clear()
            return redirect('/error?message=授權失敗，請重新登入')
        
        try:
            credentials = flow.credentials
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0])
            
            if not email:
                session.clear()
                return redirect('/error?message=無法獲取 Email，請確認 Google 帳號設置')
            
            # 檢查或創建用戶
            try:
                # 先用 email 查找用戶
                user = collection.find_one({'email': email})
                if not user:
                    # 檢查用戶名是否已存在
                    existing_user = collection.find_one({'username': name})
                    if existing_user:
                        # 如果用戶名已存在，加上隨機數字
                        from random import randint
                        name = f"{name}{randint(1, 9999)}"
                    
                    # 創建新用戶
                    collection.insert_one({
                        'username': name,
                        'email': email,
                        'password': None,
                        'oauth_type': 'google'
                    })
                    user = {'username': name}
                
                # 設置 session
                session.clear()
                session['username'] = user['username']
                return redirect('/member')
                
            except Exception as e:
                print(f"資料庫操作錯誤: {str(e)}")
                session.clear()
                return redirect('/error?message=用戶資料處理失敗，請稍後再試')
                
        except Exception as e:
            print(f"用戶信息獲取錯誤: {str(e)}")
            session.clear()
            return redirect('/error?message=無法獲取用戶信息，請重新登入')
            
    except Exception as e:
        print(f"OAuth 回調錯誤: {str(e)}")
        session.clear()
        return redirect('/error?message=登入過程發生錯誤，請重新嘗試')

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/member')
    return render_template('index.html')

@app.route('/member')
def member():
    if 'username' not in session:
        return redirect('/error')
    return render_template('member.html', username=session['username'])

@app.route('/error')
def error():
    message = request.args.get('message', '您沒有權限')
    return render_template('error.html', message=message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# 生成驗證碼
def generate_captcha():
    # 生成隨機字串
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choices(chars, k=6))
    
    # 創建圖片
    width = 120
    height = 40
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 添加干擾線
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray')
    
    # 繪製文字
    for i, char in enumerate(code):
        x = 10 + i * 20
        y = random.randint(5, 15)
        draw.text((x, y), char, fill='black')
    
    # 轉換為 bytes
    image_io = io.BytesIO()
    image.save(image_io, 'PNG')
    image_io.seek(0)
    
    return code, image_io

# 驗證碼路由
@app.route('/captcha')
def captcha():
    code, image_io = generate_captcha()
    session['captcha'] = code
    return send_file(image_io, mimetype='image/png')

# 修改註冊路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        captcha = request.form.get('captcha')
        
        # 驗證輸入
        if not username or not password or not confirm_password or not captcha:
            return redirect('/error?message=請填寫完整資訊')
        
        # 驗證碼檢查
        if captcha.lower() != session.get('captcha', '').lower():
            return redirect('/error?message=驗證碼錯誤')
        
        # 檢查用戶名是否已存在
        existing_user = collection.find_one({'username': username})
        if existing_user:
            return redirect('/error?message=帳號已經存在')
        
        try:
            collection.insert_one({
                'username': username,
                'password': password,
                'oauth_type': 'local',
                'created_at': datetime.now()
            })
            return redirect('/login')
        except Exception as e:
            print(f"註冊錯誤: {str(e)}")
            return redirect('/error?message=註冊失敗，請稍後再試')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 只驗證用戶名和密碼
        user = collection.find_one({
            'username': username,
            'password': password
        })
        
        if user:
            session['username'] = user['username']
            return redirect('/member')
        else:
            return redirect('/error?message=帳號或密碼錯誤')
    
    return render_template('login.html')

# 添加錯誤處理
@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Server Error: %s', error)
    return render_template('error.html', message='伺服器錯誤，請稍後再試'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return render_template('error.html', message='發生未知錯誤，請稍後再試'), 500

# 添加這個路由來處理根路徑的靜態文件
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('public/js', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('public/images', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('public/css', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
