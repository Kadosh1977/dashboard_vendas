import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json

st.set_page_config(layout =  'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBORD DE VENDAS :shopping_trolley:')

## Formatação da barra lateral na API
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

## Carregamento da página
url = 'https://labdados.com/produtos'
query_string = {'regiao':regiao.lower(), 'ano':ano}
response = requests.get(url, params = query_string)
dados = response.json()
df = pd.DataFrame(dados)

df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format= '%d/%m/%Y')

#Filtro por vendedores na barra lateral
filtro_vendedores = st.sidebar.multiselect('Vendedores', df['Vendedor'].unique())
if filtro_vendedores:
    df = df[df['Vendedor'].isin(filtro_vendedores)]


## Tabela Receita
receita_estados = df.groupby('Local da compra')['Preço'].sum()
receita_estados = df.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index= True).sort_values('Preço', ascending = False)
receita_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()
receita_categorias = df.groupby('Categoria do Produto')['Preço'].sum().sort_values(ascending = False)

## Tabela Quantidade de Vendas

quantidade_estado = df.groupby('Local da compra')['Produto'].count()
quantidade_estado = df.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(quantidade_estado, left_on='Local da compra', right_index= True).sort_values('Produto', ascending = False)
quantidade_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Produto'].count().reset_index()
#min_quantidade = quantidade_mensal['Produto'].min()
max_quantidade = quantidade_mensal['Produto'].max()
quantidade_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
quantidade_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()
quantidade_categorias = df.groupby('Categoria do Produto')['Produto'].count().sort_values(ascending = False)

## Tabela vandedores:

vendedores = pd.DataFrame(df.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


## Gráficos Receitas
fig_mapa_receita = px.scatter_geo(receita_estados, lat = 'lat', lon = 'lon', scope = 'south america', size = 'Preço', template = 'seaborn', hover_name = 'Local da compra', hover_data = {'lat' : False, 'lon': False }, title = 'Receita por Estado')
fig_receita_mensal = px.line(receita_mensal,x = 'Mês', y = 'Preço', markers = True, range_y = (0, receita_mensal.max()), color='Ano', line_dash = 'Ano',title = 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')
fig_receita_estados = px.bar(receita_estados.head(), x = 'Local da compra', y = 'Preço', text_auto = True, title = 'Top estados')
fig_receita_estados.update_layout(yaxis_title = 'Receita')
fig_receita_categorias = px.bar(receita_categorias, text_auto = True, title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Gráficos Quantidades de Vendas
fig_mapa_quantidade_vendas = px.scatter_geo(quantidade_estado, lat = 'lat', lon = 'lon', scope = 'south america', size = 'Produto', template = 'seaborn', hover_name = 'Local da compra', hover_data = {'lat' : False, 'lon': False }, title = 'Vendas por Estado')
fig_quantidade_mensal = px.line(quantidade_mensal,x = 'Mês', y = 'Produto', markers = True, range_y = (180, max_quantidade), color='Ano', line_dash = 'Ano',title = 'Quantidade mensal')
fig_quantidade_mensal.update_layout(yaxis_title = 'Quantidade de vendas')
fig_quantidade_estado = px.bar(quantidade_estado.head(), x = 'Local da compra', y = 'Produto', text_auto = True, title = 'Top estados')
fig_quantidade_estado.update_layout(yaxis_title = 'Quantidade de vendas')
fig_quantidade_categorias = px.bar(quantidade_categorias, text_auto = True, title = 'Quantidade por categoria')

## Gráficos Vendedores



## visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

##with st.sidebar

with aba1:
    coluna1, colun2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(df['Preço'].sum(), 'R$' ))
        st.plotly_chart(fig_mapa_receita, use_container_widht = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with colun2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(df['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_quantidade_vendas, use_container_widht = True)
        st.plotly_chart(fig_quantidade_estado, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        st.plotly_chart(fig_quantidade_mensal, use_container_width = True)
        st.plotly_chart(fig_quantidade_categorias, use_container_width = True)



with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(df['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores), x='sum', y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index, text_auto=True, title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores), x='count', y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index, text_auto=True,  title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)


