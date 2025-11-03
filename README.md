# Modificación del repositorio

## 1. **Crear una rama de trabajo** 
    Nunca trabajes directamente sobre main (hará que todo sea mucho más caótico)
    Crea una rama nueva para cada módulo o tarea:

    ```bash
    git checkout -b nombre-de-tu-rama
    ```
    Usa nombres cortos y descriptivos sin espacios

## 2. **Hacer cambios y confirmarlos**        

    ```bash
    git add .
    git commit -m "Descripción corta y clara del cambio realizado"
    ```

## 3. **Subir tu rama al repositorio remoto**

    ```bash
    git push origin nombre-de-tu-rama
    ```

## 4. **Crear un Pull Request (PR)**

En GitHub, os vais ahora a https://github.com/jomafer97/practica2_LT, y os saldrá la opción de hacer un Pull Request (PR)

#### 1. **Selecciona tu rama como source (origen).**

#### 2. **Selecciona main como target (destino).**

#### 3. **Añade un título y una descripción de lo que hiciste.**

#### 4. **Envía el Pull Request.**

💬 Otros miembros pueden revisar tu código, hacer comentarios o aprobar el merge.

## 5. **Mantener tu rama actualizada con main**
Antes de seguir trabajando, sincroniza tu rama para evitar conflictos futuros:

    ```bash
    git checkout main
    git pull origin main
    git checkout nombre-de-tu-rama
    git merge main
    ```

## 6. **Opcional. Borrar ramas viejas**
    Después de que tu PR haya sido fusionado:

    ```bash
    git branch -d nombre-de-tu-rama            # Borra rama local
    git push origin --delete nombre-de-tu-rama # Borra rama remota
    ```

## Resumen rápido de comandos

| 🧭 Acción | 💻 Comando |
|-----------|------------|
| Crear una nueva rama | `git checkout -b mi-rama` |
| Ver ramas locales | `git branch` |
| Cambiar de rama | `git checkout otra-rama` |
| Subir tu rama al remoto | `git push origin mi-rama` |
| Actualizar tu copia local con `main` | `git pull origin main` |
| Fusionar los cambios de `main` en tu rama | `git merge main` |
| Subir después de resolver conflictos | `git add . && git commit && git push` |


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
    Navega a la carpeta `Client/`, **activa el entorno virtual** y ejecuta la aplicación Kivy.
    ```bash
    cd Client
    source .venv/bin/activate  # ¡Actívalo siempre!
    python3 main.py
    ```
    *Se abrirá la ventana de la aplicación.*

