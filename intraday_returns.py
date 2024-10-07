import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import concurrent.futures


#authenticator.logout('logout','sidebar')
# intraday data of each asset
def get_intraday_data(asset):
    url = f'https://cotacao.b3.com.br/mds/api/v1/DailyFluctuationHistory/{asset}'
    
    try:
        response = requests.get(url)  # Timeout para evitar requisições lentas
        if response.status_code == 200:
            return asset, response.json()  # Retorna o ativo e os dados JSON
        else:
            print(f"Erro ao acessar os dados de {asset}: {response.status_code}")
            return asset, None
    except requests.RequestException as e:
        print(f"Erro na requisição do ativo {asset}: {e}")
        return asset, None

# processa os dados intraday da url e organizar em um DataFrame

def process_data(asset_data, asset_code, lista_assets_erro):
    if asset_data is None:
        return None

    try:
        # Extraindo os dados de intraday
        data = asset_data['TradgFlr']['scty']['lstQtn']
        
        # Criando um DataFrame
        df = pd.DataFrame(data)
        
        # Filtrando as colunas necessárias
        df = df[['dtTm', 'prcFlcn']].copy()
        
        # Renomeando as colunas e ajustando o índice
        df['dtTm'] = pd.to_datetime(df['dtTm'], format='%H:%M:%S').dt.time
        df = df.set_index('dtTm')
        
        # Renomeando a coluna com o código do ativo
        df.columns = [asset_code]
        
        return df
    except KeyError as e:
        print(f"Erro ao processar os dados de {asset_code}: {e}")
        lista_assets_erro.append(asset_code)
        st.write(f"Erro ao processar os dados de {asset_code}")
        return None


# Função para buscar e processar os dados de um único ativo
def fetch_and_process_data(asset, lista_assets_erro):
    asset_code, raw_data = get_intraday_data(asset)
    return process_data(raw_data, asset_code, lista_assets_erro)

# portfolio data
def portfolio_request(fund):
    response = requests.get(st.secrets['portfolio']+f'{fund}')
    portfolio = pd.DataFrame(response.json())
    portfolio.pct_aum = portfolio.pct_aum.astype('float')
    return portfolio

# returns request
def returns_request():
    df_fundos = []
    datas_cota = []
    
    fundos = ['avantgarde_fia', 'avantgarde_abs', 'avantgarde_div', 'avantgarde_gvmi']
    for nome_fundo in fundos:
        if nome_fundo == 'avantgarde_fia':
            nome_abreviacao = 'fia'
            benchmark_name = 'ibx'
        elif nome_fundo == 'avantgarde_abs':
            nome_abreviacao = 'abs'
            benchmark_name = 'cdi'
        elif nome_fundo == 'avantgarde_div':
            nome_abreviacao = 'div'
            benchmark_name = 'ibov'
        elif nome_fundo == 'avantgarde_gvmi':
            nome_abreviacao = 'gvmi'
            benchmark_name = 'ibov'
            
    
        lamina_url = st.secrets['lamina']+f'{nome_fundo}'
    
        response = requests.get(lamina_url)
        # pegar apenas os dados de mes, ano, fund_12m_cumulative_return, index_12m_cumulative_return
        data = response.json()
    
        nome_mes = data['fund_return_last_date'].split(' ')[2]
        nome_ano = data['fund_return_last_date'].split(' ')[4]
        retorno_fundo = data['fund_cumulative_return']
        retorno_benchmark = data['index_cumulative_return']
        retorno_fundo_12m = data['fund_12m_cumulative_return']
        retorno_benchmark_12m = data['index_12m_cumulative_return']
        # data cota de cada fundo
        dia_cota = data['fund_return_last_date'].split()[0]
        mes_cota = data['fund_return_last_date'].split()[2][:3] # apenas 3 primeiras letras do mes

        datas_cota.append(f' | {nome_abreviacao.upper()}: {dia_cota} de {mes_cota}')
    
        # retorno do mes e ano apenas
        return_table_url = st.secrets['table']+f'{nome_fundo}'
    
        response = requests.get(return_table_url)
    
        for json_tabela_retorno in response.json():
            if json_tabela_retorno['ANO'] == int(nome_ano) and json_tabela_retorno['RET (%)'] == 'FUNDO':
                retorno_fundo_mes = json_tabela_retorno[nome_mes[:3].upper()] # 3 primeiras letras do mes p coletar retorno
                retorno_fundo_ano = json_tabela_retorno['ANUAL']
                #retorno_fundo_acum = json_tabela_retorno['ACUM']
    
            elif json_tabela_retorno['ANO'] == int(nome_ano) and json_tabela_retorno['RET (%)'] != 'FUNDO':
                retorno_benchmark_mes = json_tabela_retorno[nome_mes[:3].upper()] # 3 primeiras letras do mes p coletar retorno
                retorno_benchmark_ano = json_tabela_retorno['ANUAL']
                #retorno_benchmark_acum = json_tabela_retorno['ACUM']
    
        df_fundos.append({
                    'Fundo': nome_abreviacao.upper(),
                    'Benchmark': benchmark_name.upper(),
                    'Mes Fundo': retorno_fundo_mes,
                    'Mes Benchmark': retorno_benchmark_mes,
                    '12M Fundo': retorno_fundo_12m,
                    '12M Benchmark': retorno_benchmark_12m,
                    'Ano Fundo': retorno_fundo_ano,
                    'Ano Benchmark': retorno_benchmark_ano,
                    'Acum. Fundo': retorno_fundo,
                    'Acum. Benchmark': retorno_benchmark
                })
            
    df = pd.DataFrame(df_fundos)
    
    # Configurar o index como o nome do fundo e o benchmark
    df.set_index(['Benchmark', 'Fundo'], inplace=True)
    
    # Função para comparar e colorir pares de células
    def highlight_pair(val1, val2):
        if val1 > val2:
            return ['background-color: #228B22', 'background-color: #B22222']  # Val1 maior (verde escuro), Val2 menor (vermelho)
        elif val1 < val2:
            return ['background-color: #B22222', 'background-color: #228B22']  # Val1 menor (vermelho), Val2 maior (verde escuro)
        else:
            return ['', '']  # Sem cor se forem iguais
    
    # Função para aplicar as cores comparando pares de colunas
    def apply_highlight(row):
        return highlight_pair(row['Mes Fundo'], row['Mes Benchmark']) + \
               highlight_pair(row['12M Fundo'], row['12M Benchmark']) + \
               highlight_pair(row['Ano Fundo'], row['Ano Benchmark']) + \
               highlight_pair(row['Acum. Fundo'], row['Acum. Benchmark'])
    
    # Aplicar o estilo ao DataFrame usando style.apply
    df = df.style.apply(apply_highlight, axis=1)
    
    df = df.format(lambda x: f"{x:.2f}%", subset=pd.IndexSlice[:, :])

    return df, datas_cota
    

def portfolio_returns(fund, result_df):
    
    portfolio = fund
    ativos_no_portfolio = result_df[result_df.columns.intersection(portfolio['ticker'])] # apenas os ativos que estão no portfólio 
    pesos = portfolio.set_index('ticker').loc[ativos_no_portfolio.columns, 'pct_aum'] # ativos_no_portfolio é um df com as colunas sendo os tickers
    portfolio_returns = (ativos_no_portfolio * pesos).sum(axis=1) # soma por linha
    return portfolio_returns, pesos # return nos pesos p ver o quanto o retorno 

def atualiza():
    
    portfolio_gvmi = portfolio_request('gvmi')
    portfolio_div = portfolio_request('div')
    portfolio_fia = portfolio_request('fia')
    portfolio_abs = portfolio_request('abs')
    
    # ibov portfolio
    url = 'https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/eyJsYW5ndWFnZSI6ImVuLXVzIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjEyMCwiaW5kZXgiOiJJQk9WIiwic2VnbWVudCI6IjEifQ=='
    response = requests.get(url)
    portfolio_ibov = pd.DataFrame(response.json()['results'])
    portfolio_ibov = portfolio_ibov.rename(columns={'cod':'ticker',
                                                'part':'pct_aum'})
    portfolio_ibov.pct_aum = portfolio_ibov.pct_aum.astype('float') / 100
        
    assets = pd.concat([portfolio_gvmi['ticker'], 
                        portfolio_div['ticker'],
                        portfolio_fia['ticker'],
                        portfolio_abs['ticker'],
                        portfolio_ibov['ticker']]).drop_duplicates().reset_index(drop=True) 
    # Coletar e processar os dados para cada ativo
    dfs = []
    
    lista_assets_erro = []

    # Usando multithreading para fazer as requisições em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Fazendo as requisições e processando os dados em paralelo
        futures = [executor.submit(fetch_and_process_data, asset, lista_assets_erro) for asset in assets]
        
        for future in concurrent.futures.as_completed(futures):
            processed_df = future.result()
            if processed_df is not None:
                dfs.append(processed_df)

    # transformando a lista de erros em df após aplicar a funcao
    df_erro = pd.DataFrame(lista_assets_erro, columns=['Assets sem dados'])
    df_erro = df_erro[df_erro['Assets sem dados'].str.len() < 8].reset_index() # tira os bonds


    # unindo todos os tickers em 1 dataframe
    if dfs:
        result_df = pd.concat(dfs, axis=1)
        result_df.sort_index(inplace=True)
    else:
        st.write('Ainda não há dados!')
        print("Nenhum dado disponível")

    result_df = result_df.ffill() # considera a ultima variacao qnd for nan
    
    returns_gvmi, pesos_gvmi = portfolio_returns(portfolio_gvmi, result_df)
    returns_div, pesos_div = portfolio_returns(portfolio_div, result_df)
    returns_fia, pesos_fia = portfolio_returns(portfolio_fia, result_df)
    returns_abs, pesos_abs = portfolio_returns(portfolio_abs, result_df)
    returns_ibov, pesos_ibov = portfolio_returns(portfolio_ibov, result_df)

    # Função para definir a cor do titulo conforme o valor
    def cor_valor(valor):
        valor_formatado = f"{valor:.3f}".replace('.', ',')  # Formatar o valor e substituir ponto por vírgula
        if valor > 0:
            return f"<span style='color:green'>{valor_formatado}%</span>"
        elif valor < 0:
            return f"<span style='color:red'>{valor_formatado}%</span>"
        else:
            return f"<span style='color:black'>{valor_formatado}%</span>"
    
    # Definindo o título com HTML e cores conforme os valores
    titulo = f'FIA: {cor_valor(returns_fia.values[-1])} | ' \
             f'ABS: {cor_valor(returns_abs.values[-1])} | ' \
             f'DIV: {cor_valor(returns_div.values[-1])} | ' \
             f'GVMI: {cor_valor(returns_gvmi.values[-1])} | ' \
             f'IBOV: {cor_valor(returns_ibov.values[-1])}'

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=returns_fia.index,
        y=returns_fia.values,
        mode='lines',
        name='FIA',
        line=dict(color='#2ca02c')
    ))
    fig.add_trace(go.Scatter(
        x=returns_abs.index,
        y=returns_abs.values,
        mode='lines',
        name='ABS',
        line=dict(color='#8c564b')
    ))
    fig.add_trace(go.Scatter(
        x=returns_div.index,
        y=returns_div.values,
        mode='lines',
        name='DIV',
        line=dict(color='#ff7f0e')
    ))
    fig.add_trace(go.Scatter(
        x=returns_gvmi.index,
        y=returns_gvmi.values,
        mode='lines',
        name='GVMI',
        line=dict(color='#1f77b4')
    ))
    fig.add_trace(go.Scatter(
        x=returns_ibov.index,
        y=returns_ibov.values,
        mode='lines',
        name='IBOV',
        line=dict(color='#B0B0B0')
    ))
    
    fig.update_layout(
        title=f'Intraday Returns {returns_ibov.index[-1]} | {titulo}',
        width=1500,  # Largura
        height=500,  # Altura
        yaxis=dict(
            tickformat=".3f",  # Formatação do eixo y
            ticksuffix="%"
        ),
        shapes=[
            dict(
                type="line",
                x0=returns_fia.index.min(),  # Ponto inicial no eixo x (mínimo valor do índice)
                x1=returns_fia.index.max(),  # Ponto final no eixo x (máximo valor do índice)
                y0=0,  # Ponto inicial no eixo y
                y1=0,  # Ponto final no eixo y (fixo em 0)
                line=dict(
                    color="red",
                    width=0.65
                )
            )
        ]
    )
  

    return fig, pesos_gvmi, pesos_div, pesos_fia, pesos_abs, df_erro
