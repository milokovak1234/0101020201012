import streamlit as st
import av
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoTransformerBase
from pyzbar.pyzbar import decode

class BarcodeScanner(VideoTransformerBase):
    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        
        # Convertir la imagen a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Decodificar los códigos de barras en la imagen
        barcodes = decode(gray)
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Extraer el texto del código de barras
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            
            # Mostrar el texto en la imagen
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Guardar el código detectado en el estado de Streamlit
            st.session_state['barcode'] = barcode_data

        return av.VideoFrame.from_ndarray(image, format="bgr24")

st.title("Escáner de Código de Barras 📷")

st.write("Apunta la cámara trasera hacia un código de barras.")

if "barcode" not in st.session_state:
    st.session_state['barcode'] = None

webrtc_ctx = webrtc_streamer(
    key="barcode-scanner",
    mode=WebRtcMode.SENDRECV,
    video_transformer_factory=BarcodeScanner,
    async_processing=True
)

# Mostrar el código de barras detectado
if st.session_state['barcode']:
    st.success(f"Código Detectado: {st.session_state['barcode']}")
