"""
Pantallas simplificadas usando MainPanel y Step2Panel.
Cada Screen simplemente agrega el Panel correspondiente + botones de navegación.

ACTUALIZADO: Importa y usa Step3Panel, Step4Panel y Step5Panel.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from .panels import MainPanel
from .panel_2 import Step2Panel
from .panel_3 import Step3Panel
from .panel_4 import Step4Panel
from .panel_5 import Step5Panel
from .panel_6 import Step6Panel

class BaseScreen(Screen):
    """Clase base para todas las pantallas."""

    title = "Paso"
    show_back = False
    show_next = True

    panel_class = MainPanel

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")

        self.panel = self.panel_class()
        layout.add_widget(self.panel)

        button_layout = BoxLayout(size_hint_y=0.15, spacing=10, padding=5)

        if self.show_back:
            back_btn = Button(text="ANTERIOR", background_color=(1, 0.5, 0.2, 1))
            back_btn.bind(on_press=self._go_back)
            button_layout.add_widget(back_btn)

        if self.show_next:
            next_btn = Button(text="SIGUIENTE", background_color=(0.2, 0.6, 1, 1))
            next_btn.bind(on_press=self._go_next)
            button_layout.add_widget(next_btn)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_enter(self):
        """Actualiza el título (si el panel tiene status_bar)."""

        if hasattr(self.panel, "ids") and "status_bar" in self.panel.ids:
            self.panel.ids.status_bar.text = f"[b]{self.title}[/b]"

    def _go_back(self, *args):
        app = App.get_running_app()
        screens = [
            app.main_window,
            app.second_window,
            app.third_window,
            app.fourth_window,
            app.fifth_window,
            app.sixth_window,
        ]
        current_idx = screens.index(self)
        if current_idx > 0:
            self.manager.switch_to(screens[current_idx - 1], direction="right")

    def _go_next(self, *args):
        app = App.get_running_app()
        screens = [
            app.main_window,
            app.second_window,
            app.third_window,
            app.fourth_window,
            app.fifth_window,
            app.sixth_window,
        ]
        current_idx = screens.index(self)
        if current_idx < len(screens) - 1:
            self.manager.switch_to(screens[current_idx + 1], direction="left")


class MainWindow(BaseScreen):
    """Pantalla 1: Configuración Inicial"""

    title = "Paso 1: Configuración Inicial"
    panel_class = MainPanel  # Usa el Panel 1
    show_back = False
    show_next = True


class SecondWindow(BaseScreen):  # Modificado para usar BaseScreen
    """Pantalla 2: ERLANG + Parámetros Globales"""

    title = "Paso 2: ERLANG + Parámetros Globales"
    panel_class = Step2Panel  # Usa el Panel 2
    show_back = True
    show_next = True

    def on_enter(self):
        """Actualiza el título."""
        super().on_enter()
        # Lógica específica de panel_2 (si es necesaria)
        self.panel._update_summary_display()


class ThirdWindow(BaseScreen):
    """Pantalla 3: Parámetros de Tráfico"""

    title = "Paso 3: Parámetros de Tráfico (BW)"
    panel_class = Step3Panel  # Usa el Panel 3
    show_back = True
    show_next = True

    def on_enter(self):
        """Actualiza el título."""
        super().on_enter()
        self.panel._update_summary_display()


class FourthWindow(BaseScreen):
    """Pantalla 4: Simulación de Costes"""

    title = "Paso 4: Simulación de Costes"
    panel_class = Step4Panel  # Usa el Panel 4
    show_back = True
    show_next = True

    def on_enter(self):
        """Actualiza el título."""
        super().on_enter()
        self.panel._update_summary_display()


class FifthWindow(BaseScreen):
    """Pantalla 5: Simulación PLR"""

    title = "Paso 5: Simulación PLR"
    panel_class = Step5Panel  # Usa el Panel 5
    show_back = True
    show_next = True

    def on_enter(self):
        """Actualiza el título."""
        super().on_enter()
        self.panel._update_summary_display()

class SixthWindow(BaseScreen):
    """Pantalla 6: Simulación REPORT"""

    title = "Paso 6: Simulación REPORT"
    panel_class = Step6Panel 
    show_back = True
    show_next = False

    def on_enter(self):
        """Actualiza el título."""
        super().on_enter()
        self.panel._update_summary_display()

