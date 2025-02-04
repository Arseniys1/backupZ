import argparse
import os
import platform
import sys
from pprint import pprint

from backupZ.backups_manager import BackupsManager
from backupZ.config_parser import ConfigParser
from backupZ.patterns.singleton import Singleton


class App(Singleton):
    def __init__(self):
        self._current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        self._parser = ConfigParser()
        self._backups_manager = BackupsManager()
        self.__parse_arguments()

    def __parse_arguments(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("-cd", "--config-dir", help="Путь к папке конфигов", default="")

        self.args = parser.parse_args()

    def __parse_config(self):
        self._parser.parse_directory(f"{self._current_directory}/configs")

        self._config = self._parser.get_config()
        pprint(self._config)

    def _set_parser_variables(self):
        self._parser.variables = {
            "OS": platform.system()
        }

    def main(self):
        self._set_parser_variables()
        self.__parse_config()

        if self._parser.errors_exists:
            print("Исправьте ошибки в конфигурации")
            return

        self._backups_manager.set_config(self._config)
        self._backups_manager.start_watching_time()


