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

    authenticator.logout('Logout','sidebar')

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

        atualizar_dados = st.sidebar.button('Atualizar Dados')

        # Botão no sidebar que seleciona 'Intraday Returns'
        if atualizar_dados:
            selecionar_intraday()
        
        fig, pesos_gvmi, pesos_div, pesos_fia, pesos_abs, df_erro = intraday_returns.atualiza()
        st.plotly_chart(fig)
        
        col1, col2, col3 = st.columns([3, 2, 10])  # tamanhos das colunas
        
        with col1:
            st.write(f'Dados de {abs(pesos_fia * 100).sum():.2f}% do Portfólio - FIA')
            st.write(f'Dados de {abs(pesos_abs * 100).sum():.2f}% do Portfólio - ABS')
            st.write(f'Dados de {abs(pesos_div * 100).sum():.2f}% do Portfólio - DIV')
            st.write(f'Dados de {abs(pesos_gvmi * 100).sum():.2f}% do Portfólio - GVMI')

        # Exibindo a lista como DataFrame na coluna 2
        with col2:
            if df_erro is not None and not df_erro.empty:
                st.dataframe(df_erro)

        # Inicializando o estado do DataFrame se ele ainda não existir
        if 'df_table' not in st.session_state:
            st.session_state.df_table, datas_cota = intraday_returns.returns_request()
    
        with col3:
            # Atualiza df_table somente se o botão "Atualizar Dados" não foi clicado
            if not atualizar_dados:
                st.session_state.df_table, datas_cota = intraday_returns.returns_request()

            st.write(f'Tabela de Rentabilidade {datas_cota}')
            st.dataframe(st.session_state.df_table)

                
            
        

            

