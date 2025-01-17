from pathlib import Path
import argparse

# Создаем парсер
parser = argparse.ArgumentParser()

# Добавляем аргументы
parser.add_argument("-cd", "--config-dir", help="Путь к папке конфигов", default="")

# Парсим аргументы
args = parser.parse_args()

current_directory = Path(__file__).resolve().parent


def main():
    print(current_directory)


if __name__ == '__main__':
    main()

