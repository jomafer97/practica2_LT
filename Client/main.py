from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from gui.screens import (
    MainWindow,
    SecondWindow,
    ThirdWindow,
    FourthWindow,
    FifthWindow,
)

# Cargar el archivo KV externo
Builder.load_file("kivy/layout.kv")


class MainApp(App):

    title = "Calculadora VoIP"

    def build(self):
        screen_manager = ScreenManager()

        # Crear las 5 pantallas
        MainApp.main_window = MainWindow(name="main_window")
        MainApp.second_window = SecondWindow(name="second_window")
        MainApp.third_window = ThirdWindow(name="third_window")
        MainApp.fourth_window = FourthWindow(name="fourth_window")
        MainApp.fifth_window = FifthWindow(name="fifth_window")

        # Añadir al ScreenManager
        screen_manager.add_widget(MainApp.main_window)
        screen_manager.add_widget(MainApp.second_window)
        screen_manager.add_widget(MainApp.third_window)
        screen_manager.add_widget(MainApp.fourth_window)
        screen_manager.add_widget(MainApp.fifth_window)

        return screen_manager


if __name__ == "__main__":
    MainApp().run()
