import customtkinter as ctk
from tkinter import messagebox
from src.database.supabase_client import supabase

class UserTable(ctk.CTkFrame):
    def __init__(self, master, edit_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_callback = edit_callback
        self.summary_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", height=50)
        self.summary_frame.pack(fill="x", padx=20, pady=5)
        self.total_label = ctk.CTkLabel(self.summary_frame, text="TRABAJADORES ACTIVOS: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#27ae60")
        self.total_label.pack(pady=10)
        self.table_frame = ctk.CTkScrollableFrame(self, width=1200, height=400)
        self.table_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.anchos = [250, 190, 320, 170, 90]
        self.render_headers()

    def render_headers(self):
        headers = ["Nombre", "Teléfono", "Dirección", "Clasificación", "Acción"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)
        for i, text in enumerate(headers):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold"), width=self.anchos[i], anchor="center").grid(row=0, column=i, padx=5)

    def update_data(self, users):
        for widget in self.table_frame.winfo_children():
            if widget != self.table_frame.winfo_children()[0]: widget.destroy()
        for user in users:
            row = ctk.CTkFrame(self.table_frame); row.pack(fill="x", pady=2)
            rol = "Moños" if user['rol_trabajo'] == "mono" else "Bisutería"
            ctk.CTkLabel(row, text=user['nombre_full'], width=self.anchos[0], anchor="center").grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=user.get('telefono', ''), width=self.anchos[1], anchor="center").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=user.get('direccion', ''), width=self.anchos[2], anchor="center").grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row, text=rol, width=self.anchos[3], anchor="center").grid(row=0, column=3, padx=5)
            if self.edit_callback:
                ctk.CTkButton(
                    row,
                    text="✏️",
                    width=36,
                    height=28,
                    fg_color="#2980b9",
                    hover_color="#1f618d",
                    command=lambda x=user: self.edit_callback(x),
                ).grid(row=0, column=4, padx=8)
        self.total_label.configure(text=f"TRABAJADORES ACTIVOS: {len(users)}")

class InventoryTable(ctk.CTkFrame):
    def __init__(self, master, reabastecer_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.reabastecer_callback = reabastecer_callback
        self.summary_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", height=60)
        self.summary_frame.pack(fill="x", padx=20, pady=10)
        self.total_label = ctk.CTkLabel(self.summary_frame, text="STOCK TOTAL BODEGA: 0", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1f6aa5")
        self.total_label.pack(pady=15)
        
        self.table_frame = ctk.CTkScrollableFrame(self, width=1400, height=450)
        self.table_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.anchos = [180, 100, 120, 120, 120, 180]
        self.render_headers()

    def render_headers(self):
        headers = ["Referencia", "Valor U.", "Stock Bodega", "Stock Salida", "Stock Entrega", "Acciones"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)
        for i, text in enumerate(headers):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold"), width=self.anchos[i], anchor="center").grid(row=0, column=i, padx=5)

    def update_data(self, products):
        for widget in self.table_frame.winfo_children():
            if widget != self.table_frame.winfo_children()[0]: widget.destroy()
        total_bodega = 0
        for p in products:
            row = ctk.CTkFrame(self.table_frame); row.pack(fill="x", pady=2)
            total_bodega += p['stock_total']
            
            ctk.CTkLabel(row, text=p['nombre_ref'], width=self.anchos[0], anchor="center").grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=f"${p['valor_unitario']:,}", width=self.anchos[1], anchor="center").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=p['stock_total'], width=self.anchos[2], anchor="center", font=("bold", 13)).grid(row=0, column=2, padx=5)
            
            ctk.CTkLabel(row, text=p.get('stock_en_calle', 0), width=self.anchos[3], anchor="center", text_color="#e67e22").grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row, text=p.get('stock_terminado', 0), width=self.anchos[4], anchor="center", text_color="#27ae60").grid(row=0, column=4, padx=5)
            
            btn_f = ctk.CTkFrame(row, fg_color="transparent", width=self.anchos[5]); btn_f.grid(row=0, column=5, padx=5)
            ctk.CTkButton(btn_f, text="+ Stock", width=70, height=25, command=lambda x=p: self.reabastecer_callback(x)).pack(side="left", padx=5)
            ctk.CTkButton(btn_f, text="🕒", width=30, height=25, command=lambda x=p: self.ver_h(x)).pack(side="left", padx=2)
            
        self.total_label.configure(text=f"STOCK TOTAL BODEGA: {total_bodega}")

    def ver_h(self, p):
        from src.database.supabase_client import supabase
        
        # Obtener todos los despachos y entregas de este producto
        despachos = supabase.table("despachos").select("*, usuarios(*), productos(*)").eq("producto_id", p['id']).order("fecha_salida", desc=True).execute().data
        
        historial = []
        
        for d in despachos:
            # Agregar la salida del despacho
            historial.append({
                'fecha': d['fecha_salida'],
                'tipo': 'DESPACHO',
                'trabajadora': d['usuarios']['nombre_full'],
                'cantidad': d['cant_despachada'],
                'timestamp': d['fecha_salida'] + " 00:00"
            })
            
            # Agregar si hubo entregas
            if d['cant_entregada'] > 0:
                historial.append({
                    'fecha': d['updated_at'][:10] if 'updated_at' in d else d['fecha_salida'],
                    'tipo': 'ENTREGA',
                    'trabajadora': d['usuarios']['nombre_full'],
                    'cantidad': d['cant_entregada'],
                    'timestamp': d['updated_at'] if 'updated_at' in d else d['fecha_salida'] + " 00:00"
                })
        
        # Ordenar por timestamp descendente
        historial.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if not historial:
            messagebox.showinfo("Historial de Referencia", f"Sin movimientos para {p['nombre_ref']}")
            return
        
        # Construir texto del historial
        txt_lineas = [f"HISTORIAL: {p['nombre_ref']}"]
        txt_lineas.append("=" * 70)
        
        for h in historial:
            linea = f"{h['fecha']} | {h['tipo']:10} | {h['trabajadora']:20} | {h['cantidad']} und."
            txt_lineas.append(linea)
        
        txt = "\n".join(txt_lineas)
        messagebox.showinfo("Historial de Referencia", txt)

class DespachosTable(ctk.CTkFrame):
    def __init__(self, master, entregar_callback, edit_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.entregar_callback = entregar_callback
        self.edit_callback = edit_callback
        self.summary_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", height=50)
        self.summary_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(self.summary_frame, text="CONTROL DE OPERACIONES", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.table_frame = ctk.CTkScrollableFrame(self, width=1700, height=500)
        self.table_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.anchos = [140, 140, 80, 80, 100, 100, 110, 110, 120, 120]
        self.render_headers()

    def render_headers(self):
        headers = ["Trabajadora", "Referencia", "C. Desp.", "C. Entreg.", "Val. Total", "A Pagar", "F. Salida", "F. Entrega", "Estado", "Acción"]
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)
        for i, text in enumerate(headers):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold", size=11), width=self.anchos[i], anchor="center").grid(row=0, column=i, padx=2)

    def update_data(self, despachos):
        for widget in self.table_frame.winfo_children():
            if widget != self.table_frame.winfo_children()[0]: widget.destroy()
        for d in despachos:
            est = d['estado']
            col = "#27ae60" if est == "completado" else "#f1c40f"
            txt_est = "FINALIZADO" if est == "completado" else "PENDIENTE"
            
            # Efecto visual deshabilitado si está completado
            bg_row = "#2a2a2a" if est == "completado" else "#1a1a1a"
            text_color_disabled = "#7f7f7f" if est == "completado" else "white"
            
            row = ctk.CTkFrame(self.table_frame, fg_color=bg_row); row.pack(fill="x", pady=2)
            
            # Obtener fecha de entrega esperada
            fecha_entrega = d.get('fecha_entrega_esperada', '-')
            if not fecha_entrega:
                fecha_entrega = '-'
            
            ctk.CTkLabel(row, text=d['usuarios']['nombre_full'], width=self.anchos[0], anchor="center", text_color=text_color_disabled).grid(row=0, column=0, padx=2)
            ctk.CTkLabel(row, text=d['productos']['nombre_ref'], width=self.anchos[1], anchor="center", text_color=text_color_disabled).grid(row=0, column=1, padx=2)
            ctk.CTkLabel(row, text=d['cant_despachada'], width=self.anchos[2], anchor="center", text_color=text_color_disabled).grid(row=0, column=2, padx=2)
            ctk.CTkLabel(row, text=d['cant_entregada'], width=self.anchos[3], anchor="center", font=ctk.CTkFont(weight="bold"), text_color=text_color_disabled).grid(row=0, column=3, padx=2)
            ctk.CTkLabel(row, text=f"${d['valor_total_esperado']:,}", width=self.anchos[4], anchor="center", text_color=text_color_disabled).grid(row=0, column=4, padx=2)
            ctk.CTkLabel(row, text=f"${d['valor_pagado_real']:,}", width=self.anchos[5], anchor="center", text_color="#7f7f7f" if est == "completado" else "#2ecc71").grid(row=0, column=5, padx=2)
            ctk.CTkLabel(row, text=d['fecha_salida'], width=self.anchos[6], anchor="center", text_color=text_color_disabled).grid(row=0, column=6, padx=2)
            ctk.CTkLabel(row, text=fecha_entrega, width=self.anchos[7], anchor="center", text_color="#7f7f7f" if est == "completado" else "#3498db").grid(row=0, column=7, padx=2)
            ctk.CTkLabel(row, text=txt_est, width=self.anchos[8], anchor="center", text_color=col if est == "pendiente" else "#7f7f7f", font=ctk.CTkFont(weight="bold")).grid(row=0, column=8, padx=2)
            btn_f = ctk.CTkFrame(row, fg_color="transparent", width=self.anchos[9]); btn_f.grid(row=0, column=9, padx=2)
            btn_c = ctk.CTkFrame(btn_f, fg_color="transparent"); btn_c.pack(expand=True)
            if est != "completado":
                ctk.CTkButton(btn_c, text="Recibir", width=60, height=25, fg_color="#e67e22", command=lambda x=d: self.entregar_callback(x)).pack(side="left", padx=2)
            else:
                # Botón deshabilitado para despachos completados
                ctk.CTkButton(btn_c, text="Completado", width=60, height=25, fg_color="#7f7f7f", state="disabled").pack(side="left", padx=2)
            if self.edit_callback:
                ctk.CTkButton(btn_c, text="✏️", width=30, height=25, fg_color="#3498db", command=lambda x=d: self.edit_callback(x)).pack(side="left", padx=2)
            ctk.CTkButton(btn_c, text="🕒", width=30, height=25, command=lambda x=d: self.ver_log(x)).pack(side="left", padx=2)

    def ver_log(self, d):
        valor_unit = float(d['productos'].get('valor_unitario', 0) or 0)
        saldo_pendiente = float(d.get('valor_pagado_real', 0) or 0)
        total_generado = float(d.get('cant_entregada', 0) or 0) * valor_unit
        total_pagado = max(total_generado - saldo_pendiente, 0)
        fecha_pago = d.get('fecha_pago') or "Sin pago registrado"
        actualizado = d.get('updated_at', 'N/A')

        msg = (
            f"AUDITORÍA ACUMULADA\n"
            f"Salida: {d['fecha_salida']}\n"
            f"Entregado: {d['cant_entregada']}/{d['cant_despachada']}\n"
            f"Fecha Esperada: {d.get('fecha_entrega_esperada', 'N/A')}\n"
            f"Pagado histórico: ${total_pagado:,.2f}\n"
            f"Saldo pendiente actual: ${saldo_pendiente:,.2f}\n"
            f"Último pago: {fecha_pago}\n"
            f"Modificado: {actualizado[:16] if isinstance(actualizado, str) else actualizado}"
        )
        messagebox.showinfo("Historial Despacho", msg)