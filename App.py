import pandas as pd 
import streamlit as st 
import altair as alt
import datetime as dt
from PIL import Image   



# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title='Dashboard de Vendas',
    page_icon='$',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.meuoutrosite.com.br',
        'about': 'Ess app foi desenvolvido para estudos de análise de dados.'
    }
)

# ---- Criar o dataFrame

df = pd.read_excel(
    io = './Datasets/system_extraction.xlsx',
    engine='openpyxl',
    sheet_name='salesreport',
    usecols='A:J,',
    nrows=4400
)

# --- Criar o sidebar
with st.sidebar:
    logo_teste = Image.open('./Mídia/logo vizion.png')
    st.image(logo_teste, width=300)
    st.subheader("MENU - DASHBOARD")
    fVendedor = st.selectbox(
        "Selecione o Vendedor:",
        options=df["Vendedor"].unique()
    )
    
    fProduto = st.selectbox(
        "Selecione o Produto:",
        options=df["Produto vendido"].unique()
    )
    fCliente = st.selectbox(
        "Selecione o Cliente:",
        options=df["Cliente"].unique()
    )
#Tabela Qtde vendida por produto    
tab1_qtde_produto = df.loc[(
    df["Vendedor"] == fVendedor) &
    (df["Cliente"] == fCliente)
]
tab1_qtde_produto = tab1_qtde_produto.drop(columns=['Data'])
tab1_qtde_produto = tab1_qtde_produto.groupby('Produto vendido').sum(numeric_only=True).reset_index()

#Tabela de Vendas e Margem
tab2_vendas_margem = df.loc[(
    df['Vendedor'] == fVendedor) &
    (df['Produto vendido'] == fProduto) &
    (df['Cliente'] == fCliente)
]

#Tabela Vendas por Vendedor
tab3_Vendas_Vendedor = df.loc[(
    df['Produto vendido'] == fProduto) &
    (df['Cliente'] == fCliente)
]
tab3_Vendas_Vendedor = tab3_Vendas_Vendedor.groupby('Vendedor').sum(numeric_only=True).reset_index()
tab3_Vendas_Vendedor = tab3_Vendas_Vendedor.drop(columns=['Nº pedido', 'Preço'])

#Vendas por Cliente
tab4_Venda_Cliente = df.loc[(
    df['Vendedor'] == fVendedor) &
    (df['Produto vendido'] == fProduto) 
]
tab4_Venda_Cliente = tab4_Venda_Cliente.groupby('Cliente').sum(numeric_only=True).reset_index()

#Vendas Mensais
tab5_vendas_mensais = df.loc[(
    df['Vendedor'] == fVendedor) &
    (df['Produto vendido'] == fProduto) &
    (df['Cliente'] == fCliente)
]
tab5_vendas_mensais['mm'] = tab5_vendas_mensais['Data'].dt.strftime('%m/%y')
##### PADRÕES #########
cor_grafico = '#9DD1F1'
altura_grafico = 250

#GRÁFICO 1.0 Qtde vendida por produto
graf1_qtde_produto = alt.Chart(tab1_qtde_produto).mark_bar(
    color= cor_grafico,
    cornerRadiusTopLeft=9,
    cornerRadiusTopRight=9,
).encode(
    x = 'Produto vendido',
    y = 'Quantidade',
    tooltip = ['Produto vendido', 'Quantidade']
).properties(height=altura_grafico, title='QUANTIDADE VENDIDA POR PRODUTO'
).configure_axis(grid=False).configure_view(strokeWidth=0)

#GRÁFICO 1.1 Valor da venda por produto
graf1_valor_produto = alt.Chart(tab1_qtde_produto).mark_bar(
    color= cor_grafico,
    cornerRadiusTopLeft=9,
    cornerRadiusTopRight=9,
).encode(
    x = 'Produto vendido',
    y = 'Quantidade',
    tooltip = ['Produto vendido', 'Valor Pedido']
).properties(height=altura_grafico, title='VALOR TOTAL POR PRODUTO'
).configure_axis(grid=False).configure_view(strokeWidth=0)

#GRAFICO Tabela Vendas por Vendedor
graf2_Vendas_Vendedor = alt.Chart(tab3_Vendas_Vendedor).mark_arc(
    innerRadius=100,
    outerRadius=150
).encode(
    theta = alt.Theta(field='Valor Pedido', type='quantitative', stack=True),
    color=alt.Color(
        field='Vendedor',
        type='nominal',
        legend=None
    ),
    tooltip=['Vendedor', 'Valor Pedido']
).properties(height=500, width=560, title='VALOR VENDA POR VENDEDOR')
rot2Ve = graf2_Vendas_Vendedor.mark_text(radius=210, size=14).encode(text='Vendedor')
rot2Vp = graf2_Vendas_Vendedor.mark_text(radius=180, size=12).encode(text='Valor Pedido')

#GRAFICO Vendas por cliente
graf4_vendas_cliente = alt.Chart(tab4_Venda_Cliente).mark_bar(
    color= cor_grafico,
    cornerRadiusTopLeft=9,
    cornerRadiusTopRight=9,
).encode(
    x = 'Cliente',
    y = 'Valor Pedido',
    tooltip = ['Cliente', 'Valor Pedido']
).properties(height=altura_grafico, title='VENDAS POR CLIENTE'
).configure_axis(grid=False).configure_view(strokeWidth=0)

# VENDAS MENSAIS
graf5_vendas_mensais = alt.Chart(tab5_vendas_mensais).mark_line(
    color=cor_grafico,
).encode(
   alt.X('monthdate(Data):T'),
   y = 'Valor Pedido:Q'
).properties(height=altura_grafico, title= 'VENDAS MENSAL').configure_axis(grid=False).configure_view(strokeWidth=0)

### PÁGINA PRINCIPAL ###

total_vendas = round(tab2_vendas_margem['Valor Pedido'].sum(numeric_only=True), 2)
total_margem = round(tab2_vendas_margem['Margem Lucro'].sum(numeric_only=True), 2)
porc_margem = int(100*total_margem/total_vendas)

st.header(":bar_chart: DASHBOARD DE VENDAS")

dst1, dst2, dst3, dst4 = st.columns([1,1,1,1])

with dst1:
    st.write("**VENDAS TOTAIS:**")
    st.info(f"R$ {total_vendas}")

with dst2:
    st.write('**MARGEN TOTAL:**')
    st.info(f"R$ {total_margem}")
    
with dst3:
    st.write('**MARGEM %**')
    st.info(f"{porc_margem}%")
st.markdown('---')    

### Colunas dos gráficos

col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.altair_chart(graf4_vendas_cliente, use_container_width=True) 
    st.altair_chart(graf5_vendas_mensais, use_container_width=True)

with col2:
    st.altair_chart(graf1_qtde_produto, use_container_width=True)
    st.altair_chart(graf1_valor_produto, use_container_width=True)
    
with col3:
    st.altair_chart(graf2_Vendas_Vendedor+rot2Ve+rot2Vp, use_container_width=True)
st.markdown('---')
