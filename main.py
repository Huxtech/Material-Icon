from kivy.config import Config
Config.set('graphics', 'resizable', 0)
# # Config.set('graphics', 'borderless', 1)
Config.set('kivy', 'window_icon', "icon.png")
Config.set('graphics', 'background_color', "1,1,1,1")
Config.set('graphics', 'window_state', "normal")
# # Config.set('graphics', 'fullscreen', "normal")
Config.set('graphics', 'width', 320)
Config.set('graphics', 'minimum_width', 320)
Config.set('graphics', 'height', 640)
Config.set('graphics', 'minimum_height', 640)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
# Config.write()


from kivy.app import App
from bottomnavigation import BottomNavBar
from kivy.lang import Builder
from kivy import platform
from kivy.graphics import Color, Rectangle
from kivy.properties import ColorProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from utils import rel_path

if platform == "android":
    from kvdroid.tools import check_keyboard_visibility_and_get_height
    from _android import set_soft_input_adjust_nothing
    set_soft_input_adjust_nothing()


class BaseBox(BoxLayout):
    # Kivy properties allow passing values via __init__ kwargs seamlessly
    bg_color = ColorProperty([1, 1, 1, 1])
    _height = NumericProperty(0)

    def __init__(self, **kwargs):
        # Set full width (1) and fixed height (None) by default
        super().__init__(**kwargs)
        
        # Setup canvas instructions
        with self.canvas.before:
            self._color_instruction = Color(rgba=self.bg_color)
            self._rect_instruction = Rectangle(pos=self.pos, size=self.size)

        # Bind size, position, and color changes to automatic canvas updates
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(bg_color=self._update_color)

    def _update_canvas(self, instance, value):
        """Re-fits the background rectangle whenever size or position changes."""
        self._rect_instruction.pos = self.pos
        self._rect_instruction.size = self.size

    def _update_color(self, instance, value):
        """Updates the background color dynamically if bg_color is changed later."""
        self._color_instruction.rgba = value


class BottomNavDemoApp(App):
    font_name = rel_path("icon/MaterialSymbolsRounded.ttf")
    temp_root = ObjectProperty()
    
    def build(self):
        if platform == "android":
            from kvdroid.tools.display import get_statusbar_height, get_navbar_height
            self.statusbar_height = get_statusbar_height()
            self.navbar_height = get_navbar_height()
        else:
            self.statusbar_height = 0
            self.navbar_height = 0
        
        self.title = "Bottom Navigation Demo"
        sc = {
            "RoundIcon": ("app.round", "RoundIconScreen", "crown"),
            "SharpIcon": ("app.sharp", "SharpIconScreen", "health_cross"),
            "OutlinedIcon": ("app.outline", "OutlinedIconScreen", "margin"),
        }
        Builder.load_file(rel_path("main.kv"))
        root = BottomNavBar(
            screen_config=sc,
            # active_color=
            # inactive_color=
            # bg_color=(1,1,0,1),
            # item_bg_color=(1,0,0,1)
        )
        
        self.temp_root = BaseBox(size_hint=(1, 1), orientation='vertical', padding=[0, self.statusbar_height, 0, self.navbar_height])
        self.temp_root.add_widget(root)
        return self.temp_root
    
    def on_resume(self):
        if platform == "android":
            set_soft_input_adjust_nothing()
    
    
    def input_handler(self, instance, search_container):
        search_container.is_focused = instance.focus
        if platform == "android":
            visible, height = check_keyboard_visibility_and_get_height()
            if visible:
                self.temp_root.padding = [0, self.statusbar_height, 0, height]
            else:
                self.temp_root.padding = [0, self.statusbar_height, 0, self.navbar_height]
            
   
if __name__ == "__main__":
    BottomNavDemoApp().run()
    
    
