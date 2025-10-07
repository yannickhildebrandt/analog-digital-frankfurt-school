import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- App-Konfiguration ---
st.set_page_config(
    page_title="Signal-Digitalisierer",
    page_icon="⚡",
    layout="wide"
)

# --- App-Titel und Einleitung ---
st.title("⚡ Der interaktive Signal-Digitalisierer")
st.markdown(
    "Diese App visualisiert die zwei Kernschritte der Analog-Digital-Wandlung: **Abtastung** und **Quantisierung**. "
    "Verwende die Schieberegler in der Seitenleiste, um zu sehen, wie sich die Parameter auf das digitale Signal auswirken."
)

# --- Seitenleiste für die interaktiven Steuerelemente ---
st.sidebar.header("Einstellungen der Digitalisierung")

# Regler für die Abtastrate (Sampling)
sampling_rate = st.sidebar.slider(
    "Abtastrate (Samples pro Sekunde)",
    min_value=1,
    max_value=40,
    value=10,
    step=1,
    help="Wie oft wird das Signal pro Sekunde gemessen? (Zeit-Diskretisierung)"
)

# Regler für die Bit-Tiefe (Quantisierung)
bit_depth = st.sidebar.slider(
    "Bit-Tiefe (Anzahl der Bits)",
    min_value=1,
    max_value=8,
    value=3,
    step=1,
    help="Wie viele Bits werden zur Darstellung eines Abtastwerts verwendet? (Wert-Diskretisierung)"
)
num_levels = 2**bit_depth
st.sidebar.markdown(f"➡️ **{num_levels}** mögliche Werte (Quantisierungsstufen)")

# --- Signal-Definition ---
# Ein einfaches analoges Sinus-Signal
T = 1.0  # Dauer des Signals in Sekunden
f = 2.0  # Frequenz des Signals in Hz
t_analog = np.linspace(0, T, 1000) # Zeitachse für das "perfekte" analoge Signal
amplitude = 1.0
analog_signal = amplitude * np.sin(2 * np.pi * f * t_analog)

# --- Schritt 1: Abtastung (Sampling) ---
# Erzeugt die diskreten Zeitpunkte basierend auf der Abtastrate
num_samples = int(T * sampling_rate)
t_sampled = np.linspace(0, T, num_samples, endpoint=False)
sampled_signal = amplitude * np.sin(2 * np.pi * f * t_sampled)

# --- Schritt 2: Quantisierung (Quantization) ---
# Berechnet die Quantisierungsstufen und "snappt" die Abtastwerte auf diese Stufen
min_val, max_val = -amplitude, amplitude
quantization_levels = np.linspace(min_val, max_val, num_levels)
quantized_signal = np.zeros_like(sampled_signal)
for i, sample in enumerate(sampled_signal):
    # Finde den nächstgelegenen Quantisierungslevel
    closest_level_index = np.argmin(np.abs(quantization_levels - sample))
    quantized_signal[i] = quantization_levels[closest_level_index]

# --- Visualisierung der Ergebnisse ---
st.header("1. Das analoge Ausgangssignal")
st.markdown("Dies ist unser 'perfektes', zeit- und wertkontinuierliches Signal, das wir digitalisieren wollen.")

fig1, ax1 = plt.subplots(figsize=(10, 3))
ax1.plot(t_analog, analog_signal, label="Analoges Signal")
ax1.set_title("Wertkontinuierlich & Zeitkontinuierlich")
ax1.set_xlabel("Zeit (t)")
ax1.set_ylabel("Amplitude")
ax1.grid(True)
st.pyplot(fig1)

st.header("2. Der Digitalisierungsprozess")
st.markdown(
    "Hier sehen wir die Auswirkungen der **Abtastung** und **Quantisierung** in einem kombinierten Diagramm. "
    "Die roten Punkte sind die abgetasteten Werte (`zeitdiskret`), die blauen Stufenlinien zeigen die quantisierten Werte (`wertdiskret`)."
)

# Erzeuge ein kombiniertes Diagramm, das alles zeigt
fig2, ax2 = plt.subplots(figsize=(10, 5))
# Das originale analoge Signal als Referenz im Hintergrund
ax2.plot(t_analog, analog_signal, 'k--', alpha=0.5, label="Originalsignal")
# Die abgetasteten Punkte
ax2.stem(t_sampled, sampled_signal, linefmt='r-', markerfmt='ro', basefmt=' ', label="Abtastwerte (Sampled)")
# Das quantisierte Signal als Treppenfunktion
ax2.step(t_sampled, quantized_signal, where='mid', color='b', linewidth=2.0, label="Quantisiertes Signal")
# Horizontale Linien für die Quantisierungsstufen
for level in quantization_levels:
    ax2.axhline(level, color='gray', linestyle=':', linewidth=0.7)

ax2.set_title(f"Digitalisierung mit {sampling_rate} Hz und {bit_depth}-Bit")
ax2.set_xlabel("Zeit (t) / Sample (n)")
ax2.set_ylabel("Amplitude")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# --- Zusammenfassung und Ergebnis ---
st.header("3. Das finale digitale Signal")
st.markdown("Das ist das Ergebnis, das im Speicher abgelegt wird: eine Sequenz von diskreten Werten zu diskreten Zeitpunkten.")

fig3, ax3 = plt.subplots(figsize=(10, 3))
ax3.stem(t_sampled, quantized_signal, linefmt='b-', markerfmt='bo', basefmt=' ')
ax3.set_title("Wertdiskret & Zeitdiskret")
ax3.set_xlabel("Sample Index (n)")
ax3.set_ylabel("Quantisierter Wert")
ax3.grid(True)
# Setzt die Y-Achsen-Ticks auf die tatsächlichen Quantisierungsstufen für Klarheit
ax3.set_yticks(quantization_levels)
st.pyplot(fig3)

st.info(
    "**Experimentieren Sie!**\n\n"
    "1.  **Erhöhen Sie die Abtastrate:** Das Signal wird originalgetreuer abgetastet.\n"
    "2.  **Verringern Sie die Abtastrate:** Unterhalb von 4 Hz sehen Sie **Aliasing** – das digitale Signal repräsentiert die ursprüngliche 2-Hz-Schwingung nicht mehr korrekt (siehe [Nyquist-Shannon-Abtasttheorem](https://de.wikipedia.org/wiki/Nyquist-Shannon-Abtasttheorem)).\n"
    "3.  **Erhöhen Sie die Bit-Tiefe:** Die quantisierten Stufen werden feiner und der Quantisierungsfehler (Abstand zwischen rotem Punkt und blauer Linie) wird kleiner.\n"
    "4.  **Verringern Sie die Bit-Tiefe:** Die Stufen werden sehr grob, was zu einem hörbaren Rauschen oder sichtbaren Farbbändern (Banding) führen würde."
)
