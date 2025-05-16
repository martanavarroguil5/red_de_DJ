import socket
import threading
import time
import random
import asyncio
import aiohttp
from typing import List

# Lista de conexiones activas de clientes
conexiones: List[socket.socket] = []

# Palabras clave para la búsqueda aleatoria de canciones
KEYWORDS = [
    "rock", "pop", "classical", "latin", "jazz", "blues", "reggaeton", "electronic",
    "hip hop", "indie", "metal", "country", "salsa", "trap"
]

DEEZER_API = "https://api.deezer.com/search"

def fetch_random_song_sync() -> str | None:
    """Función no utilizada, mantiene compatibilidad para llamadas sin asyncio."""
    return None

async def fetch_random_song() -> str | None:
    """Obtiene una canción aleatoria usando la API de búsqueda de Deezer (asíncrona)."""
    term = random.choice(KEYWORDS)  # Selecciona una palabra clave aleatoria para buscar el género de la canción.
    
    try:
        # Crea una sesión asíncrona para realizar la solicitud HTTP a la API de Deezer.
        async with aiohttp.ClientSession() as session:
            # Hace la solicitud GET a la API de Deezer con la palabra clave seleccionada y el límite de 25 resultados.
            async with session.get(DEEZER_API, params={"q": term, "limit": 25}, timeout=5) as resp:
                resp.raise_for_status()  # Lanza una excepción si la respuesta HTTP no es exitosa (código de estado 4xx o 5xx).
                
                # Convierte la respuesta JSON a un diccionario.
                data = await resp.json()
                
                # Obtiene la lista de resultados (canciones) de la respuesta JSON.
                items = data.get("data", [])
                
                # Si no se encuentran canciones, la función retorna None.
                if not items:
                    return None
                
                # Si hay resultados, selecciona una canción aleatoria de la lista de resultados.
                track = random.choice(items)
                
                # Extrae los datos relevantes de la canción: título, artista y enlace.
                title = track.get("title", "Unknown")  # Si no se encuentra el título, usa "Unknown" como valor predeterminado.
                artist = track.get("artist", {}).get("name", "Unknown")  # Similarmente para el artista.
                link = track.get("link", "")  # Si no hay enlace, usa un string vacío.
                
                # Devuelve una cadena con el título, artista, género (palabra clave seleccionada) y el enlace.
                return f"{title} – {artist}\n{term}\n{link}"
    
    # Si ocurre un error durante la solicitud HTTP o procesamiento, se captura la excepción y se imprime un mensaje de error.
    except Exception as exc:
        print(f"[ERROR] Error en la búsqueda de Deezer: {exc}")
        return None  # Si ocurre un error, devuelve None.


def broadcast_songs(interval: int = 10) -> None:
    """Envía continuamente canciones a todas las conexiones activas."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        song = loop.run_until_complete(fetch_random_song())
        if song:
            for conn in conexiones[:]:
                try:
                    conn.sendall(song.encode())  # Envía la canción a todos los clientes
                    print(f"[SEND] → {conn.getpeername()}: {song}")
                except Exception as exc:
                    print(f"[WARN] {conn.getpeername()} desconectado: {exc}")
                    conexiones.remove(conn)
                    conn.close()
        time.sleep(interval)

def accept_connections(server_socket: socket.socket) -> None:
    """Acepta nuevas conexiones de clientes y almacena sus sockets."""
    while True:
        try:
            conn, addr = server_socket.accept()
            conexiones.append(conn)  # Agrega la conexión a la lista
            print(f"[INFO] Nuevo suscriptor {addr} (total={len(conexiones)})")
        except Exception as exc:
            print(f"[ERROR] accept_connections: {exc}")

def main(host: str = "0.0.0.0", port: int = 12345) -> None:
    """Inicializa el servidor de DJ y comienza a aceptar conexiones."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))  # Asocia el servidor con la dirección IP y puerto
    server_socket.listen()  # Escucha por conexiones entrantes
    print(f"[INFO] Servidor de DJ escuchando en {host}:{port}")

    threading.Thread(target=broadcast_songs, daemon=True).start()  # Hilo para enviar canciones

    try:
        accept_connections(server_socket)  # Acepta conexiones entrantes
    finally:
        print("[INFO] Apagando – cerrando las conexiones de cliente…")
        for conn in conexiones:
            conn.close()  # Cierra las conexiones
        server_socket.close()  # Cierra el socket del servidor

if __name__ == "__main__":
    try:
        main()  # Inicia el servidor
    except KeyboardInterrupt:
        print("\n[INFO] DJ detenido por el usuario.")
