import sqlite3  # 파이썬에서 SQLite 데이터베이스를 사용하기 위한 모듈
from pathlib import Path  # 파일과 폴더의 경로를 운영체제에 맞게 다루기 위한 모듈


# -----------------------------
# 데이터베이스 파일 경로
# -----------------------------

# 현재 database.py 파일이 저장된 폴더의 절대 경로를 구하고,
# 그 폴더 안에 있는 school_manager.db 파일을 데이터베이스로 사용한다.
# 따라서 프로그램을 다른 위치에서 실행하더라도 같은 폴더의 DB 파일을 찾을 수 있다.
DB_PATH = Path(__file__).resolve().parent / "school_manager.db"


# -----------------------------
# 데이터베이스 연결
# -----------------------------

def get_connection():
    """
    데이터베이스에 연결하고
    연결 객체를 반환하는 함수
    """

    # 지정한 경로의 SQLite 데이터베이스에 연결한다.
    # 해당 파일이 아직 없다면 SQLite가 새 데이터베이스 파일을 생성한다.
    conn = sqlite3.connect(DB_PATH)

    # 조회 결과를 일반적인 숫자 인덱스뿐 아니라
    # 열 이름을 이용해서도 접근할 수 있도록 설정한다.
    conn.row_factory = sqlite3.Row

    # 다른 함수에서 SQL 명령을 실행할 수 있도록 연결 객체를 반환한다.
    return conn


# -----------------------------
# 데이터베이스 초기화
# -----------------------------

def init_database():
    """
    데이터베이스와 테이블이 없으면 생성한다.
    이미 존재하는 데이터는 유지한다.
    """

    # 데이터베이스 연결을 만들고 SQL 명령을 실행할 커서를 준비한다.
    conn = get_connection()
    cursor = conn.cursor()

    # 업무 정보를 저장할 tasks 테이블을 생성한다.
    # IF NOT EXISTS를 사용하므로 테이블이 이미 있으면 새로 만들거나
    # 기존 데이터를 삭제하지 않는다.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            category TEXT NOT NULL,

            title TEXT NOT NULL,

            detail TEXT,

            due_date TEXT,

            importance TEXT,

            assignee TEXT,

            completed INTEGER DEFAULT 0

        )
    """)

    # 실행한 테이블 생성 명령을 데이터베이스에 반영한다.
    conn.commit()

    # 초기화 작업이 끝났으므로 데이터베이스 연결을 종료한다.
    conn.close()


# -----------------------------
# 데이터베이스 연결 종료
# -----------------------------

def close_connection(conn):
    """
    데이터베이스 연결을 종료한다.
    """

    # 전달받은 연결 객체가 존재하는 경우에만 연결을 닫는다.
    if conn:
        conn.close()
