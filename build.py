import os
import subprocess
import sys


def get_data_files(base_dir=os.getcwd()):
    data_files = []
    exclude_dirs = ["_internal", "build", "dist", "venv", "__pycache__", ".git"]
    include_ext = ["kv", "png", "jpg", "jpeg", "gif", "bmp", "svg", "ico", "ttf", "codepoints", "otf", "woff", "woff2"]
    
    for root, dirs, files in os.walk(base_dir):
        arr_root = root.split(os.sep)
        for file in files:
            if all(item not in arr_root for item in exclude_dirs):
                if os.path.splitext(file)[1][1:] in include_ext:
                    # print(arr_root, file)
                    # if file.endswith(".kv"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, base_dir)
                    data_files.append((full_path, rel_path))
    return data_files


def get_hidden_imports():
    return [
        "scrollable.recycleview",
        "kivy.core.window",
        "app.outline.screen",
        "app.round.screen",
        "app.sharp.screen",
    ]

def build():
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "Material Icon",
        "--icon",
        "icon.png",
        "--windowed",
        "main.py",
    ]

    # Add data files
    for src, dst in get_data_files():
        command.extend([
            "--add-data",
            f"{src};{dst}"
        ])

    # Add hidden imports
    for module in get_hidden_imports():
        command.extend([
            "--hidden-import",
            module
        ])

    print("Running:")
    print(" ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    build()