import streamlit as st
import pandas as pd
from datetime import datetime
from itertools import groupby

def formatear_fecha(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return iso_str

def render(supabase):

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
        <h1 style='font-size:2rem; margin-bottom:0'>🖐️ CHECADOR</h1>
        <p style='color:#666; margin-top:4px'>Panel de control · <span id='fecha'></span></p>
        <script>document.getElementById('fecha').innerText = new Date().toLocaleDateString('es-MX', {weekday:'long',year:'numeric',month:'long',day:'numeric'});</script>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Métricas ──────────────────────────────────────────────────────────
    try:
        empleados  = supabase.table("EMPLEADO").select("id", count="exact").execute()
        activos    = supabase.table("EMPLEADO").select("id", count="exact").eq("activo", True).execute()
        huellas    = supabase.table("REGISTRO_HUELLA").select("id", count="exact").execute()
        pendientes = supabase.table("ASISTENCIA").select("id", count="exact").eq("estado", "pendiente").execute()
        hoy        = supabase.table("ASISTENCIA").select("id", count="exact")\
                        .gte("hora", datetime.now().strftime("%Y-%m-%d"))\
                        .eq("tipo", "entrada").execute()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("👥 Empleados",        empleados.count)
        col2.metric("✅ Activos",           activos.count)
        col3.metric("🖐️ Huellas",          huellas.count)
        col4.metric("📍 Entradas hoy",      hoy.count)
        col5.metric("⚠️ Pendientes",        pendientes.count,
                    delta=f"-{pendientes.count} sin salida" if pendientes.count > 0 else None,
                    delta_color="inverse")
    except Exception as e:
        st.error(f"Error cargando métricas: {e}")

    st.markdown("---")

    # ── Dos columnas: asistencia hoy + pares del día ──────────────────────
    col_izq, col_der = st.columns([1.2, 1.8])

    with col_izq:
        st.markdown("### 📋 Actividad de hoy")
        try:
            hoy_data = supabase.table("ASISTENCIA")\
                .select("hora, tipo, EMPLEADO(nombre)")\
                .gte("hora", datetime.now().strftime("%Y-%m-%d"))\
                .order("hora", desc=True).execute()

            if hoy_data.data:
                for r in hoy_data.data:
                    nombre = r["EMPLEADO"]["nombre"] if isinstance(r.get("EMPLEADO"), dict) else "—"
                    hora   = datetime.fromisoformat(r["hora"].replace("Z", "+00:00")).strftime("%H:%M")
                    icono  = "🟢" if r["tipo"] == "entrada" else "🔴"
                    st.markdown(
                        f"<div style='padding:8px 12px; margin:4px 0; background:#1a1a1a; border-radius:6px; border-left: 3px solid {'#00ff99' if r['tipo'] == 'entrada' else '#ff4444'}'>"
                        f"<span style='color:#888; font-size:0.8rem'>{hora}</span>&nbsp;&nbsp;"
                        f"{icono} <strong>{nombre}</strong>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("Sin actividad hoy.")
        except Exception as e:
            st.error(f"Error: {e}")

    with col_der:
        st.markdown("### 🗂️ Pares de hoy")
        try:
            pares_data = supabase.table("ASISTENCIA")\
                .select("hora, tipo, empleado_id, EMPLEADO(nombre)")\
                .gte("hora", datetime.now().strftime("%Y-%m-%d"))\
                .order("empleado_id").order("hora").execute()

            if pares_data.data:
                registros = sorted(pares_data.data, key=lambda x: (x["empleado_id"], x["hora"]))
                filas = []

                for emp_id_key, grupo in groupby(registros, key=lambda x: x["empleado_id"]):
                    grupo  = list(grupo)
                    nombre = grupo[0]["EMPLEADO"]["nombre"] if isinstance(grupo[0].get("EMPLEADO"), dict) else "—"
                    entradas = [r for r in grupo if r["tipo"] == "entrada"]
                    salidas  = [r for r in grupo if r["tipo"] == "salida"]

                    for i, entrada in enumerate(entradas):
                        entrada_dt  = datetime.fromisoformat(entrada["hora"].replace("Z", "+00:00"))
                        tiene_salida = i < len(salidas)

                        if tiene_salida:
                            salida_dt = datetime.fromisoformat(salidas[i]["hora"].replace("Z", "+00:00"))
                            minutos   = (salida_dt - entrada_dt).total_seconds() / 60
                            filas.append({
                                "Empleado": nombre,
                                "Par":      f"#{i+1}",
                                "Entrada":  entrada_dt.strftime("%H:%M"),
                                "Salida":   salida_dt.strftime("%H:%M"),
                                "Horas":    f"{minutos/60:.2f}h",
                                "Estado":   "✅"
                            })
                        else:
                            filas.append({
                                "Empleado": nombre,
                                "Par":      f"#{i+1}",
                                "Entrada":  entrada_dt.strftime("%H:%M"),
                                "Salida":   "—",
                                "Horas":    "—",
                                "Estado":   "⏳"
                            })

                if filas:
                    df = pd.DataFrame(filas)

                    def colorear(row):
                        if row["Estado"] == "✅":
                            color = "background-color: #0d2b1f"
                        else:
                            color = "background-color: #2b240d"
                        return [color] * len(row)

                    st.dataframe(
                        df.style.apply(colorear, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Sin pares registrados hoy.")
            else:
                st.info("Sin asistencias hoy.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")

    # ── Últimos 10 registros globales ─────────────────────────────────────
    st.markdown("### 🕐 Últimos registros")
    try:
        data = supabase.table("ASISTENCIA")\
            .select("hora, tipo, estado, EMPLEADO(nombre)")\
            .order("hora", desc=True).limit(10).execute()

        if data.data:
            df = pd.DataFrame(data.data)
            df["nombre"] = df["EMPLEADO"].apply(lambda x: x["nombre"] if isinstance(x, dict) else "—")
            df["hora"]   = df["hora"].apply(formatear_fecha)
            df["tipo"]   = df["tipo"].apply(lambda x: "🟢 Entrada" if x == "entrada" else "🔴 Salida")
            df["estado"] = df["estado"].apply(lambda x: "✅ Completo" if x == "completo" else "⏳ Pendiente")
            df = df.drop(columns=["EMPLEADO"])
            df = df.rename(columns={
                "nombre": "Empleado",
                "hora":   "Fecha y hora",
                "tipo":   "Tipo",
                "estado": "Estado"
            })
            st.dataframe(df[["Empleado", "Fecha y hora", "Tipo", "Estado"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No hay asistencias registradas.")
    except Exception as e:
        st.error(f"Error: {e}")