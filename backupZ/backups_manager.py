from backupZ.create_backup_configs import CreateBackupConfigs


class BackupsManager:
    def __init__(self):
        self._config = None
        self._backup_configs = None

    def set_config(self, config):
        self._config = config

    def _create_backup_configs(self):
        cbc = CreateBackupConfigs(self._config)
        self._backup_configs = cbc.create_configs()

    def start_watching_time(self):
        self._create_backup_configs()



