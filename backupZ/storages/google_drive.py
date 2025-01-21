import os

from google.auth.transport import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from backupZ.storages.backup_uploader import BackupUploader


class GoogleDriveUploader(BackupUploader):
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._authenticate()

    def _authenticate(self):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        return build('drive', 'v3', credentials=creds)

    def upload_file(self, file_path, folder_id=None):
        file_name = os.path.basename(file_path)
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File '{file_name}' uploaded to Google Drive with ID: {file.get('id')}")

    def get_free_space(self):
        about = self.service.about().get(fields="storageQuota").execute()
        storage_quota = about.get('storageQuota', {})
        total_space = int(storage_quota.get('limit', 0))  # Общий объем пространства
        used_space = int(storage_quota.get('usage', 0))   # Используемое пространство
        free_space = total_space - used_space             # Свободное пространство
        return free_space

    def _get_files_sorted_by_date(self, folder_id):
        """Возвращает список файлов в папке, отсортированных по дате создания (от старых к новым)."""
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(
            q=query,
            fields="files(id, name, createdTime)",
            orderBy="createdTime"
        ).execute()
        files = results.get('files', [])
        return files

    def _delete_file(self, file_id):
        """Удаляет файл по его ID."""
        self.service.files().delete(fileId=file_id).execute()
        print(f"Deleted file with ID: {file_id}")

    def _get_file_size(self, file_id):
        """Возвращает размер файла по его ID."""
        file = self.service.files().get(fileId=file_id, fields="size").execute()
        return int(file.get('size', 0))

