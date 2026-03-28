import streamlit as st
import pandas as pd
from datetime import datetime

def render(supabase):
    st.title("Pagos")
    st.markdown("---")

    # ── Tabla de empleados ────────────────────────────────────────────────
    with st.expander("👥 Ver empleados", expanded=True):
        try:
            emps = supabase.table("EMPLEADO").select("id, nombre, pago_hora, activo").execute()
            if emps.data:
                df = pd.DataFrame(emps.data)
                df.columns = ["ID", "Nombre", "Pago/hora", "Activo"]
                df["Activo"] = df["Activo"].map({True: "✅", False: "❌"})
                df["Pago/hora"] = df["Pago/hora"].apply(lambda x: f"${x:.2f}")
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error cargando empleados: {e}")

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["CALCULAR PAGO", "HISTORIAL"])

    with tab1:
        with st.form("form_pago"):
            emp_id = st.number_input("ID del empleado", min_value=1, step=1)
            submit = st.form_submit_button("CALCULAR")

        if submit:
            try:
                empleado = supabase.table("EMPLEADO").select("*").eq("id", emp_id).execute()
                if not empleado.data:
                    st.error("❌ Empleado no encontrado.")
                else:
                    emp       = empleado.data[0]
                    pago_hora = emp["pago_hora"]

                    ultimo_pago = supabase.table("PAGO").select("fecha_hasta")\
                        .eq("empleado_id", emp_id).order("fecha_hasta", desc=True).limit(1).execute()
                    desde = ultimo_pago.data[0]["fecha_hasta"] if ultimo_pago.data else "1970-01-01T00:00:00"

                    asistencias = supabase.table("ASISTENCIA").select("*")\
                        .eq("empleado_id", emp_id)\
                        .eq("estado", "completo")\
                        .gte("hora", desde)\
                        .order("hora").execute()

                    marcas        = asistencias.data
                    pares         = len(marcas) // 2
                    total_minutos = 0
                    desglose = []  # Lista para el desglose por día

                    for i in range(pares):
                        entrada = datetime.fromisoformat(marcas[i * 2]["hora"].replace("Z", "+00:00"))
                        salida  = datetime.fromisoformat(marcas[i * 2 + 1]["hora"].replace("Z", "+00:00"))
                        minutos = (salida - entrada).total_seconds() / 60  # ← guardar en variable
                        total_minutos += minutos
                        
                        desglose.append({
                            "Fecha":   entrada.strftime("%d/%m/%Y"),
                            "Entrada": entrada.strftime("%H:%M"),
                            "Salida":  salida.strftime("%H:%M"),
                            "Horas":   f"{minutos / 60:.2f} hrs",
                            "Pago día": f"${(minutos / 60) * pago_hora:.2f}"
                        })

                    total_horas = total_minutos / 60
                    total_pago  = total_horas * pago_hora

                    st.session_state["pago_calculado"] = {
                        "emp_id":      emp_id,
                        "nombre":      emp["nombre"],
                        "pago_hora":   pago_hora,
                        "total_horas": total_horas,
                        "total_pago":  total_pago,
                        "desde":       desde,
                        "desglose":    desglose  # Agregar desglose por día
                    }
            except Exception as e:
                st.error(f"❌ Error: {e}")

        if "pago_calculado" in st.session_state:
            p = st.session_state["pago_calculado"]
            st.markdown(f"### Empleado: {p['nombre']}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Horas trabajadas", f"{p['total_horas']:.2f} hrs")
            col2.metric("Pago por hora",    f"${p['pago_hora']:.2f}")
            col3.metric("Total a pagar",    f"${p['total_pago']:.2f}")
            st.markdown("---")
            st.subheader("Desglose por día")
            if p["desglose"]:
                df = pd.DataFrame(p["desglose"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay días trabajados en este período.")

            st.markdown("---")
            if st.button("REGISTRAR PAGO"):
                try:
                    supabase.table("PAGO").insert({
                        "empleado_id":   p["emp_id"],
                        "horas_totales": p["total_horas"],
                        "pago_total":    p["total_pago"],
                        "fecha_desde":   p["desde"],
                        "fecha_hasta":   datetime.now().isoformat(),
                        "timestampz":    datetime.now().isoformat()
                    }).execute()
                    st.success(f"✅ Pago de ${p['total_pago']:.2f} registrado.")
                    del st.session_state["pago_calculado"]
                except Exception as e:
                    st.error(f"❌ Error al registrar pago: {e}")

    with tab2:
        try:
            data = supabase.table("PAGO").select("*").order("timestampz", desc=True).execute()
            if data.data:
                st.dataframe(data.data, use_container_width=True)
            else:
                st.info("No hay pagos registrados.")
        except Exception as e:
            st.error(f"Error: {e}")