import streamlit as st
import boto3
import json
import random
import os
import time

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CORPORATIVOS
st.set_page_config(page_title="Florida Drive Academy", page_icon="🚗", layout="wide")

# Estilos CSS personalizados para la interfaz comercial (Paleta de Florida)
st.markdown("""
<style>
    .stButton>button { background-color: #002f6c; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #ffc72c; color: #002f6c; }
    .auth-box { background-color: #f8f9fa; padding: 30px; border-radius: 12px; border: 1px solid #dee2e6; }
</style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN AL MOTOR DE BASE DE DATOS DYNAMODB EN DOCKER
@st.cache_resource
def conectar_dynamodb():
    endpoint_url = os.environ.get('DYNAMODB_URL', 'http://localhost:8000')
    session = boto3.Session(
        aws_access_key_id='mockkey2026',
        aws_secret_access_key='mockkey2026',
        region_name='us-east-1'
    )
    return session.resource('dynamodb', endpoint_url=endpoint_url)

db = conectar_dynamodb()
tabla_preguntas = db.Table('FloridaDrive_Preguntas')

# 3. INICIALIZACIÓN DE VARIABLES DE SESIÓN (SESSION STATE)
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None  # 'admin' o 'client'
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"  # Login, Register, OTP

# Base de datos local simulada con contraseñas seguras para desarrollo
if "mock_users_db" not in st.session_state:
    st.session_state.mock_users_db = {
        "admin@floridadrive.com": {"password": "admin123", "role": "admin", "verified": True},
        "gabrielmorenovargas@gmail.com": {"password": "GabuchoMoreno35", "role": "client", "verified": True}
    }

if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "pending_user_data" not in st.session_state:
    st.session_state.pending_user_data = {}

# Estados de progreso del simulador de examen
if "indice_global" not in st.session_state: st.session_state.indice_global = 0
if "volteada" not in st.session_state: st.session_state.volteada = False
if "respuesta_seleccionada" not in st.session_state: st.session_state.respuesta_seleccionada = None
if "set_completado" not in st.session_state: st.session_state.set_completado = False
if "total_correctas" not in st.session_state: st.session_state.total_correctas = 0
if "total_incorrectas" not in st.session_state: st.session_state.total_incorrectas = 0

def obtener_preguntas_nosql():
    try:
        response = tabla_preguntas.scan()
        # Ordenar las preguntas por su ID para mantener la secuencia del 1 al 60
        items = response.get('Items', [])
        return sorted(items, key=lambda x: int(x['id']))
    except Exception:
        return []

banco_preguntas = obtener_preguntas_nosql()
TAMANO_SET = 5
# --- CAPA A: FLUJO DE AUTENTICACIÓN Y GESTIÓN DE USUARIOS ---
if not st.session_state.user_authenticated:
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    
    with col2:
        st.write("")
        st.image("https://wikimedia.org", width=100)
        st.title("☀️ Portal Florida Drive")
        st.caption("Validación de Identidad y Control de Accesos Comercial")
        st.markdown("---")
        
        # A1. INTERFAZ DE INICIO DE SESIÓN
        if st.session_state.auth_mode == "Login":
            st.subheader("Iniciar Sesión")
            email_input = st.text_input("Correo Electrónico", key="login_email").strip()
            pass_input = st.text_input("Contraseña", type="password", key="login_pass").strip()
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Ingresar al Portal", use_container_width=True):
                    if not email_input or not pass_input:
                        st.error("Por favor ingresa tus datos y presiona Enter antes de continuar.")
                    elif email_input in st.session_state.mock_users_db:
                        user = st.session_state.mock_users_db[email_input]
                        if user["password"] == pass_input:
                            st.session_state.user_authenticated = True
                            st.session_state.user_role = user["role"]
                            st.session_state.user_email = email_input
                            st.success("Acceso autorizado con éxito.")
                            st.rerun()
                        else:
                            st.error("Contraseña incorrecta.")
                    else:
                        st.error("El usuario no existe en los registros actuales. Regístrate abajo.")
            with col_b2:
                if st.button("Crear Cuenta", use_container_width=True):
                    st.session_state.auth_mode = "Register"
                    st.rerun()
                    
        # A2. INTERFAZ DE REGISTRO NUEVO
        elif st.session_state.auth_mode == "Register":
            st.subheader("Registro de Usuario")
            new_email = st.text_input("Ingresa tu Correo", key="reg_email").strip()
            new_pass = st.text_input("Crea tu Contraseña", type="password", key="reg_pass").strip()
            role_type = st.selectbox("Asignar Perfil de Acceso", ["Cliente (Estudiante)", "Administrador"])
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("Generar Código OTP", use_container_width=True):
                    if not new_email or not new_pass:
                        st.warning("Todos los campos de registro son obligatorios.")
                    elif new_email in st.session_state.mock_users_db:
                        st.error("Este correo ya se encuentra registrado.")
                    else:
                        st.session_state.generated_otp = str(random.randint(100000, 999999))
                        st.session_state.pending_user_data = {
                            "email": new_email,
                            "password": new_pass,
                            "role": "admin" if role_type == "Administrator" else "client"
                        }
                        st.session_state.auth_mode = "OTP"
                        st.rerun()
            with col_r2:
                if st.button("Volver al Login", use_container_width=True):
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                    
        # A3. INTERFAZ DE VERIFICACIÓN OTP
        elif st.session_state.auth_mode == "OTP":
            st.subheader("✉️ Código de Verificación")
            st.info(f"🔑 [AWS Cognito Emulation] Código enviado a tu correo: **{st.session_state.generated_otp}**")
            otp_input = st.text_input("Introduce los 6 dígitos recibidos", max_chars=6).strip()
            
            if st.button("Verificar Cuenta", use_container_width=True):
                if otp_input == st.session_state.generated_otp:
                    u_data = st.session_state.pending_user_data
                    st.session_state.mock_users_db[u_data["email"]] = {
                        "password": u_data["password"],
                        "role": u_data["role"],
                        "verified": True
                    }
                    st.success("¡Cuenta verificada! Redirigiendo a inicio de sesión...")
                    time.sleep(1)
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                else:
                    st.error("Código de seguridad incorrecto. Inténtalo de nuevo.")
# --- CAPA B: SISTEMA DE VISTAS SEGURAS (USUARIOS AUTENTICADOS) ---
else:
    col_h1, col_h2 = st.columns([0.8, 0.2])
    with col_h1:
        st.title("🚗 Florida DMV Premium Training Matrix")
        st.write(f"Sesión Activa: **{st.session_state.user_email}**")
    with col_h2:
        st.write("")
        if st.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.user_authenticated = False
            st.session_state.user_role = None
            st.rerun()
            
    st.markdown("---")
    
    # 👑 PANEL 1: VISTA EXCLUSIVA DEL ADMINISTRADOR (PROTECCIÓN DE PRIVACIDAD)
    if st.session_state.user_role == "admin":
        st.header("📈 Centro de Control y Estadísticas del Sistema")
        st.subheader("Mapeo de Preguntas Activas en DynamoDB Local (Streaming)")
        
        st.metric("Total de Preguntas en la Base de Datos NoSQL", len(banco_preguntas))
        
        if banco_preguntas:
            st.write(banco_preguntas)
        else:
            st.info("La base de datos está vacía. Realiza la siembra desde tu terminal de Docker.")
            
        st.markdown("---")
        st.subheader("👥 Directorio de Usuarios Registrados")
        
        for correo, info in st.session_state.mock_users_db.items():
            estado_verificacion = "✅ Cuenta Verificada / Activa" if info["verified"] else "⚠️ Registro Pendiente"
            st.markdown(f"• **Usuario:** `{correo}` | **Estado:** {estado_verificacion}")

    # 🎓 PANEL 2: VISTA EXCLUSIVA DEL CLIENTE (MOTOESTUDIO FLASHCARDS INTERACTIVAS)
    else:
        col_izq, col_der = st.columns([0.65, 0.35], gap="large")
        
        with col_izq:
            if not banco_preguntas:
                st.error("No se encontraron preguntas en el contenedor NoSQL. Por favor, realiza la siembra desde la terminal.")
            elif st.session_state.indice_global < len(banco_preguntas) and not st.session_state.set_completado:
                q = banco_preguntas[st.session_state.indice_global]
                num_pregunta_en_set = (st.session_state.indice_global % TAMANO_SET) + 1
                
                st.markdown(f"### Tarjeta {num_pregunta_en_set} de {TAMANO_SET} (Mazo Global: {st.session_state.indice_global + 1}/{len(banco_preguntas)})")
                st.markdown(f"<div style='background-color:#f1f3f5; padding:20px; border-radius:10px; margin-bottom:20px;'><h4>{q['pregunta']}</h4></div>", unsafe_allow_html=True)
                
                # --- CONTROL DE SINTAXIS ADAPTATIVO (Maneja Listas y Diccionarios por igual) ---
                raw_opciones = q['opciones']
                if isinstance(raw_opciones, dict):
                    opciones = list(raw_opciones.values())
                else:
                    opciones = list(raw_opciones)
                
                # Asegurar de forma segura que existan 4 alternativas para poblar el cuadrante
                while len(opciones) < 4:
                    opciones.append("N/A")
                
                fila1_c1, fila1_c2 = st.columns(2)
                fila2_c1, fila2_c2 = st.columns(2)
                
                def pick_opt(val):
                    if not st.session_state.volteada: st.session_state.respuesta_seleccionada = val

                with fila1_c1:
                    opt_a = opciones[0]
                    lbl = f"🔵 {opt_a}" if st.session_state.respuesta_seleccionada == opt_a else opt_a
                    if st.button(f"A) {lbl}", key="c_opt0", use_container_width=True, disabled=st.session_state.volteada): 
                        pick_opt(opt_a)
                        st.rerun()
                with fila1_c2:
                    opt_b = opciones[1]
                    lbl = f"🔵 {opt_b}" if st.session_state.respuesta_seleccionada == opt_b else opt_b
                    if st.button(f"B) {lbl}", key="c_opt1", use_container_width=True, disabled=st.session_state.volteada): 
                        pick_opt(opt_b)
                        st.rerun()
                with fila2_c1:
                    opt_c = opciones[2]
                    lbl = f"🔵 {opt_c}" if st.session_state.respuesta_seleccionada == opt_c else opt_c
                    if st.button(f"C) {lbl}", key="c_opt2", use_container_width=True, disabled=st.session_state.volteada): 
                        pick_opt(opt_c)
                        st.rerun()
                with fila2_c2:
                    opt_d = opciones[3]
                    lbl = f"🔵 {opt_d}" if st.session_state.respuesta_seleccionada == opt_d else opt_d
                    if st.button(f"D) {lbl}", key="c_opt3", use_container_width=True, disabled=st.session_state.volteada): 
                        pick_opt(opt_d)
                        st.rerun()

                st.markdown("")
                if not st.session_state.volteada:
                    if st.button("Verificar Respuesta", type="primary", use_container_width=True):
                        if st.session_state.respuesta_seleccionada is None:
                            st.warning("Selecciona una opción del cuadrante antes de continuar.")
                        else:
                            st.session_state.volteada = True
                            st.rerun()
                            
                if st.session_state.volteada:
                    # --- NORMALIZADOR DE RESPUESTAS INTELIGENTE (Resuelve error de letras) ---
                    resp_correcta_raw = str(q['respuesta_correcta']).strip().lower()
                    
                    mapeo_letras = {
                        "a": opciones[0],
                        "b": opciones[1],
                        "c": opciones[2],
                        "d": opciones[3]
                    }
                    
                    if resp_correcta_raw in mapeo_letras:
                        solucion_verdadera = mapeo_letras[resp_correcta_raw]
                    else:
                        solucion_verdadera = q['respuesta_correcta']
                    
                    es_cor = st.session_state.respuesta_seleccionada == solucion_verdadera
                    
                    if es_cor: 
                        st.success("🎉 ¡Respuesta Correcta! Excelente trabajo.")
                    else: 
                        st.error(f"❌ Incorrecto. Opción Correcta: {solucion_verdadera}")
                    
                    st.markdown(f"<div style='background-color:#e9ecef; padding:15px; border-radius:8px; border-left:4px solid #002f6c; margin-bottom:15px;'>💡 <b>Referencia Oficial del Manual:</b> {q['explicacion']}</div>", unsafe_allow_html=True)
                    
                    if st.button("Siguiente Tarjeta ➡️", use_container_width=True):
                        if es_cor: st.session_state.total_correctas += 1
                        else: st.session_state.total_incorrectas += 1
                        st.session_state.indice_global += 1
                        st.session_state.volteada = False
                        st.session_state.respuesta_seleccionada = None
                        if st.session_state.indice_global % TAMANO_SET == 0:
                            st.session_state.set_completado = True
                        st.rerun()
            
            elif st.session_state.set_completado:
                st.subheader("🏁 Bloque de Estudio Completado")
                st.write("Has alcanzado con éxito el límite de este set de 5 tarjetas.")
                if st.button("Desbloquear Siguiente Bloque (5 Nuevas Tarjetas)", type="primary", use_container_width=True):
                    st.session_state.set_completado = False
                    st.rerun()
            else:
                st.balloons()
                st.success("🏆 ¡Felicidades! Has completado todas las tarjetas del mazo demo.")
                if st.button("Reiniciar Progreso General", use_container_width=True):
                    st.session_state.indice_global = 0
                    st.session_state.total_correctas = 0
                    st.session_state.total_incorrectas = 0
                    st.session_state.set_completado = False
                    st.rerun()
                    
        with col_der:
            st.markdown("### 📊 Panel de Rendimiento")
            st.markdown("---")
            st.metric("Aciertos ✅", st.session_state.total_correctas)
            st.metric("Errores ❌", st.session_state.total_incorrectas)
            
            prog = (st.session_state.indice_global % TAMANO_SET) + 1 if not st.session_state.set_completado else TAMANO_SET
            deg = int((prog / TAMANO_SET) * 360)
            st.markdown(f"""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <p style="font-weight:bold; color:#6c757d; margin-bottom:10px;">Estado del Set</p>
                <div style="width:110px; height:110px; border-radius:50%; background:conic-gradient(#002f6c {deg}deg, #e9ecef 0deg); display:flex; align-items:center; justify-content:center;">
                    <div style="width:90px; height:90px; border-radius:50%; background-color:white; display:flex; align-items:center; justify-content:center; font-weight:bold; color:#002f6c; font-size:16px;">
                        {prog} / {TAMANO_SET}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
