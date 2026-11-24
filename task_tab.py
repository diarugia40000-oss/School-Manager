import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date


# 프로그램 전체에서 사용할 글꼴을 지정한다.
FONT = "Pretendard"


# 데이터베이스와 연결된 업무 처리 함수들을 가져온다.
# 실제 데이터 추가, 조회, 수정, 삭제는 task_service.py에서 처리한다.
from task_service import (
    add_task,
    get_tasks_by_category,
    get_task,
    update_task,
    complete_task,
    undo_complete_task,
    delete_task
)


class TaskTab(ctk.CTkFrame):
    """
    학업, 동아리, 행사 등 각 분야의 업무를 관리하는 화면이다.
    CTkFrame을 상속받아 기존 프로그램의 화면 안에 탭 형태로 배치할 수 있다.
    """

    def __init__(self, master, category, refresh_callback):
        # 부모 화면을 기준으로 새로운 프레임을 생성한다.
        super().__init__(master)

        # 현재 화면이 관리할 업무 분야를 저장한다.
        self.category = category

        # 업무 변경 후 대시보드와 캘린더 등을 갱신하기 위한 함수를 저장한다.
        self.refresh_callback = refresh_callback

        # 부모 화면의 배경색을 그대로 사용하도록 설정한다.
        self.configure(fg_color="transparent")

        # 화면에 필요한 위젯을 배치하고 업무 목록을 불러온다.
        self.build_ui()
        self.refresh()

    # -----------------------------
    # 화면 구성
    # -----------------------------

    def build_ui(self):
        """
        업무 등록 영역과 업무 목록 영역을 생성하고 배치한다.
        """

        # 창 크기가 변경될 때 첫 번째 열과 업무 목록 영역이 함께 늘어나도록 설정한다.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 현재 관리 중인 업무 분야를 화면 상단에 표시한다.
        ctk.CTkLabel(
            self,
            text=self.category,
            font=(FONT, 28, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(15, 10)
        )

        # -----------------------------
        # 업무 등록 영역
        # -----------------------------

        # 업무 정보를 입력할 수 있는 프레임을 생성한다.
        form_frame = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        form_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=15,
            pady=10
        )

        # 입력 항목 옆의 입력창이 남은 공간을 차지하도록 설정한다.
        form_frame.grid_columnconfigure(1, weight=1)

        # 업무명 입력 항목의 이름을 표시한다.
        ctk.CTkLabel(
            form_frame,
            text="업무명",
            font=(FONT, 15, "bold")
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=8
        )

        # 사용자가 업무명을 입력할 수 있는 입력창을 생성한다.
        self.title_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="업무명을 입력하세요",
            font=(FONT, 15)
        )

        self.title_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=8
        )

        # 상세 내용 입력 항목의 이름을 표시한다.
        ctk.CTkLabel(
            form_frame,
            text="상세 내용",
            font=(FONT, 15, "bold")
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=8
        )

        # 업무에 대한 추가 설명을 입력할 수 있는 창을 생성한다.
        self.detail_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="상세 내용을 입력하세요",
            font=(FONT, 15)
        )

        self.detail_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=8
        )

        # 마감일 입력 항목의 이름을 표시한다.
        ctk.CTkLabel(
            form_frame,
            text="마감일",
            font=(FONT, 15, "bold")
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=8
        )

        # 업무의 마감일을 입력할 수 있는 창을 생성한다.
        self.date_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="YYYY-MM-DD",
            font=(FONT, 15)
        )

        self.date_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=8
        )

        # 키보드 입력이 발생할 때마다 날짜 형식을 자동으로 정리한다.
        # 예: 20261120을 입력하면 2026-11-20으로 표시한다.
        self.date_entry.bind(
            "<KeyRelease>",
            lambda event: self.format_date_entry(self.date_entry)
        )

        # 중요도 입력 항목의 이름을 표시한다.
        ctk.CTkLabel(
            form_frame,
            text="중요도",
            font=(FONT, 15, "bold")
        ).grid(
            row=3,
            column=0,
            padx=10,
            pady=8
        )

        # 중요도를 선택할 수 있는 버튼 3개를 생성한다.
        # 선택한 중요도는 StringVar에 저장된다.
        self.importance_var, self.importance_selector = self.create_importance_selector(
            form_frame,
            initial="보통"
        )

        self.importance_selector.grid(
            row=3,
            column=1,
            sticky="w",
            padx=10,
            pady=8
        )

        # 담당자 입력 항목의 이름을 표시한다.
        ctk.CTkLabel(
            form_frame,
            text="담당자",
            font=(FONT, 15, "bold")
        ).grid(
            row=4,
            column=0,
            padx=10,
            pady=8
        )

        # 업무를 담당하는 사람의 이름을 입력할 수 있는 창을 생성한다.
        self.assignee_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="담당자 입력 (선택)",
            font=(FONT, 15)
        )

        self.assignee_entry.grid(
            row=4,
            column=1,
            sticky="ew",
            padx=10,
            pady=8
        )

        # 버튼을 누르면 입력한 정보를 데이터베이스에 등록한다.
        ctk.CTkButton(
            form_frame,
            text="업무 등록",
            font=(FONT, 15, "bold"),
            command=self.add_new_task
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            padx=10,
            pady=12
        )

        # -----------------------------
        # 업무 목록 영역
        # -----------------------------

        # 등록된 업무를 표 형태로 보여줄 프레임을 생성한다.
        list_frame = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        list_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=15,
            pady=10
        )

        # 표가 창의 크기에 맞게 확장되도록 설정한다.
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # 업무 목록의 제목을 표시한다.
        ctk.CTkLabel(
            list_frame,
            text="업무 목록",
            font=(FONT, 21, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=10
        )

        # -----------------------------
        # 업무 목록 표 설정
        # -----------------------------

        # tkinter의 표 형식 위젯인 Treeview의 디자인을 설정한다.
        style = ttk.Style()

        # 업무 목록의 행 높이와 글꼴을 지정한다.
        style.configure(
            "Treeview",
            rowheight=48,
            font=(FONT, 15)
        )

        # 표의 제목 부분에 사용할 글꼴을 지정한다.
        style.configure(
            "Treeview.Heading",
            font=(FONT, 15, "bold")
        )

        # 표에 표시할 데이터 항목을 튜플로 정의한다.
        columns = (
            "id",
            "title",
            "due_date",
            "importance",
            "assignee",
            "status"
        )

        # 실제 업무 데이터를 표시할 Treeview를 생성한다.
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # 각 열에 표시될 제목을 지정한다.
        self.tree.heading("id", text="번호")
        self.tree.heading("title", text="업무명")
        self.tree.heading("due_date", text="마감일")
        self.tree.heading("importance", text="중요도")
        self.tree.heading("assignee", text="담당자")
        self.tree.heading("status", text="상태")

        # 각 열의 너비와 글자 정렬 방식을 설정한다.
        self.tree.column("id", width=55, anchor="center")
        self.tree.column("title", width=220)
        self.tree.column("due_date", width=120, anchor="center")
        self.tree.column("importance", width=90, anchor="center")
        self.tree.column("assignee", width=100, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        # 표를 화면에 배치한다.
        self.tree.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        # 업무가 많아졌을 때 목록을 위아래로 이동할 수 있도록 스크롤바를 생성한다.
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.grid(
            row=1,
            column=1,
            sticky="ns",
            pady=10
        )

        # 표의 스크롤 위치와 스크롤바를 서로 연결한다.
        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        # -----------------------------
        # 중요도별 글자 색상 설정
        # -----------------------------

        # 중요도에 따라 표에 표시되는 글자 색상을 다르게 지정한다.
        self.tree.tag_configure(
            "importance_high",
            foreground="#FF6B75"
        )
        self.tree.tag_configure(
            "importance_medium",
            foreground="#FFD166"
        )
        self.tree.tag_configure(
            "importance_low",
            foreground="#54D6A1"
        )

        # 업무 항목을 더블클릭하면 상세 정보 창을 실행한다.
        self.tree.bind(
            "<Double-1>",
            self.show_task_detail
        )

        # -----------------------------
        # 업무 관리 버튼 영역
        # -----------------------------

        # 완료, 수정, 삭제 버튼을 배치할 프레임을 생성한다.
        button_frame = ctk.CTkFrame(
            list_frame,
            fg_color="transparent"
        )

        button_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=12
        )

        # 선택한 업무의 완료 상태를 변경하는 버튼이다.
        ctk.CTkButton(
            button_frame,
            text="완료 / 완료 취소",
            font=(FONT, 15, "bold"),
            command=self.toggle_complete
        ).pack(
            side="left",
            padx=5
        )

        # 선택한 업무의 정보를 수정하는 버튼이다.
        ctk.CTkButton(
            button_frame,
            text="업무 수정",
            font=(FONT, 15, "bold"),
            command=self.edit_task
        ).pack(
            side="left",
            padx=5
        )

        # 선택한 업무를 삭제하는 버튼이다.
        ctk.CTkButton(
            button_frame,
            text="업무 삭제",
            font=(FONT, 15, "bold"),
            fg_color="#C94C4C",
            hover_color="#A83B3B",
            command=self.remove_task
        ).pack(
            side="left",
            padx=5
        )

    # -----------------------------
    # 날짜 자동 하이픈 입력
    # -----------------------------

    def format_date_entry(self, entry):
        """
        사용자가 숫자 8자리를 입력하면 YYYY-MM-DD 형식으로 자동 변환한다.
        입력 도중에도 커서 위치가 크게 바뀌지 않도록 처리한다.
        """

        # 현재 입력된 문자열과 커서 위치를 가져온다.
        current_text = entry.get()
        cursor_position = entry.index("insert")

        # 커서 앞에 입력된 숫자의 개수를 기억해 커서 위치를 보정한다.
        digits_before_cursor = sum(
            character.isdigit()
            for character in current_text[:cursor_position]
        )

        # 숫자가 아닌 문자를 제거하고 최대 8자리까지만 가져온다.
        digits = "".join(
            character for character in current_text
            if character.isdigit()
        )[:8]

        # 입력된 숫자의 길이에 따라 하이픈을 추가한다.
        if len(digits) <= 4:
            formatted = digits
        elif len(digits) <= 6:
            formatted = f"{digits[:4]}-{digits[4:]}"
        else:
            formatted = f"{digits[:4]}-{digits[4:6]}-{digits[6:]}"

        # 기존 문자열과 변환된 문자열이 다를 때만 입력창을 갱신한다.
        if formatted != current_text:
            entry.delete(0, "end")
            entry.insert(0, formatted)

            # 하이픈이 추가된 위치를 고려하여 커서 위치를 다시 계산한다.
            new_cursor = digits_before_cursor
            if digits_before_cursor > 4:
                new_cursor += 1
            if digits_before_cursor > 6:
                new_cursor += 1

            # 계산된 위치가 문자열의 길이를 넘지 않도록 제한한다.
            entry.icursor(min(new_cursor, len(formatted)))

    # -----------------------------
    # 중요도 선택 버튼
    # -----------------------------

    def create_importance_selector(self, parent, initial="보통"):
        """
        높음, 보통, 낮음 중 하나를 선택하는 버튼들을 생성한다.
        선택된 버튼에는 테두리를 표시하여 현재 선택 상태를 구분한다.
        """

        # 중요도별 기본 색상과 마우스를 올렸을 때의 색상을 저장한다.
        colors = {
            "높음": ("#A93643", "#C94B59"),
            "보통": ("#8A6A1F", "#A9852B"),
            "낮음": ("#23734F", "#2D9164")
        }

        # 현재 선택된 중요도를 문자열 변수로 관리한다.
        variable = ctk.StringVar(value=initial)

        # 중요도 버튼들을 배치할 프레임을 생성한다.
        selector = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        # 생성된 버튼을 중요도 이름과 연결하여 저장할 딕셔너리이다.
        buttons = {}

        # 사용자가 특정 중요도 버튼을 선택했을 때 실행되는 함수이다.
        def select_importance(value):

            # 선택한 중요도 값을 변수에 저장한다.
            variable.set(value)

            # 모든 버튼을 확인하여 선택된 버튼에만 테두리를 표시한다.
            for label, button in buttons.items():
                button.configure(
                    border_width=2 if label == value else 0
                )

        # 세 가지 중요도에 대한 버튼을 반복문으로 생성한다.
        for value in ("높음", "보통", "낮음"):

            # 현재 중요도에 해당하는 버튼 색상을 가져온다.
            base_color, hover_color = colors[value]

            button = ctk.CTkButton(
                selector,
                text=value,
                width=72,
                height=34,
                font=(FONT, 14, "bold"),
                text_color="#FFFFFF",
                fg_color=base_color,
                hover_color=hover_color,
                corner_radius=8,

                # 처음 선택된 중요도 버튼에만 테두리를 표시한다.
                border_width=2 if value == initial else 0,
                border_color="#FFFFFF",

                # lambda를 사용해 버튼마다 서로 다른 선택값을 전달한다.
                command=lambda selected=value: select_importance(selected)
            )

            button.pack(
                side="left",
                padx=(0, 6)
            )

            # 나중에 선택 상태를 변경할 수 있도록 버튼을 저장한다.
            buttons[value] = button

        # 선택기마다 자신의 버튼 목록과 선택 함수를 보관한다.
        selector._importance_buttons = buttons
        selector._select_importance = select_importance

        # 선택된 값과 버튼 프레임을 반환한다.
        return variable, selector

    def update_importance_selector(self):
        """
        중요도 값이 변경되었을 때 버튼의 테두리 표시를 갱신한다.
        """

        # 중요도 선택기가 생성되어 있는지 확인한다.
        if hasattr(self, "importance_selector"):

            # 현재 선택된 중요도 값을 가져온다.
            selected = self.importance_var.get()

            # 각 버튼의 선택 상태에 따라 테두리를 설정한다.
            for label, button in self.importance_selector._importance_buttons.items():
                button.configure(
                    border_width=2 if label == selected else 0
                )

    # -----------------------------
    # 마감일 검사
    # -----------------------------

    def validate_due_date(self, due_date, parent=None):
        """
        입력한 마감일이 올바른 형식인지 확인하고,
        이미 지난 날짜가 입력되었는지도 검사한다.
        """

        # 마감일을 입력하지 않은 경우에는 등록을 허용한다.
        if not due_date:
            return True

        try:
            # 입력 문자열을 날짜 객체로 변환한다.
            parsed_date = date.fromisoformat(due_date)

            # 변환된 날짜를 다시 문자열로 바꾸어 형식이 정확한지 확인한다.
            if parsed_date.isoformat() != due_date:
                raise ValueError

        except ValueError:
            # 날짜 형식이 잘못된 경우 경고창을 표시한다.
            messagebox.showwarning(
                "입력 오류",
                "마감일은 YYYY-MM-DD 형식으로 입력해 주세요.",
                parent=parent or self
            )
            return False

        # 오늘보다 이전 날짜는 마감일로 설정할 수 없도록 한다.
        if parsed_date < date.today():
            messagebox.showwarning(
                "마감일 오류",
                "이미 지난 날짜는 마감일로 설정할 수 없습니다.",
                parent=parent or self
            )
            return False

        # 모든 검사를 통과하면 True를 반환한다.
        return True

    # -----------------------------
    # 업무 등록
    # -----------------------------

    def add_new_task(self):
        """
        입력창에 작성한 업무 정보를 가져와 데이터베이스에 저장한다.
        """

        # 각 입력창에서 값을 가져오고 양쪽 공백을 제거한다.
        title = self.title_entry.get().strip()
        detail = self.detail_entry.get().strip()
        due_date = self.date_entry.get().strip()
        importance = self.importance_var.get()
        assignee = self.assignee_entry.get().strip()

        # 업무명은 필수 입력 항목이므로 비어 있는지 확인한다.
        if not title:
            messagebox.showwarning(
                "입력 오류",
                "업무명을 입력해 주세요.",
                parent=self
            )
            return

        # 마감일이 올바르지 않으면 이후 등록 과정을 중단한다.
        if not self.validate_due_date(due_date):
            return

        # 입력한 업무 정보를 데이터베이스에 추가한다.
        add_task(
            self.category,
            title,
            detail,
            due_date,
            importance,
            assignee
        )

        # 등록이 끝나면 입력창을 비우고 관련 화면을 갱신한다.
        self.clear_form()
        self.refresh_all()

        # 업무가 정상적으로 등록되었음을 사용자에게 알린다.
        messagebox.showinfo(
            "등록 완료",
            "업무가 등록되었습니다.",
            parent=self
        )

    # -----------------------------
    # 입력창 초기화
    # -----------------------------

    def clear_form(self):
        """
        업무 등록이 끝난 후 입력창의 내용을 초기 상태로 되돌린다.
        """

        # 각 입력창에 작성된 내용을 삭제한다.
        self.title_entry.delete(0, "end")
        self.detail_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.assignee_entry.delete(0, "end")

        # 중요도를 기본값인 보통으로 변경한다.
        self.importance_var.set("보통")

        # 중요도 버튼의 테두리 표시도 기본값에 맞게 갱신한다.
        self.update_importance_selector()

    # -----------------------------
    # 업무 목록 갱신
    # -----------------------------

    def refresh(self):
        """
        데이터베이스에서 현재 분야의 업무를 다시 불러와 표를 갱신한다.
        """

        # 기존 표에 표시된 모든 항목을 삭제한다.
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 현재 화면의 분야에 해당하는 업무 목록을 데이터베이스에서 가져온다.
        tasks = get_tasks_by_category(self.category)

        # 목록에 표시되는 번호는 현재 목록 기준으로 1부터 다시 부여한다.
        # 실제 데이터베이스 ID는 Treeview의 iid에 별도로 저장한다.
        for display_number, task in enumerate(tasks, start=1):

            # 데이터베이스에 저장된 완료 여부를 글자로 변환한다.
            status = (
                "완료"
                if task["completed"]
                else "미완료"
            )

            # 중요도가 비어 있는 경우 기본값인 보통으로 표시한다.
            importance = task["importance"] or "보통"

            # 중요도에 맞는 글자 색상 태그를 선택한다.
            importance_tag = {
                "높음": "importance_high",
                "보통": "importance_medium",
                "낮음": "importance_low"
            }.get(importance, "importance_medium")

            # 업무 정보를 표에 한 행씩 추가한다.
            self.tree.insert(
                "",
                "end",

                # 실제 데이터베이스 ID를 항목의 고유 식별자로 저장한다.
                iid=str(task["id"]),

                # 화면에 표시할 업무 정보를 순서대로 전달한다.
                values=(
                    display_number,
                    task["title"],
                    task["due_date"] or "-",
                    importance,
                    task["assignee"] or "-",
                    status
                ),

                # 중요도에 따라 글자 색상을 적용한다.
                tags=(importance_tag,)
            )

    # -----------------------------
    # 전체 화면 갱신
    # -----------------------------

    def refresh_all(self):
        """
        업무 목록과 다른 화면의 정보를 함께 갱신한다.
        """

        # 현재 탭의 업무 목록을 새로 불러온다.
        self.refresh()

        # 콜백 함수가 존재하면 대시보드나 캘린더 등도 갱신한다.
        if self.refresh_callback:
            self.refresh_callback()

    # -----------------------------
    # 선택한 업무 ID 가져오기
    # -----------------------------

    def get_selected_task_id(self):
        """
        표에서 선택한 업무의 실제 데이터베이스 ID를 반환한다.
        선택한 항목이 없으면 경고창을 표시한다.
        """

        # Treeview에서 현재 선택된 항목의 고유 식별자를 가져온다.
        selected = self.tree.selection()

        # 아무 업무도 선택하지 않았다면 경고창을 표시한다.
        if not selected:
            messagebox.showwarning(
                "선택 오류",
                "업무를 먼저 선택해 주세요.",
                parent=self
            )
            return None

        # 화면에 표시되는 순번이 아니라 실제 데이터베이스 ID를 반환한다.
        return int(selected[0])

    # -----------------------------
    # 완료 상태 변경
    # -----------------------------

    def toggle_complete(self):
        """
        선택한 업무의 완료 상태를 변경한다.
        이미 완료된 업무라면 미완료 상태로 되돌린다.
        """

        # 선택한 업무의 데이터베이스 ID를 가져온다.
        task_id = self.get_selected_task_id()

        # 선택된 업무가 없으면 함수를 종료한다.
        if task_id is None:
            return

        # 해당 ID에 해당하는 업무 정보를 데이터베이스에서 조회한다.
        task = get_task(task_id)

        # 업무 정보가 존재하지 않으면 함수를 종료한다.
        if task is None:
            return

        # 현재 완료 상태에 따라 반대 상태로 변경한다.
        if task["completed"]:
            undo_complete_task(task_id)
        else:
            complete_task(task_id)

        # 변경된 완료 상태를 화면에 반영한다.
        self.refresh_all()

    # -----------------------------
    # 업무 삭제
    # -----------------------------

    def remove_task(self):
        """
        사용자가 선택한 업무를 데이터베이스에서 삭제한다.
        삭제 전에 확인창을 표시하여 실수로 삭제하는 것을 방지한다.
        """

        # 선택한 업무의 실제 데이터베이스 ID를 가져온다.
        task_id = self.get_selected_task_id()

        # 업무가 선택되지 않았다면 삭제 과정을 중단한다.
        if task_id is None:
            return

        # 사용자에게 삭제 여부를 묻는 확인창을 표시한다.
        answer = messagebox.askyesno(
            "업무 삭제",
            "선택한 업무를 삭제하시겠습니까?",
            parent=self
        )

        # 사용자가 취소를 선택하면 삭제하지 않는다.
        if not answer:
            return

        # 확인을 선택한 경우 데이터베이스에서 해당 업무를 삭제한다.
        delete_task(task_id)

        # 삭제 결과를 업무 목록과 다른 화면에 반영한다.
        self.refresh_all()

    # -----------------------------
    # 업무 수정
    # -----------------------------

    def edit_task(self):
        """
        선택한 업무의 기존 정보를 수정할 수 있는 별도의 창을 생성한다.
        """

        # 현재 선택된 업무의 실제 데이터베이스 ID를 가져온다.
        task_id = self.get_selected_task_id()

        # 선택한 업무가 없다면 수정 과정을 중단한다.
        if task_id is None:
            return

        # 해당 업무의 기존 정보를 데이터베이스에서 가져온다.
        task = get_task(task_id)

        # 업무 정보가 존재하지 않으면 함수를 종료한다.
        if task is None:
            return

        # 기존 업무 정보를 수정할 별도의 창을 생성한다.
        window = ctk.CTkToplevel(self)

        window.title("업무 수정")
        window.geometry("420x480")
        window.resizable(False, False)

        # 수정 창을 현재 프로그램의 하위 창으로 설정한다.
        window.transient(self.winfo_toplevel())

        # 수정 창이 열려 있는 동안 다른 창을 조작하지 못하도록 설정한다.
        window.grab_set()

        # 두 번째 열의 입력창이 남은 공간을 차지하도록 설정한다.
        window.grid_columnconfigure(1, weight=1)

        # 기존 업무 정보를 항목별로 정리한다.
        # 상세 내용, 마감일, 담당자가 비어 있으면 빈 문자열을 사용한다.
        fields = [
            ("업무명", task["title"]),
            ("상세 내용", task["detail"] or ""),
            ("마감일", task["due_date"] or ""),
            ("담당자", task["assignee"] or "")
        ]

        # 각 입력창을 항목 이름과 연결하여 저장할 딕셔너리이다.
        entries = {}

        # 업무 정보 항목마다 이름과 입력창을 생성한다.
        for row, (label, value) in enumerate(fields):

            # 입력 항목의 이름을 화면에 표시한다.
            ctk.CTkLabel(
                window,
                text=label,
                font=(FONT, 15, "bold")
            ).grid(
                row=row,
                column=0,
                padx=15,
                pady=12
            )

            # 기존 업무 정보가 입력된 수정용 입력창을 생성한다.
            entry = ctk.CTkEntry(
                window,
                width=230,
                font=(FONT, 15)
            )

            # 데이터베이스에서 가져온 기존 값을 입력창에 넣는다.
            entry.insert(0, value)

            entry.grid(
                row=row,
                column=1,
                padx=15,
                pady=12,
                sticky="ew"
            )

            # 마감일 입력창에는 날짜 자동 하이픈 기능을 연결한다.
            if label == "마감일":
                entry.bind(
                    "<KeyRelease>",
                    lambda event, target=entry: self.format_date_entry(target)
                )

            # 나중에 수정된 값을 가져올 수 있도록 입력창을 저장한다.
            entries[label] = entry

        # -----------------------------
        # 수정 창의 중요도 선택 영역
        # -----------------------------

        ctk.CTkLabel(
            window,
            text="중요도",
            font=(FONT, 15, "bold")
        ).grid(
            row=4,
            column=0,
            padx=15,
            pady=12
        )

        # 기존 업무의 중요도를 기본 선택값으로 설정한다.
        edit_importance_var, edit_importance_frame = self.create_importance_selector(
            window,
            initial=task["importance"] or "보통"
        )

        edit_importance_frame.grid(
            row=4,
            column=1,
            padx=15,
            pady=12,
            sticky="w"
        )

        # -----------------------------
        # 수정 내용 저장
        # -----------------------------

        def save_changes():
            """
            수정 창에 입력된 정보를 검사한 뒤 데이터베이스에 저장한다.
            """

            # 수정 창의 입력창에서 변경된 값을 가져온다.
            title = entries["업무명"].get().strip()
            detail = entries["상세 내용"].get().strip()
            due_date = entries["마감일"].get().strip()
            assignee = entries["담당자"].get().strip()

            # 업무명이 비어 있으면 수정할 수 없도록 한다.
            if not title:
                messagebox.showwarning(
                    "입력 오류",
                    "업무명을 입력해 주세요.",
                    parent=window
                )
                return

            # 마감일이 올바르지 않으면 저장을 중단한다.
            if not self.validate_due_date(due_date, parent=window):
                return

            # 수정한 정보를 데이터베이스에 반영한다.
            update_task(
                task_id,
                self.category,
                title,
                detail,
                due_date,
                edit_importance_var.get(),
                assignee
            )

            # 저장이 완료되면 수정 창을 닫고 화면을 갱신한다.
            window.destroy()
            self.refresh_all()

            # 수정이 완료되었음을 사용자에게 알린다.
            messagebox.showinfo(
                "수정 완료",
                "업무 정보가 수정되었습니다.",
                parent=self
            )

        # 수정 내용을 데이터베이스에 저장하는 버튼을 생성한다.
        ctk.CTkButton(
            window,
            text="수정 내용 저장",
            font=(FONT, 15, "bold"),
            command=save_changes
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            pady=25
        )

    # -----------------------------
    # 업무 상세 내용 확인
    # -----------------------------

    def show_task_detail(self, event=None):
        """
        업무 목록에서 항목을 더블클릭했을 때 상세 정보를 보여준다.
        """

        # 선택한 업무의 실제 데이터베이스 ID를 가져온다.
        task_id = self.get_selected_task_id()

        # 선택된 업무가 없으면 상세 정보 창을 열지 않는다.
        if task_id is None:
            return

        # 데이터베이스에서 해당 업무의 전체 정보를 조회한다.
        task = get_task(task_id)

        # 업무 정보가 존재하지 않으면 함수를 종료한다.
        if task is None:
            return

        # 업무 상세 정보를 표시할 별도의 창을 생성한다.
        detail_window = ctk.CTkToplevel(self)

        detail_window.title("업무 상세 정보")
        detail_window.geometry("400x400")

        # 상세 정보 창을 현재 프로그램의 하위 창으로 설정한다.
        detail_window.transient(self.winfo_toplevel())

        # 업무 정보를 여러 줄의 문자열로 구성한다.
        # 값이 비어 있는 경우에는 '없음', '미정', '미지정' 등으로 표시한다.
        content = (
            f"업무명: {task['title']}\n\n"
            f"분야: {task['category']}\n\n"
            f"상세 내용: {task['detail'] or '없음'}\n\n"
            f"마감일: {task['due_date'] or '미정'}\n\n"
            f"중요도: {task['importance'] or '미설정'}\n\n"
            f"담당자: {task['assignee'] or '미지정'}\n\n"
            f"상태: {'완료' if task['completed'] else '미완료'}"
        )

        # 구성한 업무 정보를 상세 정보 창에 표시한다.
        ctk.CTkLabel(
            detail_window,
            text=content,
            font=(FONT, 16),
            justify="left",
            wraplength=350
        ).pack(
            padx=25,
            pady=30,
            anchor="w"
        )

        # 버튼을 누르면 상세 정보 창을 닫는다.
        ctk.CTkButton(
            detail_window,
            text="닫기",
            font=(FONT, 15, "bold"),
            command=detail_window.destroy
        ).pack(
            pady=10
        )