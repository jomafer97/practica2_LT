# Modificación del repositorio

1.  **Clona el repositorio (si es la primera vez)**

    ⚠️ Si ya has clonado el repositorio antes, simplemente actualízalo ([+info](#mantener-tu-rama-actualizada-con-main))

    ```bash
    git clone git@github.com:jomafer97/practica2_LT.git
    cd practica2_LT
    ```
    Si os da fallo, es porque tendréis que configurar SSH con github pero no tiene mucha historia, chatgpt os lo explicará perfecto
2. **Crear una rama de trabajo**

    Nunca trabajes directamente sobre main (hará que todo sea mucho más caótico)
    Crea una rama nueva para cada módulo o tarea:

    ```bash
    git checkout -b nombre-de-tu-rama
    ```
    Usa nombres cortos y descriptivos sin espacios

    **Ya puedes modificar lo que necesites!**
3. **Una vez hechos los cambios:**

    ```bash
    git add .
    git commit -m "Descripción corta y clara del cambio realizado"
    ```

4. **Subir tu rama al repositorio remoto**

    ```bash
    git push origin nombre-de-tu-rama
    ```

5. **Crear un Pull Request (PR)**

En GitHub, os vais ahora a https://github.com/jomafer97/practica2_LT, y os saldrá la opción de hacer un Pull Request (PR)

1. **Selecciona tu rama como source (origen).**

2. **Selecciona main como target (destino).**

3. **Añade un título y una descripción de lo que hiciste.**

4. **Envía el Pull Request.**

💬 Otros miembros pueden revisar tu código, hacer comentarios o aprobar el merge.

### **Mantener tu rama actualizada con main**

- Antes de seguir trabajando, sincroniza tu rama para evitar conflictos futuros:

    ```bash
    git checkout main
    git pull origin main
    git checkout nombre-de-tu-rama
    git merge main
    ```

### **Opcional. Borrar ramas viejas**
- Después de que tu PR haya sido fusionado:

    ```bash
    git branch -d nombre-de-tu-rama            # Borra rama local
    git push origin --delete nombre-de-tu-rama # Borra rama remota
    ```

# Frontend

## 1. Requisitos Previos

1.  **Configura el Entorno Virtual** para el frontend. Es una "caja" aislada para instalar las librerías de Python y no ensuciar tu sistema.

    ```bash
    # Navega a la carpeta del frontend
    cd Client

    # 1. Crea el entorno virtual (llámalo ".venv")
    python3 -m venv .venv

    # 2. Actívalo (verás (.venv) al inicio de tu línea de comandos)
    source .venv/bin/activate

    # 3. Instala las dependencias (Kivy) dentro del entorno
    pip install -r ../requirements.txt
    ```
    *Nota: Solo necesitas crear el entorno (`-m venv`) la primera vez. Las siguientes veces, solo necesitas activarlo (`source .venv/bin/activate`).*

## 2. Ejecución

1.  **Frontend:**
    Navega a la carpeta `Client/`, **activa el entorno virtual** y ejecuta la aplicación Kivy.
    ```bash
    cd Client
    source .venv/bin/activate  # ¡Actívalo siempre!
    python3 main.py
    ```
    *Se abrirá la ventana de la aplicación.*

# CREACIÓN NUEVA PESTAÑA PARA EL FRONT

1. **Modificación Kivy:**

    1. En *layout.kv* copiar y pegar a partir de **# --- PANEL --- #** hasta encontrar el siguiente **# --- PANEL --- #**(El PANEL 6 es el que menos cosas tiene y es el más sencillo)* Modificar <StepXPanel> por el nuemero siguiente *7* 

    2. Modificar etiqueta Label dentro del primer BoxLayout para que se actualice la etiqueta de arriba en la que se indica el paso en el que estamos
    ```
            Label:
            text: "<cambiar al texto que querais>"
            font_size: '16sp'
            color: (0.9, 0.9, 0.9, 1)
            text_size: self.width, None
    ```
    3. En el segundo BoxLayout modificar el **on_press** donde se le pasa la acción.

    ```
        BoxLayout:
        orientation: 'horizontal'
        spacing: 10
        size_hint_y: 0.35

        ImageButton:
            source: 'assets/email.png'
            on_press: root.handle_button_press('<descripcion_corta_de_la funcion>')
    ```

    4. En el último Button, modificar el **on_press** para llamar a la función del frontend
    
    ```
        Button:
        text: 'Enviar Email (Paso 6)'
        size_hint_y: 0.15
        font_size: '16sp'
        background_color: (0.2, 0.8, 0.2, 1)
        on_press: root.nombre_de_la_funcion()
    ``` 
2. **Creación nuevo panel_.py**
    1. Copiar uno de los panel.py que haya *(el panel_6.py es quizás el que menos cosas tenga)*

    2. Moficiar parámetros globales, que serán los argumentos del popup que se creará los argumentos en este caso son la etiqueta con la que lo mostraremos en el formulario, el tipo de dato, el valor por defecto y el nombre para almacenar el dato. 

    ``` 
    EMAIL_PARAMS_FIELDS = [
    ("Introduzca su email", "str", "correo de ejemplo", "email"),]
    ``` 

    3. Modificar el nombre de la clase al <StepXPanel> que hayais puesto antes.

    4. Modificar el **def handle_button_press(self, button_name)** para pasarle la descripción corta de la función que hemos indicado en el *layout.kv*, si no coincide el botón no funcionará.

    ```
    def handle_button_press(self, button_name): 
        if button_name == "<descripcion_corta_de_la_funcion>":
            self.open_config_popup()
    ```

    5. Modificar la función **def open_config_popup(self)** con el nombre que se le haya puesto a los parámetros globales. Esta función lo que hace es configurar el mensaje **REQUEST** para luego enviarlo.
    
    ```
    def open_config_popup(self):
        """Abre popup para configurar Parámetros de REPORT."""
        form = GridForm()

        for label_text, input_type, default, field_name in <NOMBRE_PARAMETROS_GLOBALES>:
            widget = self._create_input_field(form, label_text, default, input_type)
            widget.bind(
                text=lambda i, v, lt=label_text: self._on_field_change(i, v, lt)
            )
            # Inicializar valor por defecto
            self._on_field_change(widget, default, label_text)

        popup = ConfigPopup(
            title_text=field_name, content_widget=form
        )
        popup.open()
    ```

    6. Modificar la función **def send_email_data(self)** para enviar el REQUEST con el payload. 

    ```
    def send_<cambiar_por_el_que_querais>_data(self):
        """Envía REQUEST al servidor."""
        app = App.get_running_app()
        email_data = getattr(app, "summary_data", {}).get(self.section, {})


        try:
            <nombre_variable>_<tipo_variable> = <nombre_variable>_data.get("<variable>", "")
            if not <nombre_variable>_<tipo_variable>r:
                self._show_error_popup("<mensaje de error que querais>")
                return

            payload = {"<variable_del_request>": <nombre_variable>_<tipo_variable>}

            MessageSender.send("<NOMBRE_REQUEST>", payload, callback=self._on_<nombre_que_querais>_response)
        except (ValueError, KeyError) as e:
            self._show_error_popup(f"Valores inválidos: {str(e)}")
    ```

    7. Modificar la función **def _on_email_response()**. Con esta función hacemos el callback para procesar la respuesta, es importante cambiar el nombre de las variables para que correspondan con las definidas antes.

    ```
    def _on_<nombre_que_querais>_response(self, response):
        """Callback para procesar la respuesta REQUEST_RESPONSE."""
        try:
            <nombre_variable>_data = response if isinstance(response, dict) else {}

            app = App.get_running_app()
            # Guardar la respuesta COMPLETA
            app.<nombre_variable>_results_data = <nombre_variable>_data

            self.show_<nombre_que_querais>_results()
        except Exception as e:
            self._show_error_popup(f"Error procesando respuesta REPORT: {str(e)}")

    ```

    8. Modificar la función **def show_email_results**. Esta función muestra las respuestas que se le haya mandado el servidor.

    ```
    def show_<nombre_que_querais>_results(self):
        """Muestra el texto plano"""
        app = App.get_running_app()
        form = GridForm(cols=2) <-- Con Cols modificamos el número de columnas, en caso de que sea solo una respuesta pues se borra y se deja ()

        results = getattr(
            app,
            <"nombre_de_la_respuesta">,
            {"<la_respuesta_en_sí>"},
        )

        for key, value in results.items():
            form.add_widget(Label(text=f"{key}:"))
            form.add_widget(Label(text=str(value), color=(1, 1, 1, 1), size_hint_x=1))

    ```

    9. Modificar la función **def _get_field_name()**. En este caso hay que modificar el nombre de los parámetros globales.

    ```
    def _get_field_name(self, label_text):
        for label, _, _, field_name in <NOMBRE_PARAMETROS_GLOBALES>:
            if label == label_text:
                return field_name
        return None
    ```


3. **Modificación screens.py**

    1. Importar el nuevo panel creado:

    ```
    from .<nombre_panel> import StepXPanel
    ```

    2. Modificar la función **def _go_back()**. Esta función define el funcionamiento del botón de atrás, que hace que retroceda.

    ```
    def _go_back(self, *args):
        app = App.get_running_app()
        screens = [
            app.main_window,
            app.second_window,
            app.third_window,
            app.fourth_window,
            app.fifth_window,
            app.sixth_window,
            app.seventh_window, <-- Esto luego se modificará en el main.py

        ]
        current_idx = screens.index(self)
        if current_idx > 0:
            self.manager.switch_to(screens[current_idx - 1], direction="right") <-- Si cambiais a "left" se cambia el efecto de movimiento
    ```

    3. Modificar la función **def _go_next** de igual forma.

    4. Añadir la clase, copiando y pegando la última y modificando los parámetros.

    ```
    class SeventhWindow(BaseScreen): <-- En este caso ya está modificada

    title = "<Titulo que querais>"
    panel_class = Step6Panel 
    show_back = True
    show_next = False

    def on_enter(self):
        """Actualiza el título."""
        super().on_enter()
        self.panel._update_summary_display()
    ```

    Importante, hay que cambiar en la clase anterior **show_next** a *True* para que aparezca el botón de SIGUIENTE.

4. **Modificación main.py**

    1. Importar la ventana creada.

    ```
    from gui.screens import (
    MainWindow,
    SecondWindow,
    ThirdWindow,
    FourthWindow,
    FifthWindow,
    SixthWindow,
    SeventhWindow, <-- Aquí ya está modificada
        )
    ```
    2. Modificar la clase **MainApp()**

    ```
     # Crear las 5 pantallas
        MainApp.main_window = MainWindow(name="main_window")
        MainApp.second_window = SecondWindow(name="second_window")
        MainApp.third_window = ThirdWindow(name="third_window")
        MainApp.fourth_window = FourthWindow(name="fourth_window")
        MainApp.fifth_window = FifthWindow(name="fifth_window")
        MainApp.sixth_window = SixthWindow(name="sixth_window")
        MainApp.seventh_window = SeventhWindow(name="seventh_window") <-- Aquí ya está modificada


        # Añadir al ScreenManager
        screen_manager.add_widget(MainApp.main_window)
        screen_manager.add_widget(MainApp.second_window)
        screen_manager.add_widget(MainApp.third_window)
        screen_manager.add_widget(MainApp.fourth_window)
        screen_manager.add_widget(MainApp.fifth_window)
        screen_manager.add_widget(MainApp.sixth_window)
        screen_manager.add_widget(MainApp.seventh_window) <-- Aquí ya está modificada
    ```






