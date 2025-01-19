import yadisk


def upload_to_yadisk(token, local_path, remote_path):
    y = yadisk.YaDisk(token=token)

    if y.exists(remote_path):
        print("Файл уже существует на Яндекс.Диске.")
    else:
        try:
            y.upload(local_path, remote_path)
            print(f"Файл {local_path} успешно загружен на Яндекс.Диск как {remote_path}.")
        except yadisk.exceptions.PathExistsError:
            print("Файл уже существует на Яндекс.Диске.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

