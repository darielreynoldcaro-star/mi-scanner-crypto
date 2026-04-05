import streamlit as st
import requests
import time

# Configuración visual de la aplicación
st.set_page_config(
    page_title="Crypto Live Tracker",
    page_icon="📈",
    layout="centered"
)

def get_live_price(crypto_id):
    """Obtiene el precio en tiempo real desde la API de CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[crypto_id]['usd']
    except Exception:
        return None

# Interfaz de Usuario
st.title("💰 Calculadora de Cripto en Vivo")
st.markdown("---")

# Selección de activos
col1, col2 = st.columns(2)
with col1:
    coin = st.selectbox(
        "Selecciona una criptomoneda:",
        ["bitcoin", "ethereum", "fantom", "binancecoin", "solana"],
        index=0
    )
with col2:
    amount = st.number_input("Tu balance:", min_value=0.0, value=1.0, step=0.0001)

# Contenedor dinámico para que no se refresque toda la página
placeholder = st.empty()

st.info("La aplicación se actualiza automáticamente cada 15 segundos.")

# Bucle de actualización
while True:
    price = get_live_price(coin)
    
    if price is not None:
        total_value = amount * price
        
        with placeholder.container():
            # Mostramos el precio y el cálculo con formato de moneda
            st.metric(
                label=f"Precio Actual de {coin.upper()}", 
                value=f"${price:,.2f} USD"
            )
            
            st.subheader(f"Valor de tu cartera: ${total_value:,.2f} USD")
            
            st.caption(f"Última actualización: {time.strftime('%H:%M:%S')}")
    else:
        st.error("No se pudo obtener el precio. Reintentando...")
    
    time.sleep(15)
