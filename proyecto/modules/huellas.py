import streamlit as st
from datetime import datetime

def render(supabase):
    st.title("🫆 Huellas Dactilares")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Ver Huellas", "➕ Registrar / Reemplazar"])

    # =====================
    #   TAB 1 — VER HUELLAS
    # =====================
    with tab1:
        try:
            data = supabase.table("REGISTRO_HUELLA") \
                .select("id, timestamp, EMPLEADO(id, nombre)") \
                .execute()

            if not data.data:
                st.info("No hay huellas registradas.")
            else:
                # Formatear para mostrar
                rows = []
                for r in data.data:
                    emp = r.get("EMPLEADO") or {}
                    rows.append({
                        "Slot (ID Huella)": r["id"],
                        "Empleado":         emp.get("nombre", "—"),
                        "ID Empleado":      emp.get("id", "—"),
                        "Registrada":       formatear_fecha(r["timestamp"]) if r.get("timestamp") else "—",
                    })

                st.dataframe(rows, use_container_width=True)
                st.caption(f"{len(rows)} huella(s) registrada(s)")

        except Exception as e:
            st.error(f"Error al cargar huellas: {e}")

    # =====================
    #   TAB 2 — REGISTRAR
    # =====================
    with tab2:

        # Tabla de empleados como referencia
        with st.expander("👥 Ver empleados disponibles", expanded=False):
            try:
                empleados = supabase.table("EMPLEADO") \
                    .select("id, nombre") \
                    .eq("activo", True) \
                    .order("id") \
                    .execute()
                if empleados.data:
                    st.dataframe(empleados.data, use_container_width=True)
                else:
                    st.info("No hay empleados activos.")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            emp_id = st.number_input("ID del empleado", min_value=1, step=1)
        with col2:
            slot = st.number_input("Slot en sensor (1-162)", min_value=1, max_value=162, step=1)

        # Verificar si ya tiene huella registrada
        huella_existente = None
        if emp_id:
            try:
                existe = supabase.table("REGISTRO_HUELLA") \
                    .select("id, EMPLEADO(nombre)") \
                    .eq("empleado_id", emp_id) \
                    .execute()
                if existe.data:
                    huella_existente = existe.data[0]
            except:
                pass

        # Mostrar advertencia si ya tiene huella
        if huella_existente:
            nombre_emp = (huella_existente.get("EMPLEADO") or {}).get("nombre", "—")
            st.warning(
                f"⚠️ **{nombre_emp}** ya tiene una huella registrada en el slot **{huella_existente['id']}**. "
                f"Si continúas se reemplazará."
            )
            boton_label = "🔄 Reemplazar huella"
        else:
            boton_label = "💾 Registrar huella"

        st.markdown(" ")

        # Instrucciones
        with st.expander("ℹ️ ¿Cómo registrar una huella?", expanded=False):
            st.markdown("""
            1. Anota el **ID del empleado** de la tabla de arriba
            2. Elige un **slot libre** entre 1 y 162
            3. Haz clic en **Registrar huella**
            4. Ve al sensor físico y sigue las instrucciones en la pantalla
            5. El sensor pedirá el mismo dedo **dos veces**
            """)

        if st.button(boton_label, type="primary", use_container_width=True):
            # Validar que el empleado existe
            try:
                emp_check = supabase.table("EMPLEADO") \
                    .select("nombre") \
                    .eq("id", emp_id) \
                    .execute()
                if not emp_check.data:
                    st.error(f"❌ No existe un empleado con ID {emp_id}.")
                    return
                nombre = emp_check.data[0]["nombre"]
            except Exception as e:
                st.error(f"Error al verificar empleado: {e}")
                return

            # Verificar que el slot no esté ocupado por otro empleado
            try:
                slot_ocupado = supabase.table("REGISTRO_HUELLA") \
                    .select("empleado_id, EMPLEADO(nombre)") \
                    .eq("id", slot) \
                    .execute()
                if slot_ocupado.data:
                    otro = (slot_ocupado.data[0].get("EMPLEADO") or {}).get("nombre", "—")
                    otro_id = slot_ocupado.data[0]["empleado_id"]
                    if otro_id != emp_id:
                        st.error(f"❌ El slot {slot} ya está ocupado por **{otro}**. Elige otro slot.")
                        return
            except Exception as e:
                st.error(f"Error al verificar slot: {e}")
                return

            # Guardar
            try:
                # Borrar huella anterior si existe
                supabase.table("REGISTRO_HUELLA") \
                    .delete() \
                    .eq("empleado_id", emp_id) \
                    .execute()

                # Insertar nueva
                supabase.table("REGISTRO_HUELLA").insert({
                    "id":          slot,
                    "empleado_id": emp_id,
                    "timestamp":   datetime.now().isoformat()
                }).execute()

                if huella_existente:
                    st.success(f"✅ Huella de **{nombre}** reemplazada en slot {slot}.")
                else:
                    st.success(f"✅ Huella de **{nombre}** registrada en slot {slot}.")

                st.info("📡 Ahora ve al sensor físico y enrolla la huella en ese slot.")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")


def formatear_fecha(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return iso_str