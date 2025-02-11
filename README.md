# ReportRadar

## 🚀 프로젝트 개요
ReportRadar는 증권 리포트 기반의 주식 LLM 서비스입니다. 대략적인 기능은 아래와 같습니다. 
1. 주어진 리포트의 내용을 검색해 사용자에게 해당 종목에 대한 정보를 제공합니다.
2. 미국 주식에 대한 최신 뉴스를 요약하여 제공합니다.


## 👥 팀 소개
끝까지 도전하며 함께 배우고 성장하는 팀, CV 미정입니다!
문제 해결을 위해 끊임없이 노력하며, 다양한 경험을 통해 새로운 지식을 배우고 성장하려는 열정과 적극적인 태도를 가진 팀입니다.

## 💻 팀원 소개
| 전인석 | 김준원 | 신석준 | 김민환 | 이준학 | 
| --- | --- | --- | --- | --- |
| <a href="https://github.com/inDseok" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/KimJunWon98" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/SeokjunShin" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/alsghks1066" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/danlee0113" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> |

## 🛠 기술 스택
!!!! 고쳐야 함!!!!
- **언어:** Python, Html, CSS, JavaScript
- **프레임워크:** FastAPI, LangChain, (FAISS??)
- **데이터베이스:** MySQL
- **기타:** Docker, AWS EC2, AWS Route53

## 📆 프로젝트 타임라인


## 🔧 설치 및 실행 방법 (AWS EC2 인스턴스 서버 기준)
```bash
# EC2 인스턴스 생성(리전 서울로), 탄력적 IP 설정 후 진행
# 저장소 클론
git clone https://github.com/boostcampaitech7/level4-cv-finalproject-hackathon-cv-23-lv3.git
cd level4-cv-finalproject-hackathon-cv-23-lv3

# 기본 설정
sudo apt-get update
sudo apt-get remove docker docker-engine docker.io

# docker 설치
sudo apt install docker.io

sudo systemctl start docker
sudo docker ps
sudo systemctl enable docker
docker —version

# docker-compose 설치
sudo apt install docker-compose 

# .env 파일 생성 후 내용 채워넣기

# Docker 네트워크 생성 (이미 있으면 생략)
sudo docker network ls
sudo docker network create example-network

# 오류 발생한다면 docker-compose.yml 에서 db volumes 수정
# - ./init.sql:/docker-entrypoint-initdb.d/init.sql

# Docker 빌드
sudo docker-compose -f docker-compose.yml up -d --build
sudo docker ps
sudo docker images

# Docker 컨테이너 실행
sudo docker exec -it backend-con /bin/bash

# 컨테이너 내부에서 fastAPI실행
uvicorn app.main:app --host 0.0.0.0 --port 9000

# 참고 유튜브 : https://www.youtube.com/watch?v=oIX6T4X6hGM
```

## 📌 웹페이지 소개
서비스를 웹페이지에서 사용하려면 다음 링크를 통해 접속하실 수 있습니다. [ReportRadar](http://reportradar.site:9000/)

### 소개 페이지 
<img width="1322" alt="img (3)" src="https://github.com/user-attachments/assets/f6639f9b-c489-4acd-922d-97e59d9c2745">


## 📊 서비스 아키텍쳐
![image](https://github.com/user-attachments/assets/68a01da9-1843-4cf0-941b-8f8f653cda93)

!!!!!!설명필요!!!!!!!

## 📚 참고 자료
- [teddynote 님의 langchain 튜토리얼](https://github.com/teddylee777/langchain-kr)

