# Duplex Medical (Kivy)

Это настольное приложение на Python + Kivy, перенесённое из версии на Vue.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Что уже перенесено

- верхняя панель с навигацией по разделам;
- главный экран со списком ошибок в данных пациентов;
- фильтрация по статусу, отделению и типу ошибки;
- импорт ошибок из XML (локальный файл или URL);
- пример XML для импорта: `example_errors.xml`.
