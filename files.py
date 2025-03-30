import os


ALLOWED_EXTENSIONS = {'yml'}
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def read_config_file(config_file):
    config_str = config_file.read().decode('utf-8')
    return config_str


def read_test_file(test_file):
    test_str = test_file.read().decode('utf-8')
    return test_str


def delete_file():
    try:
        os.remove(os.path.join(CONFIG_DIR, "configuration.yml"))
        os.remove(os.path.join(CONFIG_DIR, "checks_custom.yml"))
    except OSError:
        pass
