import streamlit as st
import pandas as pd

eleicao2022 = st.session_state["data"]
#Montar pagina
st.markdown("# Base")


st.dataframe(eleicao2022)