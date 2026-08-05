from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout



def load_icons(codepoints_file):
    icons = {}
    try:
        with open(codepoints_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or len(line.split()) != 2:
                    continue
                name, code = line.split()
                icons[name] = f"\\u{code.lower()}"
    except FileNotFoundError:
        print(f"Error: File not found at '{codepoints_file}'")
    return icons


class SearchBarContainer(BoxLayout):
    is_focused = BooleanProperty(False)


class IconRow(BoxLayout):
    name = StringProperty("")
    icon = StringProperty("")
    ttf_path = StringProperty("")
    unicode_value = StringProperty("")


class IconList(BoxLayout):
    all_icons = ListProperty([])

    def __init__(self, codepoint_file, ttf_path, **kwargs):
        super().__init__(**kwargs)
        self.load_data(codepoint_file, ttf_path)

    def load_data(self, codepoint_file, ttf_path):
        icons = load_icons(codepoint_file)
        data = []

        for name, unicode_value in icons.items():
            try:
                hex_str = unicode_value.replace("\\u", "")
                unicode_char = chr(int(hex_str, 16))
            except Exception:
                continue

            data.append({
                "name": name,
                "unicode_value": unicode_value,
                "icon": unicode_char,
                "ttf_path": ttf_path
            })

        self.all_icons = data
        self.ids.rv.data = data

    def search(self, text):
        text = text.lower().strip()
        if not text:
            self.ids.rv.data = self.all_icons
            return

        self.ids.rv.data = [
            item for item in self.all_icons
            if text in item["name"].lower()
        ]
