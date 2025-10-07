import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write as write_wav
from PIL import Image
import requests
from io import BytesIO

# --- App-Konfiguration ---
st.set_page_config(
    page_title="Signal-Digitalisierer",
    page_icon="⚡",
    layout="wide"
)

# --- App-Titel und Einleitung ---
st.title("⚡ Der interaktive Signal-Digitalisierer")
st.markdown(
    "Diese App visualisiert die Analog-Digital-Wandlung. Wähle einen Tab, um die Grundlagen zu verstehen oder Realwelt-Beispiele zu erkunden."
)

# --- Tabs für die verschiedenen Bereiche ---
tab1, tab2, tab3 = st.tabs(["Grundlagen der Digitalisierung", "🎤 Realwelt: Audio", "🖼️ Realwelt: Bilder"])

# ==============================================================================
# TAB 1: GRUNDLAGEN (DER BISHERIGE CODE)
# ==============================================================================
with tab1:
    st.header("Die Theorie: Abtastung & Quantisierung")
    
    col1, col2 = st.columns([1, 2]) # Layout in Spalten
    
    with col1:
        st.subheader("Einstellungen")
        # Regler für die Abtastrate (Sampling)
        sampling_rate = st.slider(
            "Abtastrate (Samples/Sek.)", 1, 40, 10, 1,
            help="Wie oft wird das Signal pro Sekunde gemessen? (Zeit-Diskretisierung)"
        )
        # Regler für die Bit-Tiefe (Quantisierung)
        bit_depth = st.slider(
            "Bit-Tiefe (Anzahl der Bits)", 1, 8, 3, 1,
            help="Wie viele Bits zur Darstellung eines Werts? (Wert-Diskretisierung)"
        )
        num_levels = 2**bit_depth
        st.markdown(f"➡️ **{num_levels}** mögliche Werte (Quantisierungsstufen)")
        
        st.info(
            "**Experimentieren Sie!**\n\n"
            "1.  **Abtastrate ↑:** Das Signal wird originalgetreuer.\n"
            "2.  **Abtastrate ↓:** Unter 4 Hz tritt **Aliasing** auf!\n"
            "3.  **Bit-Tiefe ↑:** Die Stufen werden feiner (weniger Quantisierungsfehler).\n"
            "4.  **Bit-Tiefe ↓:** Die Stufen werden sehr grob."
        )

    with col2:
        # --- Signal-Definition ---
        T, f, amplitude = 1.0, 2.0, 1.0
        t_analog = np.linspace(0, T, 1000)
        analog_signal = amplitude * np.sin(2 * np.pi * f * t_analog)
        
        # --- Abtastung & Quantisierung ---
        num_samples = int(T * sampling_rate)
        t_sampled = np.linspace(0, T, num_samples, endpoint=False)
        sampled_signal = amplitude * np.sin(2 * np.pi * f * t_sampled)
        
        quantization_levels = np.linspace(-amplitude, amplitude, num_levels)
        quantized_signal = np.array([quantization_levels[np.argmin(np.abs(quantization_levels - s))] for s in sampled_signal])

        # --- Visualisierung ---
        st.subheader("Visualisierung des Prozesses")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(t_analog, analog_signal, 'k--', alpha=0.5, label="Originalsignal")
        ax.stem(t_sampled, sampled_signal, linefmt='r-', markerfmt='ro', basefmt=' ', label="Abtastwerte")
        ax.step(t_sampled, quantized_signal, where='mid', color='b', linewidth=2.0, label="Quantisiertes Signal")
        for level in quantization_levels:
            ax.axhline(level, color='gray', linestyle=':', linewidth=0.7)
        ax.set_title(f"Digitalisierung mit {sampling_rate} Hz und {bit_depth}-Bit")
        ax.set_xlabel("Zeit (t) / Sample (n)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)


# ==============================================================================
# TAB 2: REALWELT: AUDIO
# ==============================================================================
with tab2:
    st.header("Anwendungsfall: Digitalisierung von Audio")
    st.markdown("Hören Sie, wie sich Abtastrate und Bit-Tiefe auf die Qualität eines einfachen Tons auswirken.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Audio-Parameter")
        audio_samplerate = st.select_slider(
            "Abtastrate (Hz)",
            options=[4000, 8000, 11025, 22050, 44100],
            value=8000,
            help="CD-Qualität hat 44100 Hz. Telefonqualität nur 8000 Hz."
        )
        audio_bitdepth = st.select_slider(
            "Bit-Tiefe",
            options=[2, 4, 8, 16],
            value=4,
            help="CD-Qualität hat 16 Bit. Eine geringe Bit-Tiefe erzeugt hörbares Rauschen."
        )
        ton_frequenz = 440 # Frequenz des Testtons (Kammerton A)

        st.info(
            f"**Hören Sie genau hin!**\n\n"
            f"1. **Nyquist-Theorem:** Die Abtastrate muss > {2*ton_frequenz} Hz sein. Probieren Sie 4000 Hz – der Ton klingt 'falsch' (Aliasing).\n\n"
            f"2. **Quantisierungsrauschen:** Wählen Sie eine niedrige Bit-Tiefe (z.B. 2 oder 4 Bit). Sie werden ein deutliches, 'kratziges' Rauschen im Hintergrund hören."
        )

    with col2:
        st.subheader("Generiertes Audio-Signal")
        
        # Generiere einen 2-Sekunden-Ton
        duration = 2
        t = np.linspace(0., duration, int(audio_samplerate * duration), endpoint=False)
        amplitude = np.iinfo(np.int16).max * 0.5 # Skalieren für 16-Bit Audio
        
        # Analoges Signal (theoretisch)
        data = amplitude * np.sin(2. * np.pi * ton_frequenz * t)
        
        # Quantisierung
        num_levels_audio = 2**audio_bitdepth
        quant_step = 2 * amplitude / num_levels_audio
        # Runden auf die nächste Quantisierungsstufe
        data_quantized = np.round(data / quant_step) * quant_step
        
        # In Bytes konvertieren für die Wiedergabe
        wav_data = data_quantized.astype(np.int16)
        
        # In-Memory WAV-Datei erstellen
        byte_io = BytesIO()
        write_wav(byte_io, audio_samplerate, wav_data)
        
        st.audio(byte_io)

        st.write(f"**Ergebnis:** Ein 2-Sekunden-Ton ({ton_frequenz} Hz) digitalisiert mit {audio_samplerate} Hz und {audio_bitdepth} Bit.")
        
        # Visualisierung der Wellenform (Zoom)
        st.subheader("Wellenform (Zoom auf die ersten 50 Samples)")
        fig, ax = plt.subplots(figsize=(10,3))
        ax.step(np.arange(50), data_quantized[:50], where='mid')
        ax.plot(data[:50], 'r--', alpha=0.7)
        ax.set_title("Vergleich: Digital (blau) vs. Original (rot gestrichelt)")
        ax.set_xlabel("Sample Index (n)")
        ax.set_ylabel("Amplitude")
        st.pyplot(fig)


# ==============================================================================
# TAB 3: REALWELT: BILDER
# ==============================================================================
with tab3:
    st.header("Anwendungsfall: Digitalisierung von Bildern")
    st.markdown("Sehen Sie, wie sich Auflösung (Abtastung) und Farbtiefe (Quantisierung) auf ein Foto auswirken.")

    @st.cache_data
    def load_image(url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img

    # Lade ein Beispielbild
    IMG_URL = "https://images.pexels.com/photos/1528640/pexels-photo-1528640.jpeg"
    original_image = load_image(IMG_URL)

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        st.subheader("Bild-Parameter")
        resolution_percent = st.slider(
            "Auflösung (in %)", 1, 100, 50, 1,
            help="Reduziert die Anzahl der Pixel (Breite x Höhe). Dies ist die räumliche Abtastung."
        )
        
        color_depth = st.select_slider(
            "Farbtiefe (Anzahl der Farben)",
            options=[2, 4, 8, 16, 32, 64, 256],
            value=16,
            help="Reduziert die Farbpalette des Bildes. Dies ist die Quantisierung der Farbwerte."
        )
        st.info(
            "**Beobachten Sie:**\n\n"
            "1.  **Auflösung ↓:** Das Bild wird **pixelig** und unscharf.\n\n"
            "2.  **Farbtiefe ↓:** Es entstehen harte Farbübergänge und sichtbare Bänder (**Color Banding**)."
        )


    # Verarbeitung des Bildes
    # 1. Auflösung reduzieren (Abtastung)
    w, h = original_image.size
    new_w = int(w * resolution_percent / 100)
    new_h = int(h * resolution_percent / 100)
    resampled_image = original_image.resize((new_w, new_h), Image.Resampling.NEAREST)
    # Wieder auf Originalgröße skalieren, damit der Pixel-Effekt sichtbar wird
    resampled_image_display = resampled_image.resize((w, h), Image.Resampling.NEAREST)

    # 2. Farbtiefe reduzieren (Quantisierung)
    quantized_image = resampled_image_display.quantize(colors=color_depth, method=Image.Quantize.MEDIANCUT)
    # Wieder in RGB konvertieren, damit Streamlit es anzeigen kann
    final_image = quantized_image.convert("RGB")

    with col2:
        st.subheader("Originalbild")
        st.image(original_image, caption=f"{original_image.width}x{original_image.height} Pixel, Millionen von Farben")

    with col3:
        st.subheader("Digitalisiertes Ergebnis")
        st.image(final_image, caption=f"{new_w}x{new_h} Pixel, auf {color_depth} Farben reduziert")
