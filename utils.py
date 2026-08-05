import sys, os

def rel_path(file_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(base_path, file_path)
    return full_file_path

