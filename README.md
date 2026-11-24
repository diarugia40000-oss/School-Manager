# School Manager

학교생활에 필요한 학업, 동아리, 행사 업무를 한곳에서 관리할 수 있는 Python 데스크톱 프로그램입니다.

## 주요 기능

- 학업, 동아리, 행사별 업무 관리
- 업무 등록, 조회, 수정 및 삭제
- 업무 완료 상태 관리
- 중요도에 따른 색상 구분
- 마감일 확인 및 날짜별 업무 조회
- 대시보드를 통한 업무 현황과 완료율 확인
- SQLite 데이터베이스를 이용한 업무 정보 저장

## 실행 환경

- Windows
- Python 3
- 필요한 Python 라이브러리: `customtkinter`

## 설치 및 실행 방법

1. GitHub 저장소에서 **Code → Download ZIP**을 선택해 프로젝트를 다운로드합니다.
2. ZIP 파일의 압축을 풉니다.
3. 압축을 푼 프로젝트 폴더에서 터미널을 엽니다.
4. 필요한 라이브러리를 설치합니다.

```bash
py -m pip install -r requirements.txt
```

5. 프로그램을 실행합니다.

```bash
py main.py
```

## 데이터 저장

업무 정보는 SQLite 데이터베이스 파일에 저장됩니다. 데이터베이스 파일은 각 사용자의 컴퓨터에서 생성·관리되며, 다른 사용자의 데이터와 공유되지 않습니다.

개인 업무 정보가 포함될 수 있으므로 데이터베이스 파일(`*.db`)은 GitHub 저장소에 업로드하지 않습니다.

## 프로젝트 파일 구성

```text
School Manager/
├── main.py
├── database.py
├── task_service.py
├── dashboard.py
├── task_tab.py
├── calendar_view.py
├── requirements.txt
├── README.md
└── .gitignore
```
