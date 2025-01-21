from datetime import datetime

import yadisk

from backupZ.storages.backup_uploader import BackupUploader


class YandexDiskUploader(BackupUploader):
    def __init__(self, token):
        self.client = yadisk.YaDisk(token=token)

    def upload_file(self, file_path, remote_path):
        if not self.client.exists(remote_path):
            self.client.upload(file_path, remote_path)
            print(f"File '{file_path}' uploaded to Yandex.Disk at '{remote_path}'")
        else:
            print(f"File '{remote_path}' already exists on Yandex.Disk")

    def get_free_space(self):
        disk_info = self.client.get_disk_info()
        total_space = disk_info.total_space  # Общий объем пространства
        used_space = disk_info.used_space    # Используемое пространство
        free_space = total_space - used_space  # Свободное пространство
        return free_space

    def _get_files_sorted_by_date(self, remote_path):
        """Возвращает список файлов в папке, отсортированных по дате изменения (от старых к новым)."""
        files = []
        for item in self.client.listdir(remote_path):
            if item.type == 'file':
                files.append({
                    'path': item.path,
                    'modified': item.modified
                })
        # Сортируем по дате изменения
        files.sort(key=lambda x: datetime.fromisoformat(x['modified']))
        return [file['path'] for file in files]

    def _delete_file(self, file_path):
        """Удаляет файл по его пути."""
        self.client.remove(file_path)
        print(f"Deleted file: {file_path}")

    def _get_file_size(self, file_path):
        """Возвращает размер файла по его пути."""
        file_info = self.client.get_meta(file_path)
        return file_info.size

