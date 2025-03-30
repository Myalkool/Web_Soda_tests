import os
import subprocess
import re

from flask import flash
from yaml import safe_load, YAMLError

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def parse_test_results(raw_output: str) -> list:
    results = []
    # Общий паттерн для ошибок (включая многострочные)
    error_pattern = re.compile(r"ERROR: (.+?)(?=\n\S+|\Z)", re.DOTALL)
    # Паттерн для результатов проверок
    check_pattern = re.compile(
        r"^(.*?) \[(PASSED|FAILED|WARN|NOT EVALUATED)\](?:.*\n?.*?check_value: ([\d.]+))?",
        re.MULTILINE
    )
    # Паттерн для деталей ошибки проверки
    error_details_pattern = re.compile(r"Error message: (.+)")

    # Обрабатываем ошибки выполнения
    for error_match in error_pattern.finditer(raw_output):
        error_message = error_match.group(1).strip()
        results.append({
            "check": "Ошибка выполнения",
            "status": "error",
            "message": error_message
        })

    # Обрабатываем результаты тестов
    for check_match in check_pattern.finditer(raw_output):
        check_name = check_match.group(1).strip()
        status = check_match.group(2).lower()
        value = check_match.group(3)

        status_map = {
            "passed": "success",
            "failed": "fail",
            "warn": "warning",
            "not evaluated": "error"
        }

        # Ищем детали ошибки после результата проверки
        error_details = error_details_pattern.search(check_match.group(0))
        message = ""

        if status == "not evaluated":
            message = "Тест не был выполнен"
        elif status == "failed":
            message = "Тест не пройден"

        if error_details:
            message += f". Причина: {error_details.group(1).strip()}"
        elif value:
            message += f". Значение: {value}" if message else f"Значение: {value}"

        results.append({
            "check": check_name,
            "status": status_map.get(status, "error"),
            "message": message or None
        })

    return results


def validate_test_structure(test):
    try:
        parsed_test = safe_load(test)
        if not isinstance(parsed_test, dict):
            flash("Ошибка test: Файл должен содержать YAML-словарь", 'danger')
            return False

        valid_structure = False
        for key, value in parsed_test.items():
            if key.startswith("checks for ") and key.strip() != "checks for":

                if not isinstance(value, list):
                    flash(f"Ошибка test: В '{key}' тесты должны быть в формате списка", 'danger')
                    return False

                if not value:
                    flash(f"Ошибка test: В '{key}' отсутствуют тесты", 'danger')
                    return False

                for check in value:
                    if isinstance(check, str):
                        continue
                    elif isinstance(check, dict):
                        if not all(isinstance(k, str) and isinstance(v, dict) for k, v in check.items()):
                            flash(f"Ошибка test: Неверный формат проверки в '{key}'", 'danger')
                            return False
                    else:
                        flash(f"Ошибка test: Неподдерживаемый формат проверки в '{key}'", 'danger')
                        return False

                valid_structure = True

        if not valid_structure:
            flash("Ошибка test: В файле отсутствует корректный 'checks for <table>'", 'danger')
            return False

        return parsed_test

    except YAMLError:
        flash("Ошибка test: Неверный синтаксис YAML. Проверьте отступы и структуру.", 'danger')
        return False


def get_data_source_name():
    with open("config/configuration.yml", "r") as file:
        config = safe_load(file)

    for key in config:
        if key.startswith("data_source "):
            return key.split("data_source ")[1]  # Вернёт имя источника данных
    return None


def run_soda_scan():
    try:
        data_source = get_data_source_name()
        if not data_source:
            flash("Ошибка: Не найден источник данных", "danger")
            return None

        result = subprocess.run(
            [
                "soda",
                "scan",
                "-d", data_source,
                "-c", "config/configuration.yml",
                "config/checks_custom.yml"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        # Всегда возвращаем объединенный вывод для анализа
        full_output = f"{result.stdout}\n{result.stderr}"
        return full_output

    except Exception as e:
        return f"Системная ошибка: {str(e)}"


def create_test_file(test):
    try:
        checks_path = os.path.join(CONFIG_DIR, "checks_custom.yml")
        with open(checks_path, "w", encoding="utf-8") as f:
            f.write(test)
    except Exception as e:
        flash(f"Ошибка в сохранении файла: {str(e)}", 'danger')
        return False
    return True

