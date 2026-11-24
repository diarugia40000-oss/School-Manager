
# CustomTkinter는 대시보드의 전체 화면과 카드형 UI를 구성하고,
# tkinter Canvas는 진행률 그래프를 직접 그리는 데 사용한다.
import customtkinter as ctk
import tkinter as tk

# 실제 업무 통계와 마감일 데이터는 task_service.py의 함수를 통해 데이터베이스에서 가져온다.
from task_service import (
    get_task_statistics,
    get_category_statistics,
    get_deadline_tasks
)


# =================================
# 디자인 설정
# =================================

FONT = "Pretendard"

COLORS = {
    "background": "#151A2B",
    "card": "#202941",
    "card_hover": "#293550",
    "text": "#F1F4FC",
    "subtext": "#AAB4CE",

    "blue": "#548CFF",
    "green": "#54D6A1",
    "orange": "#FFB45E",
    "purple": "#C18BFF",
    "red": "#FF6B75",

    "graph_bg": "#1B2338",
    "graph_line": "#35415B",
}


class Dashboard(ctk.CTkFrame):
    """전체 업무 수와 분야별 진행률, 마감일 정보를 한눈에 보여주는 대시보드."""

    def __init__(self, master):
        super().__init__(
            master,
            fg_color="transparent"
        )

        # 대시보드에 필요한 위젯을 먼저 생성한다.
        self.build_ui()

        # Canvas 크기가 바뀌면 그래프도 새 크기에 맞춰 다시 그리도록 이벤트를 연결한다.
        self.graph_canvas.bind(
            "<Configure>",
            self.on_graph_resize
        )

        # 화면 생성 직후 데이터베이스의 최신 정보를 화면에 반영한다.
        self.refresh()

    # =================================
    # 화면 구성
    # =================================

    def build_ui(self):
        """제목, 통계 카드, 분야별 그래프, 마감일 알림 영역을 배치한다."""

        # 창 크기가 변할 때 각 영역이 가로·세로 방향으로 확장될 수 있게 설정한다.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 제목 영역
        title_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        title_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=25,
            pady=(20, 5)
        )

        ctk.CTkLabel(
            title_frame,
            text="전체 업무 현황",
            font=(FONT, 29, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="학업, 동아리, 행사 업무의 진행 상황을 확인하세요.",
            font=(FONT, 16),
            text_color=COLORS["subtext"]
        ).pack(
            anchor="w",
            pady=(7, 0)
        )

        # =================================
        # 통계 카드 영역
        # =================================

        self.stats_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.stats_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=(15, 10)
        )

        # 통계 카드 4개가 같은 너비를 갖도록 uniform 옵션을 사용한다.
        for i in range(4):
            self.stats_frame.grid_columnconfigure(
                i,
                weight=1,
                uniform="stats"
            )

        # 카드 생성 함수가 반환하는 숫자 라벨을 저장해 두면,
        # 이후 통계가 바뀔 때 카드 전체를 다시 만들지 않고 숫자만 갱신할 수 있다.
        self.total_label = self.create_stat_card(
            self.stats_frame,
            0,
            "전체 업무",
            COLORS["blue"],
            "등록된 전체 업무"
        )

        self.unfinished_label = self.create_stat_card(
            self.stats_frame,
            1,
            "미완료 업무",
            COLORS["orange"],
            "진행이 필요한 업무"
        )

        self.completed_label = self.create_stat_card(
            self.stats_frame,
            2,
            "완료 업무",
            COLORS["green"],
            "완료 처리된 업무"
        )

        self.rate_label = self.create_stat_card(
            self.stats_frame,
            3,
            "전체 완료율",
            COLORS["purple"],
            "전체 업무 진행률"
        )

        # =================================
        # 아래쪽 콘텐츠 영역
        # =================================

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(5, 20)
        )

        # 왼쪽 그래프 영역을 오른쪽 마감일 알림 영역보다 넓게 배치한다.
        self.content_frame.grid_columnconfigure(
            0,
            weight=3
        )

        self.content_frame.grid_columnconfigure(
            1,
            weight=2
        )

        self.content_frame.grid_rowconfigure(
            0,
            weight=1
        )

        # =================================
        # 분야별 진행률 그래프
        # =================================

        self.graph_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["card"],
            corner_radius=18
        )

        self.graph_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
            pady=5
        )

        ctk.CTkLabel(
            self.graph_frame,
            text="분야별 업무 진행률",
            font=(FONT, 22, "bold"),
            text_color=COLORS["text"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 4)
        )

        ctk.CTkLabel(
            self.graph_frame,
            text="각 분야의 업무 완료 비율을 확인할 수 있습니다.",
            font=(FONT, 15),
            text_color=COLORS["subtext"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 12)
        )

        # Canvas는 선, 사각형, 글자 등을 좌표로 직접 배치할 수 있어 막대그래프에 적합하다.
        self.graph_canvas = tk.Canvas(
            self.graph_frame,
            height=300,
            bg=COLORS["graph_bg"],
            highlightthickness=0,
            bd=0
        )

        self.graph_canvas.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(5, 18)
        )

        # =================================
        # 마감일 알림
        # =================================

        self.deadline_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["card"],
            corner_radius=18
        )

        self.deadline_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
            pady=5
        )

        ctk.CTkLabel(
            self.deadline_frame,
            text="마감일 알림",
            font=(FONT, 22, "bold"),
            text_color=COLORS["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 4)
        )

        ctk.CTkLabel(
            self.deadline_frame,
            text="확인이 필요한 업무를 알려드립니다.",
            font=(FONT, 15),
            text_color=COLORS["subtext"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        # 마감일별 업무 목록을 여러 줄로 표시하기 위해 Textbox를 사용한다.
        self.deadline_text = ctk.CTkTextbox(
            self.deadline_frame,
            font=(FONT, 16),
            wrap="word",
            corner_radius=12,
            fg_color=COLORS["graph_bg"],
            text_color=COLORS["text"],
            border_width=0,
            scrollbar_button_color="#465575",
            scrollbar_button_hover_color="#60749C"
        )

        self.deadline_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # 마감일 알림 텍스트 색상
        # CTkTextbox는 tag_config에서 font 옵션을 지원하지 않음
        # Textbox의 tag를 이용해 마감 상태와 업무 설명에 서로 다른 글자색을 적용한다.
        self.deadline_text.tag_config(
            "overdue",
            foreground=COLORS["red"]
        )

        self.deadline_text.tag_config(
            "today",
            foreground=COLORS["orange"]
        )

        self.deadline_text.tag_config(
            "soon",
            foreground=COLORS["blue"]
        )

        self.deadline_text.tag_config(
            "task",
            foreground=COLORS["text"]
        )

        self.deadline_text.tag_config(
            "sub",
            foreground=COLORS["subtext"]
        )

    # =================================
    # 통계 카드 생성
    # =================================

    def create_stat_card(
        self,
        parent,
        column,
        title,
        color,
        description
    ):
        """통계 카드 하나를 만들고, 나중에 숫자를 바꿀 수 있는 라벨을 반환한다."""

        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color="#303B55"
        )

        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=5,
            pady=5
        )

        card.grid_columnconfigure(0, weight=1)

        # 포인트 컬러 바
        ctk.CTkFrame(
            card,
            fg_color=color,
            height=5,
            corner_radius=5
        ).pack(
            fill="x",
            padx=14,
            pady=(13, 0)
        )

        # 카드 제목
        ctk.CTkLabel(
            card,
            text=title,
            font=(FONT, 17, "bold"),
            text_color=COLORS["subtext"]
        ).pack(
            anchor="w",
            padx=17,
            pady=(15, 5)
        )

        # 통계 숫자
        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=(FONT, 34, "bold"),
            text_color=color
        )

        value_label.pack(
            anchor="w",
            padx=17,
            pady=(0, 3)
        )

        # 카드 설명
        ctk.CTkLabel(
            card,
            text=description,
            font=(FONT, 14),
            text_color=COLORS["subtext"]
        ).pack(
            anchor="w",
            padx=17,
            pady=(0, 15)
        )

        # 호출한 쪽에서 이 라벨의 text만 변경할 수 있도록 반환한다.
        return value_label

    # =================================
    # 전체 데이터 갱신
    # =================================

    def refresh(self):
        """통계, 그래프, 마감일 알림을 한 번에 최신 데이터로 갱신한다."""

        self.update_statistics()
        self.update_graph()
        self.update_deadlines()

    # =================================
    # 통계 갱신
    # =================================

    def update_statistics(self):
        """전체 업무 수와 완료율을 계산해 상단 통계 카드에 표시한다."""

        # 데이터베이스에서 전체 업무, 미완료 업무, 완료 업무의 개수를 가져온다.
        stats = get_task_statistics()

        total = stats["total"]
        unfinished = stats["unfinished"]
        completed = stats["completed"]

        # 전체 업무가 0개일 때 0으로 나누는 오류가 발생하지 않도록 조건식을 사용한다.
        # 완료율은 완료 업무 수를 전체 업무 수로 나눈 뒤 백분율로 환산한다.
        rate = (
            completed / total * 100
            if total > 0
            else 0
        )

        # configure()를 이용해 이미 만들어진 카드의 숫자 표시만 변경한다.
        self.total_label.configure(
            text=str(total)
        )

        self.unfinished_label.configure(
            text=str(unfinished)
        )

        self.completed_label.configure(
            text=str(completed)
        )

        self.rate_label.configure(
            text=f"{rate:.1f}%"
        )

    # =================================
    # 그래프 크기 변경 감지
    # =================================

    def on_graph_resize(self, event):
        """그래프 영역의 크기가 변경되었을 때 새 크기로 그래프를 다시 그린다."""

        # 위젯이 처음 생성되는 과정에서 크기가 너무 작을 때는 그래프를 그리지 않는다.
        if event.width > 100 and event.height > 100:
            self.update_graph()

    # =================================
    # 분야별 진행률 그래프
    # =================================

    def update_graph(self):
        """학업·동아리·행사 분야별 완료율을 Canvas 막대그래프로 표현한다."""

        # 분야별 전체 업무 수와 완료율을 데이터베이스에서 가져온다.
        statistics = get_category_statistics()

        canvas = self.graph_canvas

        # 이전에 그려진 그래프 요소를 모두 지운 뒤 최신 값으로 다시 그린다.
        canvas.delete("all")
        canvas.update_idletasks()

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        # 그래프를 표시하기에 캔버스가 너무 작으면 계산과 그리기를 중단한다.
        if width < 150 or height < 150:
            return

        # 각 분야의 이름과 그래프 막대에 사용할 색상을 함께 저장한다.
        categories = [
            ("학업 관리", COLORS["blue"]),
            ("동아리 관리", COLORS["green"]),
            ("행사 관리", COLORS["orange"])
        ]

        # 그래프 영역
        left = 58
        right = width - 22
        top = 42
        bottom = height - 88

        # 그래프가 실제로 그려질 수 있는 가로·세로 길이를 계산한다.
        graph_height = bottom - top
        graph_width = right - left

        if graph_height <= 0 or graph_width <= 0:
            return

        # 배경 기준선 및 세로축 숫자
        # 세로축을 0~100% 범위에서 20% 간격으로 나누어 기준선을 표시한다.
        for value in range(0, 101, 20):

            # 백분율이 커질수록 화면 위쪽에 위치하도록 y좌표를 계산한다.
            y = bottom - graph_height * value / 100

            canvas.create_line(
                left,
                y,
                right,
                y,
                fill=COLORS["graph_line"],
                width=1
            )

            canvas.create_text(
                left - 12,
                y,
                text=f"{value}%",
                anchor="e",
                fill=COLORS["subtext"],
                font=(FONT, 12)
            )

        # 막대 간격 계산
        slot_width = graph_width / 3

        # 기존보다 막대 너비 확대
        bar_width = min(
            90,
            slot_width * 0.58
        )

        # 분야별 데이터를 순서대로 읽어 막대 하나씩 그린다.
        for i, (category, color) in enumerate(categories):

            data = statistics[category]

            # 해당 분야의 완료율을 가져와 막대 높이 계산에 사용한다.
            rate = data["rate"]

            center_x = left + slot_width * (i + 0.5)

            x1 = center_x - bar_width / 2
            x2 = center_x + bar_width / 2

            # 완료율을 그래프 전체 높이에 대한 비율로 바꾸어 막대 높이를 구한다.
            bar_height = graph_height * rate / 100

            y1 = bottom - bar_height

            # 기본 막대 배경
            canvas.create_rectangle(
                x1,
                top,
                x2,
                bottom,
                fill="#303B55",
                outline=""
            )

            # 실제 진행률
            # 완료율이 0보다 클 때만 실제 진행률 막대를 그린다.
            if rate > 0:

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    bottom,
                    fill=color,
                    outline=""
                )

            # 완료율 숫자
            canvas.create_text(
                center_x,
                max(top - 15, y1 - 18),
                text=f"{rate:.1f}%",
                fill=color,
                font=(FONT, 15, "bold")
            )

            # 분야 이름
            canvas.create_text(
                center_x,
                bottom + 25,
                text=category.replace(" 관리", ""),
                fill=COLORS["text"],
                font=(FONT, 16, "bold")
            )

            # 완료 업무 / 전체 업무
            canvas.create_text(
                center_x,
                bottom + 52,
                text=f'{data["completed"]} / {data["total"]}',
                fill=COLORS["subtext"],
                font=(FONT, 12)
            )

    # =================================
    # 마감일 알림 갱신
    # =================================

    def update_deadlines(self):
        """마감일이 지난 업무, 오늘 마감인 업무, 3일 이내 마감인 업무를 표시한다."""

        # task_service에서 분류해 반환한 마감일 정보를 가져온다.
        deadline_data = get_deadline_tasks()

        # 내용을 수정하기 위해 Textbox를 잠시 활성화한다.
        self.deadline_text.configure(
            state="normal"
        )

        # 이전에 표시한 알림을 지우고 최신 업무 목록으로 교체한다.
        self.deadline_text.delete(
            "1.0",
            "end"
        )

        # 각 분류의 내부 키, 화면에 표시할 제목, 제목 색상을 묶어 관리한다.
        sections = [
            (
                "overdue",
                "마감일이 지난 업무",
                COLORS["red"]
            ),
            (
                "today",
                "오늘 마감인 업무",
                COLORS["orange"]
            ),
            (
                "soon",
                "3일 이내 마감인 업무",
                COLORS["blue"]
            )
        ]

        # 마감일 분류별로 제목과 해당 업무 목록을 차례대로 출력한다.
        for key, title, color in sections:

            tasks = deadline_data[key]

            # 섹션 제목
            self.deadline_text.insert(
                "end",
                f"\n● {title}\n",
                key
            )

            # 해당 분류에 업무가 없으면 안내 문구를 표시한다.
            if not tasks:

                self.deadline_text.insert(
                    "end",
                    "  해당 업무가 없습니다.\n\n",
                    "sub"
                )

            else:

                # 업무가 있으면 업무명, 마감일, 분야를 각각 다른 줄에 표시한다.
                for task in tasks:

                    self.deadline_text.insert(
                        "end",
                        f'  {task["title"]}\n',
                        "task"
                    )

                    self.deadline_text.insert(
                        "end",
                        f'  마감일: {task["due_date"]}\n',
                        "sub"
                    )

                    self.deadline_text.insert(
                        "end",
                        f'  분야: {task["category"]}\n\n',
                        "sub"
                    )

        # 사용자가 알림 내용을 직접 수정하지 못하도록 다시 비활성화한다.
        self.deadline_text.configure(
            state="disabled"
        )
