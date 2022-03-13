import streamlit as st
from pathlib import Path

files = st.file_uploader("uploads", accept_multiple_files=True)
destination = Path('downloads')
destination.mkdir(exist_ok=True)

for f in files:
    bytes_data = f.read()
    st.write("filename:", f.name)
    st.write(f"{len(bytes_data) = }")
    new_file = destination / f.name
    new_file.write_bytes(bytes_data)
