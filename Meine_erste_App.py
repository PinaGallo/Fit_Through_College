# Streamlit hello world app
import streamlit as st
import pandas as pd
import numpy as np


def main():
    st.write('Salü zämma!')
    st.title("Das isch Pina's app in Streamlit.")
    st.write('To run this app, use the following command:')
    st.code('streamlit run hello_world.py')
    st.sidebar.title('Das isch d Sidebar')
    st.sidebar.write('Do kama Widgets hinzuafüaga, zum Bispiel:')


    add_selectbox = st.sidebar.selectbox("Wia möchtisch Du kontaktiart werda?",("Email", "Home phone", "Mobile phone"))


    
    df = pd.DataFrame(np.random.randn(50, 20), columns=("Spalte %d" % i for i in range(20)))
    st.dataframe(df)  


    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    st.area_chart(chart_data)

    genre = st.radio(
        "What's your favorite movie genre",
        [":rainbow[Comedy]", "***Drama***", "Documentary :movie_camera:"],
        captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."])

    if genre == ':rainbow[Comedy]':
        st.write('You selected comedy.')
    else:
        st.write("You didn\'t select comedy.")





if __name__ == '__main__':
    main()
