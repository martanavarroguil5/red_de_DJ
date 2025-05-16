import socket
import tkinter as tk
from tkinter import messagebox
import webbrowser
import tkinter.simpledialog

class SongDisplay(tk.Tk):
    def __init__(self, song_info, sock, genero_favorito=None):
        super().__init__()
        self.title("Reproductor de Canciones")  # Título de la ventana
        self.geometry("400x300")  # Dimensiones de la ventana
        self.song_info = song_info  # Información de la canción
        self.song_label = None
        self.link_label = None
        self.link_url = None
        self.sock = sock  # Socket para la comunicación con el servidor
        self.genero_favorito = genero_favorito  # Nuevo: género favorito del usuario
        self.me_gusta_label = None  # Nuevo: etiqueta para mostrar "Me gusta"
        self.genero_label = None  # Nuevo: etiqueta para mostrar el género favorito
        self.create_widgets()  # Crear los widgets de la UI
        self.check_for_song()  # Inicia el polling para actualizar la canción

    def create_widgets(self):
        label = tk.Label(self, text="Canción Actual", font=("Arial", 14))  # Etiqueta para la canción actual
        label.pack(pady=10)
        # Mostrar el género favorito
        self.genero_label = tk.Label(self, text=f"Género favorito: {self.genero_favorito if self.genero_favorito else 'Ninguno'}", font=("Arial", 11), fg="purple")
        self.genero_label.pack(pady=5)
        self.song_label = tk.Label(self, text=self.song_info, font=("Arial", 12))  # Etiqueta que muestra la canción
        self.song_label.pack(pady=20)
        # Etiqueta de enlace (vacía inicialmente)
        self.link_label = tk.Label(self, text="", font=("Arial", 11, "underline"), fg="blue", cursor="hand2")
        self.link_label.pack(pady=5)
        self.link_label.bind("<Button-1>", self.open_link)  # Abre el enlace al hacer clic
        self.me_gusta_label = tk.Label(self, text="", font=("Arial", 12), fg="green")  # Nuevo
        self.me_gusta_label.pack(pady=5)
        skip_button = tk.Button(self, text="Salir", command=self.skip_song)  # Botón para saltar la canción
        skip_button.pack(pady=10)

    def skip_song(self):
        messagebox.showinfo("Acción", "Salir.")  # Muestra un mensaje al saltar la canción
        print("Canción saltada.")
        self.quit()

    def update_song(self, new_song_info):
        print(f"Recibiendo nueva canción: {new_song_info}")
        # Espera formato: Título – Artista\nGénero\nlink
        partes = new_song_info.split('\n')
        if len(partes) >= 3:
            info = partes[0]
            genero = partes[1].strip().lower()
            link = partes[2].strip()
        elif len(partes) == 2:
            info = partes[0]
            genero = ''
            link = partes[1].strip()
        else:
            info = new_song_info
            genero = ''
            link = None
        self.song_info = info
        self.link_url = link
        if self.song_label:
            self.song_label.config(text=self.song_info)  # Actualiza la etiqueta de la canción
        if self.link_label:
            if self.link_url and self.link_url.startswith('http'):
                self.link_label.config(text=self.link_url)
            else:
                self.link_label.config(text="")
        # Mostrar "Me gusta" si coincide el género favorito
        if self.me_gusta_label:
            if self.genero_favorito and genero == self.genero_favorito.lower():
                self.me_gusta_label.config(text="¡Me gusta!")
            else:
                self.me_gusta_label.config(text="")

    def open_link(self, event):
        if self.link_url and self.link_url.startswith('http'):
            webbrowser.open(self.link_url)  # Abre el enlace en el navegador

    def check_for_song(self):
        try:
            data = self.sock.recv(1024)  # Recibe datos del servidor
            if data:
                song_info = data.decode()  # Decodifica la canción
                print(f"Recibido mensaje: {song_info}")
                self.update_song(song_info)  # Actualiza la canción mostrada
        except BlockingIOError:
            pass  # No hay datos nuevos
        except Exception as e:
            print(f"Error al recibir mensaje: {e}")
        self.after(500, self.check_for_song)  # Vuelve a comprobar en 0.5s

    def pedir_cancion_genero(self, genero):
        """Solicita al servidor una canción de un género específico (simulado)."""
        # En este protocolo, el cliente no puede pedir géneros al servidor,
        # pero podemos filtrar localmente la primera canción recibida del género deseado.
        print(f"Buscando canción del género: {genero}")
        while True:
            try:
                data = self.sock.recv(1024)
                if data:
                    song_info = data.decode()
                    partes = song_info.split('\n')
                    if len(partes) >= 3:
                        cancion_genero = partes[1].strip().lower()
                        if cancion_genero == genero.lower():
                            print(f"Encontrada canción del género {genero}: {partes[0]}")
                            self.update_song(song_info)
                            break
            except BlockingIOError:
                self.after(500, lambda: self.pedir_cancion_genero(genero))
                break
            except Exception as e:
                print(f"Error al recibir mensaje: {e}")
                break

def conectar():
    host = '127.0.0.1'  # IP del servidor
    port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))  # Conecta al servidor
    sock.setblocking(False)  # No bloqueante
    print("Conectado al servidor.")
    return sock

def main():
    sock = conectar()  # Conecta al servidor
    # Ventana para elegir género favorito
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal temporalmente
    generos = [
        "rock", "pop", "classical", "latin", "jazz", "blues", "reggaeton", "electronic",
        "hip hop", "indie", "metal", "country", "salsa", "trap"
    ]
    genero_favorito = tkinter.simpledialog.askstring(
        "Género favorito",
        f"Elige tu género favorito:\n{', '.join(generos)}",
        initialvalue="rock"
    )
    root.destroy()
    if not genero_favorito:
        print("No se eligió género favorito. Cerrando.")
        return
    gui = SongDisplay("Cargando canción...", sock, genero_favorito=genero_favorito)
    gui.mainloop()

if __name__ == "__main__":
    main()
