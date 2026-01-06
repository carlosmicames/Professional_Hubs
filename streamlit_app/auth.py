import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def load_auth_config():
    """Load authentication config"""
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def setup_authenticator():
    """Setup and return authenticator"""
    config = load_auth_config()
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    return authenticator

def require_auth():
    """Require authentication before accessing app"""
    authenticator = setup_authenticator()
    
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status:
        return True, name, username, authenticator
    elif authentication_status == False:
        st.error('Username/password is incorrect')
        return False, None, None, None
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        return False, None, None, None