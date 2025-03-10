import os
from flask import flash
from yaml import safe_load, YAMLError

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def validate_config_structure(config):
    try:
        parsed_config = safe_load(config)
        if not isinstance(parsed_config, dict):
            flash("Ошибка config: Конфигурационный файл должен быть YAML-словарем", 'danger')
            return False

        # Ищем ключ, начинающийся с "data_source "
        data_source_key = next((key for key in parsed_config if key.startswith("data_source ")), None)
        if not data_source_key:
            flash("Ошибка config: Отсутствует секция 'data_source <name>'", 'danger')
            return False

        # Получаем словарь с данными источника данных
        data_source = parsed_config[data_source_key]
        if not isinstance(data_source, dict):
            flash(f"Ошибка config: '{data_source_key}' должен быть словарем", 'danger')
            return False

        # Проверяем наличие обязательных ключей в data_source
        required_keys = ["type", "connection"]
        for key in required_keys:
            if key not in data_source:
                flash(f"Ошибка config: В '{data_source_key}' отсутствует обязательный параметр '{key}'", 'danger')
                return False

        # Проверяем, что type не пустой
        if not data_source["type"]:
            flash(f"Ошибка config: В '{data_source_key}' параметр 'type' не должен быть пустым", 'danger')
            return False

        # Проверяем, что connection является словарем
        connection = data_source["connection"]
        if not isinstance(connection, dict):
            flash(f"Ошибка config: Параметр 'connection' в '{data_source_key}' должен быть словарем", 'danger')
            return False

        # Проверяем наличие обязательных полей в connection
        required_connection_keys = ["host", "port", "username", "password", "database"]
        for key in required_connection_keys:
            if key not in connection:
                flash(f"Ошибка config: В 'connection' отсутствует обязательный параметр '{key}'", 'danger')
                return False
            if not connection[key]:  # Проверяем, что параметр не пустой
                flash(f"Ошибка config: Параметр '{key}' в 'connection' не должен быть пустым", 'danger')
                return False

        # Если используется Soda Cloud, проверяем секцию soda_cloud
        if "soda_cloud" in parsed_config:
            soda_cloud = parsed_config["soda_cloud"]
            if not isinstance(soda_cloud, dict):
                flash("Ошибка config: 'soda_cloud' должен быть словарем", 'danger')
                return False

            # Проверяем наличие обязательных ключей в 'soda_cloud'
            required_soda_keys = ["host", "api_key_id", "api_key_secret"]
            for key in required_soda_keys:
                if key not in soda_cloud:
                    flash(f"Ошибка config: В 'soda_cloud' отсутствует обязательный параметр '{key}'", 'danger')
                    return False
                if not soda_cloud[key]:  # Проверяем, что параметр не пустой
                    flash(f"Ошибка config: Параметр '{key}' в 'soda_cloud' не должен быть пустым", 'danger')
                    return False

        return True

    except YAMLError as e:
        flash(f"Ошибка config: Неверный синтаксис YAML. Проверьте отступы и структуру. {str(e)}", 'danger')
        return False


def create_config_file(config):
    try:
        configur_path = os.path.join(CONFIG_DIR, "configuration.yml")
        with open(configur_path, "w") as f:
            f.write(config)

    except Exception as e:
        flash(f"Ошибка в сохранении файла: {str(e)}", 'danger')
        return False
    return True
