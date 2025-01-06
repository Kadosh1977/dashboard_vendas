import streamlit as st
import requests
import pandas as pd
import json
import time

@st.cache_data

def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon = "✅")
    time.sleep(5)
    sucesso.empty()

st.title('Utilizando o filtro')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = response.json()
df = pd.DataFrame(dados)

df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format= '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Seleciona as colunas', list(df.columns), list(df.columns))
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione os Produtros', df['Produto'].unique(), df['Produto'].unique())
with st.sidebar.expander('Categoria do Produto'):
    categoria_produto = st.multiselect('Selecione a Categoria', df['Categoria do Produto'].unique(), df['Categoria do Produto'].unique())
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o Vendedor', df['Vendedor'].unique(), df['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o Estado', df['Local da compra'].unique(), df['Local da compra'].unique())
with st.sidebar.expander('Tipo de Pagamento'):
    tipo_pagamento = st.multiselect('Forma de Pagamento', df['Tipo de pagamento'].unique(), df['Tipo de pagamento'].unique())

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a data', (df['Data da Compra'].min(), df['Data da Compra'].max()))

with st.sidebar.expander('Preço'):
    preco = st.slider('Slecione o preço', 0, 5000, (0, 5000))
with st.sidebar.expander('Frete'):
    frete = st.slider('Selecione o frete', 0, 500, (0, 500))
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a nota', 0, 5, (0, 5))
with st.sidebar.expander('Parcelamento'):
    parcelamento = st.slider('Parcelamento', 0, 24, (0, 24))

query = '''Produto in @produtos and @preco[0] <= `Preço` <= @preco[1] and @data_compra[0] <= `Data da Compra` <= @data_compra[1] \
    and `Categoria do Produto` in @categoria_produto and Vendedor in @vendedor and `Local da compra` in @local_compra and `Tipo de pagamento`in @tipo_pagamento \
        and @frete[0] <= Frete <= @frete[1] and @avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and @parcelamento[0] <= `Quantidade de parcelas` <= @parcelamento[1]'''

dados_filtrados = df.query(query)
dados_filtrados = dados_filtrados[colunas]


st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
