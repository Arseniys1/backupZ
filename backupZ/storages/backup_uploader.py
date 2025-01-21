import os
from abc import ABC, abstractmethod

class BackupUploader(ABC):
    @abstractmethod
    def upload_file(self, file_path, remote_path=None):
        """Абстрактный метод для загрузки файла."""
        pass

    @abstractmethod
    def get_free_space(self):
        """Абстрактный метод для получения оставшегося свободного пространства."""
        pass

    @abstractmethod
    def _get_files_sorted_by_date(self, remote_path):
        """Абстрактный метод для получения списка файлов, отсортированных по дате."""
        pass

    @abstractmethod
    def _delete_file(self, file_id):
        """Абстрактный метод для удаления файла."""
        pass

    def upload_file_with_cleanup(self, file_path, remote_path=None):
        """Загружает файл, удаляя старые бэкапы, если не хватает места."""
        file_size = os.path.getsize(file_path)
        free_space = self.get_free_space()

        if file_size > free_space:
            print(f"Not enough space. Required: {file_size} bytes, available: {free_space} bytes.")
            self._delete_oldest_files(file_size - free_space, remote_path)

        self.upload_file(file_path, remote_path)

    def _delete_oldest_files(self, required_space, remote_path):
        """Удаляет самые старые файлы, пока не освободится достаточно места."""
        files = self._get_files_sorted_by_date(remote_path)
        deleted_size = 0

        for file in files:
            if deleted_size >= required_space:
                break
            file_size = self._get_file_size(file)
            self._delete_file(file)
            deleted_size += file_size
            print(f"Deleted old backup: {file} ({file_size} bytes)")

        print(f"Freed up {deleted_size} bytes.")

    @abstractmethod
    def _get_file_size(self, file_id):
        """Абстрактный метод для получения размера файла."""
        pass

