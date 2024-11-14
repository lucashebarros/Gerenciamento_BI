import streamlit as st
import pandas as pd
from datetime import date
from collections import Counter
import plotly.express as px

# Funções para gerenciamento de projetos
def adicionar_projeto_na_lista(nome, descricao, status, data_inicio, data_fim):
    projetos = st.session_state['projetos']
    projetos.append({
        'id': len(projetos) + 1,
        'nome': nome,
        'descricao': descricao,
        'status': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })
    st.session_state['projetos'] = projetos

def obter_projetos():
    return st.session_state['projetos']

def atualizar_status_projeto(nome, novo_status):
    projetos = st.session_state['projetos']
    for p in projetos:
        if p['nome'] == nome:
            p['status'] = novo_status
            st.session_state['projetos'] = projetos
            return True
    return False

def obter_estatisticas_projetos():
    projetos = st.session_state['projetos']
    status_list = [p['status'] for p in projetos]
    contagem = Counter(status_list)
    estatisticas = list(contagem.items())
    return estatisticas

# Função para calcular o progresso do projeto com base nas datas
def calcular_progresso(data_inicio, data_fim):
    hoje = date.today()
    total_dias = (data_fim - data_inicio).days
    dias_passados = (hoje - data_inicio).days
    if total_dias > 0:
        progresso = max(0, min(100, int((dias_passados / total_dias) * 100)))
    else:
        progresso = 100  # Se a data de início e fim são as mesmas, progresso é 100%
    return progresso

# Função para obter o badge do status
def get_status_badge(status):
    status_dict = {
        'Parado': '🔴 Parado',
        'Em Andamento': '🟢 Em Andamento',
        'Em Desenvolvimento': '🟡 Em Desenvolvimento',
        'Em Finalização': '🔵 Em Finalização'
    }
    return status_dict.get(status, status)

# Interface do usuário
def main():
    st.title('Gerenciamento de Projetos de BI')

    # Inicializar session_state para projetos
    if 'projetos' not in st.session_state:
        st.session_state['projetos'] = []

    # Inicializar estado de login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Inicializar estado da página do aplicativo
    if 'app_page' not in st.session_state:
        st.session_state['app_page'] = 'visao_geral'

    if not st.session_state['logged_in']:
        # Exibir página de login
        pagina_login()
    else:
        # Exibir interface do aplicativo
        aplicativo()

def pagina_login():
    st.subheader('Área de Login')

    usuario = st.text_input('Usuário', key='login_usuario')
    senha = st.text_input('Senha', type='password', key='login_senha')

    if st.button('Entrar', key='entrar_button'):
        # Usuário e senha fixos
        usuario_correto = "BI Garbuio"
        senha_correta = "G@rbuio23"

        if usuario == usuario_correto and senha == senha_correta:
            st.success(f'Bem-vindo(a), {usuario}!')
            st.session_state['usuario'] = usuario
            # Definir que o usuário está logado
            st.session_state['logged_in'] = True
            # Redirecionar para a página principal do aplicativo
            st.experimental_rerun()
        else:
            st.warning('Usuário ou senha incorretos')

def aplicativo():
    st.subheader('Bem-vindo ao Sistema de Gerenciamento de Projetos')

    # Menu interno do aplicativo com chaves únicas
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        if st.button('Visão Geral', key='visao_geral_button'):
            st.session_state.app_page = 'visao_geral'
    with col2:
        if st.button('Adicionar Projeto', key='adicionar_projeto_button'):
            st.session_state.app_page = 'adicionar_projeto'
    with col3:
        if st.button('Atualizar Status', key='atualizar_status_button'):
            st.session_state.app_page = 'atualizar_status'
    with col4:
        if st.button('Relatórios', key='relatorios_button'):
            st.session_state.app_page = 'relatorios'
    with col5:
        if st.button('Logout', key='logout_button'):
            st.session_state.logged_in = False
            st.session_state.usuario = ''
            st.session_state.app_page = 'visao_geral'
            st.experimental_rerun()

    # Navegação entre as páginas do aplicativo
    if st.session_state.app_page == 'visao_geral':
        visao_geral()
    elif st.session_state.app_page == 'adicionar_projeto':
        adicionar_projeto()
    elif st.session_state.app_page == 'atualizar_status':
        atualizar_status()
    elif st.session_state.app_page == 'relatorios':
        relatorios()

def visao_geral():
    st.subheader('Lista de Projetos')

    projetos_lista = obter_projetos()
    if projetos_lista:
        # Criar DataFrame com informações adicionais de progresso
        df = pd.DataFrame(projetos_lista)
        df['Progresso (%)'] = df.apply(lambda row: calcular_progresso(row['data_inicio'], row['data_fim']), axis=1)

        # Converter datas para string para melhor visualização na tabela
        df['data_inicio_str'] = df['data_inicio'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df['data_fim_str'] = df['data_fim'].apply(lambda x: x.strftime('%d/%m/%Y'))

        # Mapear status para badges
        df['Status'] = df['status'].apply(get_status_badge)

        # Selecionar colunas para exibição
        df_display = df[['id', 'nome', 'Status', 'data_inicio_str', 'data_fim_str', 'Progresso (%)']].copy()
        df_display.rename(columns={
            'id': 'ID',
            'nome': 'Projeto',
            'data_inicio_str': 'Data Início',
            'data_fim_str': 'Data Fim',
        }, inplace=True)

        # Exibir tabela
        st.table(df_display)

        # Exibir detalhes de cada projeto em expansores
        st.write("### Detalhes dos Projetos")
        for index, row in df.iterrows():
            with st.expander(f"📁 {row['nome']}"):
                cols = st.columns([2, 1])
                with cols[0]:
                    st.markdown(f"**Descrição:** {row['descricao']}")
                    st.markdown(f"**Status:** {get_status_badge(row['status'])}")
                    st.markdown(f"**Data de Início:** {row['data_inicio_str']}")
                    st.markdown(f"**Data de Fim:** {row['data_fim_str']}")
                with cols[1]:
                    st.markdown(f"**Progresso:**")
                    st.progress(row['Progresso (%)'] / 100)

        # Visualização de Gantt Chart com melhor layout
        st.write("### Cronograma dos Projetos")
        fig = px.timeline(
            df,
            x_start="data_inicio",
            x_end="data_fim",
            y="nome",
            color="status",
            title="Cronograma dos Projetos",
            labels={"nome": "Projeto", "status": "Status"}
        )
        fig.update_yaxes(categoryorder="total ascending")
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Projetos",
            showlegend=True,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info('Nenhum projeto cadastrado.')

def adicionar_projeto():
    st.subheader('Adicionar Novo Projeto')
    with st.form(key='add_project_form'):
        nome = st.text_input('Nome do Projeto')
        descricao = st.text_area('Descrição')
        status = st.selectbox(
            'Status',
            ['Parado', 'Em Andamento', 'Em Desenvolvimento', 'Em Finalização']
        )
        data_inicio = st.date_input('Data de Início')
        data_fim = st.date_input('Data de Fim')
        submit_button = st.form_submit_button(label='Adicionar')

    if submit_button:
        if nome and descricao:
            adicionar_projeto_na_lista(nome, descricao, status, data_inicio, data_fim)
            st.success('Projeto adicionado com sucesso!')
            # Recarregar a página para atualizar o formulário
            st.experimental_rerun()
        else:
            st.warning('Por favor, preencha todos os campos.')

def atualizar_status():
    st.subheader('Atualizar Status do Projeto')
    projetos_lista = obter_projetos()
    if projetos_lista:
        df = pd.DataFrame(projetos_lista)
        lista_projetos = df['nome'].tolist()
        escolha_projeto = st.selectbox('Selecione o Projeto', lista_projetos)
        novo_status = st.selectbox('Novo Status', ['Parado', 'Em Andamento', 'Em Desenvolvimento', 'Em Finalização'])
        if st.button('Atualizar Status'):
            sucesso = atualizar_status_projeto(escolha_projeto, novo_status)
            if sucesso:
                st.success('Status atualizado com sucesso!')
            else:
                st.error('Erro ao atualizar o status do projeto.')
    else:
        st.info('Nenhum projeto cadastrado.')

def relatorios():
    st.subheader('Relatórios e Análises')
    
    # Exibir contagem de projetos por status em um gráfico de barras
    estatisticas = obter_estatisticas_projetos()
    if estatisticas:
        df_estatisticas = pd.DataFrame(estatisticas, columns=['Status', 'Quantidade'])
        
        # Mapear status para badges
        df_estatisticas['Status'] = df_estatisticas['Status'].apply(get_status_badge)
        
        st.write("### Contagem de Projetos por Status")
        fig_bar = px.bar(
            df_estatisticas,
            x='Status',
            y='Quantidade',
            title='Contagem de Projetos por Status',
            labels={'Quantidade': 'Número de Projetos'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Gráfico de pizza para distribuição dos projetos por status
        st.write("### Distribuição de Projetos por Status")
        fig_pizza = px.pie(
            df_estatisticas,
            names='Status',
            values='Quantidade',
            title="Distribuição de Projetos"
        )
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pizza, use_container_width=True)

    else:
        st.info("Nenhum projeto cadastrado para gerar relatórios.")

    # Mostrar a lista de projetos com progresso e datas
    projetos_lista = obter_projetos()
    if projetos_lista:
        st.write("### Progresso dos Projetos por Data")

        # Criar um DataFrame dos projetos com colunas adicionais
        df_projetos = pd.DataFrame(projetos_lista)
        df_projetos['Progresso (%)'] = df_projetos.apply(
            lambda row: calcular_progresso(row['data_inicio'], row['data_fim']), axis=1
        )
        df_projetos['Dias Restantes'] = (df_projetos['data_fim'] - date.today()).dt.days
        df_projetos['Data Início'] = df_projetos['data_inicio'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df_projetos['Data Fim'] = df_projetos['data_fim'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df_projetos['Status'] = df_projetos['status'].apply(get_status_badge)

        # Exibir a tabela com progresso e dias restantes
        st.table(df_projetos[['nome', 'Status', 'Data Início', 'Data Fim', 'Progresso (%)', 'Dias Restantes']])

        # Exibir uma visualização de Gantt Chart
        st.write("### Cronograma dos Projetos (Gráfico de Gantt)")
        fig_gantt = px.timeline(
            df_projetos,
            x_start="data_inicio",
            x_end="data_fim",
            y="nome",
            color="status",
            title="Linha do Tempo dos Projetos",
            labels={"nome": "Projeto", "status": "Status"}
        )
        fig_gantt.update_yaxes(categoryorder="total ascending")
        fig_gantt.update_layout(
            xaxis_title="Data",
            yaxis_title="Projetos",
            showlegend=True,
            height=600
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

    else:
        st.info("Nenhum projeto cadastrado para exibir o progresso por data.")

# Chamada da função principal
if __name__ == '__main__':
    main()
