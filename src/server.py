import streamlit as st

"""
    To run this, we gotta have installed streamlit:
        pip3 install streamlit 
        
    then:
        streamlit run server.py
    
    To check the website: http://localhost:8501/ the port is automatically assigned 

"""

if __name__ == "__main__":
    st.title("My Basic Web App")

    st.header("Welcome to my web app!")

    user_name = st.text_input("Enter your name:")

    if user_name:
        greeting = "Hello, " + user_name + "!"
        st.markdown(greeting)

    if st.button("Submit"):
        st.write("Button clicked!")
