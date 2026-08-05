from kivy.uix.screenmanager import Screen
from icon.icon_definitions import IconList
from utils import rel_path

class OutlinedIconScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "OutlinedIcon"
        font_name = "MaterialSymbolsOutlined"
        self.add_widget(IconList(
            rel_path(f"icon/{font_name}.codepoints"),
            rel_path(f"icon/{font_name}.ttf")
        ))

