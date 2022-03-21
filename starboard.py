import streamlit as st

starboard_embed_url = st.text_area('Starboard.gg iframe', value="https://ifusernameisnone.starboard.host/v1/embed/0.15.3/c3blnrq23akg00819700/nxIEOXJ/")

iframe_template = """<iframe src="{}" frameborder="0" height="600px" width="100%"></iframe>"""
st.write(starboard_embed_url)
st.markdown(iframe_template.format(starboard_embed_url), unsafe_allow_html=True)