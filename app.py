import streamlit as st
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import zipfile
import time
import base64
import uuid  # Para generar identificadores únicos

# Configurar las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless=new")  # Para versiones más recientes de Chrome
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-extensions")

# Inicializar el WebDriver usando webdriver-manager
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Resoluciones disponibles
RESOLUTIONS = {
    "Desktop 🖥️": (1920, 1080),
    "Tablet 📱": (768, 1024),
    "Mobile 📲": (375, 812)
}

# Genera un identificador único para cada ejecución
execution_id = str(uuid.uuid4())
zip_name = f"screenshots_{execution_id}.zip"
output_dir = f"screenshots_{execution_id}"

# Función para capturar la página completa
def capture_full_page(driver, url, output_path, width, height, console_placeholder):
    """
    Captura toda la página web asegurando que el contenido dinámico se cargue completamente.
    """
    console_placeholder.markdown(
        f'<div class="console">📍 Procesando URL: {url} | Resolución: {width}x{height}</div>', unsafe_allow_html=True
    )
    driver.set_window_size(width, height)
    driver.get(url)
    time.sleep(5)
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Agree') or contains(text(), 'Accept')]"))
        ).click()
        console_placeholder.markdown(
            '<div class="console">✔️ Cookies aceptadas automáticamente</div>', unsafe_allow_html=True
        )
    except Exception:
        console_placeholder.markdown(
            '<div class="console">⚠️ No se encontraron cookies</div>', unsafe_allow_html=True
        )

    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(width, total_height)
    time.sleep(2)
    try:
        driver.save_screenshot(output_path)
        console_placeholder.markdown(
            f'<div class="console">✅ Captura guardada en: {output_path}</div>', unsafe_allow_html=True
        )
    except Exception as e:
        console_placeholder.markdown(
            f'<div class="console">❌ Error al guardar la captura: {e}</div>', unsafe_allow_html=True
        )

# Función para crear un archivo ZIP
def create_zip_archive(base_dir, zip_name):
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, base_dir))

# Generar enlace de descarga para el ZIP
def create_download_button(file_path, label):
    with open(file_path, "rb") as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/{file_path.split(".")[-1]};base64,{b64}" download="{file_path.split("/")[-1]}"><button class="download-btn">{label} 📥</button></a>'
    return href

# Diseño limpio y claro
st.markdown("""
    <style>
    /* General */
    .stButton > button {
        background-color: #6a0dad;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #540a8d;
        transform: translateY(-2px);
        color: white;
        font-weight: 800;

    }
    .stExpander {
        border-radius: 5px;
        padding: 10px;
    }
            
    .console {
        background-color: #1e1e1e; /* Fondo oscuro */
        color: #f5f5f5; /* Texto claro */
        font-family: 'Courier New', monospace;
        font-size: 14px;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        text-align: center;
    }
    .spinner {
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-left-color: #6a0dad;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    .aha-message {
        background-color: #6a0dad;
        color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .aha-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .aha-body {
        font-size: 16px;
        font-weight: normal;
        margin-bottom: 10px;
    }
    .download-btn {
        background-color: white;
        color: #6a0dad;
        border: 2px solid #6a0dad;
        padding: 10px 15px;
        font-size: 14px;
        border-radius: 5px;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .download-btn:hover {
        background-color: #f5e8ff;
        color: #540a8d;
    }
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
     /* Estilos para Selects y Multiselects */

    /* Cambiar el color de fondo y texto de los tags seleccionados */
    span[data-baseweb="tag"] {
        background-color: #6a0dad !important; /* Fondo morado */
        color: white !important; /* Texto blanco */
        border-radius: 4px !important; /* Bordes redondeados */
        padding: 2px 8px !important; /* Espaciado interno */
        margin-right: 4px !important; /* Espaciado entre tags */
    }      
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.title("✨ Benchspark ✨")
st.markdown("### Compara webs en piloto automático")

# Inicializar lista de URLs
urls = []

# Bloque de configuración de capturas
with st.expander("🔧 Configuración de las capturas", expanded=True):
    # Input para URLs separadas por comas
    url_input = st.text_area("🔗 Pega las URLs separadas por comas", height=100)
    
    # Input para subir un archivo
    uploaded_file = st.file_uploader("⬆️ O sube un archivo de texto (.txt) o CSV (.csv)", type=["txt", "csv"])

    # Selector de resoluciones
    selected_resolutions = st.multiselect(
    "📐 Resoluciones disponibles:",
    list(RESOLUTIONS.keys()),
    default=list(RESOLUTIONS.keys())
)
    
    
        
# Mostrar las URLs procesadas
with st.expander("🔍 Ver URLs procesadas"):

# Botón para consultar URLs procesadas
    if st.button("🔍 Consultar URLs procesadas"):
        # Procesar URLs ingresadas manualmente
        if url_input:
            urls.extend([url.strip() for url in url_input.split(",") if url.strip()])
        
        # Procesar URLs desde un archivo
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    # Leer archivo CSV con pandas
                    df = pd.read_csv(uploaded_file)
                    if df.empty:
                        st.error("El archivo CSV subido está vacío.")
                        st.stop()
                    urls.extend(df.iloc[:, 0].dropna().tolist())  # Tomar solo la primera columna
                else:
                    # Leer archivo TXT
                    file_content = uploaded_file.read().decode("utf-8").strip()
                    if not file_content:
                        st.error("El archivo TXT subido está vacío.")
                        st.stop()
                    if "," in file_content:
                        urls.extend([url.strip() for url in file_content.split(",") if url.strip()])
                    else:
                        urls.extend([url.strip() for url in file_content.splitlines() if url.strip()])
            except Exception as e:
                st.error(f"Error al procesar el archivo subido: {e}")
                st.stop()

        # Confirmar las URLs procesadas
        if urls:
            st.success("URLs procesadas y listas para comenzar capturas.")
        else:
            st.error("No se encontraron URLs válidas. Verifica el archivo o el texto ingresado.")

    st.write(urls)



# Botón para comenzar capturas
if st.button("🚀 Comenzar capturas"):
    # Procesar URLs ingresadas manualmente
    if url_input:
        urls.extend([url.strip() for url in url_input.split(",") if url.strip()])
    
    # Procesar URLs desde un archivo subido
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                # Leer archivo CSV con pandas
                df = pd.read_csv(uploaded_file)
                if df.empty:
                    st.error("El archivo CSV subido está vacío.")
                    st.stop()
                urls.extend(df.iloc[:, 0].dropna().tolist())  # Tomar solo la primera columna
            else:
                # Leer archivo TXT
                file_content = uploaded_file.read().decode("utf-8").strip()
                if not file_content:
                    st.error("El archivo TXT subido está vacío.")
                    st.stop()
                if "," in file_content:
                    urls.extend([url.strip() for url in file_content.split(",") if url.strip()])
                else:
                    urls.extend([url.strip() for url in file_content.splitlines() if url.strip()])
        except Exception as e:
            st.error(f"Error al procesar el archivo subido: {e}")
            st.stop()

    # Validar si hay URLs para procesar
    if not urls:
        st.error("No se encontraron URLs válidas para procesar. Verifica el archivo o el texto ingresado.")
        st.stop()

    # Validar si hay resoluciones seleccionadas
    if not selected_resolutions:
        st.error("Por favor, selecciona al menos una resolución para las capturas.")
        st.stop()

    # Spinner de procesamiento
    spinner_placeholder = st.empty()
    spinner_placeholder.markdown('<div class="spinner"></div>', unsafe_allow_html=True)

    console_placeholder = st.empty()  # Consola para los mensajes

    driver = webdriver.Chrome(options=chrome_options)

    os.makedirs(output_dir, exist_ok=True)

    # Procesar cada URL
    for url in urls:
        for device in selected_resolutions:
            width, height = RESOLUTIONS[device]
            sanitized_url = url.replace("http://", "").replace("https://", "").replace("/", "_")
            output_path = os.path.join(output_dir, device, f"{sanitized_url}_{device}.png")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            capture_full_page(driver, url, output_path, width, height, console_placeholder)

    driver.quit()
    create_zip_archive(output_dir, zip_name)
    spinner_placeholder.empty()
    console_placeholder.empty()

    # Mensaje de éxito
    st.markdown(
        f"""
        <div class="aha-message">
            <div class="aha-title">🎉 ¡Capturas completadas con éxito!</div>
            <div class="aha-body">Descarga tus capturas aquí:</div>
            {create_download_button(zip_name, "Descargar capturas ZIP")}
        </div>
        """,
        unsafe_allow_html=True
    )