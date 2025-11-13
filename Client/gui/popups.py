from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty


class GridForm(GridLayout):
    pass


class ConfigPopup(Popup):
    title_text = StringProperty("Configuración")
    content_widget = ObjectProperty(None)

    def __init__(self, title_text, content_widget, **kwargs):
        super().__init__(**kwargs)
        self.title_text = title_text
        self.ids.scroll_content.add_widget(content_widget)
