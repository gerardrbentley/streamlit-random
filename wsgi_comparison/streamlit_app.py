import streamlit as st

if st.button("Do Something Fun 🎉!"):
    st.session_state.show_fun = True
elif 'show_fun' not in st.session_state:
    st.session_state.show_fun = False

if st.session_state.show_fun:
    fun_input = st.text_area('', placeholder='Type some nonsense then hit cmd/ctrl + enter')
    if len(fun_input):
        st.header(f"{len(fun_input)} Characters Processed! REVERSE REVERSE!")
        st.write(fun_input[::-1])