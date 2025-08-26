import streamlit as st

st.title("Test Streamlit App")
st.write("Hello World!")

if 'counter' not in st.session_state:
    st.session_state.counter = 0

if st.button("Click me"):
    st.session_state.counter += 1

st.write(f"Counter: {st.session_state.counter}")
