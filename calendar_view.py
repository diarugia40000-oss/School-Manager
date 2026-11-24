import calendar
from datetime import date, datetime

import customtkinter as ctk

from task_service import get_all_tasks


# -----------------------------
# 통합 달력 클래스
# -----------------------------

# CustomTkinter의 프레임을 상속받아 달력 화면을 구성하는 클래스이다.
class CalendarView(ctk.CTkFrame):

    # 달력 화면을 처음 생성할 때 실행되는 초기화 함수
    def __init__(self, master):
        super().__init__(master)

        # 현재 표시할 달과 선택된 날짜를 설정한다.
        today = date.today()

        # 현재 표시할 달은 이번 달의 1일을 기준으로 설정한다.
        self.current_date = today.replace(day=1)

        # 처음 선택된 날짜는 오늘 날짜로 설정한다.
        self.selected_date = today

        # 데이터베이스에서 불러온 업무 목록을 저장할 리스트
        self.tasks = []

        # 달력 화면의 위젯을 생성한다.
        self.build_ui()

        # 업무 데이터를 불러오고 달력을 처음 표시한다.
        self.refresh()

    # -----------------------------
    # 화면 구성
    # -----------------------------
    def build_ui(self):

        # 화면을 왼쪽 달력 영역과 오른쪽 일정 영역으로 나눈다.
        # weight 값에 따라 화면이 확장될 때 영역별 크기가 조정된다.
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # 상단에 통합 달력 제목을 표시한다.
        title = ctk.CTkLabel(
            self,
            text="통합 달력",
            font=("맑은 고딕", 24, "bold")
        )
        title.grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=20, pady=(15, 10)
        )

        # -----------------------------
        # 왼쪽: 달력 영역
        # -----------------------------

        # 날짜 버튼들이 배치될 왼쪽 달력 프레임을 생성한다.
        calendar_frame = ctk.CTkFrame(self)
        calendar_frame.grid(
            row=1, column=0,
            sticky="nsew", padx=(20, 10), pady=10
        )

        # 달력 프레임 내부의 열과 행이 화면 크기에 맞춰 확장되도록 설정한다.
        calendar_frame.grid_columnconfigure(0, weight=1)
        calendar_frame.grid_rowconfigure(2, weight=1)

        # 월 이동 영역
        # 이전 달, 현재 연월, 다음 달을 표시하는 영역이다.
        month_frame = ctk.CTkFrame(
            calendar_frame,
            fg_color="transparent"
        )
        month_frame.grid(
            row=0, column=0,
            sticky="ew", padx=10, pady=15
        )

        # 가운데 연월 표시 영역이 남은 공간을 차지하도록 설정한다.
        month_frame.grid_columnconfigure(1, weight=1)

        # 이전 달로 이동하는 버튼을 생성한다.
        self.prev_button = ctk.CTkButton(
            month_frame,
            text="◀",
            width=45,
            command=self.previous_month
        )
        self.prev_button.grid(row=0, column=0, padx=5)

        # 현재 표시 중인 연도와 월을 나타내는 레이블이다.
        self.month_label = ctk.CTkLabel(
            month_frame,
            text="",
            font=("맑은 고딕", 20, "bold")
        )
        self.month_label.grid(row=0, column=1)

        # 다음 달로 이동하는 버튼을 생성한다.
        self.next_button = ctk.CTkButton(
            month_frame,
            text="▶",
            width=45,
            command=self.next_month
        )
        self.next_button.grid(row=0, column=2, padx=5)

        # 요일 표시
        # 달력의 각 열 위에 요일을 표시할 프레임을 생성한다.
        weekday_frame = ctk.CTkFrame(
            calendar_frame,
            fg_color="transparent"
        )
        weekday_frame.grid(
            row=1, column=0,
            sticky="ew", padx=10
        )

        # 일요일부터 토요일까지의 요일 이름을 리스트로 저장한다.
        weekdays = ["일", "월", "화", "수", "목", "금", "토"]

        # enumerate()를 사용해 요일 이름과 열 번호를 함께 가져온다.
        for column, weekday in enumerate(weekdays):

            # 각 요일을 화면에 표시할 레이블을 생성한다.
            weekday_label = ctk.CTkLabel(
                weekday_frame,
                text=weekday,
                font=("맑은 고딕", 13, "bold")
            )
            weekday_label.grid(
                row=0, column=column,
                sticky="nsew", padx=2, pady=5
            )

            # 7개의 요일 영역이 균등한 너비를 갖도록 설정한다.
            weekday_frame.grid_columnconfigure(
                column, weight=1
            )

        # 날짜 버튼 영역
        # 실제 날짜 버튼들이 배치될 프레임을 생성한다.
        self.days_frame = ctk.CTkFrame(
            calendar_frame,
            fg_color="transparent"
        )
        self.days_frame.grid(
            row=2, column=0,
            sticky="nsew", padx=10, pady=10
        )

        # 달력의 7개 열이 동일한 너비를 갖도록 설정한다.
        for column in range(7):
            self.days_frame.grid_columnconfigure(
                column, weight=1
            )

        # 최대 6주까지 표시할 수 있도록 6개의 행을 설정한다.
        for row in range(6):
            self.days_frame.grid_rowconfigure(
                row, weight=1
            )

        # -----------------------------
        # 오른쪽: 선택 날짜 일정 영역
        # -----------------------------

        # 선택한 날짜의 업무 목록을 표시할 오른쪽 프레임을 생성한다.
        detail_frame = ctk.CTkFrame(self)
        detail_frame.grid(
            row=1, column=1,
            sticky="nsew", padx=(10, 20), pady=10
        )

        # 일정 목록 영역이 남은 공간을 차지하도록 설정한다.
        detail_frame.grid_rowconfigure(1, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        # 현재 선택된 날짜를 표시할 레이블이다.
        self.selected_date_label = ctk.CTkLabel(
            detail_frame,
            text="선택한 날짜",
            font=("맑은 고딕", 19, "bold")
        )
        self.selected_date_label.grid(
            row=0, column=0,
            sticky="w", padx=15, pady=15
        )

        # 일정이 많아질 경우 스크롤할 수 있도록 스크롤 프레임을 생성한다.
        self.task_list_frame = ctk.CTkScrollableFrame(
            detail_frame
        )
        self.task_list_frame.grid(
            row=1, column=0,
            sticky="nsew", padx=10, pady=(0, 10)
        )

    # -----------------------------
    # 이전 달 이동
    # -----------------------------
    def previous_month(self):

        # 현재 표시 중인 연도와 월을 가져온다.
        year = self.current_date.year
        month = self.current_date.month

        # 현재 월이 1월이면 전년도 12월로 이동한다.
        if month == 1:
            year -= 1
            month = 12

        # 1월이 아니라면 월을 1 감소시킨다.
        else:
            month -= 1

        # 변경된 연도와 월의 1일을 현재 표시 기준 날짜로 설정한다.
        self.current_date = date(year, month, 1)

        # 이전 달로 이동하면 해당 달의 1일을 선택 날짜로 설정한다.
        self.selected_date = self.current_date

        # 변경된 달력과 일정 목록을 다시 표시한다.
        self.refresh()

    # -----------------------------
    # 다음 달 이동
    # -----------------------------
    def next_month(self):

        # 현재 표시 중인 연도와 월을 가져온다.
        year = self.current_date.year
        month = self.current_date.month

        # 현재 월이 12월이면 다음 해 1월로 이동한다.
        if month == 12:
            year += 1
            month = 1

        # 12월이 아니라면 월을 1 증가시킨다.
        else:
            month += 1

        # 변경된 연도와 월의 1일을 현재 표시 기준 날짜로 설정한다.
        self.current_date = date(year, month, 1)

        # 다음 달로 이동하면 해당 달의 1일을 선택 날짜로 설정한다.
        self.selected_date = self.current_date

        # 변경된 달력과 일정 목록을 다시 표시한다.
        self.refresh()

    # -----------------------------
    # 날짜 선택
    # -----------------------------
    def select_date(self, selected_date):

        # 사용자가 달력에서 클릭한 날짜를 선택 날짜로 저장한다.
        self.selected_date = selected_date

        # 선택된 날짜가 달력에서 강조되도록 다시 그린다.
        self.render_calendar()

        # 선택한 날짜에 해당하는 업무 목록을 갱신한다.
        self.update_selected_tasks()

    # -----------------------------
    # 캘린더 갱신
    # -----------------------------
    def refresh(self):

        # task_service 모듈을 통해 데이터베이스의 전체 업무를 가져온다.
        self.tasks = get_all_tasks()

        # 최신 업무 정보를 반영하여 달력을 다시 표시한다.
        self.render_calendar()

        # 선택된 날짜의 업무 목록도 최신 정보로 갱신한다.
        self.update_selected_tasks()

    # -----------------------------
    # 달력 날짜 표시
    # -----------------------------
    def render_calendar(self):

        # 기존 날짜 버튼 제거
        # 화면을 다시 그리기 전에 기존 날짜 위젯을 모두 삭제한다.
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        # 현재 표시 중인 연도와 월을 가져온다.
        year = self.current_date.year
        month = self.current_date.month

        # 달력 상단에 현재 연도와 월을 표시한다.
        self.month_label.configure(
            text=f"{year}년 {month}월"
        )

        # 날짜별 일정 개수 계산
        # 각 날짜에 등록된 업무 수를 저장할 딕셔너리를 생성한다.
        task_counts = {}

        # 전체 업무를 하나씩 확인하여 마감일을 조사한다.
        for task in self.tasks:

            # 현재 업무의 마감일을 가져온다.
            due_date = task["due_date"]

            # 마감일이 입력되지 않은 업무는 날짜별 개수에서 제외한다.
            if not due_date:
                continue

            try:
                # 문자열 형태의 마감일을 날짜 자료형으로 변환한다.
                task_date = datetime.strptime(
                    due_date, "%Y-%m-%d"
                ).date()

                # 해당 날짜의 업무 개수를 1 증가시킨다.
                # get()은 해당 날짜가 딕셔너리에 없으면 기본값 0을 반환한다.
                task_counts[task_date] = (
                    task_counts.get(task_date, 0) + 1
                )

            # 날짜 형식이 올바르지 않으면 해당 업무를 건너뛴다.
            except ValueError:
                continue

        # 일요일부터 시작하는 달력 생성
        # firstweekday=6은 일요일을 한 주의 첫 번째 요일로 설정한다.
        cal = calendar.Calendar(
            firstweekday=6
        )

        # 현재 월을 주 단위로 나눈 날짜 목록을 가져온다.
        # 해당 월에 속하지 않는 빈칸은 숫자 0으로 표시된다.
        weeks = cal.monthdayscalendar(year, month)

        # 각 주의 행 번호와 날짜 목록을 순서대로 가져온다.
        for row, week in enumerate(weeks):

            # 한 주에 포함된 날짜와 열 번호를 순서대로 가져온다.
            for column, day in enumerate(week):

                # 날짜가 0이면 현재 달에 속하지 않는 빈칸이므로 건너뛴다.
                if day == 0:
                    continue

                # 연도, 월, 일을 결합해 날짜 객체를 생성한다.
                current_day = date(year, month, day)

                # 해당 날짜에 등록된 업무 수를 가져온다.
                # 업무가 없으면 0으로 설정한다.
                count = task_counts.get(current_day, 0)

                # 버튼에 표시할 내용
                # 날짜 숫자를 기본 텍스트로 설정한다.
                button_text = str(day)

                # 해당 날짜에 업무가 있으면 업무 개수도 함께 표시한다.
                if count > 0:
                    button_text += f"\n{count}건"

                # 기본 색상
                # 일반 날짜 버튼의 배경색과 글자색을 설정한다.
                button_color = "#E5E7EB"
                text_color = "#222222"

                # 오늘 날짜 표시
                # 오늘 날짜는 다른 날짜와 구분되도록 배경색을 변경한다.
                if current_day == date.today():
                    button_color = "#B7D7F5"

                # 선택된 날짜 표시
                # 선택 날짜는 오늘 날짜보다 우선하여 강조 표시한다.
                if current_day == self.selected_date:
                    button_color = "#3478C8"
                    text_color = "white"

                # 날짜 버튼을 생성한다.
                day_button = ctk.CTkButton(
                    self.days_frame,
                    text=button_text,
                    font=("맑은 고딕", 13, "bold"),
                    fg_color=button_color,
                    hover_color="#8FB8E8",
                    text_color=text_color,
                    corner_radius=8,

                    # lambda의 기본 인수로 현재 날짜를 저장한다.
                    # 이를 통해 각 버튼이 서로 다른 날짜를 선택하도록 한다.
                    command=lambda d=current_day: self.select_date(d)
                )

                # 날짜 버튼을 달력의 해당 행과 열에 배치한다.
                day_button.grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=3,
                    pady=3
                )

    # -----------------------------
    # 선택한 날짜의 일정 표시
    # -----------------------------
    def update_selected_tasks(self):

        # 기존 일정 표시 제거
        # 이전에 생성된 일정 카드나 안내 문구를 모두 삭제한다.
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        # 현재 선택한 날짜를 변수에 저장한다.
        selected = self.selected_date

        # 선택한 날짜를 연도, 월, 일 형식으로 변환하여 표시한다.
        self.selected_date_label.configure(
            text=selected.strftime("%Y년 %m월 %d일")
        )

        # 선택 날짜에 해당하는 일정 검색
        # 선택한 날짜에 마감되는 업무를 저장할 리스트를 생성한다.
        selected_tasks = []

        # 전체 업무를 순회하며 마감일이 선택 날짜와 일치하는지 확인한다.
        for task in self.tasks:

            # 선택 날짜를 YYYY-MM-DD 문자열로 변환해 마감일과 비교한다.
            if task["due_date"] == selected.strftime("%Y-%m-%d"):
                selected_tasks.append(task)

        # 선택한 날짜에 업무가 없으면 안내 문구를 표시하고 함수를 종료한다.
        if not selected_tasks:
            empty_label = ctk.CTkLabel(
                self.task_list_frame,
                text="등록된 일정이 없습니다.",
                font=("맑은 고딕", 14),
                text_color="gray"
            )
            empty_label.pack(pady=30)
            return

        # 중요도 순서대로 정렬
        # 중요도에 따라 정렬할 수 있도록 각각의 숫자를 지정한다.
        importance_order = {
            "높음": 0,
            "보통": 1,
            "낮음": 2
        }

        # sort()를 사용해 중요도가 높은 업무부터 정렬한다.
        # 딕셔너리에 없는 중요도는 기본값 3으로 처리한다.
        selected_tasks.sort(
            key=lambda task: importance_order.get(
                task["importance"], 3
            )
        )

        # 일정별 카드 생성
        # 정렬된 업무를 하나씩 카드 형태로 화면에 표시한다.
        for task in selected_tasks:
            self.create_task_card(task)

    # -----------------------------
    # 일정 카드 생성
    # -----------------------------
    def create_task_card(self, task):

        # 업무 한 건을 표시할 카드 프레임을 생성한다.
        card = ctk.CTkFrame(
            self.task_list_frame,
            corner_radius=10
        )
        card.pack(
            fill="x",
            padx=5,
            pady=6
        )

        # 업무 카테고리에 따라 서로 다른 색상을 지정한다.
        category_colors = {
            "학업 관리": "#3478C8",
            "동아리 관리": "#2E9D75",
            "행사 관리": "#D58A32"
        }

        # 업무의 카테고리에 해당하는 색상을 가져온다.
        # 등록되지 않은 카테고리라면 기본 회색을 사용한다.
        category_color = category_colors.get(
            task["category"], "#777777"
        )

        # 업무의 카테고리를 카드 상단에 표시한다.
        category_label = ctk.CTkLabel(
            card,
            text=task["category"],
            font=("맑은 고딕", 11, "bold"),
            text_color=category_color
        )
        category_label.pack(
            anchor="w", padx=12, pady=(10, 2)
        )

        # 업무 제목을 가져온다.
        title_text = task["title"]

        # 업무가 완료된 상태라면 제목 뒤에 완료 표시를 추가한다.
        if task["completed"]:
            title_text += "  (완료)"

        # 업무 제목을 카드에 표시한다.
        title_label = ctk.CTkLabel(
            card,
            text=title_text,
            font=("맑은 고딕", 14, "bold"),
            wraplength=250,
            justify="left"
        )
        title_label.pack(
            anchor="w", padx=12, pady=3
        )

        # 업무의 중요도를 표시한다.
        # 중요도가 입력되지 않은 경우에는 '미설정'으로 표시한다.
        importance_label = ctk.CTkLabel(
            card,
            text=f"중요도: {task['importance'] or '미설정'}",
            font=("맑은 고딕", 11),
            text_color="gray"
        )
        importance_label.pack(
            anchor="w", padx=12, pady=(0, 3)
        )

        # 담당자가 입력되어 있는 경우에만 담당자 정보를 표시한다.
        if task["assignee"]:
            assignee_label = ctk.CTkLabel(
                card,
                text=f"담당자: {task['assignee']}",
                font=("맑은 고딕", 11),
                text_color="gray"
            )
            assignee_label.pack(
                anchor="w", padx=12, pady=(0, 3)
            )

        # 상세 내용이 입력되어 있는 경우에만 상세 내용을 표시한다.
        if task["detail"]:
            detail_label = ctk.CTkLabel(
                card,
                text=task["detail"],
                font=("맑은 고딕", 11),
                wraplength=250,
                justify="left"
            )
            detail_label.pack(
                anchor="w", padx=12, pady=(0, 10)
            )

        # 상세 내용이 없는 경우 카드 아래쪽 여백을 설정한다.
        else:
            card.pack_configure(pady=6)