import streamlit as st
import parselmouth
from parselmouth.praat import call
import io
import soundfile as sf
import pandas as pd
import numpy as np



def process_upload():
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    bytes_data = uploaded_file.getvalue()

    x, fs = sf.read(io.BytesIO(bytes_data))
    sf.write('tmp.wav', x, fs)
    sound = parselmouth.Sound('tmp.wav')
    sound.name = file_details['FileName']
    return sound, file_details

def waveform_plot(sound):
    st.write("Cache miss: waveform_plot(", sound, ",) ran")
    waveform = pd.DataFrame({"Amplitude": sound.values[0].T})
    st.line_chart(waveform)


def measure_pitch(sound, time_step):
    if time_step == 0:
        time_step = None
    pitch = sound.to_pitch_ac(time_step=time_step, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
    pitch.name = file_details['FileName']
    mean_pitch = call(pitch, "Get mean", 0, 0, 'Hertz')
    return mean_pitch, pitch


def measure_formants(sound, *args, **kwargs):
    # measure formants
    formant_path_object = call(sound, "To FormantPath (burg)", 0.005, 7.0, 5250.0, 0.025, 50.0, 0.05, 4)
    formant_object = call(formant_path_object, "Extract Formant")
    formant_object.name = file_details['FileName']
    f1 = call(formant_object, "Get mean", 1, 0, 0, "Hertz")
    f2 = call(formant_object, "Get mean", 2, 0, 0, "Hertz")
    f3 = call(formant_object, "Get mean", 3, 0, 0, "Hertz")
    f4 = call(formant_object, "Get mean", 4, 0, 0, "Hertz")
    return f1, f2, f3, f4


def display_results():
    # Display info about sound\
    #st.markdown('# Sound details')
    sound_expander = st.beta_expander(label='Sound details')
    sound_expander.text(sound)
    st.markdown('# Voice Pitch')
    st.markdown(f'## Mean Pitch.......{round(mean_pitch, 3)} Hz')
    pitch_expander = st.beta_expander(label='Voice Pitch details')
    pitch_expander.text(pitch)
    st.markdown('# Formant Frequencies')
    st.markdown('## Average Formants (Hz')
    df = pd.DataFrame({
        'F1':[round(f1)],
        'F2':[round(f2)],
        'F3':[round(f3)],
        'F4':[round(f4)],
    })
    st.table(df,)

def sidebar():
    # Sidebar with analysis parameters
    time_step = st.sidebar.slider('Time step (ms)', 0, 100, 0) / 100
    pitch_floor = st.sidebar.slider('Pitch Floor (Hz)', 20, 300, 75)
    pitch_ceiling = st.sidebar.slider('Pitch Ceiling (Hz)', 100, 1000, 600)
    return time_step, pitch_floor, pitch_ceiling


# Create sidebar
time_step, pitch_floor, pitch_ceiling = sidebar()

# Upload the file
uploaded_file = st.file_uploader("Upload Files", type=['wav', 'mp3'])

if uploaded_file:
    # Process upload
    sound, file_details = process_upload()
    # Display sound
    waveform_plot(sound)
    # Measure voice pitch
    mean_pitch, pitch = measure_pitch(sound, time_step)
    # Measure formants
    f1, f2, f3, f4 = measure_formants(sound)
    # Display results
    display_results()


