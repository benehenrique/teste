import streamlit as st
import streamlit_authenticator as stauth


st.set_page_config(page_title='Avantgarde', layout = 'wide')

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

    # Define o estado inicial para o selectbox
    if 'menu' not in st.session_state:
        st.session_state.menu = 'Intraday Returns'

    # Função para alterar o valor do selectbox
    def selecionar_intraday():
        st.session_state.menu = 'Intraday Returns' #atualiza dados

    
    # Menu lateral para navegar entre as páginas. Insira o nome dentro das listas p criar mais paginas. O index indica em qual pagina o app deve iniciar
    menu = st.sidebar.selectbox('Escolha a página', ['Intraday Returns'], index=['Intraday Returns'].index(st.session_state.menu))

    #if menu == 'Escolha':
     #   st.write('Avantgarde Asset Managment')

    

    if menu == 'Intraday Returns':
        
        import intraday_returns

        # Botão no sidebar que seleciona 'Intraday Returns'
        if st.sidebar.button('Atualizar Dados'):
            selecionar_intraday()
        
        
        fig, pesos_gvmi, pesos_div, pesos_fia, pesos_abs, df_erro = intraday_returns.atualiza()
        st.plotly_chart(fig)
        col1, col2, col3 = st.columns([3, 2, 8])  # Ajuste os tamanhos das colunas se necessário
        with col1:
            st.write(f'Dados de {abs(pesos_gvmi * 100).sum():.2f}% do Portfólio - GVMI')
            st.write(f'Dados de {abs(pesos_div * 100).sum():.2f}% do Portfólio - DIV')
            st.write(f'Dados de {abs(pesos_fia * 100).sum():.2f}% do Portfólio - FIA')
            st.write(f'Dados de {abs(pesos_abs * 100).sum():.2f}% do Portfólio - ABS')
        # Exibindo a lista como DataFrame na coluna 2
        with col2:
            if df_erro is not None and not df_erro.empty:
                st.dataframe(df_erro)

        with col3:
            df_table = intraday_returns.returns_request()
            st.dataframe(df_table)

                
            
        

            

