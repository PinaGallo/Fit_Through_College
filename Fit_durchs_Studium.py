import streamlit as st
import pandas as pd


from github_contents import GithubContents


def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"])
        
def main():
    st.title("Fit durchs Studium")


if __name__=="__main__":
    main()
