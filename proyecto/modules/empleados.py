import streamlit as st
from datetime import datetime

def render(supabase):
    st.title("Empleados")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["LISTAR", "INSERTAR", "EDITAR / ELIMINAR"])

    with tab1:
        try:
            data = supabase.table("EMPLEADO").select("*").execute()
            if data.data:
                st.dataframe(data.data, use_container_width=True)
            else:
                st.info("No hay empleados registrados.")
        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        with st.form("form_insertar_empleado"):
            emp_id = st.number_input("ID", min_value=1, step=1)
            nombre = st.text_input("Nombre")
            pago   = st.number_input("Pago por hora", min_value=0.0, step=0.5)
            activo = st.checkbox("Activo", value=True)
            submit = st.form_submit_button("INSERTAR")

        if submit:
            if not nombre:
                st.error("El nombre es obligatorio.")
            else:
                try:
                    supabase.table("EMPLEADO").insert({
                        "id":        emp_id,
                        "nombre":    nombre,
                        "pago_hora": pago,
                        "activo":    activo,
                        "timestamp": datetime.now().isoformat()
                    }).execute()
                    st.success(f"✅ Empleado '{nombre}' insertado.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Editar pago/hora")
            with st.form("form_editar"):
                edit_id    = st.number_input("ID del empleado", min_value=1, step=1, key="edit_id")
                nuevo_pago = st.number_input("Nuevo pago por hora", min_value=0.0, step=0.5)
                edit_submit = st.form_submit_button("ACTUALIZAR")
            if edit_submit:
                try:
                    supabase.table("EMPLEADO").update({"pago_hora": nuevo_pago}).eq("id", edit_id).execute()
                    st.success("✅ Pago actualizado.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        with col2:
            st.subheader("Eliminar empleado")
            with st.form("form_eliminar"):
                del_id    = st.number_input("ID del empleado", min_value=1, step=1, key="del_id")
                confirmar = st.checkbox("Confirmo que quiero eliminar este empleado")
                del_submit = st.form_submit_button("ELIMINAR")
            if del_submit:
                if not confirmar:
                    st.warning("⚠️ Debes confirmar antes de eliminar.")
                else:
                    try:
                        supabase.table("EMPLEADO").delete().eq("id", del_id).execute()
                        st.success("✅ Empleado eliminado.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
