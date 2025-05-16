# red_de_DJ
# Mini DJ Streaming App

Pequeña demo cliente‑servidor en Python que reparte canciones aleatorias usando la API pública de Deezer.

## Archivos

- **ManagerDJ.py** – Servidor TCP que cada 10 s solicita un tema y lo difunde.
- **listener.py** – Cliente Tkinter que muestra la canción.

## Uso rápido

```bash
python3 ManagerDJ.py   # ejecuta UNA vez: levanta el servidor

python3 listener.py    # ejecuta TANTAS veces como clientes quieras
```

Requiere Python 3.10+, `aiohttp` y Tkinter. Licencia MIT.
