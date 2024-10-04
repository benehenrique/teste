import streamlit as st
import streamlit_authenticator as stauth


st.set_page_config(page_title='Login', layout = 'wide')

# user authentication
# Configuração das credenciais
credentials = {
    "usernames": {
        st.secrets['user']: {"name": "User One", "password": st.secrets['password'], "email": "teste"},
    }
}

# Configuração da autenticação
authenticator = stauth.Authenticate(
    credentials,
    "app_cookie_name",  # Nome do cookie
    "app_signature_key",  # Chave de assinatura
    cookie_expiry_days=0  # Expiração do cookie
)

# login
authenticator.login()

if st.session_state['authentication_status'] == False:
    st.error('Username/password incorreto')

elif st.session_state['authentication_status'] == None:
    st.warning('Insira Username e Password')

elif st.session_state['authentication_status']:

    authenticator.logout('logout','sidebar')

    # Menu lateral para navegar entre as páginas
    menu = st.sidebar.selectbox('Escolha a página', ['Escolha', 'Intraday Returns'])

    # Inicializa a chave de sessão se não existir
    if 'dados_atualizados' not in st.session_state:
        st.session_state.dados_atualizados = False

    if menu == 'Intraday Returns':
        import intraday_returns  
        from intraday_returns import atualiza

        if not st.session_state.dados_atualizados:
            fig, pesos_gvmi, pesos_div, pesos_fia, pesos_abs, df_erro = atualiza()
            st.plotly_chart(fig)

            

