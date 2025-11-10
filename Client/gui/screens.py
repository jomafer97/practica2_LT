from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.app import App  # ✅ para acceder a la app actual sin importar main.py
from .panels import MainPanel


class MainWindow(Screen):
    """Pantalla 1: Solo botón NEXT"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainPanel())
        button_next = Button(
            text="NEXT",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0.875, "y": 0},
            background_color=(0.2, 0.6, 1, 1),
        )
        button_next.bind(on_release=self.go)
        self.add_widget(button_next)

    def go(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.second_window, direction="left")


class SecondWindow(Screen):
    """Pantalla 2: BACK / NEXT"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainPanel())

        button_back = Button(
            text="BACK",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0, "y": 0},
            background_color=(1, 0.5, 0.2, 1),
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

        button_next = Button(
            text="NEXT",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0.875, "y": 0},
            background_color=(0.2, 0.6, 1, 1),
        )
        button_next.bind(on_release=self.go_next)
        self.add_widget(button_next)

    def go_back(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.main_window, direction="right")

    def go_next(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.third_window, direction="left")


class ThirdWindow(Screen):
    """Pantalla 3"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainPanel())

        button_back = Button(
            text="BACK",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0, "y": 0},
            background_color=(1, 0.5, 0.2, 1),
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

        button_next = Button(
            text="NEXT",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0.875, "y": 0},
            background_color=(0.2, 0.6, 1, 1),
        )
        button_next.bind(on_release=self.go_next)
        self.add_widget(button_next)

    def go_back(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.second_window, direction="right")

    def go_next(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.fourth_window, direction="left")


class FourthWindow(Screen):
    """Pantalla 4"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainPanel())

        button_back = Button(
            text="BACK",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0, "y": 0},
            background_color=(1, 0.5, 0.2, 1),
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

        button_next = Button(
            text="NEXT",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0.875, "y": 0},
            background_color=(0.2, 0.6, 1, 1),
        )
        button_next.bind(on_release=self.go_next)
        self.add_widget(button_next)

    def go_back(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.third_window, direction="right")

    def go_next(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.fifth_window, direction="left")


class FifthWindow(Screen):
    """Pantalla 5: Solo BACK"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainPanel())

        button_back = Button(
            text="BACK",
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={"x": 0, "y": 0},
            background_color=(1, 0.5, 0.2, 1),
        )
        button_back.bind(on_release=self.go_back)
        self.add_widget(button_back)

    def go_back(self, w):
        app = App.get_running_app()
        self.manager.switch_to(app.fourth_window, direction="right")
