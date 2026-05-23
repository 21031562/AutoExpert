import tkinter as tk
from tkinter import messagebox, ttk

from catalogo import CATEGORIAS_BASE, obtener_catalogo_sintomas
from diagnostico import diagnosticar


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
        self.umbral_match = tk.DoubleVar(value=0.5)
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

        ttk.Label(frame_superior, text="Match minimo (0-1):").pack(side="left")
        ttk.Spinbox(
            frame_superior,
            from_=0.1,
            to=1.0,
            increment=0.1,
            width=5,
            textvariable=self.umbral_match,
        ).pack(side="left", padx=(6, 16))

        ttk.Label(
            frame_superior,
            textvariable=self.total_seleccionados,
        ).pack(side="left", padx=(16, 0))

        frame_central = ttk.Frame(self, padding=(10, 0, 10, 10))
        frame_central.pack(fill="both", expand=True)
        frame_central.columnconfigure(0, weight=1)
        frame_central.columnconfigure(1, weight=2)
        frame_central.rowconfigure(0, weight=1)

        sintomas_labelframe = ttk.LabelFrame(
            frame_central,
            text="Sintomas",
            padding=8,
        )
        sintomas_labelframe.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )
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

        self.canvas_sintomas.create_window(
            (0, 0),
            window=self.frame_checkboxes,
            anchor="nw",
        )
        self.canvas_sintomas.configure(yscrollcommand=self.scrollbar_sintomas.set)

        self.canvas_sintomas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_sintomas.grid(row=0, column=1, sticky="ns")

        resultado_labelframe = ttk.LabelFrame(
            frame_central,
            text="Resultados",
            padding=8,
        )
        resultado_labelframe.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        resultado_labelframe.rowconfigure(0, weight=1)
        resultado_labelframe.columnconfigure(0, weight=1)

        self.texto_resultados = tk.Text(
            resultado_labelframe,
            wrap="word",
            state="disabled",
        )
        scrollbar_resultados = ttk.Scrollbar(
            resultado_labelframe,
            orient="vertical",
            command=self.texto_resultados.yview,
        )
        self.texto_resultados.configure(yscrollcommand=scrollbar_resultados.set)
        self.texto_resultados.grid(row=0, column=0, sticky="nsew")
        scrollbar_resultados.grid(row=0, column=1, sticky="ns")

        frame_inferior = ttk.Frame(self, padding=(10, 0, 10, 10))
        frame_inferior.pack(fill="x")
        ttk.Button(
            frame_inferior,
            text="Diagnosticar",
            command=self._diagnosticar,
        ).pack(side="right")

    def _cambiar_categoria(self, _event=None):
        self._renderizar_sintomas()

    def _alternar_sintoma(self, sintoma, variable):
        if variable.get():
            self.sintomas_seleccionados.add(sintoma)
        else:
            self.sintomas_seleccionados.discard(sintoma)

        self.total_seleccionados.set(
            f"Seleccionados: {len(self.sintomas_seleccionados)}"
        )

    def _renderizar_sintomas(self):
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()

        categoria = self.categoria_actual.get()
        sintomas_categoria = self.catalogo.get(categoria, [])
        self.variables_categoria = {}

        if not sintomas_categoria:
            ttk.Label(
                self.frame_checkboxes,
                text="No hay sintomas para esta categoria.",
            ).pack(anchor="w")
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

    def _diagnosticar(self):
        try:
            umbral = float(self.umbral_match.get())
        except (TypeError, ValueError):
            messagebox.showerror("Error", "El umbral de match debe ser numerico.")
            return

        umbral = max(0.0, min(1.0, umbral))

        try:
            top_n = int(self.top_n.get())
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Top N debe ser un numero entero.")
            return

        top_n = max(5, min(10, top_n))

        try:
            resultados = diagnosticar(
                sintomas_usuario=sorted(self.sintomas_seleccionados),
                min_match=umbral,
                top_n=top_n,
            )
        except (FileNotFoundError, ValueError) as error:
            messagebox.showerror("Error de diagnostico", str(error))
            return

        self._mostrar_resultados(resultados)

    def _mostrar_resultados(self, resultados):
        self.texto_resultados.configure(state="normal")
        self.texto_resultados.delete("1.0", "end")

        if not resultados:
            self.texto_resultados.insert(
                "end",
                "No se encontraron diagnosticos con el umbral seleccionado.\n",
            )
            self.texto_resultados.configure(state="disabled")
            return

        for posicion, resultado in enumerate(resultados, start=1):
            self.texto_resultados.insert("end", f"{posicion}. {resultado['diagnostico']}\n")
            self.texto_resultados.insert(
                "end",
                (
                    f"   modulo: {resultado['modulo']}\n"
                    f"   match: {resultado['match']} ({resultado['match_ratio'] * 100:.1f}%)\n"
                    f"   score: {resultado['score']} | prioridad: {resultado['prioridad']}\n"
                    f"   prueba: {resultado['prueba']}\n"
                    f"   solucion: {resultado['solucion']}\n"
                ),
            )

            matched = ", ".join(resultado["condiciones_matched"]) or "-"
            missing = ", ".join(resultado["condiciones_missing"]) or "-"

            self.texto_resultados.insert(
                "end",
                f"   condiciones_matched: {matched}\n",
            )
            self.texto_resultados.insert(
                "end",
                f"   condiciones_missing: {missing}\n\n",
            )

        self.texto_resultados.configure(state="disabled")


if __name__ == "__main__":
    app = AutoExpertDesktopApp()
    app.mainloop()
