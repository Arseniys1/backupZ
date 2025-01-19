import os
import re
import json
import yaml
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Directive:
    """Класс для представления директивы."""
    key: str
    value: str
    source_file: str
    line_num: int

@dataclass
class BlockArgs:
    """Класс для представления аргументов блока."""
    raw_args: str  # Сырые аргументы (например, "*:80")
    parsed_args: Dict[str, str] = field(default_factory=dict)  # Парсированные аргументы (например, {"host": "*", "port": "80"})

    def __post_init__(self):
        """Парсит аргументы при создании объекта."""
        self.parsed_args = self._parse_args(self.raw_args)

    def _parse_args(self, raw_args: str) -> Dict[str, str]:
        """Парсит аргументы блока."""
        if not raw_args:
            return {}

        # Пример: *:80 -> {"host": "*", "port": "80"}
        args_dict = {}
        parts = raw_args.split()
        for part in parts:
            if ':' in part:
                host, port = part.split(':', 1)
                args_dict["host"] = host
                args_dict["port"] = port
            elif '=' in part:
                key, value = part.split('=', 1)
                args_dict[key] = value
            else:
                args_dict[part] = True  # Аргумент без значения (флаг)
        return args_dict

@dataclass
class Block:
    """Класс для представления блока."""
    name: str
    args: BlockArgs  # Аргументы блока
    directives: Dict[str, Directive] = field(default_factory=dict)
    blocks: Dict[str, 'Block'] = field(default_factory=dict)
    source_file: str = ""
    line_num: int = 0

@dataclass
class Config:
    """Класс для представления всей конфигурации."""
    blocks: Dict[str, Block] = field(default_factory=dict)
    directives: Dict[str, Directive] = field(default_factory=dict)

class ConfigParser:
    def __init__(self):
        self.config = Config()  # Конфигурация
        self.current_context: List[Block] = []  # Текущий контекст (вложенные блоки)
        self.errors: List[str] = []  # Список для хранения ошибок
        self.variables: Dict[str, str] = {}  # Словарь для хранения переменных
        self.current_file: Optional[str] = None  # Текущий файл, который парсится

    def parse_file(self, filename: str):
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

    def parse_directory(self, directory: str):
        """Рекурсивно парсит все файлы в указанной папке."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.conf'):  # Парсим только .conf файлы
                    filepath = os.path.join(root, file)
                    self.parse_file(filepath)

    def _parse_line(self, line: str, line_num: int, filename: str):
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

    def _clean_value(self, value: str) -> str:
        """Убирает лишние кавычки из значения."""
        return value.strip('"\'')

    def _enter_block(self, block_name: str, block_args: str, line_num: int, filename: str):
        """Обрабатывает вход в блок."""
        args = BlockArgs(raw_args=block_args)  # Создаем объект BlockArgs
        new_block = Block(name=block_name, args=args, source_file=filename, line_num=line_num)
        if self.current_context:
            # Если есть текущий контекст, добавляем новый блок как вложенный
            self.current_context[-1].blocks[block_name] = new_block
        else:
            # Иначе добавляем блок на верхний уровень
            self.config.blocks[block_name] = new_block
        self.current_context.append(new_block)

    def _exit_block(self, line: str, line_num: int, filename: str):
        """Обрабатывает выход из блока."""
        block_close_match = re.match(r'</(\w+)>', line)
        if not block_close_match:
            self.errors.append(f"Неправильный закрывающий тег в файле {filename}, строка {line_num}: {line}")
            return

        block_name = block_close_match.group(1)
        if not self.current_context:
            self.errors.append(f"Лишний закрывающий тег </{block_name}> в файле {filename}, строка {line_num}")
            return

        last_block_name = self.current_context[-1].name
        if last_block_name.split('[')[0] != block_name:  # Учитываем условия в If
            self.errors.append(f"Несоответствие блоков в файле {filename}, строка {line_num}: ожидался </{last_block_name.split('[')[0]}>, но найден </{block_name}>")
            return

        self.current_context.pop()

    def _add_directive(self, key: str, value: str, line_num: int, filename: str):
        """Добавляет директиву в текущий контекст."""
        directive = Directive(key=key, value=value, source_file=filename, line_num=line_num)
        if self.current_context:
            # Если есть текущий контекст, добавляем директиву в текущий блок
            self.current_context[-1].directives[key] = directive
        else:
            # Иначе добавляем директиву на верхний уровень
            self.config.directives[key] = directive

    def _replace_variables(self, line: str, line_num: int, filename: str) -> str:
        """Заменяет переменные ${VAR} на их значения."""
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in self.variables:
                self.errors.append(f"Неизвестная переменная ${{{var_name}}} в файле {filename}, строка {line_num}")
                return match.group(0)
            return self.variables[var_name]

        return re.sub(r'\$\{(\w+)\}', replace_var, line)

    def _validate_directive(self, key: str, value: str, line_num: int, filename: str):
        """Проверяет допустимость значений директив."""
        if key == "Listen":
            if not value.isdigit():
                self.errors.append(f"Недопустимое значение порта в файле {filename}, строка {line_num}: {value}")
        # Добавьте другие проверки по мере необходимости

    def get_config(self) -> Config:
        """Возвращает итоговую конфигурацию."""
        return self.config

    def export_json(self, filename: str):
        """Экспортирует конфигурацию в JSON."""
        with open(filename, 'w') as file:
            json.dump(self._config_to_dict(self.config), file, indent=4)

    def export_yaml(self, filename: str):
        """Экспортирует конфигурацию в YAML."""
        with open(filename, 'w') as file:
            yaml.dump(self._config_to_dict(self.config), file, default_flow_style=False)

    def _config_to_dict(self, config: Config) -> Dict:
        """Преобразует объект Config в словарь."""
        result = {
            "directives": {k: vars(v) for k, v in config.directives.items()},
            "blocks": {k: self._block_to_dict(v) for k, v in config.blocks.items()}
        }
        return result

    def _block_to_dict(self, block: Block) -> Dict:
        """Преобразует объект Block в словарь."""
        return {
            "name": block.name,
            "args": vars(block.args),  # Преобразуем BlockArgs в словарь
            "directives": {k: vars(v) for k, v in block.directives.items()},
            "blocks": {k: self._block_to_dict(v) for k, v in block.blocks.items()},
            "source_file": block.source_file,
            "line_num": block.line_num
        }

