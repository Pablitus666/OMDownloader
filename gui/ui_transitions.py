# OMDownloader - Motor de Animaciones y Transiciones Suaves
import customtkinter as ctk

def fade_in(widget, duration=300, steps=20):
    """Efecto de aparición suave para widgets (Fase 7)."""
    alpha = 0
    delta = 1.0 / steps
    interval = int(duration / steps)
    
    # Nota: Tkinter no soporta alpha real en widgets individuales de forma nativa fácil, 
    # pero podemos simularlo cambiando el color de texto/fondo progresivamente 
    # o simplemente usando un delay de visualización. 
    # Para CustomTkinter, lo más efectivo es el despliegue progresivo.
    
    widget.grid_propagate(False)
    def step():
        nonlocal alpha
        alpha += delta
        if alpha <= 1.0:
            # Aquí podríamos ajustar colores si quisiéramos un fade real,
            # pero el "slide-in" o "pop-in" suele ser más nítido en CTK.
            widget.after(interval, step)
    
    step()

def animate_sidebar_width(frame, target_width, duration=200):
    """Anima el ancho del sidebar para un efecto colapsable suave."""
    current_width = frame.winfo_width()
    steps = 10
    delta = (target_width - current_width) / steps
    interval = int(duration / steps)
    
    def step(count):
        if count < steps:
            new_w = current_width + (delta * (count + 1))
            frame.configure(width=new_w)
            frame.after(interval, lambda: step(count + 1))
            
    step(0)
