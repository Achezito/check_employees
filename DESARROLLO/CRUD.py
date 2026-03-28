from supabase import create_client
from datetime import datetime
from DESARROLLO.LISTAR import listar_empleados

url = "https://wbppynaecoeesmmtlpdh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndicHB5bmFlY29lZXNtbXRscGRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxMjM3NDIsImV4cCI6MjA4ODY5OTc0Mn0.X_kpjY1WcN_p8py6y98pwoxM1qDCvds8hI5lq14fWMI"

supabase = create_client(url, key)



while True:
    print("\n¿Qué quieres testear?")
    print("1 - Insertar empleado")
    print("2 - Listar empleados")
    print("3 - Registrar huella")
    print("4 - Ver registros de huella")
    print("5 - Ingresar asistencia")
    print("0 - Salir")

    opcion = input("Elige una opción: ")

    if opcion == "0":
        print("👋 Saliendo...")
        break

    # --- 1. INSERTAR EMPLEADO ---
    elif opcion == "1":
        while True:
            emp_id = int(input("ID del empleado: "))
            nombre = input("Nombre: ")
            pago   = float(input("Pago por hora: "))
            activo = input("¿Activo? (s/n): ").lower() == "s"
            try:
                supabase.table("EMPLEADO").insert({
                    "id": emp_id,
                    "nombre": nombre,
                    "pago_hora": pago,
                    "activo": activo,
                    "timestamp": datetime.now().isoformat()
                }).execute()
                print("✅ Empleado insertado.")
            except Exception as e:
                print(f"❌ Error: {e}")

            otro = input("¿Agregar otro empleado? (s/n): ")
            if otro.lower() == "n":
                break  # Vuelve al menú principal

    # --- 2. LISTAR EMPLEADOS ---
    elif opcion == "2":
        listar_empleados()

    # --- 3. REGISTRAR HUELLA ---
    elif opcion == "3":
        listar_empleados()
        
        huella_id = int(input("ID del registro de huella: "))   
        emp_id = int(input("ID del empleado a registrar huella: "))
        try:
            supabase.table("REGISTRO_HUELLA").insert({
                "id": huella_id,
                "empleado_id": emp_id,
                "timestamp": datetime.now().isoformat()
            }).execute()
            print("✅ Huella registrada.")
        except Exception as e:
            print(f"❌ Error: {e}")

    # --- 4. VER REGISTROS DE HUELLA ---
    elif opcion == "4":
        try:
            data = supabase.table("REGISTRO_HUELLA").select("*").execute()
            for reg in data.data:
                print(reg)
        except Exception as e:
            print(f"❌ Error: {e}")
    elif opcion == "5":
        listar_empleados()
    while True:
        emp_id = int(input("ID del empleado para ingresar asistencia: "))
        try:
            supabase.table("ASISTENCIA").insert({
                "empleado_id": emp_id,
                "hora": datetime.now().isoformat()
            }).execute()
            print("✅ Asistencia ingresada.")
        except Exception as e:
            print(f"❌ Error: {e}")
        otro = input("¿Ingresar asistencia para otro empleado? (s/n): ")
        if otro.lower() == "n":
            break  # Vuelve al menú principal
