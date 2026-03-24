import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from src.database.supabase_client import supabase
from src.services.notifications import enviar_notificacion_async, enviar_notificacion_entrega

class UserDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Nuevo Usuario")
        self.geometry("400x650")
        self.after(10, self.focus_force)
        self.grab_set()
        self.callback = callback
        
        ctk.CTkLabel(self, text="Registro de Trabajador", font=("Arial", 20, "bold")).pack(pady=20)
        self.entry_n = ctk.CTkEntry(self, placeholder_text="Nombre Completo", width=300)
        self.entry_n.pack(pady=10)
        self.entry_t = ctk.CTkEntry(self, placeholder_text="Teléfono", width=300)
        self.entry_t.pack(pady=10)
        self.entry_d = ctk.CTkEntry(self, placeholder_text="Dirección", width=300)
        self.entry_d.pack(pady=10)
        self.opt = ctk.CTkOptionMenu(self, values=["Seleccione una categoría...", "Moños", "Bisutería"], width=300)
        self.opt.set("Seleccione una categoría...")
        self.opt.pack(pady=10)
        
        ctk.CTkButton(self, text="Guardar Trabajador", command=self.save, fg_color="#27ae60").pack(pady=30)

    def save(self):
        nombre = self.entry_n.get()
        cat_selec = self.opt.get()
        
        if not nombre.strip():
            messagebox.showwarning("Error", "Por favor ingrese un nombre")
            return
        
        if cat_selec == "Seleccione una categoría...":
            messagebox.showwarning("Error", "Por favor seleccione una categoría")
            return
        
        rol = "mono" if cat_selec == "Moños" else "bisuteria"
        try:
            supabase.table("usuarios").insert({
                "nombre_full": nombre, 
                "telefono": self.entry_t.get(), 
                "direccion": self.entry_d.get(),
                "rol_trabajo": rol
            }).execute()
            
            enviar_notificacion_async("Nuevo Trabajador Registrado", f"Se ha registrado a <b>{nombre}</b> en el área de {rol.upper()}.")
            
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class UserEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, user, callback):
        super().__init__(parent)
        self.user = user
        self.callback = callback
        self.title("Editar Trabajador")
        self.geometry("460x560")
        self.minsize(430, 520)
        self.after(10, self.focus_force)
        self.grab_set()

        ctk.CTkLabel(self, text="Editar Información", font=("Arial", 20, "bold")).pack(pady=(18, 10))

        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        ctk.CTkLabel(form, text="Nombre Completo", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(8, 4))
        self.entry_n = ctk.CTkEntry(form, placeholder_text="Ingrese el nombre completo", width=360)
        self.entry_n.pack(fill="x")
        self.entry_n.insert(0, str(user.get("nombre_full", "") or ""))

        ctk.CTkLabel(form, text="Teléfono", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(12, 4))
        self.entry_t = ctk.CTkEntry(form, placeholder_text="Ingrese el teléfono", width=360)
        self.entry_t.pack(fill="x")
        self.entry_t.insert(0, str(user.get("telefono", "") or ""))

        ctk.CTkLabel(form, text="Dirección", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(12, 4))
        self.entry_d = ctk.CTkEntry(form, placeholder_text="Ingrese la dirección", width=360)
        self.entry_d.pack(fill="x")
        self.entry_d.insert(0, str(user.get("direccion", "") or ""))

        ctk.CTkLabel(form, text="Categoría", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(12, 4))
        self.opt = ctk.CTkOptionMenu(form, values=["Moños", "Bisutería"], width=360)
        self.opt.pack(fill="x")
        self.opt.set("Moños" if user.get("rol_trabajo") == "mono" else "Bisutería")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 18))
        ctk.CTkButton(footer, text="Cancelar", command=self.destroy, fg_color="#5D6D7E", width=120).pack(side="left")
        ctk.CTkButton(footer, text="Guardar Cambios", command=self.save, fg_color="#2980b9", width=180).pack(side="right")

    def save(self):
        nombre = self.entry_n.get().strip()
        if not nombre:
            messagebox.showwarning("Error", "El nombre no puede estar vacío")
            return

        rol = "mono" if self.opt.get() == "Moños" else "bisuteria"

        try:
            supabase.table("usuarios").update({
                "nombre_full": nombre,
                "telefono": self.entry_t.get().strip(),
                "direccion": self.entry_d.get().strip(),
                "rol_trabajo": rol,
                "updated_at": "now()"
            }).eq("id", self.user["id"]).execute()

            enviar_notificacion_async(
                "Trabajador Actualizado",
                f"Se actualizó la ficha de <b>{nombre}</b>."
            )

            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Nueva Referencia")
        self.geometry("400x550")
        self.after(10, self.focus_force)
        self.grab_set()
        self.callback = callback

        ctk.CTkLabel(self, text="Nuevo Producto", font=("Arial", 20, "bold")).pack(pady=20)
        self.entry_r = ctk.CTkEntry(self, placeholder_text="Referencia", width=300)
        self.entry_r.pack(pady=10)
        self.opt = ctk.CTkOptionMenu(self, values=["Seleccione una categoría...", "Moños", "Bisutería"], width=300)
        self.opt.set("Seleccione una categoría...")
        self.opt.pack(pady=10)
        self.entry_v = ctk.CTkEntry(self, placeholder_text="Valor Unitario", width=300)
        self.entry_v.pack(pady=10)
        self.entry_s = ctk.CTkEntry(self, placeholder_text="Stock Inicial", width=300)
        self.entry_s.pack(pady=10)
        
        ctk.CTkButton(self, text="Registrar Producto", command=self.save, fg_color="#2980b9").pack(pady=30)

    def save(self):
        ref = self.entry_r.get()
        cat_selec = self.opt.get()
        
        if not ref.strip():
            messagebox.showwarning("Error", "Por favor ingrese una referencia")
            return
        
        if cat_selec == "Seleccione una categoría...":
            messagebox.showwarning("Error", "Por favor seleccione una categoría")
            return
        
        try:
            res = supabase.table("productos").insert({
                "nombre_ref": ref, 
                "categoria": "mono" if cat_selec == "Moños" else "bisuteria", 
                "valor_unitario": float(self.entry_v.get()), 
                "stock_total": int(self.entry_s.get()),
                "stock_en_calle": 0,
                "stock_terminado": 0
            }).execute()
            
            enviar_notificacion_async("Nueva Referencia", f"Se creó la referencia <b>{ref}</b> con {self.entry_s.get()} unidades.")
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ReabastecerDialog(ctk.CTkToplevel):
    def __init__(self, parent, p, callback):
        super().__init__(parent)
        self.title("Abastecer Bodega")
        self.geometry("350x250")
        self.after(10, self.focus_force)
        self.grab_set()
        self.p = p
        self.callback = callback
        
        ctk.CTkLabel(self, text=f"Sumar a: {p['nombre_ref']}", font=("Arial", 14, "bold")).pack(pady=15)
        self.entry = ctk.CTkEntry(self, placeholder_text="Cantidad", width=200)
        self.entry.pack(pady=15); self.entry.focus()
        
        ctk.CTkButton(self, text="Confirmar Ingreso", command=self.proc, fg_color="#27ae60").pack()

    def proc(self):
        try:
            cant = int(self.entry.get())
            new_val = self.p['stock_total'] + cant
            supabase.table("productos").update({"stock_total": new_val, "updated_at": "now()"}).eq("id", self.p['id']).execute()
            
            enviar_notificacion_async("Reabastecimiento Bodega", f"Ingreso de {cant} unidades para <b>{self.p['nombre_ref']}</b>. Total: {new_val}")
            
            self.callback(); self.destroy()
        except: messagebox.showerror("Error", "Ingrese un número válido")

class DespachoDialog(ctk.CTkToplevel):
    def __init__(self, parent, cat, callback):
        super().__init__(parent)
        self.title("Ejecutar Salida")
        self.geometry("450x750")
        self.after(10, self.focus_force)
        self.grab_set()
        self.cat = cat
        self.callback = callback
        
        # Timers para debouncing
        self.timer_usuarios = None
        self.timer_productos = None
        
        self.users = supabase.table("usuarios").select("*").eq("rol_trabajo", cat).execute().data
        self.prods = supabase.table("productos").select("*").eq("categoria", cat).gt("stock_total", 0).execute().data
        
        ctk.CTkLabel(self, text="Nuevo Despacho", font=("Arial", 18, "bold")).pack(pady=20)
        
        # Buscador de trabajadora
        ctk.CTkLabel(self, text="Buscar Trabajadora:", font=("Arial", 11, "bold")).pack(pady=(10, 0), padx=30, anchor="w")
        self.search_user = ctk.CTkEntry(self, placeholder_text="Digite para filtrar...", width=350)
        self.search_user.pack(pady=5)
        self.search_user.bind("<KeyRelease>", lambda e: self._debounce_usuarios())
        
        opciones_usuario = ["Seleccione un usuario..."] + [x['nombre_full'] for x in self.users]
        self.c_u = ctk.CTkComboBox(self, values=opciones_usuario, width=350, state="readonly")
        self.c_u.set("Seleccione un usuario...")
        self.c_u.pack(pady=10)
        
        # Buscador de referencia
        ctk.CTkLabel(self, text="Buscar Referencia:", font=("Arial", 11, "bold")).pack(pady=(10, 0), padx=30, anchor="w")
        self.search_prod = ctk.CTkEntry(self, placeholder_text="Digite para filtrar...", width=350)
        self.search_prod.pack(pady=5)
        self.search_prod.bind("<KeyRelease>", lambda e: self._debounce_productos())
        
        opciones_producto = ["Seleccione una referencia..."] + [f"{x['nombre_ref']} (Disp: {x['stock_total']})" for x in self.prods]
        self.c_p = ctk.CTkComboBox(self, values=opciones_producto, width=350, state="readonly")
        self.c_p.set("Seleccione una referencia...")
        self.c_p.pack(pady=10)
        
        self.entry_c = ctk.CTkEntry(self, placeholder_text="Cantidad", width=350)
        self.entry_c.pack(pady=10)
        
        ctk.CTkLabel(self, text="Fecha de Entrega Esperada", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        fecha_frame = ctk.CTkFrame(self, fg_color="transparent")
        fecha_frame.pack(pady=10)
        self.entry_fecha = DateEntry(fecha_frame, width=12, background='#2980b9', foreground='white', borderwidth=2, year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, font=("Arial", 11))
        self.entry_fecha.pack()
        
        ctk.CTkButton(self, text="REGISTRAR SALIDA", command=self.go, fg_color="#e67e22", height=40).pack(pady=30)

    def _debounce_usuarios(self):
        """Debounce para búsqueda de usuarios"""
        if self.timer_usuarios:
            self.after_cancel(self.timer_usuarios)
        self.timer_usuarios = self.after(200, self.actualizar_combo_usuarios)

    def _debounce_productos(self):
        """Debounce para búsqueda de productos"""
        if self.timer_productos:
            self.after_cancel(self.timer_productos)
        self.timer_productos = self.after(200, self.actualizar_combo_productos)

    def _create_section(self, parent, title, row):
        """Helper para crear títulos de sección"""
        label = ctk.CTkLabel(parent, text=title, font=("Arial", 13, "bold"), text_color="#3498db")
        label.grid(row=row, column=0, sticky="w", padx=20, pady=(15, 4))
        
        separator = ctk.CTkFrame(parent, fg_color="#3498db", height=2)
        separator.grid(row=row+1, column=0, sticky="ew", padx=20, pady=(0, 0))

    def actualizar_combo_usuarios(self):
        """Filtrar usuarios según búsqueda y auto-seleccionar el primero"""
        search_text = self.search_user.get().strip().lower()
        if search_text:
            filtered = [u for u in self.users if search_text in u['nombre_full'].lower()]
        else:
            filtered = self.users
        
        opciones = ["Seleccione un usuario..."] + [x['nombre_full'] for x in filtered]
        self.c_u.configure(values=opciones)
        
        # Auto-seleccionar el primer resultado filtrado si hay búsqueda activa
        if search_text and filtered:
            self.c_u.set(filtered[0]['nombre_full'])
        else:
            self.c_u.set("Seleccione un usuario...")

    def actualizar_combo_productos(self):
        """Filtrar productos según búsqueda y auto-seleccionar el primero"""
        search_text = self.search_prod.get().strip().lower()
        if search_text:
            filtered = [p for p in self.prods if search_text in p['nombre_ref'].lower()]
        else:
            filtered = self.prods
        
        opciones = ["Seleccione una referencia..."] + [f"{x['nombre_ref']} (Disp: {x['stock_total']})" for x in filtered]
        self.c_p.configure(values=opciones)
        
        # Auto-seleccionar el primer resultado filtrado si hay búsqueda activa
        if search_text and filtered:
            self.c_p.set(f"{filtered[0]['nombre_ref']} (Disp: {filtered[0]['stock_total']})")
        else:
            self.c_p.set("Seleccione una referencia...")

    def go(self):
        try:
            u_nom = self.c_u.get()
            if u_nom == "Seleccione un usuario...":
                messagebox.showwarning("Error", "Por favor seleccione un usuario")
                return
            
            p_nom = self.c_p.get()
            if p_nom == "Seleccione una referencia...":
                messagebox.showwarning("Error", "Por favor seleccione una referencia")
                return
            
            u = next(x for x in self.users if x['nombre_full'] == u_nom)
            p_ref = p_nom.split(" (Disp:")[0]
            p = next(x for x in self.prods if x['nombre_ref'] == p_ref)
            cant = int(self.entry_c.get())
            fecha_entrega = self.entry_fecha.get().strip()
            
            if cant > p['stock_total']: 
                messagebox.showerror("Error", "Cantidad no disponible")
                return
            
            if fecha_entrega and not self._validar_fecha(fecha_entrega):
                messagebox.showerror("Error", "Formato de fecha inválido (use YYYY-MM-DD)")
                return
            
            supabase.table("despachos").insert({
                "usuario_id": u['id'], "producto_id": p['id'], "cant_despachada": cant, 
                "fecha_salida": datetime.now().strftime("%Y-%m-%d"),
                "fecha_entrega_esperada": fecha_entrega if fecha_entrega else None,
                "valor_total_esperado": cant * p['valor_unitario'], "estado": "pendiente",
                "estado_pago": "pendiente"
            }).execute()
            
            supabase.table("productos").update({
                "stock_total": p['stock_total'] - cant, 
                "stock_en_calle": p.get('stock_en_calle', 0) + cant
            }).eq("id", p['id']).execute()
            
            enviar_notificacion_async("Nuevo Despacho", f"Se entregaron <b>{cant}</b> unidades de {p_ref} a {u_nom}.")
            
            self.callback(); self.destroy()
        except Exception as e: messagebox.showerror("Error", str(e))
    
    def _validar_fecha(self, fecha_str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except:
            return False

class RecepcionDialog(ctk.CTkToplevel):
    def __init__(self, parent, d, callback):
        super().__init__(parent)
        self.d = d; self.callback = callback
        self.title("Recepción de Trabajo")
        self.geometry("400x400")
        self.after(10, self.focus_force); self.grab_set()
        
        falta = d['cant_despachada'] - d['cant_entregada']
        ctk.CTkLabel(self, text=f"Recibiendo: {d['productos']['nombre_ref']}", font=("Arial", 14, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text=f"Pendiente por recibir: {falta} und.", font=("Arial", 12), text_color="#7f8c8d").pack()
        self.e = ctk.CTkEntry(self, width=200, placeholder_text="Cantidad recibida"); self.e.pack(pady=20); self.e.focus()
        
        ctk.CTkButton(self, text="CONFIRMAR RECEPCIÓN", command=self.save, fg_color="#27ae60", height=40).pack(pady=20)

    def save(self):
        try:
            nueva = int(self.e.get())
            if nueva <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a cero")
                return

            falta = self.d['cant_despachada'] - self.d['cant_entregada']
            if nueva > falta:
                messagebox.showerror("Error", f"No puede recibir más de lo pendiente ({falta} und.)")
                return

            total_acumulado = self.d['cant_entregada'] + nueva
            p = self.d['productos']
            u_nom = self.d['usuarios']['nombre_full']
            valor_unitario = float(p['valor_unitario'])
            saldo_actual = float(self.d.get('valor_pagado_real', 0) or 0)
            nuevo_saldo = saldo_actual + (nueva * valor_unitario)
            estado_entrega = "completado" if total_acumulado == self.d['cant_despachada'] else "pendiente"
            
            supabase.table("despachos").update({
                "cant_entregada": total_acumulado, 
                "valor_pagado_real": nuevo_saldo,
                "estado_pago": "pendiente",
                "fecha_pago": None,
                "estado": estado_entrega,
                "updated_at": "now()"
            }).eq("id", self.d['id']).execute()
            
            supabase.table("productos").update({
                "stock_total": p['stock_total'] + nueva,
                "stock_en_calle": p['stock_en_calle'] - nueva,
                "stock_terminado": p.get('stock_terminado', 0) + nueva
            }).eq("id", p['id']).execute()
            
            enviar_notificacion_entrega(
                trabajador=u_nom,
                referencia=p['nombre_ref'],
                recibida=nueva,
                total_despachado=self.d['cant_despachada'],
                acumulado=total_acumulado
            )
            
            self.callback(); self.destroy()
        except Exception as e: messagebox.showerror("Error", str(e))

class DespachoEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, despacho, callback):
        super().__init__(parent)
        self.despacho = despacho
        self.callback = callback
        self.title("Editar Fecha de Entrega")
        self.geometry("550x650")
        self.resizable(False, False)
        self.after(10, self.focus_force)
        self.grab_set()
        
        # Configurar color de fondo
        self.configure(fg_color="#1a1a1a")

        # Título principal
        titulo = ctk.CTkLabel(self, text="Editar Despacho", font=("Arial", 24, "bold"), text_color="#ecf0f1")
        titulo.pack(pady=(20, 5))
        
        subtitulo = ctk.CTkLabel(self, text="Modifica la fecha de entrega esperada", font=("Arial", 11), text_color="#95a5a6")
        subtitulo.pack(pady=(0, 20))
        
        # Frame principal
        form = ctk.CTkFrame(self, fg_color="#262626", corner_radius=10)
        form.pack(padx=20, pady=(0, 15), fill="both", expand=True)
        form.grid_columnconfigure(0, weight=1)

        # Campos deshabilitados (solo lectura)
        self._create_field(form, "Trabajadora", despacho['usuarios']['nombre_full'], 0, read_only=True)
        self._create_field(form, "Referencia", despacho['productos']['nombre_ref'], 2, read_only=True)
        self._create_field(form, "Cantidad Despachada", str(despacho['cant_despachada']), 4, read_only=True)
        self._create_field(form, "Cantidad Entregada", str(despacho['cant_entregada']), 6, read_only=True)

        # Campo de fecha EDITABLE
        label_fecha = ctk.CTkLabel(form, text="Fecha de Entrega Esperada", anchor="w", font=("Arial", 12, "bold"), text_color="#f39c12")
        label_fecha.grid(row=8, column=0, sticky="w", padx=20, pady=(20, 8))
        
        fecha_frame = ctk.CTkFrame(form, fg_color="transparent")
        fecha_frame.grid(row=9, column=0, sticky="w", padx=20, pady=(0, 20))
        
        # Parsear fecha actual
        fecha_actual = despacho.get('fecha_entrega_esperada') or ''
        if fecha_actual:
            try:
                fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d")
                year, month, day = fecha_obj.year, fecha_obj.month, fecha_obj.day
            except:
                year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        else:
            year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        
        self.entry_fecha = DateEntry(fecha_frame, width=12, background='#2980b9', foreground='white', borderwidth=2, year=year, month=month, day=day, font=("Arial", 11))
        self.entry_fecha.pack()

        # Botones
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(footer, text="Cancelar", command=self.destroy, fg_color="#34495e", hover_color="#2c3e50", width=150, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(footer, text="Guardar Fecha", command=self.save, fg_color="#2980b9", hover_color="#1f618d", width=250, height=40, font=("Arial", 12, "bold")).pack(side="right")

    def _create_field(self, parent, label_text, value, row, read_only=False):
        """Helper para crear campos de entrada"""
        label = ctk.CTkLabel(parent, text=label_text, anchor="w", font=("Arial", 11, "bold"), text_color="#bdc3c7")
        label.grid(row=row, column=0, sticky="w", padx=20, pady=(20 if row == 0 else 15, 6))
        
        entry = ctk.CTkEntry(parent, placeholder_text=label_text, width=360, height=36, font=("Arial", 11))
        entry.grid(row=row+1, column=0, sticky="ew", padx=20, pady=(0, 0))
        entry.insert(0, value)
        if read_only:
            entry.configure(state="disabled", text_color="#7f7f7f")
        
        # Ajustar grid weight para expansión
        parent.grid_columnconfigure(0, weight=1)

    def save(self):
        # Obtener fecha del DateEntry
        fecha_date = self.entry_fecha.get_date()
        nueva_fecha = fecha_date.strftime("%Y-%m-%d")

        try:
            supabase.table("despachos").update({
                "fecha_entrega_esperada": nueva_fecha,
                "updated_at": "now()"
            }).eq("id", self.despacho["id"]).execute()

            messagebox.showinfo("Éxito", "Fecha de entrega actualizada correctamente")
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ReporteTrabajadorDialog(ctk.CTkToplevel):
    def __init__(self, parent, n, datos):
        super().__init__(parent)
        self.title(f"Estado de Cuenta: {n}")
        self.geometry("700x850")
        self.configure(fg_color="white")
        self.after(10, self.focus_force)

        sc = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=0)
        sc.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(sc, text="ALUNA - REPORTE DE TRABAJO", font=("Courier", 24, "bold"), text_color="black").pack(pady=(30,5))
        ctk.CTkLabel(sc, text=f"TRABAJADOR(A): {n.upper()}", font=("Courier", 18, "bold"), text_color="black").pack()
        ctk.CTkLabel(sc, text="_" * 60, text_color="black").pack(pady=20)
        
        total_acumulado = 0
        for d in datos:
            total_acumulado += d.get('valor_pagado_real', 0)
            block = ctk.CTkFrame(sc, fg_color="#f8f9fa", border_width=1, border_color="#dddddd")
            block.pack(fill="x", pady=15, padx=20)
            ctk.CTkLabel(block, text=f"REF: {d['productos']['nombre_ref'].upper()}", font=("Courier", 16, "bold"), text_color="#2c3e50").pack(pady=10)
            
            detalles = [
                ("CANTIDAD RECIBIDA:", f"{d['cant_despachada']} und."),
                ("CANTIDAD ENTREGADA:", f"{d['cant_entregada']} und."),
                ("CANTIDAD PENDIENTE:", f"{d['cant_despachada'] - d['cant_entregada']} und."),
                ("SALDO A PAGAR:", f"${d['valor_pagado_real']:,}"),
                ("ESTADO:", d['estado'].upper())
            ]
            for label, valor in detalles:
                line = ctk.CTkFrame(block, fg_color="transparent")
                line.pack(fill="x", padx=40, pady=2)
                ctk.CTkLabel(line, text=label, font=("Courier", 13, "bold"), text_color="black", width=220, anchor="w").pack(side="left")
                ctk.CTkLabel(line, text=valor, font=("Courier", 13), text_color="black", anchor="w").pack(side="left")
        
        ctk.CTkLabel(sc, text="_" * 60, text_color="black").pack(pady=20)
        ctk.CTkLabel(sc, text=f"TOTAL A PAGAR: $ {total_acumulado:,.2f}", font=("Courier", 26, "bold"), text_color="#27ae60").pack(pady=20)

        ctk.CTkButton(self, text="CERRAR REPORTE", command=self.destroy, fg_color="black").pack(pady=10)

class AgendarPagoDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback, fecha_predefinida=None):
        super().__init__(parent)
        self.title("Agendar Nuevo Pago")
        self.geometry("400x450")
        self.after(10, self.focus_force)
        self.grab_set()
        self.callback = callback

        ctk.CTkLabel(self, text="Programar Corte de Pago", font=("Arial", 18, "bold")).pack(pady=20)
        
        self.entry_fecha = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD", width=300)
        self.entry_fecha.pack(pady=10)
        
        if fecha_predefinida:
            self.entry_fecha.insert(0, fecha_predefinida)
        
        self.opt_cat = ctk.CTkOptionMenu(self, values=["Moños", "Bisutería"], width=300)
        self.opt_cat.pack(pady=10)
        
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Descripción (Ej: Quincena Marzo)", width=300)
        self.entry_desc.pack(pady=10)
        self.entry_desc.focus()
        
        ctk.CTkButton(self, text="Guardar en Calendario", command=self.save, fg_color="#8E44AD").pack(pady=30)

    def save(self):
        fecha = self.entry_fecha.get().strip()
        desc = self.entry_desc.get().strip()
        cat = "mono" if self.opt_cat.get() == "Moños" else "bisuteria"
        
        if not fecha or not desc:
            messagebox.showerror("Error", "Debe llenar todos los campos")
            return
            
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            supabase.table("calendario_pagos").insert({
                "fecha_programada": fecha,
                "categoria": cat,
                "descripcion": desc,
                "estado": "pendiente"
            }).execute()
            
            # Enviar notificación
            categoria_txt = "MOÑOS" if cat == "mono" else "BISUTERÍA"
            enviar_notificacion_async(
                "Pago Agendado en Calendario",
                f"<b>Categoría:</b> {categoria_txt}<br><b>Fecha:</b> {fecha}<br><b>Descripción:</b> {desc}"
            )
            
            messagebox.showinfo("Éxito", "Pago agendado.")
            self.callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Formato YYYY-MM-DD inválido")
        except Exception as e:
            messagebox.showerror("Error", str(e))