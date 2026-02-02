import re
import os


def get_highest_file_version(folder: str, pattern: re.compile) -> str:
    """
    Gets highest known version of a file in a given folder.

    Args:
        folder (str): Folder to traverse.
        pattern (re.compile): Pattern to match.

    Returns:
        str: Highest current version.
    """
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
    """
    Gets highest known version of a folder in a given folder.

    Args:
        folder (str): Folder to traverse.
        pattern (re.compile): Pattern to match.

    Returns:
        str: Highest current version.
    """
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
    """
    Gets path of the next Usd version to create.

    Args:
        file_base (str): Base file name.
        folder (str): Folder to traverse.
        extension (str, optional): Extension of Usd file. Defaults to "usd".

    Returns:
        str: Versioned Usd file path.
    """
    pattern = re.compile(rf"^{re.escape(file_base)}_v(\d+)\.(usd[a-z]*)$")
    version = get_highest_file_version(folder, pattern)
    next_version = version + 1
    return fr"{folder}\{file_base}_v{next_version:03d}.{extension}"


def get_next_ma_file(file_base: str, folder: str, extension="ma") -> str:
    """
    Gets path of the next Ma version to create.

    Args:
        file_base (str): Base file name.
        folder (str): Folder to traverse.
        extension (str, optional): Extension of Ma file. Defaults to "ma".

    Returns:
        str: Versioned Ma file path.
    """
    pattern = re.compile(rf"^{re.escape(file_base)}_v(\d+)\.ma$")
    version = get_highest_file_version(folder, pattern)
    next_version = version + 1
    return fr"{folder}\{file_base}_v{next_version:03d}.{extension}"


def get_next_render_folder(folder: str) -> str:
    """
    Gets path of the next render folder version to create.

    Args:
        folder (str): Folder to traverse.

    Returns:
        str: Next version of folder to create.
    """
    pattern = re.compile(rf"v(\d+)")
    version = get_highest_folder_version(folder, pattern)
    next_version = version + 1
    return fr"v{next_version:03d}"


def reformat_path(path: str) -> str:
    """
    Formats path of university drive from local name to network name.

    Args:
        path (str): Path to reformat.

    Returns:
        str: Reformated path.
    """
    new_path = path.replace(r"P:/", "//monster/projects/")
    return new_path


if __name__ == "__main__":
    folder = fr"{os.getenv('PROJ')}\30_assets\depot\Char\Tubey\Geo"
    file = "Tubey"
    get_highest_file_version(file, folder)
    
    #print(os.listdir(folder))
