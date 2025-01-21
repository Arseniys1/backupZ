from abc import ABC, abstractmethod


class CheckDirectives(ABC):
    def __init__(self, main_block):
        self._main_block = main_block

    @abstractmethod
    def check_directives(self):
        pass

