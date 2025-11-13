"""
Pantallas simplificadas usando MainPanel y Step2Panel.
Cada Screen simplemente agrega el Panel correspondiente + botones de navegación.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from .panels import MainPanel
from .panel_2 import Step2Panel


class BaseScreen(Screen):
    """Clase base para todas las pantallas."""
    
    title = "Paso"
    show_back = False
    show_next = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Panel principal
        self.panel = MainPanel()
        layout.add_widget(self.panel)
        
        # Botones de navegación
        button_layout = BoxLayout(size_hint_y=0.15, spacing=10, padding=5)
        
        if self.show_back:
            back_btn = Button(text="◄ BACK", background_color=(1, 0.5, 0.2, 1))
            back_btn.bind(on_press=self._go_back)
            button_layout.add_widget(back_btn)
        
        if self.show_next:
            next_btn = Button(text="NEXT ►", background_color=(0.2, 0.6, 1, 1))
            next_btn.bind(on_press=self._go_next)
            button_layout.add_widget(next_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def on_enter(self):
        """Actualiza la barra de estado al entrar en la pantalla."""
        if hasattr(self.panel, 'ids') and 'status_bar' in self.panel.ids:
            self.panel.ids.status_bar.text = f"[b]{self.title}[/b]"
    
    def _go_back(self, *args):
        app = App.get_running_app()
        screens = [app.main_window, app.second_window, app.third_window, app.fourth_window, app.fifth_window]
        current_idx = screens.index(self)
        if current_idx > 0:
            self.manager.switch_to(screens[current_idx - 1], direction="right")
    
    def _go_next(self, *args):
        app = App.get_running_app()
        screens = [app.main_window, app.second_window, app.third_window, app.fourth_window, app.fifth_window]
        current_idx = screens.index(self)
        if current_idx < len(screens) - 1:
            self.manager.switch_to(screens[current_idx + 1], direction="left")


class MainWindow(BaseScreen):
    """Pantalla 1: Configuración Inicial"""
    title = "Paso 1: Configuración Inicial"
    show_back = False
    show_next = True


class SecondWindow(Screen):
    """Pantalla 2: ERLANG + Parámetros Globales"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Panel específico para Paso 2
        self.panel = Step2Panel()
        layout.add_widget(self.panel)
        
        # Botones de navegación
        button_layout = BoxLayout(size_hint_y=0.15, spacing=10, padding=5)
        
        back_btn = Button(text="◄ BACK", background_color=(1, 0.5, 0.2, 1))
        back_btn.bind(on_press=self._go_back)
        button_layout.add_widget(back_btn)
        
        next_btn = Button(text="NEXT ►", background_color=(0.2, 0.6, 1, 1))
        next_btn.bind(on_press=self._go_next)
        button_layout.add_widget(next_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def on_enter(self):
        """Actualiza la barra de estado al entrar en la pantalla."""
        if hasattr(self.panel, 'ids') and 'status_bar' in self.panel.ids:
            self.panel.ids.status_bar.text = "[b]Paso 2: ERLANG + Parámetros Globales[/b]"
    
    def _go_back(self, *args):
        app = App.get_running_app()
        screens = [app.main_window, app.second_window, app.third_window, app.fourth_window, app.fifth_window]
        current_idx = screens.index(self)
        if current_idx > 0:
            self.manager.switch_to(screens[current_idx - 1], direction="right")
    
    def _go_next(self, *args):
        app = App.get_running_app()
        screens = [app.main_window, app.second_window, app.third_window, app.fourth_window, app.fifth_window]
        current_idx = screens.index(self)
        if current_idx < len(screens) - 1:
            self.manager.switch_to(screens[current_idx + 1], direction="left")


class ThirdWindow(BaseScreen):
    """Pantalla 3: Parámetros de Tráfico"""
    title = "Paso 3: Parámetros de Tráfico"
    show_back = True
    show_next = True


class FourthWindow(BaseScreen):
    """Pantalla 4: Simulación"""
    title = "Paso 4: Simulación"
    show_back = True
    show_next = True


class FifthWindow(BaseScreen):
    """Pantalla 5: Resultados Finales"""
    title = "Paso 5: Resultados Finales"
    show_back = True
    show_next = False
