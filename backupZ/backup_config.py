

class Scripts:
    def __init__(self):
        self._dir = None
        self._before_command = None
        self._after_command = None
        self._script_exit_code = 0


class BackupConfig:
    def __init__(self):
        self._filename = "backup %Y-%m-%d %H:%M:%S"
        self._day = 1
        self._time = None
        self._dir = None

        self._storages = []
        self._scripts = []

    def set_filename(self, filename):
        self._filename = filename

    def set_day(self, day):
        self._day = day

    def set_time(self, time):
        self._time = time

    def set_dir(self, _dir):
        self._dir = _dir

    def add_storage(self, storage):
        self._storages.append(storage)

    def add_script(self, script):
        self._scripts.append(script)


