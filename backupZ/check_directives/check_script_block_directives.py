from backupZ.check_directives.check_directives import CheckDirectives


class CheckScriptBlockDirectives(CheckDirectives):
    def __init__(self, main_block):
        super().__init__(main_block)
        self._scripts_block_found = False
        self._dir_directive_found = False
        self._before_command_found = False
        self._after_command_found = False

    def check_directives(self):
        for block in self._main_block.blocks:
            if block.name == "Scripts":
                self._scripts_block_found = True

                for directive in block.directives:
                    if directive.name == "Dir":
                        pass

