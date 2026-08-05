from collections import namedtuple
from importlib import import_module
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import (
    StringProperty,
    ObjectProperty,
    BooleanProperty,
    NumericProperty,
)
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.graphics import Color, Rectangle, RoundedRectangle
from utils import rel_path

NavItemSpec = namedtuple("NavItemSpec", ["name", "label", "icon"])



class NavItem(ButtonBehavior, BoxLayout):
    name = StringProperty("")
    active = BooleanProperty(False)
    _bg_opacity = NumericProperty(0)

    # Base background height
    base_bg_h = dp(32)

    # Scale multiplier for spring animation (1.0 = normal width/height)
    bg_scale_x = NumericProperty(1.0)
    bg_scale_y = NumericProperty(1.0)

    def __init__(
        self,
        active_color,
        inactive_color,
        item_bg_color,
        name,
        label,
        icon,
        **kwargs
    ):
        super().__init__(
            orientation="vertical",
            padding=(0, dp(6)),
            spacing=dp(2),
            **kwargs,
        )
        self.name = name
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.item_bg_color = item_bg_color

        self.icon = Label(
            text=icon, font_name=rel_path("icon/MaterialSymbolsRounded.ttf"), font_size=dp(20), color=inactive_color
        )
        self.text_label = Label(
            text=label,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(14),
            color=inactive_color,
        )
        self.add_widget(self.icon)
        self.add_widget(self.text_label)

        # Draw background instruction
        with self.canvas.before:
            self._bg_color = Color(*self.item_bg_color[:3], self._bg_opacity)
            self._bg_rect = RoundedRectangle(
                pos=(0, 0), size=(0, 0), radius=[dp(16)]
            )

        # Bind position/size updates to redrawing the background shape
        self.icon.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(
            pos=self._update_bg,
            size=self._update_bg,
            bg_scale_x=self._update_bg,
            bg_scale_y=self._update_bg,
            _bg_opacity=self._update_bg_opacity,
        )
        self.bind(active=self._on_active)

        # Defer initial state sync until layout completes
        Clock.schedule_once(self._post_init_layout, 0)

    def _post_init_layout(self, *_):
        self._update_bg()
        if self.active:
            self._bg_opacity = self.item_bg_color[3]

    def _on_active(self, *_):
        target_color = self.active_color if self.active else self.inactive_color
        target_opacity = self.item_bg_color[3] if self.active else 0

        Animation(color=target_color, d=0.12, t="out_quad").start(self.icon)
        Animation(color=target_color, d=0.12, t="out_quad").start(self.text_label)
        Animation(_bg_opacity=target_opacity, d=0.12, t="out_quad").start(self)

        Animation.cancel_all(self, 'bg_scale_x', 'bg_scale_y')

        if self.active:
            # Icon pop animation
            self.icon.font_size = dp(24)
            Animation(font_size=dp(20), d=0.15, t="out_back").start(self.icon)

            # Spring Animation using scale factors so layout width isn't overwritten
            expand_anim = Animation(
                bg_scale_x=1.15,
                bg_scale_y=1.25,
                d=0.1,
                t="out_quad",
            )
            spring_anim = Animation(
                bg_scale_x=1.0,
                bg_scale_y=1.0,
                d=0.45,
                t="out_elastic",
            )
            (expand_anim + spring_anim).start(self)
        else:
            self.bg_scale_x = 1.0
            self.bg_scale_y = 1.0

    def _update_bg(self, *_):
        # Calculate target width (90% of NavItem total width)
        target_w = self.width * 0.9 * self.bg_scale_x
        target_h = self.base_bg_h * self.bg_scale_y

        # Center relative to icon
        self._bg_rect.pos = (
            self.icon.center_x - (target_w / 2),
            self.icon.center_y - (target_h / 2),
        )
        self._bg_rect.size = (target_w, target_h)

    def _update_bg_opacity(self, *args):
        self._bg_color.a = self._bg_opacity



class NavBase(BoxLayout):
    active = StringProperty("")
    screen_manager = ObjectProperty(None, allow_none=True)


    def __init__(
        self,
        active_color,
        inactive_color,
        bg_color,
        item_bg_color,
        items,
        screen_manager=None,
        active=None,
        **kwargs
    ):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            **kwargs,
        )
        self.screen_manager = screen_manager
        self._items = {}
        self._order = [item.name for item in items]

        with self.canvas.before:
            Color(*bg_color)
            self._bg = Rectangle(
                pos=(self.x, self.y + dp(1)), size=(self.width, self.height - dp(1))
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

        for item in items:
            nav_item = NavItem(
                active_color,
                inactive_color,
                item_bg_color,
                item.name,
                item.label,
                item.icon
            )
            nav_item.bind(on_release=self._make_handler(item.name))
            self.add_widget(nav_item)
            self._items[item.name] = nav_item

        self.active = active or (items[0].name if items else "")

    def _make_handler(self, name):
        def handler(_instance):
            self.select(name)

        return handler

    def _update_bg(self, *_):
        self._bg.pos = (self.x, self.y + dp(1))
        self._bg.size = (self.width, self.height - dp(1))

    def select(self, name):
        if name not in self._items:
            return
        self.active = name

    def set_badge(self, name, count):
        if name in self._items:
            self._items[name].badge = count

    def on_active(self, *_):
        for name, item in self._items.items():
            item.active = name == self.active

        self.screen_manager.transition = FadeTransition(duration=0.18)
        self.screen_manager.current = self.active
 
class SM(ScreenManager):
    screen_config = None
    
    def __init__(self, screen_config={}, **kwargs):
        super().__init__(**kwargs)
        self.orientation="vertical"
        self.screen_config = screen_config

    def on_current(self, instance, value):
        if not self.has_screen(value):
            screen_module_path, screen_class_name, screen_icon = self.screen_config[value]
            screen_module = import_module(
                screen_module_path + ".screen"
            )
            screen_class = getattr(screen_module, screen_class_name)
            screen = screen_class()
            self.add_widget(screen)
        supra = super().on_current(instance, value)
        return supra


class BottomNavBar(BoxLayout):
    def __init__(
        self,
        screen_config={},
        active_color=(0.30, 0.34, 0.98, 1),
        inactive_color=(0.56, 0.56, 0.60, 1),
        bg_color=(1, 1, 1, 1),
        item_bg_color=(0.30, 0.34, 0.98, 0.12),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.orientation="vertical"
        items = []
        for s in list(screen_config):
            items.append(NavItemSpec(s, s, screen_config[s][2]))

        self.sm = SM(screen_config)
        
        nav = NavBase(
            active_color,
            inactive_color,
            bg_color,
            item_bg_color,
            items=items,
            screen_manager=self.sm,
            active=list(screen_config)[0],
        )
        
        self.add_widget(self.sm)
        self.add_widget(nav)
        
    
    
        
