from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.label import Label

from kivy_garden.hover import HoverBehavior, HoverManager

Builder.load_string("""
<RootWidget>:
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
""")


class RootWidget(HoverBehavior, Label):

    background_color = ColorProperty('darkgreen')

    def on_hover_enter(self, me):
        self.text = f'Enter: {me.pos}'

    def on_hover_update(self, me):
        self.text = f'Update: {me.pos}'

    def on_hover_leave(self, me):
        self.text = f'Leave: {me.pos}'


class SimpleHoverApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hover_manager = HoverManager()

    def build(self):
        return RootWidget(size_hint=(0.5, 0.5),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})

    def on_start(self):
        super().on_start()
        self.root_window.register_event_manager(self.hover_manager)

    def on_stop(self):
        super().on_stop()
        self.root_window.unregister_event_manager(self.hover_manager)


if __name__ == '__main__':
    SimpleHoverApp().run()
