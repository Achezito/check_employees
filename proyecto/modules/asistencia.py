import streamlit as st
import pandas as pd
from datetime import datetime

def formatear_fecha(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return iso_str

def render(supabase):
    st.title("Asistencia")
    st.markdown("---")

    tab2, tab3 = st.tabs(["VER ASISTENCIA", "PENDIENTES"])

    # ── Tab 2 — Ver Asistencia por pares ──────────────────────────────────
    with tab2:
        col1, col2, _ = st.columns([1, 1, 2])
        with col1:
            filtro_emp = st.number_input("Empleado (0 = todos)", min_value=0, step=1)
        with col2:
            filtro_estado = st.selectbox("Estado", ["Todos", "✅ Completos", "⏳ Incompletos"])

        try:
            query = supabase.table("ASISTENCIA")\
                .select("id, hora, tipo, estado, empleado_id, EMPLEADO(nombre)")\
                .order("empleado_id")\
                .order("hora")

            if filtro_emp > 0:
                query = query.eq("empleado_id", filtro_emp)

            data = query.execute()

            if not data.data:
                st.info("No hay registros.")
            else:
                from itertools import groupby
                registros = sorted(data.data, key=lambda x: (x["empleado_id"], x["hora"]))
                dias = []

                for emp_id_key, grupo in groupby(registros, key=lambda x: x["empleado_id"]):
                    grupo  = list(grupo)
                    nombre = grupo[0]["EMPLEADO"]["nombre"] if isinstance(grupo[0].get("EMPLEADO"), dict) else "—"

                    por_fecha = {}
                    for r in grupo:
                        fecha = datetime.fromisoformat(r["hora"].replace("Z", "+00:00")).strftime("%d/%m/%Y")
                        por_fecha.setdefault(fecha, []).append(r)

                    for fecha, registros_dia in por_fecha.items():
                        entradas = [r for r in registros_dia if r["tipo"] == "entrada"]
                        salidas  = [r for r in registros_dia if r["tipo"] == "salida"]
                        total_pares = max(len(entradas), len(salidas))

                        for i in range(total_pares):
                            tiene_entrada = i < len(entradas)
                            tiene_salida  = i < len(salidas)

                            entrada_str = "—"
                            salida_str  = "—"
                            horas_str   = "—"
                            estado      = "⏳ Incompleto"

                            if tiene_entrada:
                                entrada_dt  = datetime.fromisoformat(entradas[i]["hora"].replace("Z", "+00:00"))
                                entrada_str = entrada_dt.strftime("%H:%M")

                            if tiene_salida:
                                salida_dt  = datetime.fromisoformat(salidas[i]["hora"].replace("Z", "+00:00"))
                                salida_str = salida_dt.strftime("%H:%M")

                            if tiene_entrada and tiene_salida:
                                minutos   = (salida_dt - entrada_dt).total_seconds() / 60
                                horas_str = f"{minutos / 60:.2f} hrs"
                                estado    = "✅ Completo"

                            dias.append({
                                "Empleado": nombre,
                                "Fecha":    fecha,
                                "Par #":    f"#{i + 1}",
                                "Entrada":  entrada_str,
                                "Salida":   salida_str,
                                "Horas":    horas_str,
                                "Estado":   estado
                            })

                df = pd.DataFrame(dias)

                if filtro_estado == "✅ Completos":
                    df = df[df["Estado"] == "✅ Completo"]
                elif filtro_estado == "⏳ Incompletos":
                    df = df[df["Estado"] == "⏳ Incompleto"]

                if df.empty:
                    st.info("No hay registros con ese filtro.")
                else:
                    def colorear_par(row):
                        color = "background-color: #1a2a1a" if row["Par #"] == "#1" else "background-color: #1a1a2a"
                        return [color] * len(row)

                    st.dataframe(
                        df.style.apply(colorear_par, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption(f"{len(df)} pares encontrados")

        except Exception as e:
            st.error(f"Error: {e}")

    # ── Tab 3 — Pendientes ─────────────────────────────────────────────────
    with tab3:
        try:
            pendientes = supabase.table("ASISTENCIA")\
                .select("id, hora, empleado_id, EMPLEADO(nombre)")\
                .eq("estado", "pendiente")\
                .order("hora", desc=True)\
                .execute()

            if not pendientes.data:
                st.success("✅ No hay entradas pendientes.")
            else:
                st.markdown(f"### ⏳ {len(pendientes.data)} entrada(s) sin salida")
                st.caption("Estos empleados marcaron entrada pero no han registrado salida.")
                st.markdown("---")

                for reg in pendientes.data:
                    nombre   = (reg.get("EMPLEADO") or {}).get("nombre", "Desconocido")
                    hora_fmt = formatear_fecha(reg["hora"])
                    reg_id   = reg["id"]

                    with st.container():
                        col_info, col_salida, col_eliminar = st.columns([3, 1.5, 1.5])

                        with col_info:
                            st.markdown(f"**👤 {nombre}**")
                            st.caption(f"Entrada: {hora_fmt}  •  ID registro: {reg_id}")

                        with col_salida:
                            if st.button("✅ Registrar salida", key=f"salida_{reg_id}", use_container_width=True):
                                st.session_state[f"confirmar_salida_{reg_id}"] = True

                        with col_eliminar:
                            if st.button("🗑️ Eliminar", key=f"eliminar_{reg_id}", use_container_width=True):
                                st.session_state[f"confirmar_eliminar_{reg_id}"] = True

                        # Confirmación salida
                        if st.session_state.get(f"confirmar_salida_{reg_id}"):
                            st.warning(f"¿Registrar salida manual para **{nombre}**?")
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("Sí, registrar", key=f"si_salida_{reg_id}", use_container_width=True, type="primary"):
                                    try:
                                        supabase.table("ASISTENCIA").update({
                                            "tipo":   "salida",
                                            "estado": "completo"
                                        }).eq("id", reg_id).execute()
                                        st.success(f"✅ Salida registrada para {nombre}.")
                                        del st.session_state[f"confirmar_salida_{reg_id}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
                            with c2:
                                if st.button("Cancelar", key=f"no_salida_{reg_id}", use_container_width=True):
                                    del st.session_state[f"confirmar_salida_{reg_id}"]
                                    st.rerun()

                        # Confirmación eliminar
                        if st.session_state.get(f"confirmar_eliminar_{reg_id}"):
                            st.error(f"¿Eliminar el registro de entrada de **{nombre}** del {hora_fmt}? Esto no se puede deshacer.")
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("Sí, eliminar", key=f"si_elim_{reg_id}", use_container_width=True, type="primary"):
                                    try:
                                        supabase.table("ASISTENCIA").delete().eq("id", reg_id).execute()
                                        st.success("✅ Registro eliminado.")
                                        del st.session_state[f"confirmar_eliminar_{reg_id}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
                            with c2:
                                if st.button("Cancelar", key=f"no_elim_{reg_id}", use_container_width=True):
                                    del st.session_state[f"confirmar_eliminar_{reg_id}"]
                                    st.rerun()

                        st.markdown("---")

        except Exception as e:
            st.error(f"Error: {e}")