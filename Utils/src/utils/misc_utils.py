import os

def count_python_lines(root_folder):
    total_lines = 0
    py_files = 0

    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        line_count = sum(1 for _ in f)
                        total_lines += line_count
                        py_files += 1
                except OSError as e:
                    print(f"Could not read {file_path}: {e}")

    return total_lines, py_files


if __name__ == "__main__":
    folder = input("Enter folder path: ").strip()
    total_lines, py_files = count_python_lines(folder)
    
    print(f"Python files found: {py_files}")
    print(f"Total lines of Python code: {total_lines}")

    