import re
import json
import yaml
from collections import defaultdict

class ConfigParser:
    def __init__(self):
        self.config = defaultdict(dict)
        self.current_context = []
        self.errors = []
        self.variables = {}  # Словарь для хранения переменных

    def parse(self, filename):
        """Основной метод для парсинга конфигурационного файла."""
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                self._parse_line(line.strip(), line_num)

        if self.errors:
            print("Ошибки при парсинге:")
            for error in self.errors:
                print(error)

    def _parse_line(self, line, line_num):
        """Парсит одну строку конфигурации."""
        try:
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                return

            # Обработка условий <If ...>
            if_match = re.match(r'<If\s+(.*?)>', line)
            if if_match:
                condition = if_match.group(1)
                self._enter_block(f"If[{condition}]", "", line_num)
                return

            # Обработка блоков <BlockName ...>
            block_match = re.match(r'<(\w+)\s+(.*?)>', line)
            if block_match:
                block_name, block_args = block_match.groups()
                self._enter_block(block_name, block_args, line_num)
                return

            # Обработка закрывающих тегов </BlockName>
            if line.startswith('</'):
                self._exit_block(line, line_num)
                return

            # Обработка переменных ${VAR}
            line = self._replace_variables(line, line_num)

            # Обработка директив
            directive_match = re.match(r'(\w+)\s+(.*)', line)
            if directive_match:
                key, value = directive_match.groups()
                self._validate_directive(key, value, line_num)
                self._add_directive(key, value, line_num)
            else:
                self.errors.append(f"Синтаксическая ошибка в строке {line_num}: {line}")

        except Exception as e:
            self.errors.append(f"Ошибка в строке {line_num}: {str(e)}")

    def _enter_block(self, block_name, block_args, line_num):
        """Обрабатывает вход в блок."""
        self.current_context.append((block_name, block_args))

    def _exit_block(self, line, line_num):
        """Обрабатывает выход из блока."""
        block_close_match = re.match(r'</(\w+)>', line)
        if not block_close_match:
            self.errors.append(f"Неправильный закрывающий тег в строке {line_num}: {line}")
            return

        block_name = block_close_match.group(1)
        if not self.current_context:
            self.errors.append(f"Лишний закрывающий тег </{block_name}> в строке {line_num}")
            return

        last_block_name, _ = self.current_context[-1]
        if last_block_name.split('[')[0] != block_name:  # Учитываем условия в If
            self.errors.append(f"Несоответствие блоков: ожидался </{last_block_name.split('[')[0]}>, но найден </{block_name}> в строке {line_num}")
            return

        self.current_context.pop()

    def _add_directive(self, key, value, line_num):
        """Добавляет директиву в текущий контекст."""
        context_key = self._get_context_key()
        if key in self.config[context_key]:
            self.errors.append(f"Дублирующая директива '{key}' в строке {line_num}")
        self.config[context_key][key] = value

    def _get_context_key(self):
        """Генерирует ключ для текущего контекста."""
        return '/'.join([f"{name}[{args}]" for name, args in self.current_context])

    def _replace_variables(self, line, line_num):
        """Заменяет переменные ${VAR} на их значения."""
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in self.variables:
                self.errors.append(f"Неизвестная переменная ${{{var_name}}} в строке {line_num}")
                return match.group(0)
            return self.variables[var_name]

        return re.sub(r'\$\{(\w+)\}', replace_var, line)

    def _validate_directive(self, key, value, line_num):
        """Проверяет допустимость значений директив."""
        if key == "Listen":
            if not value.isdigit():
                self.errors.append(f"Недопустимое значение порта в строке {line_num}: {value}")
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

