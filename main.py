from pathlib import Path
import argparse

from backupZ.config_parser import ConfigParser

# Создаем парсер
parser = argparse.ArgumentParser()

# Добавляем аргументы
parser.add_argument("-cd", "--config-dir", help="Путь к папке конфигов", default="")

# Парсим аргументы
args = parser.parse_args()

current_directory = Path(__file__).resolve().parent


def main():
    parser = ConfigParser()
    parser.variables = {
        "DOCUMENT_ROOT": "/var/www/html",  # Пример переменной
        "SERVER_NAME": "example.com"
    }

    # Парсим все .conf файлы в папке configs
    parser.parse_directory(f"{current_directory}/configs")

    config = parser.get_config()

    # Вывод результата
    import pprint
    pprint.pprint(config)


if __name__ == '__main__':
    main()

