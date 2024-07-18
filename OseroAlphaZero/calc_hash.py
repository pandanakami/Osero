import hashlib
from path_mng import get_path


# ハッシュ値を計算する関数
def calculate_file_hash(filepath, hash_algo="sha256"):
    hash_function = hashlib.new(hash_algo)
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hash_function.update(chunk)
    return hash_function.hexdigest()


if __name__ == "__main__":
    # ハッシュ値の計算
    hash_value = calculate_file_hash(get_path("model/latest.h5"))
    print(hash_value)
