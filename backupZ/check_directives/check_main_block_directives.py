import os
from datetime import datetime

from backupZ.check_directives.check_directives import CheckDirectives


class CheckMainBlockDirectives(CheckDirectives):
    def __init__(self, main_block):
        super().__init__(main_block)
        self._dir_directive_found = False
        self._time_directive_found = False

    def check_directives(self):
        for directive in self._main_block.directives:
            if directive.key == "Dir":
                if self._validate_dir_directive(directive):
                    self._dir_directive_found = True
            elif directive.key == "Time":
                if self._validate_time_directive(directive):
                    self._time_directive_found = True

        if self._dir_directive_found and self._time_directive_found:
            return True

    def _validate_dir_directive(self, directive):
        if os.path.isdir(directive.value):
            return True
        else:
            print(f"Не верно указан путь у директивы Dir. В файле: {directive.source_file} строка: {directive.line_num}")

    def _validate_time_directive(self, directive):
        try:
            datetime.strptime(directive.value, '%H:%M')
            return True
        except ValueError:
            print(f"Не верно указано время бэкапа у директивы Time. В файле: {directive.source_file} строка: {directive.line_num}")

