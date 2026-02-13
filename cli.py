import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp


SERVER_URL = "http://127.0.0.1:5000/errors"  # <-- адрес сервера


class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(80), **kwargs)

        with self.canvas.before:
            Color(0.12, 0.53, 0.83, 1)  # Синий фон
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.add_widget(Label(
            text="КГБУЗ 'Уссурийская ЦГБ'\nDuplex",
            bold=True,
            color=(1, 1, 1, 1),
            halign="left"
        ))

        self.add_widget(Label(
            text="Иван Иванов\nСистемный администратор",
            color=(1, 1, 1, 1),
            halign="right"
        ))

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class ErrorRow(BoxLayout):
    def __init__(self, fio, error_text, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(50), **kwargs)

        self.add_widget(Label(text=fio, halign="left"))
        self.add_widget(Label(text=error_text, halign="left"))


class ErrorTable(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)

    def update_data(self, data):
        self.layout.clear_widgets()

        for item in data:
            row = ErrorRow(item["fio"], item["error"])
            self.layout.add_widget(row)


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # HEADER
        self.add_widget(Header())

        # FILTERS
        filter_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=10, padding=10)

        self.btn_type = Button(text="Ошибка в ЕУМК")
        self.btn_status = Button(text="Не исправлены")
        self.btn_start = Button(text="Начать", background_color=(1, 0, 0, 1))

        self.btn_start.bind(on_press=self.load_data)

        filter_layout.add_widget(self.btn_type)
        filter_layout.add_widget(self.btn_status)
        filter_layout.add_widget(Widget())
        filter_layout.add_widget(self.btn_start)

        self.add_widget(filter_layout)

        # TABLE HEADER
        header_row = BoxLayout(size_hint_y=None, height=dp(40))
        header_row.add_widget(Label(text="ФИО", bold=True))
        header_row.add_widget(Label(text="Ошибка", bold=True))
        self.add_widget(header_row)

        # TABLE
        self.table = ErrorTable()
        self.add_widget(self.table)

        # Автозагрузка при старте
        Clock.schedule_once(lambda dt: self.load_data(), 1)

    def load_data(self, instance=None):
        try:
            response = requests.get(SERVER_URL)
            if response.status_code == 200:
                data = response.json()
                self.table.update_data(data)
        except Exception as e:
            print("Ошибка подключения к серверу:", e)


class DuplexApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    DuplexApp().run()
