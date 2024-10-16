import flet
from flet import (
    Checkbox,
    Column,
    FloatingActionButton,
    IconButton,
    OutlinedButton,
    Page,
    Row,
    Tab,
    Tabs,
    Text,
    TextField,
    UserControl,
    colors,
    icons
)
import sqlite3


class DataBaseAccess():
    """
    データベースアクセスクラス
    """
    def __init__(self):
        self.dbname = "todo.db"

    def create_table(self):
        """
        テーブル作成
        """
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS task (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT, 
                    task_status INTEGER DEFAULT 0);"""
        cur.execute(sql)

        conn.commit()
        conn.close()

    def get_task(self):
        """
        タスク取得
        """
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        sql = "SELECT * FROM task;"
        cur.execute(sql)
        result = cur.fetchall()

        conn.commit()
        conn.close()

        return result

    def insert_task(self, task_name, task_status):
        """
        タスク登録
        """
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        sql = f"""INSERT INTO task (task_name, task_status)
                VALUES ("{task_name}", {task_status})
        ;"""
        cur.execute(sql)

        conn.commit()
        id = cur.execute("select last_insert_rowid();").fetchall()[0]
        conn.close()

        return id

    def update_task(self, id, task_name, task_status):
        """
        タスク更新
        """
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        sql = f"""UPDATE task SET
            task_name = "{task_name}",
            task_status = {task_status}
            WHERE id = {id}
        ;"""
        cur.execute(sql)

        conn.commit()
        conn.close()

    def delete_task(self, id):
        """
        タスク削除
        """
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        sql = f"""DELETE FROM task
            WHERE id = {id}
        ;"""
        cur.execute(sql)

        conn.commit()
        conn.close()


class Task(UserControl):
    """
    ToDoアプリ内でのタスクを司るクラス
    """
    def __init__(self, kye: int, task_name: str, task_status: int, task_status_change: any, task_delete: any):
        super().__init__()
        self.kye = kye
        self.completed = True if task_status == 1 else False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        """
        画面構成の定義
        """
        # チェックボックス
        self.display_task = Checkbox(
            value=self.completed, label=self.task_name, on_change=self.status_changed, key=self.kye
        )
        # 編集テキストボックス
        self.edit_name = TextField(expand=1)

        # 表示ビュー
        self.display_view = Row(
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked
                        ),
                        IconButton(
                            icon=icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked
                        )
                    ]
                )
            ]
        )
        # 編集ビュー
        self.edit_view = Row(
            visible=False,
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked
                )
            ]
        )
        
        return Column(controls=[self.display_view, self.edit_view])
    
    def edit_clicked(self, e):
        """
        編集ボタン押下処理
        """
        # ラベルの更新
        self.edit_name.value = self.display_task.label
        # 表示ビューと編集ビューの表示切替
        self.display_view.visible = False
        self.edit_view.visible = True

        self.update()

    def save_clicked(self, e):
        """
        保存ボタン押下処理
        """
        # ラベルの更新
        self.display_task.label = self.edit_name.value
        # 表示ビューと編集ビューの表示切替
        self.display_view.visible = True
        self.edit_view.visible = False
        # DBの更新
        db.update_task(self.display_task.key, self.edit_name.value, 1 if self.display_task.value else 0)

        self.update()

    def status_changed(self, e):
        """
        チェックボックス押下処理
        """
        self.completed = self.display_task.value
        self.task_status_change(self)
        # DBの更新
        db.update_task(self.display_task.key, self.display_task.label, 1 if self.display_task.value else 0)

    def delete_clicked(self, e):
        """
        削除ボタン押下処理
        """
        self.task_delete(self)


class TodoApp(UserControl):
    """
    ToDoアプリのタスク以外の画面を司るクラス
    """
    def build(self):
        # タスク追加テキストボックス
        self.new_task = TextField(
            hint_text="What needs to be done?",
            on_submit=self.add_clicked,
            expand=True
        )
        # タスク
        self.tasks = Column()
        tasks = db.get_task()
        for item in tasks:
            # タスククラスのインスタンスを作成
            task = Task(item[0], item[1], item[2], self.task_status_change, self.task_delete)
            # タスクを追加
            self.tasks.controls.append(task)
        # タブ
        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all"), Tab(text="active"), Tab(text="completed")]
        )
        # アイテム数
        self.items_left = Text("0 items left")

        return Column(
            width=600,
            controls=[
                Row([Text(value="Todos", style=flet.TextThemeStyle.HEADLINE_MEDIUM)], alignment=flet.MainAxisAlignment.CENTER),
                Row(
                    controls=[
                        self.new_task,
                        FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked)
                    ]
                ),
                Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        Row(
                            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=flet.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                OutlinedButton(
                                    text="Clear completed", on_click=self.clear_clicked
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    def add_clicked(self, e):
        """
        追加ボタン押下処理
        """
        if self.new_task.value:
            # タスククラスのインスタンスを作成
            id = db.insert_task(self.new_task.value, 0)
            task = Task(id, self.new_task.value, 0, self.task_status_change, self.task_delete)
            # タスクを追加
            self.tasks.controls.append(task)
            # タスク追加テキストボックスをクリア
            self.new_task.value = ""
            # タスク追加テキストボックスにフォーカス
            self.new_task.focus()
            # 表示を更新
            self.update()

    def task_status_change(self, task):
        # 表示を更新
        self.update()

    def task_delete(self, task):
        # タスクを削除
        self.tasks.controls.remove(task)
        # DBの削除
        db.delete_task(task.kye)
        # 表示を更新
        self.update()

    def tabs_changed(self, task):
        # 表示を更新
        self.update()

    def clear_clicked(self, e):
        """
        完了済タスク削除ボタン押下処理
        """
        for task in self.tasks.controls[:]:
            if task.completed:
                # タスク削除処理を呼び出す
                self.task_delete(task)

    def update(self):
        """
        更新処理
        UserControlクラスのupdate()をオーバーライド
        """
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completed == False)
                or (status == "completed" and task.completed)
            ) 
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active item(s) left"
        super().update()


def main(page: Page):
    """
    アプリのウィンドウに関する定義
    """
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.scroll = flet.ScrollMode.ADAPTIVE
    page.update()

    db.create_table()
    app = TodoApp()

    page.add(app)

db = DataBaseAccess()
flet.app(target=main)
