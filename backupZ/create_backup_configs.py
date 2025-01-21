from backupZ.backup_config import BackupConfig
from backupZ.check_directives.check_main_block_directives import CheckMainBlockDirectives
from backupZ.check_directives.check_script_block_directives import CheckScriptBlockDirectives


class CreateBackupConfigs:
    def __init__(self, config):
        self._config = config

    def _check_important_directives(self, main_block):
        main_block_checker = CheckMainBlockDirectives(main_block)
        return main_block_checker.check_directives()

    def _check_important_scripts_directives(self, main_block):
        scripts_block_checker = CheckScriptBlockDirectives(main_block)
        return scripts_block_checker.check_directives()

    def _fill_backup_config_directives(self, main_block, backup_config):
        for directive in main_block.directives:
            if directive.key == "Dir":
                backup_config.set_dir(directive.value)
            elif directive.key == "Day":
                backup_config.set_day(directive.value)
            elif directive.key == "Time":
                backup_config.set_time(directive.value)
            elif directive.key == "FileName":
                backup_config.set_filename(directive.value)

    def _fill_backup_config_blocks(self, main_block, backup_config):
        for block in main_block.blocks:
            if block.name == "Scripts":
                pass

    def create_configs(self):
        backup_configs = []

        for main_block in self._config.blocks:
            if not self._check_important_directives(main_block):
                print(
                    f"Для блока {main_block.name} в файле: {main_block.source_file} строка: {main_block.line_num}. Не указаны или не верно указаны важные директивы. Пропускаю его.")
                continue

            backup_config = BackupConfig()

            self._fill_backup_config_directives(main_block, backup_config)

            if not self._check_important_scripts_directives(main_block):
                print(
                    f"В блоке {main_block.name} в файле: {main_block.source_file} строка: {main_block.line_num}. Не указаны или не верно указаны важные директивы для блока Scripts. Пропускаю его.")
                continue

            self._fill_backup_config_blocks(main_block, backup_config)

            print(backup_config)

