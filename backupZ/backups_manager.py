from backupZ.check_directives import CheckMainBlockDirectives


class BackupsManager:
    def __init__(self):
        self._config = None

    def set_config(self, config):
        self._config = config

    def start_watching_time(self):
        self._walk_trough_blocks()

    def _check_important_directives(self, block):
        main_block_checker = CheckMainBlockDirectives(block)
        return main_block_checker.check_directives()

    def _walk_trough_blocks(self):
        for main_block in self._config.blocks:
            if not self._check_important_directives(main_block):
                print(
                    f"Для блока {main_block.name} в файле: {main_block.source_file} строка: {main_block.line_num}. Не указаны или не верно указаны важные директивы. Пропускаю его.")
                continue
            # for directive in main_block.directives:
            #     pass
