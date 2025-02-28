import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from datetime import datetime
import csv
import shutil

# Configuração da página para modo wide
st.set_page_config(layout="wide")

# Função para classificar o IMC infantil
def classificar_imc_infantil(imc, idade, sexo):
    # Tabela de referência de percentis para IMC (valores aproximados)
    # Percentil 5, 85 e 95 para crianças de 4 a 5 anos
    tabela_percentis = {
        4: {"M": {"p5": 14.0, "p85": 16.0, "p95": 17.0},  # Masculino
            "F": {"p5": 13.8, "p85": 15.8, "p95": 16.8}}, # Feminino
        5: {"M": {"p5": 14.5, "p85": 16.5, "p95": 17.5},  # Masculino
            "F": {"p5": 14.3, "p85": 16.3, "p95": 17.3}}  # Feminino
    }

    # Obtém os percentis para a idade e sexo
    p5 = tabela_percentis[idade][sexo]["p5"]
    p85 = tabela_percentis[idade][sexo]["p85"]
    p95 = tabela_percentis[idade][sexo]["p95"]

    # Classifica o IMC
    if imc < p5:
        return "Abaixo do peso"
    elif p5 <= imc < p85:
        return "Peso normal"
    elif p85 <= imc < p95:
        return "Sobrepeso"
    else:
        return "Obesidade"

# Função para carregar dados do CSV
def carregar_dados():
    try:
        dados = pd.read_csv('dados_criancas.csv', names=["Nome", "Idade", "Altura", "Peso", "IMC", "Data da Pesagem", "Sexo"])
        # Adicionar classificação do IMC infantil
        dados["Classificação"] = dados.apply(
            lambda row: classificar_imc_infantil(row["IMC"], row["Idade"], row["Sexo"]),
            axis=1
        )
        return dados
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Idade", "Altura", "Peso", "IMC", "Data da Pesagem", "Sexo", "Classificação"])

# Função para calcular o IMC
def calcular_imc(peso, altura):
    return peso / (altura ** 2)

# Função para gerar descrição do IMC
def gerar_descricao_imc(classificacao):
    if classificacao == "Abaixo do peso":
        return "A criança está abaixo do peso ideal. Recomenda-se acompanhamento nutricional."
    elif classificacao == "Peso normal":
        return "A criança está no peso ideal. Parabéns!"
    elif classificacao == "Sobrepeso":
        return "A criança está com sobrepeso. Recomenda-se atenção à alimentação e prática de atividades físicas."
    else:
        return "A criança está com obesidade. Recomenda-se acompanhamento médico e nutricional."

# Função para salvar dados no CSV
def salvar_dados(nome, idade, altura, peso, imc, data_pesagem, sexo):
    with open('dados_criancas.csv', mode='a', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([nome, idade, altura, peso, imc, data_pesagem, sexo])

# Função para gerar certificado em PDF
def gerar_certificado(nome, idade, altura, peso, imc, descricao, data_pesagem, sexo):
    if not os.path.exists("certificados"):
        os.makedirs("certificados")
    
    # Substitui as barras na data por hífens
    data_formatada = data_pesagem.replace("/", "-")
    filename = f"certificados/{nome}_{data_formatada}_certificado.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Certificado de Saúde Infantil")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Nome: {nome}")
    c.drawString(100, 670, f"Idade: {idade} anos")
    c.drawString(100, 640, f"Altura: {altura:.2f} m")
    c.drawString(100, 610, f"Peso: {peso:.2f} kg")
    c.drawString(100, 580, f"IMC: {imc:.2f} ({classificar_imc_infantil(imc, idade, sexo)})")
    c.drawString(100, 550, f"Data da Pesagem: {data_pesagem}")
    c.drawString(100, 520, "Descrição:")
    c.drawString(100, 490, descricao)
    c.save()
    return filename

# Função para limpar todos os dados
def limpar_dados():
    # Remove o arquivo de dados
    if os.path.exists("dados_criancas.csv"):
        os.remove("dados_criancas.csv")
    
    # Remove a pasta de certificados e seu conteúdo
    if os.path.exists("certificados"):
        shutil.rmtree("certificados")
    
    st.success("Todos os dados e certificados foram removidos com sucesso!")

# Página Inicial
def pagina_inicial():
    st.title("Bem-vindo ao Sistema IMCKIDS")
    st.write("Desenvolvido por Marcelo Pereira, aluno do curso de Tecnologia em Ciência de Dados da UNINTER")
    st.markdown("""
    O **Sistema IMCKIDS** é uma ferramenta desenvolvida para uma escola infantil, com o objetivo de calcular o **Índice de Massa Corporal (IMC)** de crianças de **4 a 5 anos**.  
    Este sistema utiliza critérios específicos para classificar o IMC infantil, com base em **percentis de crescimento**.  
    É importante destacar que ele **não é adequado** para o cálculo de IMC de adultos ou crianças fora dessa faixa etária.  
    **Para outras faixas etárias ou situações específicas, consulte um profissional de saúde.**  
    
    ### Atenção:
    "Este sistema encontra-se em uma versão de desenvolvimento (protótipo) e ainda receberá correções e melhorias ao longo do tempo."
    
    ### Como usar:
    1. **Cadastro**: Na página de cadastro, insira os dados da criança (nome, idade, altura, peso e sexo) para calcular o IMC.
    2. **Certificados**: Após o cadastro, você pode gerar e baixar um certificado com os dados da criança.
    3. **Análises e Gráficos**: Visualize gráficos e análises dos dados cadastrados.
    4. **Limpar Dados**: Use o botão no menu lateral para remover todos os dados e certificados, caso deseje começar do zero.

    
    """)

# Página de Cadastro
def pagina_cadastro():
    st.title("Cadastro de Crianças e Cálculo de IMC")

    # Formulário para inserção de dados
    with st.form("form_imc"):
        nome = st.text_input("Nome da criança")
        idade = st.number_input("Idade da criança", min_value=4, max_value=5, step=1)
        altura = st.number_input("Altura da criança (em metros)", min_value=0.5, max_value=2.5, step=0.01)
        peso = st.number_input("Peso da criança (em kg)", min_value=5.0, max_value=100.0, step=0.1)
        sexo = st.selectbox("Sexo da criança", options=["M", "F"], format_func=lambda x: "Masculino" if x == "M" else "Feminino")
        data_pesagem = st.date_input("Data da Pesagem", datetime.today())
        enviar = st.form_submit_button("Calcular IMC e Salvar")

        if enviar:
            if altura <= 0 or peso <= 0:
                st.error("Altura e peso devem ser maiores que zero.")
            else:
                imc = calcular_imc(peso, altura)
                classificacao = classificar_imc_infantil(imc, idade, sexo)
                descricao = gerar_descricao_imc(classificacao)
                st.success(f"O IMC da criança {nome} é: {imc:.2f} ({classificacao})")
                salvar_dados(nome, idade, altura, peso, imc, data_pesagem.strftime("%d/%m/%Y"), sexo)
                st.info("Dados salvos com sucesso!")

                # Gerar certificado
                certificado_path = gerar_certificado(nome, idade, altura, peso, imc, descricao, data_pesagem.strftime("%d/%m/%Y"), sexo)
                st.session_state.certificado_path = certificado_path  # Armazena o caminho do certificado na sessão

    # Botão de download fora do formulário
    if "certificado_path" in st.session_state:
        with open(st.session_state.certificado_path, "rb") as f:
            st.download_button(
                label="Baixar Certificado",
                data=f,
                file_name=os.path.basename(st.session_state.certificado_path),
                mime="application/pdf"
            )

# Página de Certificados
def pagina_certificados():
    st.title("Certificados Gerados")

    if not os.path.exists("certificados"):
        st.warning("Nenhum certificado gerado ainda.")
        return

    certificados = os.listdir("certificados")
    if not certificados:
        st.warning("Nenhum certificado gerado ainda.")
    else:
        for certificado in certificados:
            with open(f"certificados/{certificado}", "rb") as f:
                st.download_button(
                    label=f"Baixar {certificado}",
                    data=f,
                    file_name=certificado,
                    mime="application/pdf"
                )

# Página de Análises e Gráficos
def pagina_analises():
    st.title("Análises e Gráficos")

    dados = carregar_dados()
    if dados.empty:
        st.warning("Nenhum dado cadastrado ainda.")
    else:
        # Linha 1: Dados Salvos e Gráfico de Pizza
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Dados Salvos")
            st.dataframe(dados)

        with col2:
            st.subheader("Gráfico de Pizza: Distribuição por Classificação de IMC")
            classificacao_counts = dados["Classificação"].value_counts()
            fig_pizza = px.pie(
                classificacao_counts,
                values=classificacao_counts.values,
                names=classificacao_counts.index,
                title="Distribuição por Classificação de IMC"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

        # Linha 2: Gráfico de Barras e Gráfico de Barras Empilhadas
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Gráfico de Barras: Idade, Peso e IMC por Criança")
            fig_barras = go.Figure()
            fig_barras.add_trace(go.Bar(
                x=dados["Nome"],
                y=dados["Idade"],
                name="Idade",
                marker_color='blue'
            ))
            fig_barras.add_trace(go.Bar(
                x=dados["Nome"],
                y=dados["Peso"],
                name="Peso",
                marker_color='green'
            ))
            fig_barras.add_trace(go.Bar(
                x=dados["Nome"],
                y=dados["IMC"],
                name="IMC",
                marker_color='orange'
            ))
            fig_barras.update_layout(
                barmode='group',
                xaxis_title="Criança",
                yaxis_title="Valores",
                title="Idade, Peso e IMC por Criança"
            )
            st.plotly_chart(fig_barras, use_container_width=True)

        with col4:
            st.subheader("Gráfico de Barras Empilhadas: Contribuição por Criança")
            fig_empilhadas = go.Figure()
            fig_empilhadas.add_trace(go.Bar(
                x=dados["Nome"],
                y=dados["Idade"],
                name="Idade",
                marker_color='blue'
            ))
            fig_empilhadas.add_trace(go.Bar(
                x=dados["Nome"],
                y=dados["Peso"],
                name="Peso",
                marker_color='green'
            ))
            fig_empilhadas.add_trace(go.Bar(
                x=dados["Nome"],
                y=dados["IMC"],
                name="IMC",
                marker_color='orange'
            ))
            fig_empilhadas.update_layout(
                barmode='stack',
                xaxis_title="Criança",
                yaxis_title="Valores",
                title="Contribuição de Idade, Peso e IMC por Criança"
            )
            st.plotly_chart(fig_empilhadas, use_container_width=True)

# Menu Lateral
def main():
    st.sidebar.title("Menu")
    pagina = st.sidebar.radio("Selecione a Página", ["Página Inicial", "Cadastro", "Certificados", "Análises e Gráficos"])

    # Botão para limpar dados
    if st.sidebar.button("Limpar Dados"):
        limpar_dados()

    if pagina == "Página Inicial":
        pagina_inicial()
    elif pagina == "Cadastro":
        pagina_cadastro()
    elif pagina == "Certificados":
        pagina_certificados()
    elif pagina == "Análises e Gráficos":
        pagina_analises()

if __name__ == "__main__":
    main()
