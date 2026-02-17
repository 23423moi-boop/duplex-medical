from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List
import urllib.request
import xml.etree.ElementTree as ET

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager


KV = '''
#:import dp kivy.metrics.dp

<HeaderBar@BoxLayout>:
    size_hint_y: None
    height: dp(72)
    padding: dp(12)
    spacing: dp(14)
    canvas.before:
        Color:
            rgba: .12, .23, .54, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "Duplex"
        bold: True
        color: 1,1,1,1
        font_size: '20sp'
        size_hint_x: .22
    BoxLayout:
        spacing: dp(8)
        size_hint_x: .55
        Button:
            text: "Главная"
            on_release: app.root.current = 'home'
        Button:
            text: "Проверка"
            on_release: app.root.current = 'check'
        Button:
            text: "Отчёты"
            on_release: app.root.current = 'reports'
        Button:
            text: "Настройки"
            on_release: app.root.current = 'settings'
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: .23
        Label:
            text: "Иван Иванов"
            color: 1,1,1,1
            font_size: '13sp'
        Label:
            text: "Системный администратор"
            color: .84,.89,.98,1
            font_size: '11sp'

<RootManager>:
    HomeScreen:
        name: 'home'
    PlaceholderScreen:
        name: 'check'
        title: '🔍 Проверка данных'
    PlaceholderScreen:
        name: 'reports'
        title: '📊 Отчёты'
    PlaceholderScreen:
        name: 'settings'
        title: '⚙️ Настройки'

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        HeaderBar:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(14)
            spacing: dp(8)
            Label:
                text: '📋 Список ошибок в данных пациентов'
                size_hint_y: None
                height: dp(34)
                bold: True
                color: .12,.16,.25,1
                text_size: self.width, None
                halign: 'left'
                valign: 'middle'
            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(8)
                Spinner:
                    id: status_spinner
                    text: root.filter_status
                    values: ['all', 'new', 'in_progress', 'resolved']
                    on_text: root.filter_status = self.text; root.apply_filters()
                Spinner:
                    id: dep_spinner
                    text: root.filter_department
                    values: root.department_values
                    on_text: root.filter_department = self.text; root.apply_filters()
                Spinner:
                    id: type_spinner
                    text: root.filter_type
                    values: ['all', 'ERR-EUMK-001', 'ERR-25347', 'ERR-DATE-009']
                    on_text: root.filter_type = self.text; root.apply_filters()
            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(8)
                TextInput:
                    id: file_input
                    hint_text: 'Путь к XML файлу (например example_errors.xml)'
                TextInput:
                    id: url_input
                    hint_text: 'URL XML (необязательно)'
                Button:
                    text: 'Импорт XML'
                    size_hint_x: .22
                    on_release: root.import_xml(file_input.text, url_input.text)
            Label:
                id: import_status
                text: root.import_message
                size_hint_y: None
                height: dp(24)
                color: .2,.2,.2,1
                text_size: self.width, None
                halign: 'left'
                valign: 'middle'
            ScrollView:
                do_scroll_x: False
                GridLayout:
                    id: items_box
                    cols: 1
                    spacing: dp(8)
                    padding: [0, dp(8), 0, dp(18)]
                    size_hint_y: None
                    height: self.minimum_height

<ErrorCard@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(110)
    padding: dp(10)
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: .96,.97,.99,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
    Label:
        text: root.title_text
        bold: True
        color: .1,.12,.18,1
        text_size: self.width, None
        halign: 'left'
        valign: 'middle'
    Label:
        text: root.subtitle_text
        color: .26,.30,.36,1
        text_size: self.width, None
        halign: 'left'
        valign: 'middle'
    Label:
        text: root.meta_text
        color: .37,.42,.49,1
        font_size: '12sp'
        text_size: self.width, None
        halign: 'left'
        valign: 'middle'

<PlaceholderScreen>:
    BoxLayout:
        orientation: 'vertical'
        HeaderBar:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(24)
            spacing: dp(12)
            Label:
                text: root.title
                font_size: '26sp'
                color: .1,.12,.18,1
            Label:
                text: 'Раздел в процессе переноса из Vue в Kivy.'
                color: .32,.34,.4,1
'''


@dataclass
class ErrorItem:
    patient_id: str
    patient_name: str
    department: str
    error_code: str
    description: str
    status: str
    date: str
    db_name: str


class RootManager(ScreenManager):
    pass


class PlaceholderScreen(Screen):
    title = StringProperty("")


class HomeScreen(Screen):
    items_box = ObjectProperty(None)
    filter_status = StringProperty("all")
    filter_department = StringProperty("all")
    filter_type = StringProperty("all")
    import_message = StringProperty("Готово к импорту XML.")
    department_values = ListProperty(["all", "Терапевтическое", "Хирургическое", "Кардиология"])
    data: List[ErrorItem]

    def on_kv_post(self, base_widget):
        self.data = [
            ErrorItem("P-4521", "Двайнанин Александр Ильич", "Терапевтическое", "ERR-EUMK-001", "Несоответствие данных диагноза", "new", "25.10.2025", "БАРС"),
            ErrorItem("P-3892", "Двустимчук Олег Дмитриевич", "Хирургическое", "ERR-25347", "Дублирование записей", "in_progress", "24.10.2025", "ЕЦП"),
            ErrorItem("P-1107", "Чупрунова Алёна Максимовна", "Кардиология", "ERR-DATE-009", "Конфликт даты госпитализации", "resolved", "22.10.2025", "БАРС"),
        ]
        self.apply_filters()

    def apply_filters(self):
        if not self.ids:
            return
        self.ids.items_box.clear_widgets()
        for item in self.filtered_data():
            card = Builder.template(
                "ErrorCard",
                title_text=f"{item.patient_name} ({item.patient_id})",
                subtitle_text=f"{item.error_code}: {item.description}",
                meta_text=f"Отделение: {item.department} • Статус: {item.status} • БД: {item.db_name} • {item.date}",
            )
            self.ids.items_box.add_widget(card)

    def filtered_data(self) -> List[ErrorItem]:
        result = self.data
        if self.filter_status != "all":
            result = [x for x in result if x.status == self.filter_status]
        if self.filter_department != "all":
            result = [x for x in result if x.department == self.filter_department]
        if self.filter_type != "all":
            result = [x for x in result if x.error_code == self.filter_type]
        return result

    def import_xml(self, file_path: str, xml_url: str):
        try:
            xml_text = self._load_xml(file_path.strip(), xml_url.strip())
            parsed = self._parse_xml(xml_text)
            if not parsed:
                self.import_message = "Импорт выполнен, но записи не найдены."
                return
            self.data = parsed
            self.import_message = f"Импортировано записей: {len(parsed)} ({datetime.now().strftime('%H:%M:%S')})"
            self.apply_filters()
        except Exception as exc:
            self.import_message = f"Ошибка импорта: {exc}"

    def _load_xml(self, file_path: str, xml_url: str) -> str:
        if file_path:
            return Path(file_path).read_text(encoding="utf-8")
        if xml_url:
            with urllib.request.urlopen(xml_url, timeout=10) as response:
                return response.read().decode("utf-8")
        raise ValueError("Укажите путь к файлу или URL")

    def _parse_xml(self, text: str) -> List[ErrorItem]:
        root = ET.fromstring(text)
        items: List[ErrorItem] = []
        for row in root.findall(".//error"):
            items.append(
                ErrorItem(
                    patient_id=row.findtext("patientId", default="N/A"),
                    patient_name=row.findtext("patientName", default="Неизвестный пациент"),
                    department=row.findtext("department", default="Не указано"),
                    error_code=row.findtext("errorCode", default="N/A"),
                    description=row.findtext("description", default="Без описания"),
                    status=row.findtext("status", default="new"),
                    date=row.findtext("date", default="-"),
                    db_name=row.findtext("dbName", default="-"),
                )
            )
        return items


class DuplexMedicalApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootManager()


if __name__ == "__main__":
    DuplexMedicalApp().run()
