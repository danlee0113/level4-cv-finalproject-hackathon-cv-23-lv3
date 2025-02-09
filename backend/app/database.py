# app/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, exists
from sqlalchemy.orm import sessionmaker

from .models import Base, User, Industry, UserIndustry, ChatSession, ChatMessage

# .env 파일 로드
load_dotenv()

# DATABASE_URL 환경 변수 사용
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    echo=True,          # SQLAlchemy가 실행하는 쿼리를 콘솔에 표시
    pool_recycle=3600,  # 연결 재활용 시간 설정
    pool_pre_ping=True  # 연결 유효성 검사
)

# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import bcrypt

def hash_password(plain_password: str) -> str:
    """
    평문 비밀번호를 받아 bcrypt로 해싱된 비밀번호를 반환합니다.
    """
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def init_db():
    """
    테이블 생성 및 초기 데이터 삽입 수행.
    기존 사용자의 비밀번호가 해싱되지 않은 경우 해싱하여 업데이트.
    """
    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 세션 생성
    session = SessionLocal()

    try:
        # --- 기존 사용자 비밀번호 해싱 ---
        users = session.query(User).all()
        for user in users:
            if not (user.password.startswith('$2a$') or user.password.startswith('$2b$')) or len(user.password) != 60:
                print(f"해싱되지 않은 비밀번호를 발견했습니다. 사용자: {user.email}")
                hashed_pw = hash_password(user.password)
                user.password = hashed_pw
                print(f"사용자 {user.email}의 비밀번호가 해싱되었습니다.")

        session.commit()  # 비밀번호 업데이트 커밋
        print("기존 사용자 비밀번호 해싱이 완료되었습니다.")

        # --- 초기 사용자 데이터 삽입 ---
        users_data = [
            {"nickname": "admin", "email": "admin@example.com", "password": "admin"},
            {"nickname": "alice", "email": "alice@example.com", "password": "password1"},
            {"nickname": "bob", "email": "bob@example.com", "password": "password2"},
            {"nickname": "charlie", "email": "charlie@example.com", "password": "password3"},
            {"nickname": "david", "email": "david@example.com", "password": "password4"},
            {"nickname": "erin", "email": "erin@example.com", "password": "password5"},
            {"nickname": "frank", "email": "frank@example.com", "password": "password6"},
            {"nickname": "grace", "email": "grace@example.com", "password": "password7"},
            {"nickname": "hank", "email": "hank@example.com", "password": "password8"},
            {"nickname": "jack", "email": "jack@example.com", "password": "password9"},
        ]

        for user_data in users_data:
            user_exists = session.execute(
                select(exists().where(User.email == user_data["email"]))
            ).scalar()
            if not user_exists:
                # 비밀번호 해싱 적용
                user_data["password"] = hash_password(user_data["password"])
                user = User(**user_data)  # nickname, email, password
                session.add(user)
                print(f"새 사용자 추가: {user.email}")

        session.commit()
        print("새 사용자 데이터 삽입이 완료되었습니다.")

        # --- 산업 데이터 삽입 ---
        industries_data = [
            {"industry_name": "Technology"},
            {"industry_name": "Finance"},
            {"industry_name": "Healthcare"},
            {"industry_name": "Retail"},
            {"industry_name": "Manufacturing"},
            {"industry_name": "Education"},
            {"industry_name": "Hospitality"},
            {"industry_name": "Transportation"},
            {"industry_name": "Entertainment"},
            {"industry_name": "Agriculture"},
        ]

        for industry_data in industries_data:
            industry_exists = session.execute(
                select(exists().where(Industry.industry_name == industry_data["industry_name"]))
            ).scalar()
            if not industry_exists:
                industry = Industry(**industry_data)
                session.add(industry)
                print(f"새 산업 추가: {industry.industry_name}")

        session.commit()
        print("산업 데이터 삽입이 완료되었습니다.")

        # --- 사용자-산업 연관 데이터 삽입 ---
        users = session.execute(select(User)).scalars().all()
        industries = session.execute(select(Industry)).scalars().all()

        # nickname을 key로 하는 딕셔너리 구성
        user_dict = {user.nickname: user for user in users}
        industry_dict = {industry.industry_name: industry for industry in industries}

        # user_industries_data에서 'username' -> 'nickname'
        user_industries_data = [
            {"nickname": "admin",   "industries": ["Technology", "Finance"]},
            {"nickname": "alice",   "industries": ["Technology", "Healthcare"]},
            {"nickname": "bob",     "industries": ["Finance", "Retail"]},
            {"nickname": "charlie", "industries": ["Retail", "Technology"]},
            {"nickname": "david",   "industries": ["Manufacturing"]},
            {"nickname": "erin",    "industries": ["Finance"]},
            {"nickname": "frank",   "industries": ["Healthcare"]},
            {"nickname": "grace",   "industries": ["Technology"]},
            {"nickname": "hank",    "industries": ["Hospitality"]},
            {"nickname": "irene",   "industries": ["Transportation"]},
            {"nickname": "jack",    "industries": ["Entertainment", "Technology"]},
        ]

        for ui in user_industries_data:
            user = user_dict.get(ui["nickname"])
            if not user:
                print(f"사용자를 찾을 수 없습니다: {ui['nickname']}")
                continue
            for industry_name in ui["industries"]:
                industry = industry_dict.get(industry_name)
                if not industry:
                    print(f"산업을 찾을 수 없습니다: {industry_name}")
                    continue
                # 이미 연관이 존재하는지 확인
                association_exists = session.execute(
                    select(exists().where(
                        UserIndustry.user_id == user.user_id,
                        UserIndustry.industry_id == industry.industry_id
                    ))
                ).scalar()
                if not association_exists:
                    user_industry = UserIndustry(user_id=user.user_id, industry_id=industry.industry_id)
                    session.add(user_industry)
                    print(f"연관 추가: {user.nickname} - {industry.industry_name}")

        session.commit()
        print("사용자-산업 연관 데이터 삽입이 완료되었습니다.")

        # --- 초기 채팅 세션 데이터 삽입 ---
        chat_sessions_data = [
            {"nickname": "admin"},
            {"nickname": "alice"},
            {"nickname": "bob"},
            {"nickname": "charlie"},
            {"nickname": "david"},
            {"nickname": "erin"},
            {"nickname": "frank"},
            {"nickname": "grace"},
            {"nickname": "hank"},
            {"nickname": "jack"},
        ]

        for cs in chat_sessions_data:
            user = user_dict.get(cs["nickname"])
            if not user:
                print(f"사용자를 찾을 수 없습니다: {cs['nickname']}")
                continue
            # 채팅 세션이 이미 존재하는지 확인
            session_exists = session.execute(
                select(exists().where(ChatSession.user_id == user.user_id))
            ).scalar()
            if not session_exists:
                chat_session = ChatSession(user_id=user.user_id)
                session.add(chat_session)
                print(f"채팅 세션 추가: {user.nickname}")

        session.commit()
        print("채팅 세션 데이터 삽입이 완료되었습니다.")

        # --- 초기 채팅 메시지 데이터 삽입 ---
        chat_sessions = session.execute(select(ChatSession)).scalars().all()
        chat_session_dict = {i+1: cs for i, cs in enumerate(chat_sessions)}  # 세션 번호와 매칭

        chat_messages_data = {
            1: [
                {"sender_role": "user",      "message": "Hello, this is user 1."},
                {"sender_role": "assistant", "message": "Hello user 1, how can I help you?"},
                {"sender_role": "user",      "message": "I am just testing the chat."},
            ],
            2: [
                {"sender_role": "user",      "message": "User 2 checking in."},
                {"sender_role": "assistant", "message": "Hi user 2, how may I assist you?"},
                {"sender_role": "user",      "message": "Just exploring the service."},
            ],
            3: [
                {"sender_role": "user",      "message": "What is the weather like today?"},
                {"sender_role": "assistant", "message": "The forecast is sunny with a chance of clouds."},
                {"sender_role": "user",      "message": "Thanks for the info!"},
            ],
            4: [
                {"sender_role": "user",      "message": "Hi there, user 4 here!"},
                {"sender_role": "assistant", "message": "Hello user 4! What can I do for you today?"},
                {"sender_role": "user",      "message": "I need some suggestions for dinner."},
            ],
            5: [
                {"sender_role": "system",    "message": "System message for session 5."},
                {"sender_role": "assistant", "message": "How can I help you, user 5?"},
                {"sender_role": "user",      "message": "I have a question about your API."},
            ],
            6: [
                {"sender_role": "user",      "message": "Hello, user 6 wants to chat."},
                {"sender_role": "assistant", "message": "Hi user 6, I am here to help."},
                {"sender_role": "user",      "message": "Great, let me ask a few things."},
            ],
            7: [
                {"sender_role": "assistant", "message": "Welcome user 7!"},
                {"sender_role": "user",      "message": "Thank you, assistant."},
                {"sender_role": "assistant", "message": "How may I assist you?"},
            ],
            8: [
                {"sender_role": "user",      "message": "Greetings from user 8."},
                {"sender_role": "assistant", "message": "Hi user 8, nice to meet you."},
                {"sender_role": "system",    "message": "System check: everything looks good."},
            ],
            9: [
                {"sender_role": "user",      "message": "User 9 saying hello."},
                {"sender_role": "assistant", "message": "Hello user 9, how can I help?"},
                {"sender_role": "user",      "message": "No issues, just testing the waters."},
            ],
            10: [
                {"sender_role": "assistant","message": "Assistant message for session 10."},
                {"sender_role": "user",     "message": "User 10 here. Thanks."},
                {"sender_role": "assistant","message": "Anytime, user 10!"},
            ],
        }

        for session_number, messages in chat_messages_data.items():
            chat_session = chat_session_dict.get(session_number)
            if not chat_session:
                print(f"채팅 세션을 찾을 수 없습니다: 세션 번호 {session_number}")
                continue
            for msg in messages:
                message_exists = session.execute(
                    select(exists().where(
                        ChatMessage.chat_session_id == chat_session.chat_session_id,
                        ChatMessage.sender_role == msg["sender_role"],
                        ChatMessage.message == msg["message"]
                    ))
                ).scalar()
                if not message_exists:
                    chat_message = ChatMessage(
                        chat_session_id=chat_session.chat_session_id,
                        sender_role=msg["sender_role"],
                        message=msg["message"]
                    )
                    session.add(chat_message)
                    print(f"채팅 메시지 추가: {msg['sender_role']} - {msg['message']}")

        session.commit()
        print("채팅 메시지 데이터 삽입이 완료되었습니다.")

        print("데이터베이스 초기화 및 초기 데이터 삽입이 성공적으로 완료되었습니다.")
    except Exception as e:
        session.rollback()
        print("데이터베이스 초기화 중 오류가 발생했습니다:", e)
    finally:
        session.close()

def get_db():
    """
    요청마다 독립적인 세션을 제공하기 위한 의존성 함수.
    FastAPI에서 엔드포인트에 Depends(get_db)를 사용하면,
    이 함수가 생성하는 세션(db)을 자동으로 주입해주고,
    엔드포인트 처리가 끝난 뒤 finally에서 세션을 닫아줍니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()