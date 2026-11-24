from database import get_connection


# -----------------------------
# 업무 카테고리
# -----------------------------

# 프로그램에서 사용할 업무 카테고리를 미리 정의한다.
# 다른 함수에서도 이 목록을 이용해 카테고리별 통계를 관리한다.
CATEGORIES = [
    "학업 관리",
    "동아리 관리",
    "행사 관리"
]


# -----------------------------
# 업무 등록
# -----------------------------

def add_task(category, title, detail, due_date,
             importance, assignee):

    # 데이터베이스에 연결하고 SQL 명령을 실행할 커서를 생성한다.
    conn = get_connection()
    cursor = conn.cursor()

    # INSERT 문을 사용해 새로운 업무 정보를 tasks 테이블에 추가한다.
    # ?는 실제 값이 들어갈 위치를 나타내며, 값은 아래 튜플로 전달한다.
    # 새로 등록한 업무는 completed 값을 0으로 설정하여 미완료 상태로 저장한다.
    cursor.execute("""
        INSERT INTO tasks (
            category,
            title,
            detail,
            due_date,
            importance,
            assignee,
            completed
        )
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (
        category,
        title,
        detail,
        due_date,
        importance,
        assignee
    ))

    # 데이터베이스에 변경 사항을 저장하고 연결을 종료한다.
    conn.commit()
    conn.close()


# -----------------------------
# 전체 업무 조회
# -----------------------------

def get_all_tasks():

    conn = get_connection()
    cursor = conn.cursor()

    # SELECT *를 사용하여 tasks 테이블에 저장된 모든 업무 정보를 조회한다.
    # CASE 문을 이용해 중요도에 따른 정렬 순서를 지정한다.
    # 중요도가 높은 업무가 먼저 표시되고, 중요도가 같으면 마감일이 빠른 순서로 정렬된다.
    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY
            CASE importance
                WHEN '높음' THEN 1
                WHEN '보통' THEN 2
                WHEN '낮음' THEN 3
                ELSE 4
            END,
            due_date ASC
    """)

    # fetchall()을 이용해 조회된 모든 업무 정보를 가져온다.
    tasks = cursor.fetchall()
    conn.close()

    return tasks


# -----------------------------
# 카테고리별 업무 조회
# -----------------------------

def get_tasks_by_category(category):

    conn = get_connection()
    cursor = conn.cursor()

    # WHERE 조건을 이용해 전달받은 카테고리에 해당하는 업무만 조회한다.
    # 중요도와 마감일을 기준으로 정렬하는 방식은 전체 업무 조회와 동일하다.
    cursor.execute("""
        SELECT *
        FROM tasks
        WHERE category = ?
        ORDER BY
            CASE importance
                WHEN '높음' THEN 1
                WHEN '보통' THEN 2
                WHEN '낮음' THEN 3
                ELSE 4
            END,
            due_date ASC
    """, (category,))

    tasks = cursor.fetchall()
    conn.close()

    return tasks


# -----------------------------
# 특정 업무 조회
# -----------------------------

def get_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    # 각 업무에 부여된 고유 ID를 기준으로 특정 업무를 조회한다.
    cursor.execute("""
        SELECT *
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    # fetchone()을 이용해 조회 결과 중 한 개의 업무 정보만 가져온다.
    task = cursor.fetchone()
    conn.close()

    return task


# -----------------------------
# 업무 수정
# -----------------------------

def update_task(task_id, category, title, detail,
                due_date, importance, assignee):

    conn = get_connection()
    cursor = conn.cursor()

    # UPDATE 문을 이용해 기존 업무의 정보를 새로운 값으로 수정한다.
    # WHERE id = ? 조건을 사용하여 지정한 ID의 업무만 수정하도록 한다.
    cursor.execute("""
        UPDATE tasks
        SET
            category = ?,
            title = ?,
            detail = ?,
            due_date = ?,
            importance = ?,
            assignee = ?
        WHERE id = ?
    """, (
        category,
        title,
        detail,
        due_date,
        importance,
        assignee,
        task_id
    ))

    # 수정된 내용을 데이터베이스에 저장한 후 연결을 종료한다.
    conn.commit()
    conn.close()


# -----------------------------
# 업무 완료 처리
# -----------------------------

def complete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    # completed 값을 1로 변경하여 해당 업무를 완료 상태로 처리한다.
    cursor.execute("""
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()


# -----------------------------
# 업무 완료 취소
# -----------------------------

def undo_complete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    # completed 값을 0으로 되돌려 완료된 업무를 미완료 상태로 변경한다.
    cursor.execute("""
        UPDATE tasks
        SET completed = 0
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()


# -----------------------------
# 업무 삭제
# -----------------------------

def delete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    # DELETE 문을 이용해 지정한 ID의 업무 정보를 데이터베이스에서 삭제한다.
    # WHERE 조건을 사용하여 다른 업무 정보는 삭제되지 않도록 한다.
    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()


# -----------------------------
# 전체 업무 통계
# -----------------------------

def get_task_statistics():

    conn = get_connection()
    cursor = conn.cursor()

    # COUNT(*)는 전체 업무의 개수를 계산한다.
    # CASE WHEN을 이용해 완료 여부에 따라 업무를 구분하고,
    # SUM으로 각 상태에 해당하는 업무의 개수를 계산한다.
    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END)
                AS unfinished,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END)
                AS completed
        FROM tasks
    """)

    # 조회된 통계 결과 한 행을 가져온다.
    result = cursor.fetchone()
    conn.close()

    # 통계 결과가 없는 경우 SUM 값은 None이 될 수 있다.
    # or 0을 사용하여 None 대신 숫자 0을 반환하도록 처리한다.
    # 딕셔너리 형태로 반환하여 다른 파일에서 항목 이름으로 통계값을 사용할 수 있게 한다.
    return {
        "total": result["total"] or 0,
        "unfinished": result["unfinished"] or 0,
        "completed": result["completed"] or 0
    }


# -----------------------------
# 카테고리별 진행률 통계
# -----------------------------

def get_category_statistics():

    conn = get_connection()
    cursor = conn.cursor()

    # GROUP BY를 이용해 카테고리별로 업무를 묶어서 통계를 계산한다.
    # COUNT(*)는 카테고리별 전체 업무 수를,
    # SUM과 CASE WHEN은 완료된 업무 수를 계산한다.
    cursor.execute("""
        SELECT
            category,
            COUNT(*) AS total,
            SUM(
                CASE WHEN completed = 1 THEN 1 ELSE 0 END
            ) AS completed
        FROM tasks
        GROUP BY category
    """)

    results = cursor.fetchall()
    conn.close()

    # 모든 카테고리의 통계값을 먼저 0으로 초기화한다.
    # 아직 등록된 업무가 없는 카테고리도 통계 결과에 포함하기 위한 과정이다.
    statistics = {}

    for category in CATEGORIES:

        statistics[category] = {
            "total": 0,
            "completed": 0,
            "rate": 0
        }

    # 데이터베이스에서 조회한 카테고리별 통계 결과를 딕셔너리에 반영한다.
    for row in results:

        total = row["total"] or 0
        completed = row["completed"] or 0

        # 전체 업무 수가 0보다 클 때 완료율을 계산한다.
        # 업무가 없는 경우에는 0으로 나누는 오류를 방지하기 위해 완료율을 0으로 설정한다.
        rate = (
            completed / total * 100
            if total > 0
            else 0
        )

        statistics[row["category"]] = {
            "total": total,
            "completed": completed,
            "rate": rate
        }

    return statistics


# -----------------------------
# 마감일 기준 업무 조회
# -----------------------------

def get_deadline_tasks():

    # 날짜를 비교하고 날짜 간격을 계산하기 위해 필요한 기능을 가져온다.
    from datetime import date, timedelta

    conn = get_connection()
    cursor = conn.cursor()

    # 현재 날짜와 현재 날짜로부터 3일 뒤의 날짜를 구한다.
    today = date.today()
    soon = today + timedelta(days=3)

    # 완료되지 않았고 마감일이 입력된 업무만 조회한다.
    # 마감일이 빠른 순서대로 정렬한다.
    cursor.execute("""
        SELECT *
        FROM tasks
        WHERE completed = 0
        AND due_date IS NOT NULL
        AND due_date != ''
        ORDER BY due_date ASC
    """)

    tasks = cursor.fetchall()
    conn.close()

    # 마감일에 따라 업무를 구분하여 저장할 리스트를 준비한다.
    result = {
        "overdue": [],
        "today": [],
        "soon": []
    }

    # 조회된 각 업무의 마감일을 날짜 자료형으로 변환하여 현재 날짜와 비교한다.
    for task in tasks:

        try:
            # 문자열 형태의 마감일을 날짜 자료형으로 변환한다.
            due = date.fromisoformat(task["due_date"])
        except (ValueError, TypeError):
            # 날짜 형식이 잘못되었거나 값이 없으면 해당 업무는 분류하지 않는다.
            continue

        if due < today:
            # 마감일이 오늘보다 이전이면 기한이 지난 업무로 분류한다.
            result["overdue"].append(task)

        elif due == today:
            # 마감일이 오늘이면 오늘 마감 업무로 분류한다.
            result["today"].append(task)

        elif today < due <= soon:
            # 마감일이 내일부터 3일 뒤 사이이면 마감 임박 업무로 분류한다.
            result["soon"].append(task)

    return result