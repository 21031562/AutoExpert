import tkinter as tk
from tkinter import messagebox, ttk

from catalogo import CATEGORIAS_BASE, obtener_catalogo_sintomas
from diagnostico import (
    PROBABLE_THRESHOLD_DEFAULT,
    POSSIBLE_THRESHOLD_DEFAULT,
    diagnosticar_probables_posibles,
)


class AutoExpertDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoExpert IA - Diagnostico Desktop")
        self.geometry("1100x700")

        self.catalogo = obtener_catalogo_sintomas()
        self.sintomas_seleccionados = set()
        self.variables_categoria = {}

        self.categorias = list(CATEGORIAS_BASE)
        categorias_extra = sorted(
            categoria
            for categoria in self.catalogo
            if categoria not in self.categorias and self.catalogo[categoria]
        )
        self.categorias.extend(categorias_extra)
        if self.catalogo.get("otros"):
            self.categorias.append("otros")

        self.categoria_actual = tk.StringVar(
            value=self.categorias[0] if self.categorias else "otros"
        )

        self.top_n = tk.IntVar(value=5)

        # Este umbral ahora representa el mínimo para "posibles"
        self.umbral_posible = tk.DoubleVar(value=POSSIBLE_THRESHOLD_DEFAULT)

        self.umbral_probable = tk.DoubleVar(value=PROBABLE_THRESHOLD_DEFAULT)

        self.total_seleccionados = tk.StringVar(value="Seleccionados: 0")

        self._crear_interfaz()
        self._renderizar_sintomas()

    def _crear_interfaz(self):
        frame_superior = ttk.Frame(self, padding=10)
        frame_superior.pack(fill="x")

        ttk.Label(frame_superior, text="Categoria:").pack(side="left")
        selector_categoria = ttk.Combobox(
            frame_superior,
            values=self.categorias,
            state="readonly",
            textvariable=self.categoria_actual,
            width=18,
        )
        selector_categoria.pack(side="left", padx=(6, 16))
        selector_categoria.bind("<<ComboboxSelected>>", self._cambiar_categoria)

        ttk.Label(frame_superior, text="Top N (5-10):").pack(side="left")
        ttk.Spinbox(
            frame_superior,
            from_=5,
            to=10,
            width=5,
            textvariable=self.top_n,
        ).pack(side="left", padx=(6, 16))

        ttk.Label(frame_superior, text="Umbral probable (0-1):").pack(side="left")
        ttk.Spinbox(
            frame_superior,
            from_=0.1,
            to=1.0,
            increment=0.05,
            width=6,
            textvariable=self.umbral_probable,
        ).pack(side="left", padx=(6, 16))

        ttk.Label(frame_superior, text="Umbral posible (0-1):").pack(side="left")
        ttk.Spinbox(
            frame_superior,
            from_=0.1,
            to=1.0,
            increment=0.05,
            width=6,
            textvariable=self.umbral_posible,
        ).pack(side="left", padx=(6, 16))

        ttk.Label(frame_superior, textvariable=self.total_seleccionados).pack(
            side="left", padx=(16, 0)
        )

        frame_central = ttk.Frame(self, padding=(10, 0, 10, 10))
        frame_central.pack(fill="both", expand=True)
        frame_central.columnconfigure(0, weight=1)
        frame_central.columnconfigure(1, weight=2)
        frame_central.rowconfigure(0, weight=1)  # contenido principal
        frame_central.rowconfigure(1, weight=0)  # botones

        sintomas_labelframe = ttk.LabelFrame(frame_central, text="Sintomas", padding=8)
        sintomas_labelframe.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sintomas_labelframe.rowconfigure(0, weight=1)
        sintomas_labelframe.columnconfigure(0, weight=1)

        self.canvas_sintomas = tk.Canvas(sintomas_labelframe, highlightthickness=0)
        self.scrollbar_sintomas = ttk.Scrollbar(
            sintomas_labelframe,
            orient="vertical",
            command=self.canvas_sintomas.yview,
        )
        self.frame_checkboxes = ttk.Frame(self.canvas_sintomas)

        self.frame_checkboxes.bind(
            "<Configure>",
            lambda _event: self.canvas_sintomas.configure(
                scrollregion=self.canvas_sintomas.bbox("all")
            ),
        )

        self.canvas_sintomas.create_window((0, 0), window=self.frame_checkboxes, anchor="nw")
        self.canvas_sintomas.configure(yscrollcommand=self.scrollbar_sintomas.set)

        self.canvas_sintomas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_sintomas.grid(row=0, column=1, sticky="ns")

        resultados_labelframe = ttk.LabelFrame(frame_central, text="Resultados", padding=8)
        resultados_labelframe.grid(row=0, column=1, sticky="nsew")
        resultados_labelframe.rowconfigure(0, weight=1)
        resultados_labelframe.columnconfigure(0, weight=1)

        # Dividir resultados en Probables / Posibles
        paned = ttk.PanedWindow(resultados_labelframe, orient="vertical")
        paned.grid(row=0, column=0, sticky="nsew")
        resultados_labelframe.rowconfigure(0, weight=1)

        frame_probables = ttk.LabelFrame(paned, text="Diagnosticos probables", padding=6)
        frame_posibles = ttk.LabelFrame(paned, text="Diagnosticos posibles", padding=6)

        paned.add(frame_probables, weight=1)
        paned.add(frame_posibles, weight=1)

        frame_probables.rowconfigure(0, weight=1)
        frame_probables.columnconfigure(0, weight=1)
        frame_posibles.rowconfigure(0, weight=1)
        frame_posibles.columnconfigure(0, weight=1)

        self.texto_probables = tk.Text(frame_probables, wrap="word", state="disabled")
        sb_prob = ttk.Scrollbar(frame_probables, orient="vertical", command=self.texto_probables.yview)
        self.texto_probables.configure(yscrollcommand=sb_prob.set)
        self.texto_probables.grid(row=0, column=0, sticky="nsew")
        sb_prob.grid(row=0, column=1, sticky="ns")

        self.texto_posibles = tk.Text(frame_posibles, wrap="word", state="disabled")
        sb_pos = ttk.Scrollbar(frame_posibles, orient="vertical", command=self.texto_posibles.yview)
        self.texto_posibles.configure(yscrollcommand=sb_pos.set)
        self.texto_posibles.grid(row=0, column=0, sticky="nsew")
        sb_pos.grid(row=0, column=1, sticky="ns")

        frame_inferior = ttk.Frame(frame_central, padding=(0, 8, 0, 0))
        frame_inferior.grid(row=1, column=0, columnspan=2, sticky="ew")
        frame_inferior.columnconfigure(0, weight=1)
        frame_inferior.columnconfigure(1, weight=1)

        ttk.Button(frame_inferior, text="Limpiar", command=self._limpiar).grid(row=0, column=0, sticky="w")
        ttk.Button(frame_inferior, text="Diagnosticar", command=self._diagnosticar).grid(row=0, column=1, sticky="e")

    def _cambiar_categoria(self, _event=None):
        self._renderizar_sintomas()

    def _alternar_sintoma(self, sintoma, variable):
        if variable.get():
            self.sintomas_seleccionados.add(sintoma)
        else:
            self.sintomas_seleccionados.discard(sintoma)

        self.total_seleccionados.set(f"Seleccionados: {len(self.sintomas_seleccionados)}")

    def _renderizar_sintomas(self):
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()

        categoria = self.categoria_actual.get()
        sintomas_categoria = self.catalogo.get(categoria, [])
        self.variables_categoria = {}

        if not sintomas_categoria:
            ttk.Label(self.frame_checkboxes, text="No hay sintomas para esta categoria.").pack(anchor="w")
            return

        for sintoma in sintomas_categoria:
            variable = tk.BooleanVar(value=sintoma in self.sintomas_seleccionados)
            self.variables_categoria[sintoma] = variable
            ttk.Checkbutton(
                self.frame_checkboxes,
                text=sintoma,
                variable=variable,
                command=lambda s=sintoma, v=variable: self._alternar_sintoma(s, v),
            ).pack(anchor="w", pady=1)

    def _limpiar_resultados(self):
        for widget in (self.texto_probables, self.texto_posibles):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.configure(state="disabled")

    def _limpiar(self):
        # 1) limpiar selección lógica (esto borra TODO, incluso de otras categorías)
        self.sintomas_seleccionados.clear()
        self.total_seleccionados.set("Seleccionados: 0")

        # 2) re-renderiza checkboxes para que se desmarquen en la categoría visible
        self._renderizar_sintomas()

        # 3) limpiar resultados
        self._limpiar_resultados()

    def _diagnosticar(self):
        try:
            probable = float(self.umbral_probable.get())
            posible = float(self.umbral_posible.get())
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Los umbrales deben ser numericos.")
            return

        probable = max(0.0, min(1.0, probable))
        posible = max(0.0, min(1.0, posible))

        try:
            top_n = int(self.top_n.get())
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Top N debe ser un numero entero.")
            return

        top_n = max(5, min(10, top_n))

        try:
            probables, posibles = diagnosticar_probables_posibles(
                sintomas_usuario=sorted(self.sintomas_seleccionados),
                probable_threshold=probable,
                possible_threshold=posible,
                top_n=top_n,
            )
        except (FileNotFoundError, ValueError) as error:
            messagebox.showerror("Error de diagnostico", str(error))
            return

        self._mostrar_resultados(probables, posibles, probable_threshold=probable, possible_threshold=posible)

    def _mostrar_en_texto(self, widget, resultados, titulo_vacio):
        widget.configure(state="normal")
        widget.delete("1.0", "end")

        if not resultados:
            widget.insert("end", titulo_vacio + "\n")
            widget.configure(state="disabled")
            return

        for posicion, resultado in enumerate(resultados, start=1):
            ratio_display = resultado.get("match_ratio_display", round(resultado["match_ratio"], 4))
            widget.insert("end", f"{posicion}. {resultado['diagnostico']}\n")
            widget.insert(
                "end",
                (
                    f"   modulo: {resultado['modulo']}\n"
                    f"   match: {resultado['match']} ({ratio_display * 100:.1f}%)\n"
                    f"   score: {resultado['score']} | prioridad: {resultado['prioridad']}\n"
                    f"   prueba: {resultado['prueba']}\n"
                    f"   solucion: {resultado['solucion']}\n"
                ),
            )

            matched = ", ".join(resultado["condiciones_matched"]) or "-"
            missing = ", ".join(resultado["condiciones_missing"]) or "-"

            widget.insert("end", f"   condiciones_matched: {matched}\n")
            widget.insert("end", f"   condiciones_missing: {missing}\n\n")

        widget.configure(state="disabled")

    def _mostrar_resultados(self, probables, posibles, probable_threshold, possible_threshold):
        self._mostrar_en_texto(
            self.texto_probables,
            probables,
            f"No hay diagnosticos probables (>= {probable_threshold:.2f}).",
        )
        self._mostrar_en_texto(
            self.texto_posibles,
            posibles,
            f"No hay diagnosticos posibles (>= {possible_threshold:.2f} y < {probable_threshold:.2f}).",
        )


if __name__ == "__main__":
    app = AutoExpertDesktopApp()
    app.mainloop()