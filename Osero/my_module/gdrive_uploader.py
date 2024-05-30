from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

auth_file = "mycreds.txt"


class GoogleDriveFacade:

    def __init__(self):
        gauth = GoogleAuth()

        if os.path.exists(auth_file):
            gauth.LoadCredentialsFile(auth_file)  # 保存された認証トークンを読み込み
        else:
            # 認証トークンが無効または存在しない場合、手動認証を実行
            gauth.CommandLineAuth()
            gauth.SaveCredentialsFile(auth_file)  # 認証トークンをファイルに保存

        self.drive = GoogleDrive(gauth)

    def create_folder(self, folder_name):
        ret = self.check_files(folder_name)
        if ret:
            folder = ret
            print(f"{folder['title']}: exists")
        else:
            folder = self.drive.CreateFile(
                {"title": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            )
            folder.Upload()

        return folder

    def check_files(
        self,
        folder_name,
    ):
        query = f'title = "{os.path.basename(folder_name)}"'

        list = self.drive.ListFile({"q": query}).GetList()
        if len(list) > 0:
            return list[0]
        return False

    def upload(
        self,
        local_file_path: str,
        save_folder_id: str = None,
        save_folder_name: str = None,
        is_convert: bool = False,
    ):
        if save_folder_id:
            pass
        elif save_folder_name:
            folder = self.create_folder(save_folder_name)
            save_folder_id = folder["id"]
        else:
            raise KeyError("save_folder_idかsave_folder_nameを指定")

        file = self.drive.CreateFile(
            {
                "title": os.path.basename(local_file_path),
                "parents": [{"id": save_folder_id}],
            }
        )
        file.SetContentFile(local_file_path)
        file.Upload({"convert": is_convert})

        drive_url = f"https://drive.google.com/uc?id={str( file['id'] )}"
        return drive_url
