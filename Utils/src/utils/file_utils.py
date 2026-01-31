import re
import os


def get_highest_file_version(folder: str, pattern: re.compile) -> str:
    highest_version = 0

    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            match = pattern.match(fname)
            if match:
                version_num = int(match.group(1))
                if version_num > highest_version:
                    highest_version = version_num

    return highest_version


def get_highest_folder_version(folder: str, pattern: re.compile) -> str:
    highest_version = 0

    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isdir(fpath):
            match = pattern.match(fname)
            if match:
                version_num = int(match.group(1))
                if version_num > highest_version:
                    highest_version = version_num

    return highest_version


def get_next_usd_file(file_base: str, folder: str, extension="usd") -> str:
    pattern = re.compile(rf"^{re.escape(file_base)}_v(\d+)\.(usd[a-z]*)$")
    version = get_highest_file_version(folder, pattern)
    next_version = version + 1
    return fr"{folder}\{file_base}_v{next_version:03d}.{extension}"


def get_next_ma_file(file_base: str, folder: str, extension="ma") -> str:
    pattern = re.compile(rf"^{re.escape(file_base)}_v(\d+)\.ma$")
    version = get_highest_file_version(folder, pattern)
    next_version = version + 1
    return fr"{folder}\{file_base}_v{next_version:03d}.{extension}"


def get_next_render_folder(folder: str):
    pattern = re.compile(rf"v(\d+)")
    version = get_highest_folder_version(folder, pattern)
    next_version = version + 1
    return fr"v{next_version:03d}"


def reformat_path(path: str):
    new_path = path.replace(r"P:/", "//monster/projects/")
    return new_path


if __name__ == "__main__":
    folder = fr"{os.getenv('PROJ')}\30_assets\depot\Char\Tubey\Geo"
    file = "Tubey"
    get_highest_file_version(file, folder)
    
    #print(os.listdir(folder))
