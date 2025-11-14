import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
from gc_service import GoogleService
import os
import base64

# --------------------------------------------
# GOOGLE CALENDAR
# --------------------------------------------
CREDENTIALS = "credentials.json"
CALENDAR_ID = "mariodanielq.p@gmail.com"
gc = GoogleService(CREDENTIALS)

# --------------------------------------------
# FUNCION BASE64
# --------------------------------------------
def img_to_b64(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# --------------------------------------------
# CSS
# --------------------------------------------
def load_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --------------------------------------------
# CONFIG STREAMLIT
# --------------------------------------------
st.set_page_config(page_title="Seven Barber Club", page_icon="✂️", layout="centered")
load_css("css/style.css")

# --------------------------------------------
# HEADER
# --------------------------------------------
st.image("assets/banner.png")
st.title("Seven Barber Club")
st.text("📍 Av. Unidad Nacional entre Juan Montalvo y Carabobo")

# --------------------------------------------
# MENU - SIN QR (PRODUCCIÓN)
# --------------------------------------------
selected = option_menu(
    menu_title=None,
    options=["Reservar", "Portafolio", "Aprendiz", "Detalles", "Reseñas"],
    icons=["calendar-check", "scissors", "person-workspace", "pin", "chat-dots"],
    orientation="horizontal",
)

# ============================================================
# RESERVAR
# ============================================================
if selected == "Reservar":

    st.subheader("✂️ Reserva tu cita (pago obligatorio)")

    col1, col2 = st.columns(2)
    nombre = col1.text_input("Tu Nombre *")
    whatsapp = col2.text_input("Tu WhatsApp * (Ej: 0987654321)")
    email = col1.text_input("Tu Email (opcional)")
    fecha = col2.date_input("Fecha *")

    hora = col2.selectbox("Hora *", [
        "09:00","10:00","11:00","12:00",
        "14:00","15:00","16:00","17:00",
        "18:00","19:00","20:00"
    ])

    servicios = {
        "Perfil de cejas": 1,
        "Afeitado / Barba": 3,
        "Corte Clásico máquina": 5,
        "Corte Clásico tijera": 5,
        "Freestyle": 7,
        "Semi Ondulado (ondas)": 20,
        "VIP": 8,
        "Aprendiz (Mario)": 2
    }

    servicio = col1.selectbox("Servicio *", [""] + list(servicios.keys()))
    nota = col1.text_area("Nota (opcional)")

    barbero = col2.selectbox("Barbero *", ["", "💈 Josué", "💈 Ariel", "🧪 Aprendiz"])

    if "mostrar_qr" not in st.session_state:
        st.session_state["mostrar_qr"] = False
    if "pago_ok" not in st.session_state:
        st.session_state["pago_ok"] = False

    if st.button("Reservar"):
        if not nombre or not whatsapp or not fecha or servicio == "" or barbero == "":
            st.warning("⚠ Debes llenar todos los campos obligatorios.")
        else:
            if barbero == "🧪 Aprendiz":
                st.session_state["pago_ok"] = True
            else:
                st.session_state["mostrar_qr"] = True

    # QR (solo si no es aprendiz)
    if st.session_state["mostrar_qr"] and not st.session_state["pago_ok"]:
        precio = servicios[servicio]

        st.markdown(f"""
        ### 💳 Confirmar pago para tu reserva
        <div class="qr-box">
            <h4>💰 Total a pagar: {precio}.00 USD</h4>
            <p>Escanea este QR para pagar y confirmar tu cita.<br>Al llegar, solo muestra tu comprobante.</p>
        </div>
        """, unsafe_allow_html=True)

        st.image("assets/qr_pago.png", width=260)

        if st.button("✔ Ya pagué"):
            st.session_state["pago_ok"] = True

    # CREAR EVENTO
    if st.session_state["pago_ok"]:
        try:
            start = datetime.combine(fecha, datetime.strptime(hora, "%H:%M").time())
            end = start + timedelta(hours=1)

            gc.crear_evento(
                calendar_id=CALENDAR_ID,
                resumen=f"Reserva {servicio} - {nombre}",
                descripcion=(
                    f"Cliente: {nombre}\n"
                    f"WhatsApp: {whatsapp}\n"
                    f"Email: {email}\n"
                    f"Servicio: {servicio}\n"
                    f"Barbero: {barbero}\n"
                    f"Nota: {nota}\n"
                    f"Pago: { '✔ PAGADO' if barbero != '🧪 Aprendiz' else 'No aplica — aprendiz' }"
                ),
                inicio=start,
                fin=end,
                timezone="America/Guayaquil"
            )

            st.success("✅ Reserva creada con éxito. ¡Gracias!")
            st.balloons()

            st.session_state["mostrar_qr"] = False
            st.session_state["pago_ok"] = False

        except Exception as e:
            st.error(f"❌ Error al crear la reserva: {e}")

# ============================================================
# PORTAFOLIO
# ============================================================
if selected == "Portafolio":

    st.subheader("📸 Portafolio — Trabajos reales")

    # Fotos perfiles
    josue_b64 = img_to_b64("assets/josue-perfil.jpg")
    ariel_b64 = img_to_b64("assets/ariel-perfil.jpg")

    # JOSUE
    st.markdown(f"""
    <div class="perfil-barbero">
        <img src="data:image/jpeg;base64,{josue_b64}">
        <h3>👑 Josué</h3>
        <p>Maestro barbero — precisión y estilo.</p>
    </div>
    """, unsafe_allow_html=True)

    for img in ["assets/corte-1.jpg","assets/corte-2.jpg","assets/corte-3.jpg"]:
        img64 = img_to_b64(img)
        st.markdown(f"""
        <div class="corte-box">
            <img src="data:image/jpeg;base64,{img64}">
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ARIEL
    st.markdown(f"""
    <div class="perfil-barbero">
        <img src="data:image/jpeg;base64,{ariel_b64}">
        <h3>💈 Ariel</h3>
        <p>Barbero profesional — cortes modernos y nítidos.</p>
    </div>
    """, unsafe_allow_html=True)

    for img in ["assets/corte-1.jpg","assets/corte-2.jpg","assets/corte-3.jpg"]:
        img64 = img_to_b64(img)
        st.markdown(f"""
        <div class="corte-box">
            <img src="data:image/jpeg;base64,{img64}">
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# APRENDIZ
# ============================================================
if selected == "Aprendiz":
    st.subheader("💈 Aprendiz — Mario")
    st.markdown("""
    ✂️ <b>Cortes de práctica profesional con supervisión.</b><br><br>
    💸 <b>Precio:</b> 2 USD — NO requiere pago adelantado.<br>
    ⏰ <b>Horario:</b> 16:00 a 20:00.<br><br>
    📌 Ideal para clientes que apoyan la formación profesional.
    """, unsafe_allow_html=True)

# ============================================================
# DETALLES
# ============================================================
if selected == "Detalles":
    st.subheader("📍 Ubicación y Horarios")
    st.image("assets/map.jpg", use_container_width=True)
    st.markdown("""
    📌 Dirección: Av. Unidad Nacional entre Juan Montalvo y Carabobo — Riobamba  
    🕒 Horario: 09:00 - 21:00 todos los días
    """)

# ============================================================
# RESEÑAS
# ============================================================
if selected == "Reseñas":
    st.subheader("💬 Opiniones reales")
    st.image("assets/review-1.png")
    st.image("assets/review-2.png")
