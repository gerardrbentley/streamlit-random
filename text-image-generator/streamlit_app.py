from datetime import datetime
from pathlib import Path
import streamlit as st
import subprocess

"""\
# Text Recognition Data Generator + Streamlit

Frontend utility for Text Recognition Data Generator (TRDG).
Generate images with random text, featuring useful manipulations and filters / selection of text data.
[See all CLI args](https://textrecognitiondatagenerator.readthedocs.io/en/latest/overview.html)

Demo of using defaults but allowing drag and drop upload of custom font!

🐙 [Github TRDG](https://github.com/Belval/TextRecognitionDataGenerator)

🎈 [Streamlit](https://docs.streamlit.io/)
"""
def ts():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

"## Use a custom font!"
import trdg

fonts_dir = Path(trdg.__file__).parent / 'fonts' / 'latin'
new_font = st.file_uploader('Upload your font file', type='.ttf', accept_multiple_files=False)
bg_options = {
    key: i for i, key in enumerate(('noise', 'white', 'crystal', 'pictures'))
}
bg = st.radio('Background', bg_options)
if new_font is not None:
    st.success(f"Uploaded {new_font.name}")
    new_path = fonts_dir / new_font.name
    new_path.write_bytes(new_font.read())
    st.success(f"Saved to {new_path}")
    status = subprocess.call(f'trdg -c 1 --font {new_path} --background {bg_options[bg]}'.split())
    for i, sample in enumerate(Path('out').iterdir()):
        st.download_button(f'Download Image #{i + 1}', sample.read_bytes(), f"gen_{ts()}.jpg", mime='image/jpeg')
        st.image(str(sample))


