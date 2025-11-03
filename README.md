# Frontend

## 1. Requisitos Previos

1.  **Clona** el repositorio (si es la primera vez).
2.  **Configura el Entorno Virtual** para el frontend. Es una "caja" aislada para instalar las librerías de Python y no ensuciar tu sistema.

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
    Navega a la carpeta `frontend/`, **activa el entorno virtual** y ejecuta la aplicación Kivy.
    ```bash
    cd Client
    source .venv/bin/activate  # ¡Actívalo siempre!
    python3 main.py
    ```
    *Se abrirá la ventana de la aplicación.*

