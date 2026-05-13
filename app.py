import os
import sqlite3
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DB_NAME = "asociacion.db"
RECIBOS_DIR = "recibos"


def get_conn():
    return sqlite3.connect(DB_NAME)


def ensure_recibos_dir():
    if not os.path.exists(RECIBOS_DIR):
        os.makedirs(RECIBOS_DIR)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión básica de asociación - Socios y pagos")
        self.geometry("900x500")

        ensure_recibos_dir()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.frame_socios = ttk.Frame(notebook)
        self.frame_pagos = ttk.Frame(notebook)
        self.frame_recibos = ttk.Frame(notebook)

        notebook.add(self.frame_socios, text="Socios")
        notebook.add(self.frame_pagos, text="Pagos")
        notebook.add(self.frame_recibos, text="Recibos")

        self.build_socios_tab()
        self.build_pagos_tab()
        self.build_recibos_tab()

    # ---------------- SOCIOS ----------------
    def build_socios_tab(self):
        frame_form = ttk.LabelFrame(self.frame_socios, text="Datos del socio")
        frame_form.pack(side="top", fill="x", padx=10, pady=10)

        labels = ["Nombre", "DNI", "Teléfono", "Email", "Dirección", "Activo (1/0)"]
        self.socio_vars = {k: tk.StringVar() for k in labels}

        for i, label in enumerate(labels):
            ttk.Label(frame_form, text=label + ":").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(frame_form, textvariable=self.socio_vars[label], width=40)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)

        self.socio_vars["Activo (1/0)"].set("1")

        frame_buttons = ttk.Frame(frame_form)
        frame_buttons.grid(row=0, column=2, rowspan=6, padx=10, pady=3, sticky="ns")

        ttk.Button(frame_buttons, text="Añadir socio", command=self.add_socio).pack(fill="x", pady=2)
        ttk.Button(frame_buttons, text="Editar socio", command=self.edit_socio).pack(fill="x", pady=2)
        ttk.Button(frame_buttons, text="Eliminar socio", command=self.delete_socio).pack(fill="x", pady=2)
        ttk.Button(frame_buttons, text="Limpiar campos", command=self.clear_socio_form).pack(fill="x", pady=2)

        frame_table = ttk.Frame(self.frame_socios)
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "nombre", "dni", "telefono", "email", "direccion", "activo")
        self.tree_socios = ttk.Treeview(frame_table, columns=columns, show="headings")
        for col in columns:
            self.tree_socios.heading(col, text=col.capitalize())
            self.tree_socios.column(col, width=100 if col != "direccion" else 200)

        self.tree_socios.pack(side="left", fill="both", expand=True)
        self.tree_socios.bind("<<TreeviewSelect>>", self.on_socio_select)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree_socios.yview)
        self.tree_socios.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.load_socios()

    def load_socios(self):
        for row in self.tree_socios.get_children():
            self.tree_socios.delete(row)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, dni, telefono, email, direccion, activo FROM socios ORDER BY nombre;")
        for row in cur.fetchall():
            self.tree_socios.insert("", "end", values=row)
        conn.close()

    def add_socio(self):
        nombre = self.socio_vars["Nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "El nombre es obligatorio.")
            return

        dni = self.socio_vars["DNI"].get().strip()
        telefono = self.socio_vars["Teléfono"].get().strip()
        email = self.socio_vars["Email"].get().strip()
        direccion = self.socio_vars["Dirección"].get().strip()
        activo = self.socio_vars["Activo (1/0)"].get().strip() or "1"

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO socios (nombre, dni, telefono, email, direccion, activo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, dni, telefono, email, direccion, int(activo)))
        conn.commit()
        conn.close()

        self.load_socios()
        self.clear_socio_form()

    def edit_socio(self):
        selected = self.tree_socios.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona un socio para editar.")
            return

        socio_id = self.tree_socios.item(selected[0])["values"][0]

        nombre = self.socio_vars["Nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "El nombre es obligatorio.")
            return

        dni = self.socio_vars["DNI"].get().strip()
        telefono = self.socio_vars["Teléfono"].get().strip()
        email = self.socio_vars["Email"].get().strip()
        direccion = self.socio_vars["Dirección"].get().strip()
        activo = self.socio_vars["Activo (1/0)"].get().strip() or "1"

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE socios
            SET nombre = ?, dni = ?, telefono = ?, email = ?, direccion = ?, activo = ?
            WHERE id = ?
        """, (nombre, dni, telefono, email, direccion, int(activo), socio_id))
        conn.commit()
        conn.close()

        self.load_socios()

    def delete_socio(self):
        selected = self.tree_socios.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona un socio para eliminar.")
            return

        socio_id = self.tree_socios.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este socio?"):
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM socios WHERE id = ?", (socio_id,))
        conn.commit()
        conn.close()

        self.load_socios()
        self.clear_socio_form()

    def clear_socio_form(self):
        for var in self.socio_vars.values():
            var.set("")
        self.socio_vars["Activo (1/0)"].set("1")

    def on_socio_select(self, event):
        selected = self.tree_socios.selection()
        if not selected:
            return
        values = self.tree_socios.item(selected[0])["values"]
        self.socio_vars["Nombre"].set(values[1])
        self.socio_vars["DNI"].set(values[2])
        self.socio_vars["Teléfono"].set(values[3])
        self.socio_vars["Email"].set(values[4])
        self.socio_vars["Dirección"].set(values[5])
        self.socio_vars["Activo (1/0)"].set(str(values[6]))

    # ---------------- PAGOS ----------------
    def build_pagos_tab(self):
        frame_form = ttk.LabelFrame(self.frame_pagos, text="Registro de pago")
        frame_form.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="Socio:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.pago_socio_var = tk.StringVar()
        self.combo_socio = ttk.Combobox(frame_form, textvariable=self.pago_socio_var, width=40, state="readonly")
        self.combo_socio.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(frame_form, text="Fecha (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.pago_fecha_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frame_form, textvariable=self.pago_fecha_var, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(frame_form, text="Concepto:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.pago_concepto_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.pago_concepto_var, width=40).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(frame_form, text="Importe:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        self.pago_importe_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.pago_importe_var, width=20).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(frame_form, text="Método de pago:").grid(row=4, column=0, sticky="w", padx=5, pady=3)
        self.pago_metodo_var = tk.StringVar()
        ttk.Entry(frame_form, textvariable=self.pago_metodo_var, width=20).grid(row=4, column=1, sticky="w", padx=5, pady=3)

        frame_buttons = ttk.Frame(frame_form)
        frame_buttons.grid(row=0, column=2, rowspan=5, padx=10, pady=3, sticky="ns")

        ttk.Button(frame_buttons, text="Registrar pago", command=self.add_pago).pack(fill="x", pady=2)
        ttk.Button(frame_buttons, text="Eliminar pago", command=self.delete_pago).pack(fill="x", pady=2)
        ttk.Button(frame_buttons, text="Limpiar campos", command=self.clear_pago_form).pack(fill="x", pady=2)

        frame_table = ttk.Frame(self.frame_pagos)
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "socio", "fecha", "concepto", "importe", "metodo")
        self.tree_pagos = ttk.Treeview(frame_table, columns=columns, show="headings")
        for col in columns:
            self.tree_pagos.heading(col, text=col.capitalize())
            self.tree_pagos.column(col, width=100 if col not in ("concepto", "socio") else 200)

        self.tree_pagos.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree_pagos.yview)
        self.tree_pagos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.load_socios_combo()
        self.load_pagos()

    def load_socios_combo(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM socios WHERE activo = 1 ORDER BY nombre;")
        socios = cur.fetchall()
        conn.close()

        self.socios_map = {f"{nombre} (ID {sid})": sid for sid, nombre in socios}
        self.combo_socio["values"] = list(self.socios_map.keys())

    def load_pagos(self):
        for row in self.tree_pagos.get_children():
            self.tree_pagos.delete(row)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, s.nombre, p.fecha, p.concepto, p.importe, p.metodo_pago
            FROM pagos p
            JOIN socios s ON p.socio_id = s.id
            ORDER BY p.fecha DESC;
        """)
        for row in cur.fetchall():
            self.tree_pagos.insert("", "end", values=row)
        conn.close()

    def add_pago(self):
        socio_label = self.pago_socio_var.get()
        if not socio_label:
            messagebox.showwarning("Aviso", "Selecciona un socio.")
            return

        socio_id = self.socios_map.get(socio_label)
        fecha = self.pago_fecha_var.get().strip()
        concepto = self.pago_concepto_var.get().strip()
        importe_str = self.pago_importe_var.get().strip()

        if not fecha or not concepto or not importe_str:
            messagebox.showwarning("Aviso", "Fecha, concepto e importe son obligatorios.")
            return

        try:
            importe = float(importe_str.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Aviso", "Importe no válido.")
            return

        metodo = self.pago_metodo_var.get().strip()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pagos (socio_id, fecha, concepto, importe, metodo_pago)
            VALUES (?, ?, ?, ?, ?)
        """, (socio_id, fecha, concepto, importe, metodo))
        conn.commit()
        conn.close()

        self.load_pagos()
        self.clear_pago_form()

    def delete_pago(self):
        selected = self.tree_pagos.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona un pago para eliminar.")
            return

        pago_id = self.tree_pagos.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este pago?"):
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
        conn.commit()
        conn.close()

        self.load_pagos()

    def clear_pago_form(self):
        self.pago_socio_var.set("")
        self.pago_fecha_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.pago_concepto_var.set("")
        self.pago_importe_var.set("")
        self.pago_metodo_var.set("")

    # ---------------- RECIBOS ----------------
    def build_recibos_tab(self):
        frame_top = ttk.LabelFrame(self.frame_recibos, text="Generación de recibos PDF")
        frame_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_top, text="Selecciona un pago y genera su recibo en PDF.").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        ttk.Button(frame_top, text="Generar recibo del pago seleccionado", command=self.generar_recibo_pago).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        ttk.Button(frame_top, text="Abrir carpeta de recibos", command=self.abrir_carpeta_recibos).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        frame_info = ttk.LabelFrame(self.frame_recibos, text="Pagos (para seleccionar)")
        frame_info.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "socio", "fecha", "concepto", "importe", "metodo")
        self.tree_pagos_recibos = ttk.Treeview(frame_info, columns=columns, show="headings")
        for col in columns:
            self.tree_pagos_recibos.heading(col, text=col.capitalize())
            self.tree_pagos_recibos.column(col, width=100 if col not in ("concepto", "socio") else 200)

        self.tree_pagos_recibos.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_info, orient="vertical", command=self.tree_pagos_recibos.yview)
        self.tree_pagos_recibos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.load_pagos_recibos()

    def load_pagos_recibos(self):
        for row in self.tree_pagos_recibos.get_children():
            self.tree_pagos_recibos.delete(row)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, s.nombre, p.fecha, p.concepto, p.importe, p.metodo_pago
            FROM pagos p
            JOIN socios s ON p.socio_id = s.id
            ORDER BY p.fecha DESC;
        """)
        for row in cur.fetchall():
            self.tree_pagos_recibos.insert("", "end", values=row)
        conn.close()

    def generar_recibo_pago(self):
        selected = self.tree_pagos_recibos.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona un pago para generar el recibo.")
            return

        values = self.tree_pagos_recibos.item(selected[0])["values"]
        pago_id, socio_nombre, fecha, concepto, importe, metodo = values

        ensure_recibos_dir()
        filename = os.path.join(RECIBOS_DIR, f"recibo_pago_{pago_id}.pdf")

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "RECIBO DE PAGO")

        c.setFont("Helvetica", 12)
        y = height - 100
        c.drawString(50, y, f"ID de pago: {pago_id}")
        y -= 20
        c.drawString(50, y, f"Socio: {socio_nombre}")
        y -= 20
        c.drawString(50, y, f"Fecha: {fecha}")
        y -= 20
        c.drawString(50, y, f"Concepto: {
