import logging
import queue
import threading

import matplotlib.pyplot as plt
import numpy as np
import pydub
import streamlit as st

from streamlit_webrtc import (
    RTCConfiguration,
    WebRtcMode,
    webrtc_streamer,
)

logger = logging.getLogger(__name__)


RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


GUITAR_NOTES = ['high E', 'B', 'G', 'D', 'A', 'low E']
base_guitar_freqs = [329.63,
            246.94,
            196.00,
            146.83,
            110.00,
            82.41,]
GUITAR_FREQS = np.asarray(base_guitar_freqs)
GUITAR_TUNINGS = {note: freq for note, freq in zip(GUITAR_NOTES, GUITAR_FREQS)}


def main():
    st.write("""\
    # Streamlit Guitar Tuner
    
    Powered by [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)

    Made with ❤️ from [Gar's Bar](https://tech.gerardbentley.com/)

    ## What is this?

    A simplified guitar tuner built with [Streamlit](https://streamlit.io).
    Sends the sound from your device's microphone (after you hit *Start*) then processes it to find the nearest open guitar note.
    """)
    with st.expander("Caveats"):
        st.write("""\
        This only finds one peak frequency, so if you have background noise it won't work well.

        Low strings will probably get washed out by mic noise or natural harmonics (fundamental frequency isn't the peak sometimes).
        Feel free to [research](https://music.stackexchange.com/questions/101677/why-is-the-5th-stronger-than-the-1st-in-guitar-spectrum) and [experiment](https://makersportal.com/blog/2018/9/20/audio-processing-in-python-part-iii-guitar-string-theory-and-frequency-analysis) with these resources.
        """)

    run_guitar_tuner()

    logger.debug("=== Alive threads ===")
    for thread in threading.enumerate():
        if thread.is_alive():
            logger.debug(f"  {thread.name} ({thread.ident})")




def get_nearest_note(peak):
    best_note_index = (np.abs(GUITAR_FREQS - peak)).argmin()
    return GUITAR_NOTES[best_note_index]

def run_guitar_tuner():
    """Transfer audio frames from the browser to the server and visualize them with matplotlib
    and `st.pyplot`."""
    webrtc_ctx = webrtc_streamer(
        key="guitar-tuner",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"audio": True},
    )

    left_col, right_col = st.columns(2)
    left_col.json(GUITAR_TUNINGS)

    nearest_note = right_col.empty()
    off_metric = right_col.empty()
    fig_place = st.empty()

    fig, [ax_freq, ax_time] = plt.subplots(
        2, 1, gridspec_kw={"top": 1.5, "bottom": 0.2}
    )
    sound_window_len = 5000  # 5s
    sound_window_buffer = None
    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                logger.warning("Queue is empty. Abort.")
                break

            sound_chunk = pydub.AudioSegment.empty()
            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > 0:
                if sound_window_buffer is None:
                    sound_window_buffer = pydub.AudioSegment.silent(
                        duration=sound_window_len
                    )

                sound_window_buffer += sound_chunk
                if len(sound_window_buffer) > sound_window_len:
                    sound_window_buffer = sound_window_buffer[-sound_window_len:]

            if sound_window_buffer:
                # Ref: https://own-search-and-study.xyz/2017/10/27/python%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E9%9F%B3%E5%A3%B0%E3%83%87%E3%83%BC%E3%82%BF%E3%81%8B%E3%82%89%E3%82%B9%E3%83%9A%E3%82%AF%E3%83%88%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%A0%E3%82%92%E4%BD%9C/  # noqa
                sound_window_buffer = sound_window_buffer.set_channels(
                    1
                )  # Stereo to mono
                sample = np.array(sound_window_buffer.get_array_of_samples())

                ax_time.cla()
                times = (np.arange(-len(sample), 0)) / sound_window_buffer.frame_rate
                ax_time.plot(times, sample)
                ax_time.set_xlabel("Time")
                ax_time.set_ylabel("Magnitude")

                spec = np.abs(np.fft.fft(sample))
                freq = np.fft.fftfreq(sample.shape[0], 1.0 / sound_chunk.frame_rate)
                freq = freq[: int(freq.shape[0] / 2)]
                spec = spec[: int(spec.shape[0] / 2)]
                spec[0] = spec[0] / 2

                peak = np.argmax(spec)
                peak_freq = freq[peak]

                note = get_nearest_note(peak_freq)
                real_freq = GUITAR_TUNINGS[note]
                off_metric.metric(f"Peak Frequency (Hz)", peak_freq, peak_freq - real_freq)
                nearest_note.header(note)


                ax_freq.cla()
                ax_freq.plot(freq, spec)
                ax_freq.set_xlabel("Frequency")
                ax_freq.set_yscale("log")
                ax_freq.set_ylabel("Magnitude")

                fig_place.pyplot(fig)
        else:
            logger.warning("AudioReciver is not set. Abort.")
            break


if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)

    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)

    main()
