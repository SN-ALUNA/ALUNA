import customtkinter as ctk
from tkinter import messagebox
from src.database.supabase_client import supabase
from .tables import UserTable, InventoryTable, DespachosTable
from .dialogs import (UserDialog, ProductDialog, ReabastecerDialog, 
                      DespachoDialog, RecepcionDialog, ReporteTrabajadorDialog, AgendarPagoDialog, UserEditDialog, DespachoEditDialog)
from src.services.notifications import enviar_notificacion_async
from datetime import datetime
import calendar
import os

# Librerías para PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class AlunaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ALUNA - Sistema de Gestión Integral")
        self.geometry("1480x768")
        self.minsize(1300, 800)

        self.filtro_actual = None
        self.current_tab = None
        self.datos_ultimo_reporte = None
        
        # Timers para debouncing de búsquedas
        self.inv_search_timer = None
        self.desp_search_timer = None
        
        # Colores de botones
        self.color_activo = "#3498DB"
        self.color_inactivo = "#5D6D7E"
        self.color_filtro_mono = "#E67E22"
        self.color_filtro_bisuteria = "#9B59B6"
        
        # Variables para el Calendario
        hoy = datetime.now()
        self.cal_year = hoy.year
        self.cal_month = hoy.month

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="ALUNA", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, padx=20, pady=30)
        
        self.btn_usuarios = ctk.CTkButton(self.sidebar_frame, text="Usuarios", height=45, fg_color=self.color_inactivo, command=self.show_usuarios)
        self.btn_usuarios.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_inventario = ctk.CTkButton(self.sidebar_frame, text="Inventario", height=45, fg_color=self.color_inactivo, command=self.show_inventario)
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_despachos = ctk.CTkButton(self.sidebar_frame, text="Despachos", height=45, fg_color=self.color_inactivo, command=self.show_despachos)
        self.btn_despachos.grid(row=3, column=0, padx=20, pady=10)

        self.btn_seguimiento = ctk.CTkButton(self.sidebar_frame, text="🔍 Seguimiento", height=45, fg_color=self.color_inactivo, command=self.show_seguimiento)
        self.btn_seguimiento.grid(row=4, column=0, padx=20, pady=10)

        self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📊 Reporte Proveedor", height=45, fg_color=self.color_inactivo, command=self.show_reportes)
        self.btn_reportes.grid(row=5, column=0, padx=20, pady=10)

        self.btn_pagos = ctk.CTkButton(self.sidebar_frame, text="💳 Pagos y Calendario", height=45, fg_color=self.color_inactivo, command=self.show_pagos)
        self.btn_pagos.grid(row=6, column=0, padx=20, pady=10)

        # --- MAIN CONTENT ---
        self.main_content = ctk.CTkFrame(self, corner_radius=15)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.show_inicio()

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def actualizar_estado_botones(self, seccion_activa):
        """Actualiza el color de los botones del sidebar según la sección activa"""
        botones = {
            "usuarios": self.btn_usuarios,
            "inventario": self.btn_inventario,
            "despachos": self.btn_despachos,
            "seguimiento": self.btn_seguimiento,
            "reportes": self.btn_reportes,
            "pagos": self.btn_pagos
        }
        
        for seccion, btn in botones.items():
            if seccion == seccion_activa:
                btn.configure(fg_color=self.color_activo)
            else:
                btn.configure(fg_color=self.color_inactivo)

    # --- PANTALLA INICIAL ---
    def show_inicio(self):
        self.current_tab = "inicio"
        self.clear_main_content()
        
        # Actualizar colores de botones
        self.actualizar_estado_botones(None)
        
        # Frame central para la bienvenida
        welcome_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        welcome_frame.pack(expand=True, fill="both")
        
        # Título principal
        titulo = ctk.CTkLabel(
            welcome_frame,
            text="ALUNA",
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color="#3498DB"
        )
        titulo.pack(pady=30)
        
        # Descripción del software
        desc = ctk.CTkLabel(
            welcome_frame,
            text="Sistema Integral de Gestión de Inventario",
            font=ctk.CTkFont(size=20),
            text_color="#7F8C8D"
        )
        desc.pack(pady=10)
        
        desc2 = ctk.CTkLabel(
            welcome_frame,
            text="Control de despachos, inventario, pagos y auditoría de proveedores",
            font=ctk.CTkFont(size=14),
            text_color="#95A5A6"
        )
        desc2.pack(pady=5)
        
        # Separador visual
        sep_frame = ctk.CTkFrame(welcome_frame, height=2, fg_color="#34495E")
        sep_frame.pack(fill="x", padx=100, pady=40)
        
        # Acróstico principal
        acronimo = ctk.CTkLabel(
            welcome_frame,
            text="A.L.U.N.A.",
            font=ctk.CTkFont(size=64, weight="bold"),
            text_color="#3498DB"
        )
        acronimo.pack(pady=(10, 20))

        lineas = [
            "Administración",
            "Logística",
            "Unificada para",
            "Negocios de",
            "Artesanías"
        ]

        for texto in lineas:
            ctk.CTkLabel(
                welcome_frame,
                text=texto,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#2C3E50"
            ).pack(pady=4)

    # --- NAVEGACIÓN BÁSICA ---
    def show_usuarios(self):
        self.current_tab = "usuarios"
        self.actualizar_estado_botones("usuarios")
        self.clear_main_content()
        self.create_filter_header("Gestión de Trabajadores", lambda: UserDialog(self, self.load_users_from_db))
        self.mostrar_mensaje_espera("El archivo está en silencio.", "Elige MOÑOS o BISUTERÍA para revelar la información.")
        self.user_table = UserTable(self.main_content, edit_callback=self.abrir_edicion_usuario)
        self.user_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def abrir_edicion_usuario(self, user):
        UserEditDialog(self, user, self.load_users_from_db)

    def abrir_edicion_despacho(self, despacho):
        DespachoEditDialog(self, despacho, self.load_despachos_from_db)

    def show_inventario(self):
        self.current_tab = "inventario"
        self.actualizar_estado_botones("inventario")
        self.clear_main_content()
        self.create_filter_header("Gestión de Inventario", lambda: ProductDialog(self, self.load_inventory_from_db))
        self.mostrar_mensaje_espera("Bodega en modo espera.", "Selecciona una categoría para consultar existencias.")

        search_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        search_frame.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(search_frame, text="Buscar Referencia:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        self.inv_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Digite para filtrar...", width=320, height=36)
        self.inv_search_entry.pack(side="left")
        self.inv_search_entry.bind("<KeyRelease>", lambda e: self._debounce_inv_search())

        self.inv_table = InventoryTable(self.main_content, reabastecer_callback=lambda p: ReabastecerDialog(self, p, self.load_inventory_from_db))
        self.inv_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def show_despachos(self):
        self.current_tab = "despachos"
        self.actualizar_estado_botones("despachos")
        self.clear_main_content()
        self.create_filter_header("Control de Despachos", self.abrir_dialogo_despacho)
        self.mostrar_mensaje_espera("Radar de salidas listo.", "Selecciona una categoría para cargar los movimientos.")

        search_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        search_frame.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(search_frame, text="Buscar:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        self.desp_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Referencia o trabajadora...", width=320, height=36)
        self.desp_search_entry.pack(side="left")
        self.desp_search_entry.bind("<KeyRelease>", lambda e: self._debounce_desp_search())

        self.despacho_table = DespachosTable(self.main_content, entregar_callback=lambda d: RecepcionDialog(self, d, self.load_despachos_from_db), edit_callback=self.abrir_edicion_despacho)
        self.despacho_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def show_pagos(self):
        self.current_tab = "pagos"
        self.actualizar_estado_botones("pagos")
        self.clear_main_content()

        split_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=20, pady=20)
        split_frame.grid_columnconfigure(0, weight=1)
        split_frame.grid_columnconfigure(1, weight=1)
        split_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: calendario visual
        self.panel_calendario = ctk.CTkFrame(split_frame, fg_color="#2b2b2b", corner_radius=10)
        self.panel_calendario.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.render_calendario()

        # Panel derecho: liquidador parcial
        self.panel_liquidador = ctk.CTkFrame(split_frame, fg_color="transparent")
        self.panel_liquidador.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(self.panel_liquidador, text="Liquidador por Referencias", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        search_container = ctk.CTkFrame(self.panel_liquidador, fg_color="transparent")
        search_container.pack(pady=10)
        self.entry_liq = ctk.CTkEntry(search_container, placeholder_text="Escriba el nombre...", width=250, height=40)
        self.entry_liq.pack(side="left", padx=10)
        self.entry_liq.bind("<Return>", lambda e: self.buscar_deuda_trabajadora())
        ctk.CTkButton(search_container, text="BUSCAR", width=100, height=40, fg_color="#e67e22", font=ctk.CTkFont(weight="bold"), command=self.buscar_deuda_trabajadora).pack(side="left")

        self.liq_area = ctk.CTkScrollableFrame(self.panel_liquidador, fg_color="white", corner_radius=10)
        self.liq_area.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(self.liq_area, text="Busque una trabajadora.", text_color="gray", font=("Arial", 16)).pack(pady=50)

        self.footer_liq = ctk.CTkFrame(self.panel_liquidador, fg_color="#f8f9fa", height=80, corner_radius=10)
        self.footer_liq.pack(fill="x", pady=10)
        self.lbl_total_sel = ctk.CTkLabel(self.footer_liq, text="Total Seleccionado: $ 0.00", font=("Courier", 18, "bold"), text_color="#27ae60")
        self.lbl_total_sel.pack(side="left", padx=20, pady=20)
        self.btn_pagar_sel = ctk.CTkButton(self.footer_liq, text="PAGAR SELECCIÓN", fg_color="#27ae60", state="disabled", command=self.ejecutar_pago_parcial)
        self.btn_pagar_sel.pack(side="right", padx=20, pady=20)

    # Lógica del Calendario Visual
    def cambiar_mes(self, delta):
        self.cal_month += delta
        if self.cal_month > 12:
            self.cal_month = 1
            self.cal_year += 1
        elif self.cal_month < 1:
            self.cal_month = 12
            self.cal_year -= 1
        self.render_calendario()

    def render_calendario(self):
        for widget in self.panel_calendario.winfo_children(): widget.destroy()

        # Controles de mes
        ctrl_frame = ctk.CTkFrame(self.panel_calendario, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=15, padx=20)
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        nombre_mes = meses[self.cal_month - 1]

        ctk.CTkButton(ctrl_frame, text="<", width=40, command=lambda: self.cambiar_mes(-1)).pack(side="left")
        ctk.CTkLabel(ctrl_frame, text=f"{nombre_mes} {self.cal_year}", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", expand=True)
        ctk.CTkButton(ctrl_frame, text=">", width=40, command=lambda: self.cambiar_mes(1)).pack(side="right")

        # Días de la semana
        dias_frame = ctk.CTkFrame(self.panel_calendario, fg_color="transparent")
        dias_frame.pack(fill="x", padx=10)
        nombres_dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, d in enumerate(nombres_dias):
            ctk.CTkLabel(dias_frame, text=d, font=ctk.CTkFont(weight="bold"), width=60).grid(row=0, column=i, padx=5, pady=5)

        # Buscar eventos del mes en la base de datos
        inicio_mes = f"{self.cal_year}-{self.cal_month:02d}-01"
        fin_mes = f"{self.cal_year}-{self.cal_month:02d}-{calendar.monthrange(self.cal_year, self.cal_month)[1]}"
        try:
            # Eventos de calendario de pagos
            res_eventos = supabase.table("calendario_pagos").select("*").gte("fecha_programada", inicio_mes).lte("fecha_programada", fin_mes).execute()
            eventos_por_dia = {}
            for ev in res_eventos.data:
                dia = int(ev['fecha_programada'].split("-")[2])
                if dia not in eventos_por_dia: eventos_por_dia[dia] = []
                eventos_por_dia[dia].append(ev)
            
            # Entregas esperadas (despachos con fecha_entrega_esperada)
            res_entregas = supabase.table("despachos").select("*, usuarios(*), productos(*)").gte("fecha_entrega_esperada", inicio_mes).lte("fecha_entrega_esperada", fin_mes).execute()
            entregas_por_dia = {}
            for ent in res_entregas.data:
                if ent.get('fecha_entrega_esperada'):
                    dia = int(ent['fecha_entrega_esperada'].split("-")[2])
                    if dia not in entregas_por_dia: entregas_por_dia[dia] = []
                    entregas_por_dia[dia].append(ent)
        except:
            eventos_por_dia = {}
            entregas_por_dia = {}

        # Generar Cuadrícula
        grid_frame = ctk.CTkFrame(self.panel_calendario, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cal_matriz = calendar.monthcalendar(self.cal_year, self.cal_month)
        for fila, semana in enumerate(cal_matriz):
            for col, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkFrame(grid_frame, width=60, height=60, fg_color="transparent").grid(row=fila, column=col, padx=2, pady=2)
                else:
                    # Definir color de fondo según si hay entregas esperadas
                    tiene_entregas = dia in entregas_por_dia and len(entregas_por_dia[dia]) > 0
                    bg_color = "#1e5f3a" if tiene_entregas else "#34495E"  # Verde oscuro si hay entregas
                    
                    celda = ctk.CTkFrame(grid_frame, width=60, height=60, fg_color=bg_color, corner_radius=5)
                    celda.grid(row=fila, column=col, padx=2, pady=2, sticky="nsew")
                    celda.grid_propagate(False)
                    
                    # Número del día
                    color_txt = "white"
                    hoy = datetime.now()
                    if dia == hoy.day and self.cal_month == hoy.month and self.cal_year == hoy.year:
                        color_txt = "#3498DB" # Resaltar hoy

                    # Al pulsar el día se abre el formulario con la fecha ya diligenciada.
                    ctk.CTkButton(
                        celda,
                        text=str(dia),
                        width=24,
                        height=20,
                        fg_color="transparent",
                        hover_color="#3d566e" if not tiene_entregas else "#2a7a52",
                        text_color=color_txt,
                        font=ctk.CTkFont(weight="bold"),
                        command=lambda d=dia: self.abrir_agenda_en_dia(d),
                    ).pack(anchor="ne", padx=3, pady=2)

                    # Mostrar entregas esperadas
                    if tiene_entregas:
                        # Mostrar un indicador visual de entrega
                        ctk.CTkLabel(celda, text="🚚", font=("Arial", 12)).pack(side="left", padx=2, pady=2)
                        # Botón para ver detalles de entregas
                        btn_entregas = ctk.CTkButton(celda, text="📦", width=20, height=15, fg_color="#27ae60", hover_color="#1e8449",
                                                     command=lambda d=dia, ents=entregas_por_dia[dia]: self.ver_entregas_del_dia(d, ents))
                        btn_entregas.pack(side="right", padx=2, pady=2)

                    # Dibujar indicadores si hay eventos de pago
                    if dia in eventos_por_dia:
                        for ev in eventos_por_dia[dia]:
                            c_evento = "#E67E22" if ev['categoria'] == 'mono' else "#9B59B6"
                            if ev['estado'] == 'ejecutado': c_evento = "#27ae60"
                            
                            # Botón pequeño del evento para ver detalles / completarlo
                            btn_ev = ctk.CTkButton(celda, text="•", width=40, height=15, fg_color=c_evento, hover_color="#7f8c8d",
                                                   command=lambda e=ev: self.ver_detalle_evento(e))
                            btn_ev.pack(pady=1)

    def abrir_agenda_en_dia(self, dia):
        fecha = f"{self.cal_year}-{self.cal_month:02d}-{dia:02d}"
        AgendarPagoDialog(self, self.render_calendario, fecha_predefinida=fecha)

    def ver_detalle_evento(self, ev):
        est = "FINALIZADO" if ev['estado'] == 'ejecutado' else "PENDIENTE"
        cat = "MOÑOS" if ev['categoria'] == 'mono' else "BISUTERÍA"
        msg = f"Fecha: {ev['fecha_programada']}\nCategoría: {cat}\nDescripción: {ev['descripcion']}\nEstado: {est}"
        
        if ev['estado'] == 'pendiente':
            if messagebox.askyesno("Evento del Calendario", f"{msg}\n\n¿Desea marcar este recordatorio como EJECUTADO?"):
                supabase.table("calendario_pagos").update({"estado": "ejecutado"}).eq("id", ev['id']).execute()
                self.render_calendario()
        else:
            messagebox.showinfo("Evento del Calendario", msg)

    def ver_entregas_del_dia(self, dia, entregas):
        """Mostrar quién va a entregar ese día"""
        if not entregas:
            messagebox.showinfo("Entregas", f"No hay entregas programadas para el día {dia}")
            return
        
        msg_lineas = [f"ENTREGAS ESPERADAS - {dia} de {self.cal_month:02d}/{self.cal_year}"]
        msg_lineas.append("=" * 60)
        
        for ent in entregas:
            trabajadora = ent['usuarios']['nombre_full']
            referencia = ent['productos']['nombre_ref']
            cantidad = ent['cant_despachada']
            estado = "PENDIENTE" if ent['estado'] == 'pendiente' else "COMPLETADO"
            
            msg_lineas.append(f"🧑 {trabajadora}")
            msg_lineas.append(f"   📦 Ref: {referencia} ({cantidad} und.)")
            msg_lineas.append(f"   Estado: {estado}")
            msg_lineas.append("")
        
        msg = "\n".join(msg_lineas)
        messagebox.showinfo(f"Entregas del {dia}", msg)

    # Lógica de Pagos Parciales
    def buscar_deuda_trabajadora(self):
        for widget in self.liq_area.winfo_children(): widget.destroy()
        nombre = self.entry_liq.get().strip()
        if not nombre: return
        
        # Resetear footer
        self.checkboxes_activos = [] # Tuplas (CTkCheckBox_Var, Datos_Despacho)
        self.actualizar_total_seleccionado()

        try:
            res_user = supabase.table("usuarios").select("id, nombre_full").ilike("nombre_full", f"%{nombre}%").execute()
            if not res_user.data:
                ctk.CTkLabel(self.liq_area, text=f"No se encontró a: '{nombre}'", text_color="red").pack(pady=50)
                return

            # Si hay múltiples coincidencias, priorizamos coincidencia exacta del nombre.
            user = next((u for u in res_user.data if u['nombre_full'].strip().lower() == nombre.lower()), res_user.data[0])

            # Se considera pendiente todo despacho con saldo por pagar > 0.
            # También incluimos estado_pago pendiente por compatibilidad con registros antiguos.
            res_despachos = (
                supabase.table("despachos")
                .select("id, producto_id, valor_pagado_real, productos(nombre_ref, valor_unitario)")
                .eq("usuario_id", user['id'])
                .or_("valor_pagado_real.gt.0,estado_pago.eq.pendiente")
                .gt("cant_entregada", 0)
                .order("updated_at", desc=True)
                .execute()
            )
            
            ctk.CTkLabel(self.liq_area, text=f"PENDIENTES DE: {user['nombre_full'].upper()}", font=("Courier", 18, "bold"), text_color="black").pack(pady=(10, 10))
            
            if not res_despachos.data:
                ctk.CTkLabel(self.liq_area, text="✅ No hay facturas pendientes.", font=("Arial", 16), text_color="#27ae60").pack(pady=30)
                return

            # Agrupar por referencia para sumar entregas recientes del mismo producto.
            grupos = {}
            for d in res_despachos.data:
                saldo = float(d.get('valor_pagado_real', 0) or 0)
                if saldo <= 0:
                    continue

                producto = d.get('productos') or {}
                ref = producto.get('nombre_ref', 'SIN REFERENCIA')
                valor_unit = float(producto.get('valor_unitario', 0) or 0)
                key = d.get('producto_id') or ref

                if key not in grupos:
                    grupos[key] = {
                        "referencia": ref,
                        "valor_unitario": valor_unit,
                        "saldo_pendiente": 0.0,
                        "ids": [],
                    }

                grupos[key]["saldo_pendiente"] += saldo
                grupos[key]["ids"].append(d['id'])

            if not grupos:
                ctk.CTkLabel(self.liq_area, text="✅ No hay facturas pendientes.", font=("Arial", 16), text_color="#27ae60").pack(pady=30)
                return

            for g in grupos.values():
                f = ctk.CTkFrame(self.liq_area, fg_color="#f8f9fa", border_width=1, border_color="#cccccc")
                f.pack(fill="x", padx=20, pady=5)
                
                var_check = ctk.IntVar(value=0)
                saldo = float(g.get('saldo_pendiente', 0) or 0)
                valor_unit = float(g.get('valor_unitario', 0) or 0)
                entregado_reciente = (saldo / valor_unit) if valor_unit > 0 else 0
                entregado_txt = f"{entregado_reciente:.2f}".rstrip('0').rstrip('.')
                texto = f"Ref: {g['referencia']} | Entregado reciente: {entregado_txt} und. | Saldo: ${saldo:,.2f}"
                
                chk = ctk.CTkCheckBox(f, text=texto, variable=var_check, text_color="black", command=self.actualizar_total_seleccionado)
                chk.pack(side="left", padx=15, pady=15)
                
                self.checkboxes_activos.append((var_check, g))

        except Exception as e: messagebox.showerror("Error", str(e))

    def actualizar_total_seleccionado(self):
        total = 0
        seleccionados = 0
        
        if hasattr(self, 'checkboxes_activos'):
            for var, d in self.checkboxes_activos:
                if var.get() == 1:
                    total += float(d.get('saldo_pendiente', 0) or 0)
                    seleccionados += 1
        
        self.lbl_total_sel.configure(text=f"Total a Pagar: $ {total:,.2f}")
        
        if seleccionados > 0:
            self.btn_pagar_sel.configure(state="normal")
        else:
            self.btn_pagar_sel.configure(state="disabled")

    def ejecutar_pago_parcial(self):
        ids_a_pagar = []
        for var, d in self.checkboxes_activos:
            if var.get() == 1:
                ids_a_pagar.extend(d.get('ids', []))
        ids_a_pagar = list(set(ids_a_pagar))
        
        if not ids_a_pagar: return
        
        if not messagebox.askyesno("Confirmar Pago", f"¿Registrar el pago de {len(ids_a_pagar)} referencias seleccionadas?"):
            return
            
        try:
            # Obtener datos de los despachos a pagar para el email
            despachos_pago = supabase.table("despachos").select("*, usuarios(*), productos(*)").in_("id", ids_a_pagar).execute().data
            
            total_pagado = sum([d['valor_pagado_real'] for d in despachos_pago])
            detalles_pago = "<br>".join([f"- {d['productos']['nombre_ref']}: ${d['valor_pagado_real']:,} ({d['usuarios']['nombre_full']})" for d in despachos_pago])
            
            supabase.table("despachos").update({
                "estado_pago": "pagado",
                "valor_pagado_real": 0,
                "fecha_pago": "now()"
            }).in_("id", ids_a_pagar).execute()
            
            # Enviar notificación de pago realizado
            asunto = f"Pago Registrado - {len(ids_a_pagar)} referencias"
            mensaje = f"""
            <b>Se ha registrado un pago exitoso</b><br>
            <b>Total Pagado:</b> ${total_pagado:,}<br>
            <b>Cantidad de Referencias:</b> {len(ids_a_pagar)}<br>
            <b>Detalles:</b><br>{detalles_pago}
            """
            enviar_notificacion_async(asunto, mensaje)
            
            messagebox.showinfo("Éxito", "Pago registrado. Si llegan nuevas entregas, volverán a aparecer como saldo pendiente.")
            self.buscar_deuda_trabajadora() # Recargar la lista
        except Exception as e: messagebox.showerror("Error", str(e))

    # --- MÓDULO SEGUIMIENTO (TRABAJADORES) ---
    def show_seguimiento(self):
        self.current_tab = "seguimiento"
        self.actualizar_estado_botones("seguimiento")
        self.clear_main_content()
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=30)
        ctk.CTkLabel(header, text="Módulo de Seguimiento Individual", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=10)
        search_container = ctk.CTkFrame(header, fg_color="transparent")
        search_container.pack(pady=20)
        self.entry_busqueda = ctk.CTkEntry(search_container, placeholder_text="Escriba el nombre...", width=400, height=40)
        self.entry_busqueda.pack(side="left", padx=10)
        self.entry_busqueda.bind("<Return>", lambda e: self.ejecutar_seguimiento())
        ctk.CTkButton(search_container, text="GENERAR REPORTE", width=150, height=40, fg_color="#2980b9", font=ctk.CTkFont(weight="bold"), command=self.ejecutar_seguimiento).pack(side="left")
        self.report_area = ctk.CTkScrollableFrame(self.main_content, fg_color="white", corner_radius=10)
        self.report_area.pack(fill="both", expand=True, padx=50, pady=20)
        ctk.CTkLabel(self.report_area, text="Ingrese un nombre para visualizar el estado de cuenta.", text_color="gray", font=("Arial", 16)).pack(pady=100)

    def ejecutar_seguimiento(self):
        for widget in self.report_area.winfo_children(): widget.destroy()
        nombre = self.entry_busqueda.get().strip()
        if not nombre: return
        try:
            res_user = supabase.table("usuarios").select("*").ilike("nombre_full", f"%{nombre}%").execute()
            if not res_user.data:
                ctk.CTkLabel(self.report_area, text=f"No se encontró a: '{nombre}'", text_color="red", font=("Arial", 16)).pack(pady=50)
                return
            user = res_user.data[0]
            res_despachos = supabase.table("despachos").select("*, productos(*)").eq("usuario_id", user['id']).execute()

            # Primero mostrar referencias pendientes de pago (incluye nuevas sin entrega),
            # y al final las que ya están al día.
            pendientes_pago = [d for d in res_despachos.data if d.get('estado_pago', 'pendiente') != 'pagado']
            pagados = [d for d in res_despachos.data if d.get('estado_pago', 'pendiente') == 'pagado']

            pendientes_pago.sort(key=lambda x: x.get('updated_at', x['fecha_salida']), reverse=True)
            pagados.sort(key=lambda x: x.get('updated_at', x['fecha_salida']), reverse=True)

            despachos_ordenados = pendientes_pago + pagados
            
            self.dibujar_hoja_vida(user, despachos_ordenados)
        except Exception as e: messagebox.showerror("Error", str(e))

    def dibujar_hoja_vida(self, user, despachos):
        for widget in self.report_area.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.report_area, text="ALUNA - HOJA DE TRABAJO", font=("Courier", 26, "bold"), text_color="black").pack(pady=(30, 5))
        ctk.CTkLabel(self.report_area, text=f"TRABAJADOR(A): {user['nombre_full'].upper()}", font=("Courier", 18, "bold"), text_color="black").pack()
        ctk.CTkLabel(self.report_area, text="_" * 60, text_color="black").pack(pady=10)
        
        if not despachos:
            ctk.CTkLabel(self.report_area, text="\nSIN REGISTROS DE DESPACHO", font=("Courier", 14), text_color="red").pack(pady=50)
            return

        pendientes = [d for d in despachos if d.get('estado_pago', 'pendiente') != 'pagado']
        pagados = [d for d in despachos if d.get('estado_pago', 'pendiente') == 'pagado']

        sum_total_pendiente = sum(float(d.get('valor_pagado_real', 0) or 0) for d in pendientes)
        sum_total_historico = 0
        for d in despachos:
            valor_unitario = float(d['productos'].get('valor_unitario', 0) or 0)
            sum_total_historico += float(d.get('cant_entregada', 0) or 0) * valor_unitario

        ctk.CTkLabel(self.report_area, text="SALDO PENDIENTE A PAGAR:", font=("Courier", 22, "bold"), text_color="#1a5276").pack(pady=(10, 0))
        ctk.CTkLabel(self.report_area, text=f"$ {sum_total_pendiente:,.2f}", font=("Courier", 35, "bold"), text_color="#e74c3c").pack(pady=5)
        ctk.CTkLabel(self.report_area, text=f"Total Histórico Generado (Pagado + Pendiente): $ {sum_total_historico:,.2f}", font=("Courier", 12), text_color="gray").pack(pady=(0, 15))

        def render_despacho(d, es_pagado):
            valor_unitario = float(d['productos'].get('valor_unitario', 0) or 0)
            valor_pendiente = float(d.get('valor_pagado_real', 0) or 0)
            valor_total_generado = float(d.get('cant_entregada', 0) or 0) * valor_unitario
            valor_pagado_hist = max(valor_total_generado - valor_pendiente, 0)

            bg_color = "#e8f8f5" if es_pagado else "#f8f9fa"
            border_c = "#a3e4d7" if es_pagado else "#cccccc"
            lbl_pago = "✅ PAGADO" if es_pagado else "⚠️ PENDIENTE DE PAGO"
            col_pago = "#27ae60" if es_pagado else "#e67e22"

            block = ctk.CTkFrame(self.report_area, fg_color=bg_color, corner_radius=10, border_width=1, border_color=border_c)
            block.pack(fill="x", pady=15, padx=30)

            head_f = ctk.CTkFrame(block, fg_color="transparent")
            head_f.pack(fill="x", pady=10, padx=20)
            ctk.CTkLabel(head_f, text=f"REFERENCIA: {d['productos']['nombre_ref'].upper()}", font=("Courier", 18, "bold"), text_color="#2c3e50").pack(side="left")
            ctk.CTkLabel(head_f, text=lbl_pago, font=("Courier", 14, "bold"), text_color=col_pago).pack(side="right")

            detalles = [
                ("CANTIDAD RECIBIDA:", f"{d['cant_despachada']} und."),
                ("CANTIDAD ENTREGADA:", f"{d['cant_entregada']} und."),
                ("CANTIDAD PENDIENTE:", f"{d['cant_despachada'] - d['cant_entregada']} und."),
                ("PAGADO HISTÓRICO:", f"${valor_pagado_hist:,.2f}"),
                ("SALDO PENDIENTE:", f"${valor_pendiente:,.2f}"),
                ("ESTADO ENTREGA:", d['estado'].upper())
            ]
            for label, v in detalles:
                line = ctk.CTkFrame(block, fg_color="transparent")
                line.pack(fill="x", padx=40, pady=2)
                ctk.CTkLabel(line, text=label, font=("Courier", 14, "bold"), text_color="black", width=220, anchor="w").pack(side="left")
                ctk.CTkLabel(line, text=v, font=("Courier", 14), text_color="#333333", anchor="w").pack(side="left")

        if pendientes:
            ctk.CTkLabel(self.report_area, text="REFERENCIAS PENDIENTES", font=("Courier", 14, "bold"), text_color="#e67e22").pack(pady=(5, 0))
            for d in pendientes:
                render_despacho(d, False)

        if pagados:
            ctk.CTkLabel(self.report_area, text="REFERENCIAS PAGADAS / AL DÍA", font=("Courier", 14, "bold"), text_color="#27ae60").pack(pady=(10, 0))
            for d in pagados:
                render_despacho(d, True)

        ctk.CTkLabel(self.report_area, text="ALUNA - Control de Calidad", font=("Courier", 10, "italic"), text_color="gray").pack(pady=20)

    # --- MÓDULO REPORTES (PROVEEDORES) ---
    def show_reportes(self):
        self.current_tab = "reportes"
        self.actualizar_estado_botones("reportes")
        self.clear_main_content()
        if not self.filtro_actual:
            self.filtro_actual = "mono"
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=30)
        ctk.CTkLabel(header, text="📊 Auditoría de Proveedores - Detalle de Inventario", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        ctk.CTkLabel(header, text="Informe técnico y preciso de todas las referencias en circulación", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=5)
        
        # Filtros por categoría
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.pack(pady=15)
        ctk.CTkLabel(filter_frame, text="Categoría:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        self.btn_reportes_monos = ctk.CTkButton(filter_frame, text="MOÑOS", width=120, height=35, command=lambda: self.actualizar_filtro_reportes("mono"))
        self.btn_reportes_monos.pack(side="left", padx=10)
        self.btn_reportes_bisuteria = ctk.CTkButton(filter_frame, text="BISUTERÍA", width=120, height=35, command=lambda: self.actualizar_filtro_reportes("bisuteria"))
        self.btn_reportes_bisuteria.pack(side="left", padx=10)
        self.actualizar_colores_categoria()
        
        search_container = ctk.CTkFrame(header, fg_color="transparent")
        search_container.pack(pady=10)
        
        ctk.CTkLabel(search_container, text="Buscar Referencia:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        self.search_ref_entry = ctk.CTkEntry(search_container, placeholder_text="Digite para filtrar...", width=250, height=40)
        self.search_ref_entry.pack(side="left", padx=10)
        self.search_ref_entry.bind("<KeyRelease>", lambda e: self.actualizar_combo_reportes())
        
        prods_res = supabase.table("productos").select("nombre_ref").eq("categoria", self.filtro_actual).execute()
        self.lista_refs_completa = [p['nombre_ref'] for p in prods_res.data] if prods_res.data else []
        opciones_combo = ["Seleccione una referencia..."] + self.lista_refs_completa
        self.combo_refs = ctk.CTkOptionMenu(search_container, values=opciones_combo, width=300, height=40)
        self.combo_refs.set("Seleccione una referencia...")
        self.combo_refs.pack(side="left", padx=10)
        
        ctk.CTkButton(search_container, text="▶ GENERAR INFORME", width=150, height=40, fg_color="#1E8449", font=ctk.CTkFont(weight="bold"), command=self.ejecutar_reporte_proveedor).pack(side="left", padx=10)
        
        self.report_area_prov = ctk.CTkScrollableFrame(self.main_content, fg_color="white", corner_radius=10)
        self.report_area_prov.pack(fill="both", expand=True, padx=50, pady=20)
        ctk.CTkLabel(self.report_area_prov, text="Seleccione una referencia para generar el informe completo de auditoría.", text_color="gray", font=("Arial", 14)).pack(pady=100)

    def actualizar_filtro_reportes(self, cat):
        """Actualiza el filtro de categoría en reportes"""
        self.filtro_actual = cat
        self.actualizar_colores_categoria()
        prods_res = supabase.table("productos").select("nombre_ref").eq("categoria", cat).execute()
        self.lista_refs_completa = [p['nombre_ref'] for p in prods_res.data] if prods_res.data else []
        self.search_ref_entry.delete(0, "end")
        self.actualizar_combo_reportes()

    def actualizar_combo_reportes(self):
        """Actualiza el combo de referencias según búsqueda"""
        search_text = self.search_ref_entry.get().strip().lower()
        if search_text:
            filtered = [ref for ref in self.lista_refs_completa if search_text in ref.lower()]
        else:
            filtered = self.lista_refs_completa
        opciones = ["Seleccione una referencia..."] + (filtered if filtered else ["Sin resultados"])
        self.combo_refs.configure(values=opciones)
        self.combo_refs.set("Seleccione una referencia...")
        if filtered:
            self.combo_refs.set(filtered[0])

    def ejecutar_reporte_proveedor(self):
        for widget in self.report_area_prov.winfo_children(): widget.destroy()
        ref = self.combo_refs.get()
        if not ref or ref == "Seleccione una referencia..." or ref == "Sin resultados":
            messagebox.showwarning("Selección Requerida", "Por favor seleccione una referencia válida")
            return
        try:
            p = supabase.table("productos").select("*").eq("nombre_ref", ref).single().execute().data
            desp_todos = supabase.table("despachos").select("*, usuarios(*)").eq("producto_id", p['id']).execute().data
            
            self.datos_ultimo_reporte = {"producto": p, "despachos": desp_todos}

            # --- ENCABEZADO DEL INFORME ---
            ctk.CTkButton(self.report_area_prov, text="📧 ENVIAR REPORTE POR PDF", fg_color="#E74C3C", font=("Arial", 12, "bold"), command=self.generar_y_enviar_pdf).pack(pady=10)

            ctk.CTkLabel(self.report_area_prov, text="ALUNA - AUDITORÍA DE PROVEEDORES", font=("Courier", 24, "bold"), text_color="black").pack(pady=(30, 5))
            ctk.CTkLabel(self.report_area_prov, text=f"REFERENCIA: {ref.upper()}", font=("Courier", 20, "bold"), text_color="#1E8449").pack(pady=(0, 10))
            ctk.CTkLabel(self.report_area_prov, text=f"Fecha del Informe: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", font=("Courier", 11), text_color="#555").pack()
            ctk.CTkLabel(self.report_area_prov, text="=" * 80, text_color="black").pack(pady=15)

            # --- RESUMEN GENERAL ---
            resumen_frame = ctk.CTkFrame(self.report_area_prov, fg_color="#ECF0F1", corner_radius=10, border_width=2, border_color="#95A5A6")
            resumen_frame.pack(fill="x", padx=30, pady=15)
            
            ctk.CTkLabel(resumen_frame, text="RESUMEN ACTUALIZADO", font=("Courier", 14, "bold"), text_color="#1E8449").pack(pady=(10, 0))
            
            # Calcular totales
            cant_total_cargada = sum([d['cant_despachada'] for d in desp_todos])
            cant_en_bodega = p['stock_total']
            cant_en_calle = p.get('stock_en_calle', 0)
            cant_finalizada = p.get('stock_terminado', 0)
            valor_total = cant_total_cargada * p['valor_unitario']
            
            # Obtener fechas
            fecha_cargue = min([d['fecha_salida'] for d in desp_todos]) if desp_todos else "N/A"
            fecha_modif = datetime.now().strftime('%Y-%m-%d')
            
            # Tabla resumen estilo factura
            tabla_resumen = [
                ["CONCEPTO", "CANTIDAD"],
                ["-" * 35, "-" * 25],
                [f"Cargue Inicial", f"{cant_total_cargada} und."],
                [f"En Bodega (Proceso)", f"{cant_en_bodega} und."],
                [f"En Calle (Despachos)", f"{cant_en_calle} und."],
                [f"Finalizada (Entregada)", f"{cant_finalizada} und."],
            ]
            
            for fila in tabla_resumen:
                f = ctk.CTkFrame(resumen_frame, fg_color="transparent")
                f.pack(fill="x", padx=20, pady=3)
                for i, texto in enumerate(fila):
                    ancho = [380, 200][i]
                    peso = "bold" if fila == tabla_resumen[0] else "normal"
                    ctk.CTkLabel(f, text=texto.ljust(25 if i == 0 else 20), font=("Courier", 11, peso), text_color="black", width=ancho, anchor="w").pack(side="left", padx=5)

            # Información de fechas
            fecha_f = ctk.CTkFrame(resumen_frame, fg_color="transparent")
            fecha_f.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(fecha_f, text=f"Primer Cargue: {fecha_cargue}", font=("Courier", 10), text_color="#34495E").pack(anchor="w")
            ctk.CTkLabel(fecha_f, text=f"Última Modificación: {fecha_modif}", font=("Courier", 10), text_color="#34495E").pack(anchor="w")

            # --- DETALLE DE MOVIMIENTOS ---
            ctk.CTkLabel(self.report_area_prov, text="\nDETALLE DE MOVIMIENTOS", font=("Courier", 16, "bold"), text_color="#1E8449").pack(pady=(30, 10))
            ctk.CTkLabel(self.report_area_prov, text="=" * 80, text_color="black").pack()

            if not desp_todos:
                ctk.CTkLabel(self.report_area_prov, text="Sin movimientos registrados", font=("Courier", 12), text_color="gray").pack(pady=20)
                return

            # Crear tabla de movimientos
            movimientos_frame = ctk.CTkFrame(self.report_area_prov, fg_color="#F8F9FA", corner_radius=10, border_width=1, border_color="#BDC3C7")
            movimientos_frame.pack(fill="both", expand=True, padx=30, pady=15)

            # Encabezados tabla
            encab = ctk.CTkFrame(movimientos_frame, fg_color="#34495E", corner_radius=5)
            encab.pack(fill="x", padx=10, pady=10)
            
            headers = ["FECHA", "TIPO MOVIMIENTO", "CANTIDAD", "ESTADO"]
            anchos_col = [120, 200, 150, 150]
            
            for i, h in enumerate(headers):
                ctk.CTkLabel(encab, text=h, font=("Courier", 11, "bold"), text_color="white", width=anchos_col[i]).pack(side="left", padx=8, pady=8)

            # Filas de movimientos
            for d in desp_todos:
                fila = ctk.CTkFrame(movimientos_frame, fg_color="white", border_width=1, border_color="#E8E8E8")
                fila.pack(fill="x", padx=10, pady=2)
                
                estado_desp = "PENDIENTE" if d['cant_entregada'] < d['cant_despachada'] else "COMPLETADO"
                color_estado = "#E74C3C" if estado_desp == "PENDIENTE" else "#27AE60"
                
                datos = [
                    d['fecha_salida'],
                    "DESPACHO",
                    f"{d['cant_despachada']} und.",
                    estado_desp
                ]
                
                for i, dato in enumerate(datos):
                    color_txt = color_estado if i == 3 else "black"
                    ctk.CTkLabel(fila, text=dato, font=("Courier", 10), text_color=color_txt, width=anchos_col[i]).pack(side="left", padx=8, pady=8)
                
                # Fila de entrega si existe
                if d['cant_entregada'] > 0:
                    fila_entrega = ctk.CTkFrame(movimientos_frame, fg_color="#F0F8F0", border_width=1, border_color="#D5E8D5")
                    fila_entrega.pack(fill="x", padx=(30, 10), pady=2)
                    
                    datos_entrega = [
                        d.get('updated_at', d['fecha_salida'])[:10],
                        "  └─ ENTREGA",
                        f"{d['cant_entregada']} und.",
                        "RECIBIDO"
                    ]
                    
                    for i, dato in enumerate(datos_entrega):
                        ctk.CTkLabel(fila_entrega, text=dato, font=("Courier", 10), text_color="#27AE60", width=anchos_col[i]).pack(side="left", padx=8, pady=6)

            ctk.CTkLabel(self.report_area_prov, text="\n" + "=" * 80, text_color="black").pack()
            ctk.CTkLabel(self.report_area_prov, text="Fin del Informe", font=("Courier", 11), text_color="gray").pack(pady=10)
            
        except Exception as e: messagebox.showerror("Error", str(e))

    def generar_y_enviar_pdf(self):
        data = self.datos_ultimo_reporte
        if not data: return
        try:
            p = data['producto']
            desp_todos = data['despachos']
            
            filename = f"Auditoria_{p['nombre_ref'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # Encabezado
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, 750, "ALUNA - AUDITORÍA DE PROVEEDORES")
            c.setFont("Helvetica", 12)
            c.drawString(50, 730, f"REFERENCIA: {p['nombre_ref'].upper()}")
            c.drawString(50, 710, f"Fecha del Informe: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.setLineWidth(1)
            c.line(50, 705, 550, 705)
            
            # Resumen ejecutivo
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 685, "RESUMEN EJECUTIVO")
            c.setFont("Helvetica", 10)
            
            cant_total = sum([d['cant_despachada'] for d in desp_todos])
            cant_entregada = sum([d['cant_entregada'] for d in desp_todos])
            cant_bodega = p['stock_total']
            cant_calle = p.get('stock_en_calle', 0)
            cant_final = p.get('stock_terminado', 0)
            
            y = 665
            datos_resumen = [
                f"Cargue Inicial: {cant_total} unidades",
                f"En Bodega (Proceso): {cant_bodega} unidades",
                f"En Calle (Despachos): {cant_calle} unidades",
                f"Finalizada (Entregada): {cant_final} unidades",
                f"Total Entregado: {cant_entregada} unidades",
            ]
            
            for dato in datos_resumen:
                c.drawString(60, y, dato)
                y -= 15
            
            # Tabla de movimientos
            y -= 10
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "DETALLE DE MOVIMIENTOS")
            y -= 15
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(60, y, "FECHA")
            c.drawString(130, y, "TIPO MOVIMIENTO")
            c.drawString(270, y, "CANTIDAD")
            c.drawString(380, y, "ESTADO")
            
            y -= 10
            c.setLineWidth(0.5)
            c.line(50, y, 550, y)
            y -= 10
            
            c.setFont("Helvetica", 8)
            for d in desp_todos:
                estado_desp = "PENDIENTE" if d['cant_entregada'] < d['cant_despachada'] else "COMPLETADO"
                
                c.drawString(60, y, d['fecha_salida'])
                c.drawString(130, y, "DESPACHO")
                c.drawString(270, y, f"{d['cant_despachada']} und.")
                c.drawString(380, y, estado_desp)
                y -= 10
                
                if d['cant_entregada'] > 0:
                    entrega_fecha = d.get('updated_at', d['fecha_salida'])[:10]
                    c.drawString(60, y, entrega_fecha)
                    c.drawString(130, y, "└─ ENTREGA")
                    c.drawString(270, y, f"{d['cant_entregada']} und.")
                    c.drawString(380, y, "RECIBIDO")
                    y -= 10
                
                if y < 50:
                    c.showPage()
                    y = 750
            
            c.setLineWidth(0.5)
            c.line(50, y, 550, y)
            y -= 10
            c.setFont("Helvetica", 9)
            c.drawString(50, y, f"Fin del Informe - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.save()

            # Enviar notificación
            asunto = f"Auditoría Generada: {p['nombre_ref']}"
            mensaje = f"""
            <b>Se ha generado el informe de auditoría de proveedores</b><br>
            <b>Referencia:</b> {p['nombre_ref'].upper()}<br>
            <b>Fecha:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <b>Total Cargado:</b> {cant_total} unidades<br>
            <b>Estado General:</b> {cant_bodega} en bodega, {cant_calle} en calle, {cant_final} finalizada<br>
            <b>Total Entregado:</b> {cant_entregada} unidades<br>
            <br>El archivo PDF ha sido generado: {filename}
            """
            enviar_notificacion_async(asunto, mensaje)
            messagebox.showinfo("Éxito", f"Informe generado exitosamente.\nArchivo: {filename}")
        except Exception as e: messagebox.showerror("Error PDF", str(e))

    # --- MÉTODOS APOYO ---
    def create_filter_header(self, titulo, add_command):
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header, text=titulo, font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")
        f_frame = ctk.CTkFrame(header, fg_color="transparent")
        f_frame.pack(side="left", padx=60)
        self.btn_filtro_monos = ctk.CTkButton(f_frame, text="MOÑOS", width=120, height=35, command=lambda: self.update_global_filter("mono"))
        self.btn_filtro_monos.pack(side="left", padx=10)
        self.btn_filtro_bisuteria = ctk.CTkButton(f_frame, text="BISUTERÍA", width=120, height=35, command=lambda: self.update_global_filter("bisuteria"))
        self.btn_filtro_bisuteria.pack(side="left", padx=10)
        self.actualizar_colores_categoria()
        if add_command: ctk.CTkButton(header, text="+ NUEVO", width=140, height=35, fg_color="#2980b9", command=add_command).pack(side="right")

    def _actualizar_estado_botones_categoria(self, btn_monos, btn_bisuteria):
        if btn_monos and btn_monos.winfo_exists():
            btn_monos.configure(fg_color=self.color_filtro_mono if self.filtro_actual == "mono" else self.color_inactivo)
        if btn_bisuteria and btn_bisuteria.winfo_exists():
            btn_bisuteria.configure(fg_color=self.color_filtro_bisuteria if self.filtro_actual == "bisuteria" else self.color_inactivo)

    def actualizar_colores_categoria(self):
        self._actualizar_estado_botones_categoria(
            getattr(self, 'btn_filtro_monos', None),
            getattr(self, 'btn_filtro_bisuteria', None),
        )
        self._actualizar_estado_botones_categoria(
            getattr(self, 'btn_reportes_monos', None),
            getattr(self, 'btn_reportes_bisuteria', None),
        )

    def abrir_dialogo_despacho(self):
        if not self.filtro_actual:
            messagebox.showinfo("Categoría requerida", "Primero selecciona MOÑOS o BISUTERÍA para registrar un despacho.")
            return
        DespachoDialog(self, self.filtro_actual, self.load_despachos_from_db)

    def mostrar_mensaje_espera(self, titulo, detalle):
        if hasattr(self, 'mensaje_espera') and self.mensaje_espera.winfo_exists():
            self.mensaje_espera.destroy()

        self.mensaje_espera = ctk.CTkFrame(self.main_content, fg_color="#1F2933", corner_radius=10)
        self.mensaje_espera.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(self.mensaje_espera, text=titulo, font=ctk.CTkFont(size=16, weight="bold"), text_color="#F7DC6F").pack(pady=(10, 2))
        ctk.CTkLabel(self.mensaje_espera, text=detalle, font=ctk.CTkFont(size=13), text_color="#D5DBDB").pack(pady=(0, 10))

    def ocultar_mensaje_espera(self):
        if hasattr(self, 'mensaje_espera') and self.mensaje_espera.winfo_exists():
            self.mensaje_espera.destroy()

    def update_global_filter(self, cat):
        self.filtro_actual = cat
        self.actualizar_colores_categoria()
        if self.current_tab == "usuarios": self.load_users_from_db()
        elif self.current_tab == "inventario": self.load_inventory_from_db()
        elif self.current_tab == "despachos": self.load_despachos_from_db()

    def load_users_from_db(self):
        if not self.filtro_actual:
            return
        self.ocultar_mensaje_espera()
        res = supabase.table("usuarios").select("*").eq("rol_trabajo", self.filtro_actual).order("nombre_full").execute()
        self.user_table.update_data(res.data)

    def load_inventory_from_db(self):
        if not self.filtro_actual:
            return
        self.ocultar_mensaje_espera()
        res = supabase.table("productos").select("*").eq("categoria", self.filtro_actual).order("nombre_ref").execute()
        search_text = self.inv_search_entry.get().strip().lower() if hasattr(self, 'inv_search_entry') else ""
        if search_text:
            filtered_data = [p for p in res.data if search_text in p['nombre_ref'].lower()]
        else:
            filtered_data = res.data
        self.inv_table.update_data(filtered_data)

    def load_despachos_from_db(self):
        if not self.filtro_actual:
            return
        self.ocultar_mensaje_espera()
        res = supabase.table("despachos").select("*, usuarios(*), productos(*)").order("fecha_salida", desc=True).execute()
        filtered = [d for d in res.data if d['productos']['categoria'] == self.filtro_actual]
        
        search_text = self.desp_search_entry.get().strip().lower() if hasattr(self, 'desp_search_entry') else ""
        if search_text:
            filtered = [d for d in filtered if search_text in d['productos']['nombre_ref'].lower() or search_text in d['usuarios']['nombre_full'].lower()]

        pendientes = [d for d in filtered if d.get('estado') != 'completado']
        finalizados = [d for d in filtered if d.get('estado') == 'completado']

        pendientes.sort(key=lambda x: x.get('updated_at', x.get('fecha_salida', '')), reverse=True)
        finalizados.sort(key=lambda x: x.get('updated_at', x.get('fecha_salida', '')), reverse=True)
        filtered = pendientes + finalizados
        
        self.despacho_table.update_data(filtered)

    def _debounce_inv_search(self):
        """Debounce para búsqueda de inventario - espera 300ms antes de ejecutar"""
        if self.inv_search_timer:
            self.after_cancel(self.inv_search_timer)
        self.inv_search_timer = self.after(300, self.load_inventory_from_db)

    def _debounce_desp_search(self):
        """Debounce para búsqueda de despachos - espera 300ms antes de ejecutar"""
        if self.desp_search_timer:
            self.after_cancel(self.desp_search_timer)
        self.desp_search_timer = self.after(300, self.load_despachos_from_db)


if __name__ == "__main__":
    app = AlunaApp()
    app.mainloop()