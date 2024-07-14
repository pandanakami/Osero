from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os


AUTH_FILE = "mycreds.txt"


class GoogleDriveMng:

    def __init__(self):
        gauth = GoogleAuth()

        if os.path.exists(AUTH_FILE):
            gauth.LoadCredentialsFile(AUTH_FILE)  # 保存された認証トークンを読み込み
        else:
            # 認証トークンが無効または存在しない場合、手動認証を実行
            gauth.CommandLineAuth()
            gauth.SaveCredentialsFile(AUTH_FILE)  # 認証トークンをファイルに保存

        self.drive = GoogleDrive(gauth)

    # 指定したディレクトリIDからフォルダのIDを取得する関数
    def _get_folder_id_by_name(self, name, parent_folder_id="root"):
        query = f"'{parent_folder_id}' in parents and title='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folder_list = self.drive.ListFile({"q": query}).GetList()
        if folder_list:
            return folder_list[0]["id"]
        else:
            return None

    # 指定したディレクトリIDからファイルのIDを取得する関数
    def _get_file_id_by_name(self, name, parent_folder_id):
        query = f"'{parent_folder_id}' in parents and title='{name}' and mimeType!='application/vnd.google-apps.folder' and trashed=false"
        file_list = self.drive.ListFile({"q": query}).GetList()
        if file_list:
            return file_list[0]["id"]
        else:
            return None

    # 指定したディレクトリのIDを取得する
    def _get_folder_id_by_path(self, path):
        folder_names = path.split("/")
        parent_folder_id = "root"  # 最上位の親フォルダIDは 'root'

        for name in folder_names:
            folder_id = self._get_folder_id_by_name(name, parent_folder_id)
            if folder_id:
                parent_folder_id = folder_id
            else:
                print(f"Folder '{name}' not found.")
                return None

        return parent_folder_id

    # 指定したディレクトリID内にサブディレクトリを作る
    def _create_subfolder(self, folder_name, parent_folder_id):
        folder_metadata = {
            "title": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [{"id": parent_folder_id}],
        }
        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        return folder["id"]

    # 指定したIDのファイルを取得する
    def _get_file_by_id(self, file_id):
        file = self.drive.CreateFile({"id": file_id})
        file.FetchMetadata()
        return file

    # 指定したパスの要素(フォルダ/ファイル)のIDを取得する
    def get_id_by_path(self, path):
        # ファイルかフォルダか
        if os.path.isdir(path):
            return self._get_folder_id_by_path(path)
        else:
            folder_path, file_name = path.rsplit("/", 1)
            folder_id = self._get_folder_id_by_path(folder_path)
            return self._get_file_id_by_name(file_name, folder_id)

    # 指定したパスのディレクトリを作り、IDを返す
    # 既にあれば、そのパスを返す
    def create_folder(self, folder_name):
        folder_names = folder_name.split("/")
        parent_folder_id = "root"  # 最上位の親フォルダIDは 'root'

        for name in folder_names:
            folder_id = self._get_folder_id_by_name(name, parent_folder_id)
            if folder_id:
                parent_folder_id = folder_id
            else:
                parent_folder_id = self._create_subfolder(name, parent_folder_id)

        return parent_folder_id

    # ファイルをダウンロードする
    def download_file(self, remote_file_path, local_file_path):

        remote_file_path = str.replace(remote_file_path, "\\", "/")
        if os.path.isdir(local_file_path):
            raise IsADirectoryError("ファイル指定して")

        file_id = self.get_id_by_path(remote_file_path)
        if not file_id:
            raise FileNotFoundError(f"ファイルないよ。 path:{remote_file_path}")

        file = self._get_file_by_id(file_id)
        dir = os.path.dirname(local_file_path)
        os.makedirs(dir, exist_ok=True)
        # ダウンロード
        file.GetContentFile(local_file_path)
        print(f"Download file '{file['title']}' downloaded to '{local_file_path}'")

    # ファイルをアップロードする
    def upload_file(
        self,
        local_file_path: str,
        remote_file_path: str,
    ):
        remote_file_path = str.replace(remote_file_path, "\\", "/")

        if os.path.isdir(local_file_path):
            raise IsADirectoryError("ファイル指定して")

        file_id = self.get_id_by_path(remote_file_path)
        if file_id:
            # 上書き
            file = self.drive.CreateFile({"id": file_id})
        else:
            # 新規作成
            dir_name = os.path.dirname(remote_file_path)
            dir_id = self.create_folder(dir_name)

            file = self.drive.CreateFile(
                {
                    "title": os.path.basename(remote_file_path),
                    "parents": [{"id": dir_id}],
                }
            )

        file.SetContentFile(local_file_path)
        file.Upload()

        print(f"Upload file '{file['title']}' id: '{str( file['id'] )}'")
