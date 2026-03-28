from supabase import create_client
from datetime import datetime

url = "https://wbppynaecoeesmmtlpdh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndicHB5bmFlY29lZXNtbXRscGRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxMjM3NDIsImV4cCI6MjA4ODY5OTc0Mn0.X_kpjY1WcN_p8py6y98pwoxM1qDCvds8hI5lq14fWMI"

supabase = create_client(url, key)

def listar_empleados():
    try:
        data = supabase.table("EMPLEADO").select("*").execute()
        for emp in data.data:
            print(emp)
    except Exception as e:
        print(f"❌ Error: {e}")