# OMDownloader - Componente de Lista Virtualizada de Alto Rendimiento
import customtkinter as ctk

class CTKVirtualScroll(ctk.CTkScrollableFrame):
    """Contenedor que optimiza el renderizado mostrando solo los elementos visibles.
    Ideal para historiales largos o colas masivas sin sacrificar fluidez."""
    
    def __init__(self, master, row_height=80, buffer_rows=2, **kwargs):
        super().__init__(master, **kwargs)
        self.row_height = row_height
        self.buffer_rows = buffer_rows
        self.items = []
        self.visible_widgets = {} # {item_id: widget}
        self.render_callback = None
        
        # Enlazar evento de scroll para recalcular visibilidad
        self._parent_canvas.bind("<Configure>", self._on_scroll_update)
        self._parent_canvas.bind("<MouseWheel>", self._on_scroll_update, add="+")
        self.bind("<Configure>", self._on_scroll_update)

    def set_items(self, items, render_callback):
        """Asigna los datos y la función de renderizado."""
        self.items = items
        self.render_callback = render_callback
        self._update_list()

    def _on_scroll_update(self, event=None):
        """Calcula qué elementos deben estar visibles según la posición del scroll."""
        # Pequeño delay para no saturar si el scroll es muy rápido
        self.after(5, self._update_list)

    def _update_list(self):
        if not self.items or not self.render_callback:
            return

        # 1. Calcular rango visible
        canvas = self._parent_canvas
        scroll_pos = canvas.yview()[0] # 0.0 a 1.0
        total_height = len(self.items) * self.row_height
        view_height = canvas.winfo_height()
        
        start_y = scroll_pos * total_height
        end_y = start_y + view_height
        
        start_idx = max(0, int(start_y // self.row_height) - self.buffer_rows)
        end_idx = min(len(self.items), int(end_y // self.row_height) + self.buffer_rows)
        
        visible_ids = set()
        
        # 2. Renderizar rango visible
        for i in range(start_idx, end_idx):
            item = self.items[i]
            item_id = item.get('id') if isinstance(item, dict) else str(i)
            visible_ids.add(item_id)
            
            if item_id not in self.visible_widgets:
                # Crear widget si no existe
                widget = self.render_callback(self, item)
                widget.pack(fill="x", padx=10, pady=2)
                self.visible_widgets[item_id] = widget
            else:
                # Ya existe, asegurar que está visible (pack_forget pudo haberlo ocultado)
                self.visible_widgets[item_id].pack(fill="x", padx=10, pady=2)

        # 3. Virtualización: Ocultar o destruir widgets fuera de rango
        for item_id in list(self.visible_widgets.keys()):
            if item_id not in visible_ids:
                # Podríamos ocultarlos con pack_forget para reutilizarlos, 
                # o destruirlos para liberar memoria. Destruir es más sencillo para empezar.
                self.visible_widgets[item_id].destroy()
                del self.visible_widgets[item_id]
