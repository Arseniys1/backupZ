import os
import re
import json
import yaml
from collections import defaultdict

class ConfigParser:
    def __init__(self):
        self.config = defaultdict(lambda: defaultdict(dict))  # Конфигурация по файлам
        self.current_context = []
        self.errors = []  # Список для хранения ошибок
        self.variables = {}  # Словарь для хранения переменных
        self.current_file = None  # Текущий файл, который парсится

    def parse_file(self, filename):
        """Парсит один файл конфигурации."""
        self.current_file = filename  # Устанавливаем текущий файл
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                self._parse_line(line.strip(), line_num, filename)

        # Выводим ошибки, если они есть, после завершения парсинга файла
        if self.errors:
            print(f"Ошибки при парсинге файла {filename}:")
            for error in self.errors:
                print(error)
            self.errors = []  # Очищаем список ошибок после вывода

    def parse_directory(self, directory):
        """Рекурсивно парсит все файлы в указанной папке."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.conf'):  # Парсим только .conf файлы
                    filepath = os.path.join(root, file)
                    self.parse_file(filepath)

    def _parse_line(self, line, line_num, filename):
        """Парсит одну строку конфигурации."""
        try:
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                return

            # Обработка условий <If ...>
            if_match = re.match(r'<If\s+(.*?)>', line)
            if if_match:
                condition = if_match.group(1)
                self._enter_block(f"If[{condition}]", "", line_num, filename)
                return

            # Обработка блоков <BlockName ...> или <BlockName>
            block_match = re.match(r'<(\w+)(?:\s+(.*?))?>', line)
            if block_match:
                block_name, block_args = block_match.groups()
                block_args = block_args if block_args else ""  # Если аргументов нет, используем пустую строку
                self._enter_block(block_name, block_args, line_num, filename)
                return

            # Обработка закрывающих тегов </BlockName>
            if line.startswith('</'):
                self._exit_block(line, line_num, filename)
                return

            # Обработка переменных ${VAR}
            line = self._replace_variables(line, line_num, filename)

            # Обработка директив
            directive_match = re.match(r'(\w+)\s+(.*)', line)
            if directive_match:
                key, value = directive_match.groups()
                value = self._clean_value(value)  # Убираем лишние кавычки
                self._validate_directive(key, value, line_num, filename)
                self._add_directive(key, value, line_num, filename)
            else:
                self.errors.append(f"Синтаксическая ошибка в файле {filename}, строка {line_num}: {line}")

        except Exception as e:
            self.errors.append(f"Ошибка в файле {filename}, строка {line_num}: {str(e)}")

    def _clean_value(self, value):
        """Убирает лишние кавычки из значения."""
        # Убираем кавычки с начала и конца строки
        return value.strip('"\'')

    def _enter_block(self, block_name, block_args, line_num, filename):
        """Обрабатывает вход в блок."""
        self.current_context.append((block_name, block_args))

    def _exit_block(self, line, line_num, filename):
        """Обрабатывает выход из блока."""
        block_close_match = re.match(r'</(\w+)>', line)
        if not block_close_match:
            self.errors.append(f"Неправильный закрывающий тег в файле {filename}, строка {line_num}: {line}")
            return

        block_name = block_close_match.group(1)
        if not self.current_context:
            self.errors.append(f"Лишний закрывающий тег </{block_name}> в файле {filename}, строка {line_num}")
            return

        last_block_name, _ = self.current_context[-1]
        if last_block_name.split('[')[0] != block_name:  # Учитываем условия в If
            self.errors.append(f"Несоответствие блоков в файле {filename}, строка {line_num}: ожидался </{last_block_name.split('[')[0]}>, но найден </{block_name}>")
            return

        self.current_context.pop()

    def _add_directive(self, key, value, line_num, filename):
        """Добавляет директиву в текущий контекст."""
        context_key = self._get_context_key()
        # Добавляем директиву в конфигурацию текущего файла
        self.config[filename][context_key][key] = value

    def _get_context_key(self):
        """Генерирует ключ для текущего контекста."""
        return '/'.join([f"{name}[{args}]" for name, args in self.current_context])

    def _replace_variables(self, line, line_num, filename):
        """Заменяет переменные ${VAR} на их значения."""
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in self.variables:
                self.errors.append(f"Неизвестная переменная ${{{var_name}}} в файле {filename}, строка {line_num}")
                return match.group(0)
            return self.variables[var_name]

        return re.sub(r'\$\{(\w+)\}', replace_var, line)

    def _validate_directive(self, key, value, line_num, filename):
        """Проверяет допустимость значений директив."""
        if key == "Listen":
            if not value.isdigit():
                self.errors.append(f"Недопустимое значение порта в файле {filename}, строка {line_num}: {value}")
        # Добавьте другие проверки по мере необходимости

    def get_config(self):
        """Возвращает итоговую конфигурацию."""
        return dict(self.config)

    def export_json(self, filename):
        """Экспортирует конфигурацию в JSON."""
        with open(filename, 'w') as file:
            json.dump(self.get_config(), file, indent=4)

    def export_yaml(self, filename):
        """Экспортирует конфигурацию в YAML."""
        with open(filename, 'w') as file:
            yaml.dump(self.get_config(), file, default_flow_style=False)

