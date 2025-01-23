from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 실제 운영시에는 더 복잡한 키를 사용하세요

# 테스트용 admin 계정
ADMIN_USER = {
    "email": "admin@example.com",
    "password": "admin123"
}

# 로그인 필요한 페이지 접근 제어를 위한 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # admin 계정 확인
        if email == ADMIN_USER["email"] and password == ADMIN_USER["password"]:
            session['user_id'] = email
            return redirect(url_for('index'))
        
        # 로그인 실패시
        return render_template('login.html', error="이메일 또는 비밀번호가 잘못되었습니다.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# 채팅 페이지는 로그인 필요
@app.route("/")
@login_required
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
@login_required
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)

def get_Chat_response(text):

    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens, 
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 닉네임 길이 검사
        if len(nickname) < 2 or len(nickname) > 10:
            return render_template('register.html', 
                error="닉네임은 2-10자 사이여야 합니다")

        # 비밀번호 형식 검사
        if not password.isalnum() or not all(c.islower() or c.isdigit() for c in password):
            return render_template('register.html', 
                error="비밀번호는 영문 소문자와 숫자만 사용 가능합니다")

        # 비밀번호 일치 검사
        if password != confirm_password:
            return render_template('register.html', 
                error="비밀번호가 일치하지 않습니다")

        # 이미 등록된 이메일인지 확인 (실제로는 DB 체크 필요)
        if email == ADMIN_USER["email"]:
            return render_template('register.html', 
                error="이미 등록된 이메일입니다")

        # 여기에 실제 회원가입 로직 구현 (DB 저장 등)
        
        # 회원가입 성공 시 로그인 페이지로 리다이렉트
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/mypage')
@login_required
def mypage():
    # 실제 운영 환경에서는 DB에서 사용자 정보를 가져와야 함
    user = {
        'email': session['user_id'],
        'nickname': 'User123',  # DB에서 가져와야 함
        'created_at': datetime.now()  # DB에서 가져와야 함
    }
    return render_template('mypage.html', user=user)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # 임시 사용자 데이터 (데이터베이스 연동 전)
    user = {
        'email': session['user_id'],
        'nickname': 'User123'  # 실제로는 DB에서 가져와야 함
    }
    
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        
        # 닉네임 유효성 검사
        if len(nickname) < 2 or len(nickname) > 10:
            return render_template('edit_profile.html', user=user, error="닉네임은 2-10자 사이여야 합니다")
        
        # 실제로는 여기서 DB 업데이트가 필요함
        # 임시로 성공 메시지만 표시
        return redirect(url_for('mypage'))
            
    return render_template('edit_profile.html', user=user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # 임시 검증 (실제로는 DB의 해시된 비밀번호와 비교해야 함)
        if current_password != ADMIN_USER['password']:
            return render_template('change_password.html', error="현재 비밀번호가 일치하지 않습니다")
        
        # 새 비밀번호 유효성 검사
        if not new_password.isalnum() or not all(c.islower() or c.isdigit() for c in new_password):
            return render_template('change_password.html', error="비밀번호는 영문 소문자와 숫자만 사용 가능합니다")
            
        if new_password != confirm_password:
            return render_template('change_password.html', error="새 비밀번호가 일치하지 않습니다")
        
        # 실제로는 여기서 DB 업데이트가 필요함
        # 임시로 성공 처리
        return redirect(url_for('mypage'))
            
    return render_template('change_password.html')

if __name__ == '__main__':
    app.run()
