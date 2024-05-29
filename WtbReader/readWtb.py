import struct
import csv
import os
import shutil


class MyReader:
    def __init__(self, binary_file):
        self.binary_file = binary_file

    def getUint8(self, _: bool = True) -> int:
        raw_data = self.binary_file.read(1)
        return struct.unpack("<B", raw_data)[0]  # '<B' is for little-endian 1 byte

    def getUint16(self, _: bool = True) -> int:
        raw_data = self.binary_file.read(2)
        return struct.unpack("<H", raw_data)[0]  # '<H' is for little-endian 2 byte

    def getUint32(self, _: bool = True) -> int:
        raw_data = self.binary_file.read(4)
        return struct.unpack("<I", raw_data)[0]  # '<I' is for little-endian 4 byte


class WthorHeader:
    def __init__(self, binary_file):
        dv = MyReader(binary_file)
        self.createCentry = dv.getUint8()
        self.createYear = dv.getUint8()
        self.createMonth = dv.getUint8()
        self.createDay = dv.getUint8()
        self.gameCount = dv.getUint32()
        self.count = dv.getUint16()
        self.year = dv.getUint16()
        self.boardSize = dv.getUint8()
        self.type = dv.getUint8()
        self.depth = dv.getUint8()
        dv.getUint8()  # reserve


def read_and_save_binary_data(input_file_path, output_csv_path):
    with open(input_file_path, "rb") as binary_file:

        games = []
        dv = MyReader(binary_file)
        # ヘッダ読み込み
        header = WthorHeader(binary_file)

        # データ読み込み (2)
        for _ in range(header.gameCount):

            # 大会ID
            tournamentId = dv.getUint16()
            # 黒番プレーヤーID
            blackId = dv.getUint16()
            # 白番プレーヤーID
            whiteId = dv.getUint16()
            # 黒番の石数
            blackScore = dv.getUint8()
            # 黒番の石数理論値(終盤depth手が最善だった場合)
            theoreticalBlackScore = dv.getUint8()
            transcript = ""
            # 60手分の棋譜を読み込み
            for _ in range(60):
                move = dv.getUint8()
                if move >= 11 and move <= 88:
                    # 一の位 'a' = 97
                    transcript += chr((move % 10) + 96)
                    # 十の位 '1' = 4
                    transcript += chr((move // 10) + 48)

            games.append(
                [
                    tournamentId,
                    blackId,
                    whiteId,
                    blackScore,
                    theoreticalBlackScore,
                    transcript,
                ]
            )

        # Write to CSV file
        with open(output_csv_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(
                [
                    "tournamentId",
                    "blackPlayerId",
                    "whitePlayerId",
                    "blackScore",
                    "theoreticalBlackScore",
                    "transcript",
                ]
            )
            csv_writer.writerows(games)

        print(f"save:{output_csv_path}")


def getDir(dir):
    folders = [
        os.path.abspath(os.path.join(dir, name))
        for name in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, name))
    ]

    return folders


def getFiles(dir, extension):
    # 拡張子を小文字に変換しておく
    extension = extension.lower()
    # 指定した拡張子のファイルのリストを作成
    files = [
        os.path.join(dir, file)
        for file in os.listdir(dir)
        if file.lower().endswith(extension)
    ]
    return files


def getFilesNest(dir, extension):
    return [file for dir in getDir("input") for file in getFiles(dir, "wtb")]


# 入力ファイル一覧取得
input_files = getFilesNest(dir, "wtb")

# 出力フォルダリセット
if os.path.exists("output"):
    shutil.rmtree("output")
os.makedirs("output")

# 全wtbファイル解析
for i, input_file in enumerate(input_files):
    output_file = f"output/{i}.csv"
    read_and_save_binary_data(input_file, output_file)
