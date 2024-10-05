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

        def intraday_returns_page():
            st.plotly_chart(fig)
            col1, col2 = st.columns([3, 2])  # Ajuste os tamanhos das colunas se necessário
            st.session_state.dados_atualizados = True
            with col1:
                st.write(f'Dados de {abs(pesos_gvmi * 100).sum():.2f}% do Portfólio - GVMI')
                st.write(f'Dados de {abs(pesos_div * 100).sum():.2f}% do Portfólio - DIV')
                st.write(f'Dados de {abs(pesos_fia * 100).sum():.2f}% do Portfólio - FIA')
                st.write(f'Dados de {abs(pesos_abs * 100).sum():.2f}% do Portfólio - ABS')

            # Exibindo a lista como DataFrame na coluna 2
            with col2:
                if df_erro is not None and not df_erro.empty:
                    st.dataframe(df_erro)

        if not st.session_state.dados_atualizados:
            fig, pesos_gvmi, pesos_div, pesos_fia, pesos_abs, df_erro = atualiza()
            intraday_returns_page()
        

            

