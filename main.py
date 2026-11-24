# CustomTkinter: 프로그램의 창, 버튼, 탭 등 GUI 요소를 만드는 라이브러리
import customtkinter as ctk
# ttk: 업무 목록을 표 형태로 표시하는 Treeview 등의 위젯을 사용
from tkinter import ttk

# 기능별로 분리해 둔 다른 Python 파일에서 필요한 클래스와 함수를 가져옴
from database import init_database       # 데이터베이스 초기화 함수
from task_service import CATEGORIES      # 업무 관리 카테고리 목록
from dashboard import Dashboard          # 대시보드 화면
from task_tab import TaskTab             # 카테고리별 업무 관리 화면
from calendar_view import CalendarView   # 통합 달력 화면


# =================================
# 1. 전체 디자인 설정
# =================================

# 프로그램 전체에 어두운 화면 테마와 파란색 계열의 기본 테마 적용
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 프로그램에서 공통으로 사용할 글꼴
FONT_FAMILY = "Pretendard"

# 화면 요소별 색상을 딕셔너리로 관리
# 색상을 한곳에 모아 두면 디자인을 일관되게 유지하고 수정하기 편리함
COLORS = {
    "background": "#151A2B",       # 전체 창 배경
    "header": "#1D243A",           # 상단 헤더 배경
    "surface": "#1B2236",          # 주요 화면 배경
    "surface_light": "#252E47",    # 보조 화면 및 탭 버튼 배경
    "primary": "#548CFF",          # 주요 강조 색상
    "primary_hover": "#6A9BFF",    # 주요 요소에 마우스를 올렸을 때의 색상
    "text": "#F1F4FC",              # 기본 글자 색상
    "subtext": "#AAB4CE",           # 보조 글자 색상
    "success": "#54D6A1",           # 정상·완료 상태 색상
    "warning": "#FFB45E",           # 주의 상태 색상
    "danger": "#FF6B75",            # 위험·삭제 상태 색상
}


# 메인 프로그램 창을 만드는 클래스
# CustomTkinter의 CTk를 상속받아 창과 전체 화면 구성을 관리
class SchoolManager(ctk.CTk):

    # 객체가 만들어질 때 자동으로 실행되는 초기화 함수
    def __init__(self):
        # 부모 클래스인 CTk의 초기화 기능 실행
        super().__init__()

        # 프로그램 창의 제목, 기본 크기, 최소 크기 설정
        self.title("School Manager")
        self.geometry("1200x850")
        self.minsize(1000, 720)

        # 메인 창 전체에 배경색 적용
        self.configure(
            fg_color=COLORS["background"]
        )

        # 프로그램 실행에 필요한 데이터베이스와 테이블 준비
        init_database()

        # 업무 목록 표(Treeview)의 글꼴, 색상, 행 높이 설정
        self.setup_table_style()

        # 헤더와 탭, 각 기능 화면을 생성
        self.build_ui()

    # =================================
    # 2. 테이블 디자인
    # =================================

    # 업무 목록 표의 글꼴과 색상, 행 높이 등을 설정하는 함수
    def setup_table_style(self):

        # 현재 창에 적용할 ttk 스타일 객체 생성
        style = ttk.Style(self)
        # 표의 디자인을 세부적으로 지정할 수 있는 clam 테마 선택
        style.theme_use("clam")

        # 표의 데이터가 표시되는 본문 디자인
        style.configure(
            "Treeview",
            background="#222940",       # 표 배경색
            foreground="#E8ECF5",       # 표 글자색
            fieldbackground="#222940",  # 데이터 영역 배경색
            rowheight=40,               # 각 행의 높이
            font=(FONT_FAMILY, 14),     # 글꼴과 글자 크기
            borderwidth=0               # 테두리 두께
        )

        # 표의 열 제목 부분 디자인
        style.configure(
            "Treeview.Heading",
            background="#303A55",       # 제목 영역 배경색
            foreground="#FFFFFF",       # 제목 글자색
            font=(FONT_FAMILY, 13, "bold"),
            relief="flat",              # 평평한 형태로 표시
            padding=(10, 12)            # 제목 주변 여백
        )

        # 마우스를 열 제목 위에 올렸을 때 배경색 변경
        style.map(
            "Treeview.Heading",
            background=[
                ("active", "#405071")
            ]
        )

        # 표에서 선택한 행의 배경색과 글자색 지정
        style.map(
            "Treeview",
            background=[
                ("selected", "#315B91")
            ],
            foreground=[
                ("selected", "#FFFFFF")
            ]
        )

    # =================================
    # 3. 메인 화면 구성
    # =================================

    # 헤더, 탭 메뉴, 각 기능 화면을 생성하고 배치하는 함수
    def build_ui(self):

        # 메인 창의 첫 번째 열이 남는 가로 공간을 채우도록 설정
        self.grid_columnconfigure(0, weight=1)
        # 두 번째 행이 남는 세로 공간을 채우도록 설정
        self.grid_rowconfigure(1, weight=1)

        # ---------------------------------
        # 상단 헤더
        # ---------------------------------

        # 프로그램 제목과 설명을 표시할 상단 프레임 생성
        header = ctk.CTkFrame(
            self,
            corner_radius=0,             # 모서리를 둥글게 하지 않음
            fg_color=COLORS["header"],   # 헤더 배경색
            height=90                    # 헤더 높이
        )

        # 헤더를 메인 창의 첫 번째 행에 배치하고 가로로 확장
        header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        # 내부 위젯 크기에 따라 헤더 크기가 자동 변경되지 않도록 설정
        header.grid_propagate(False)
        # 헤더의 두 번째 열이 남는 가로 공간을 차지하도록 설정
        header.grid_columnconfigure(1, weight=1)

        # 프로그램 이름을 표시하는 레이블 생성
        title = ctk.CTkLabel(
            header,
            text="School Manager",
            font=(FONT_FAMILY, 30, "bold"),
            text_color=COLORS["text"]
        )

        # 제목을 헤더 왼쪽에 배치하고 여백 지정
        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(30, 18),
            pady=15
        )

        # 프로그램의 용도를 설명하는 부제목 레이블 생성
        subtitle = ctk.CTkLabel(
            header,
            text="학교생활 통합 관리 프로그램",
            font=(FONT_FAMILY, 15),
            text_color=COLORS["subtext"]
        )

        # 부제목을 제목 오른쪽에 배치
        subtitle.grid(
            row=0,
            column=1,
            sticky="w",
            pady=15
        )

        # 프로그램의 준비 상태를 표시하는 레이블 생성
        status = ctk.CTkLabel(
            header,
            text="●  SYSTEM READY",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["success"]
        )

        # 상태 표시를 헤더 오른쪽에 배치
        status.grid(
            row=0,
            column=2,
            padx=30
        )

        # ---------------------------------
        # 헤더 아래 강조선
        # ---------------------------------

        # 헤더 아래에 파란색 강조선을 표시할 프레임 생성
        accent_line = ctk.CTkFrame(
            self,
            height=3,
            corner_radius=0,
            fg_color=COLORS["primary"]
        )

        # 강조선을 헤더와 같은 행의 아래쪽에 배치
        accent_line.grid(
            row=0,
            column=0,
            sticky="sew"
        )

        # ---------------------------------
        # 탭 화면
        # ---------------------------------

        # 기능별 화면을 탭으로 전환할 수 있는 Tabview 생성
        self.tabs = ctk.CTkTabview(
            self,
            corner_radius=16,  # 탭 화면 모서리 둥글기
            fg_color=COLORS["surface"],

            segmented_button_fg_color=COLORS["surface_light"],

            # 현재 선택된 탭 버튼의 기본색과 마우스 오버 색상
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],

            # 선택되지 않은 탭 버튼의 기본색과 마우스 오버 색상
            segmented_button_unselected_color=COLORS["surface_light"],
            segmented_button_unselected_hover_color="#35415E",

            text_color=COLORS["text"]  # 탭 버튼 글자색
        )

        # 탭 화면을 메인 창의 두 번째 행에 배치
        # sticky="nsew"는 위·아래·왼쪽·오른쪽으로 모두 확장한다는 의미
        self.tabs.grid(
            row=1,
            column=0,
            padx=22,
            pady=22,
            sticky="nsew"
        )

        # ---------------------------------
        # 탭 생성
        # ---------------------------------

        # 고정적으로 사용하는 대시보드와 통합 달력 탭 생성
        self.tabs.add("대시보드")
        self.tabs.add("통합 달력")

        # CATEGORIES에 들어 있는 항목을 하나씩 꺼내 업무 관리 탭 생성
        for category in CATEGORIES:
            self.tabs.add(category)

        # ---------------------------------
        # 대시보드 연결
        # ---------------------------------

        # 대시보드 탭 안에 Dashboard 클래스의 화면 객체 생성
        self.dashboard = Dashboard(
            self.tabs.tab("대시보드")
        )

        # 대시보드가 탭의 남는 공간을 모두 사용하도록 배치
        self.dashboard.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------
        # 통합 달력 연결
        # ---------------------------------

        # 통합 달력 탭 안에 CalendarView 화면 객체 생성
        self.calendar_view = CalendarView(
            self.tabs.tab("통합 달력")
        )

        # 달력 화면이 탭의 남는 공간을 모두 사용하도록 배치
        self.calendar_view.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------
        # 업무 관리 탭 연결
        # ---------------------------------

        # 카테고리별 업무 화면 객체를 보관할 딕셔너리
        self.task_tabs = {}

        # 각 카테고리에 대해 업무 관리 화면을 하나씩 생성
        for category in CATEGORIES:

            tab = TaskTab(
                self.tabs.tab(category),  # 화면이 들어갈 부모 탭
                category,                 # 관리할 업무의 종류
                self.refresh_all          # 업무 변경 후 전체 화면을 갱신할 함수
            )

            # 업무 관리 화면을 탭 안에 꽉 차게 배치
            tab.pack(
                fill="both",
                expand=True
            )

            # 카테고리 이름을 키로 사용해 해당 화면 객체를 저장
            # 이후 특정 카테고리 화면을 다시 갱신할 때 이용
            self.task_tabs[category] = tab

        # 프로그램을 처음 실행할 때 모든 화면의 정보를 최신 상태로 갱신
        self.refresh_all()

    # =================================
    # 4. 전체 화면 갱신
    # =================================

    # 업무가 추가·수정·삭제되었을 때 여러 화면의 표시 내용을 다시 불러오는 함수
    def refresh_all(self):

        # 대시보드의 업무 개수와 진행률 등의 정보 갱신
        self.dashboard.refresh()

        # 통합 달력의 일정 정보 갱신
        self.calendar_view.refresh()

        # 저장된 모든 업무 관리 화면을 순서대로 갱신
        for tab in self.task_tabs.values():
            tab.refresh()


# =================================
# 5. 프로그램 실행
# =================================

# 이 파일을 직접 실행했을 때만 아래 코드가 실행됨
# 다른 파일에서 main.py를 불러오는 경우에는 프로그램 창이 자동 실행되지 않음
if __name__ == "__main__":

    # SchoolManager 클래스로 프로그램 창 객체 생성
    app = SchoolManager()

    # 창을 닫을 때까지 버튼 클릭, 키보드 입력 등의 이벤트를 처리
    app.mainloop()
