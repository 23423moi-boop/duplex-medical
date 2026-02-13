from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/errors")
def get_errors():
    return jsonify([
        {"fio": "Иванов Александр Дмитриевич", "error": "Ошибка №17: дублирование записей"},
        {"fio": "Иналепенко Василий Валерьевич", "error": "Ошибка в ЕУМК: диагноз устарел"},
        {"fio": "Ионов Павел Сергеевич", "error": "Ошибка №2: неправильный формат"},
        {"fio": "Ивасиков Антон Павлович", "error": "Неполные данные"},
    ])

if __name__ == "__main__":
    app.run(debug=True)
