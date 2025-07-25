
import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# Carregar perguntas do arquivo JSON
@st.cache_data
def carregar_perguntas():
    with open("questions_ethica.json", "r", encoding="utf-8") as f:
        return json.load(f)

perguntas = carregar_perguntas()
respostas = {}

# Etapas do diagnóstico
fases = ["Setup", "Assessment", "Resolution"]
fase_atual = st.sidebar.radio("Selecione a fase", fases)

st.title(f"ETHICA – Diagnóstico Ético de IA")
st.subheader(f"Etapa: {fase_atual}")

for idx, pergunta in enumerate(perguntas[fase_atual.lower()]):
    st.markdown(f"**{pergunta['pergunta']}**")
    score = st.slider("Nota (1=baixo, 5=alto)", 1, 5, key=f"{fase_atual}_{idx}")
    comentario = st.text_area("Comentário opcional", key=f"coment_{fase_atual}_{idx}")
    respostas[f"{fase_atual}_{idx}"] = {
        "pergunta": pergunta["pergunta"],
        "dimensao": pergunta["dimensao_ethica"],
        "score": score,
        "comentario": comentario,
        "riscos": pergunta["riscos_eticos"]
    }
    st.markdown("---")

if st.button("Finalizar Diagnóstico"):
    df = pd.DataFrame(respostas).T
    st.success("Diagnóstico concluído!")

    # Radar por dimensão
    media_dimensoes = df.groupby("dimensao")["score"].mean()
    st.subheader("Radar ETHICA")
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    categorias = list(media_dimensoes.index)
    valores = media_dimensoes.tolist()
    valores += valores[:1]
    angulos = [n / float(len(categorias)) * 2 * 3.1415 for n in range(len(categorias))]
    angulos += angulos[:1]
    ax.plot(angulos, valores, linewidth=2)
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_title("Dimensões ETHICA")
    st.pyplot(fig)

    # Riscos éticos com nota baixa
    st.subheader("Riscos Éticos Identificados")
    riscos = []
    for i in respostas.values():
        if i["score"] <= 3:
            riscos.extend(i["riscos"])
    riscos_unicos = sorted(set(riscos))
    if riscos_unicos:
        for risco in riscos_unicos:
            st.markdown(f"- ⚠️ {risco}")
    else:
        st.markdown("✅ Nenhum risco crítico identificado.")

    # Gerar relatório PDF
    if st.button("Exportar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Relatório ETHICA", ln=True, align="C")
        pdf.ln(5)
        for fase in fases:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, f"Fase: {fase}", ln=True)
            for idx, row in df.iterrows():
                if idx.startswith(fase):
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(0, 8, f"{row['pergunta']} (Nota: {row['score']})\nComentário: {row['comentario']}")
            pdf.ln(5)
        pdf.output("relatorio_ethica.pdf")
        st.success("Relatório PDF gerado com sucesso.")
        with open("relatorio_ethica.pdf", "rb") as file:
            st.download_button("📄 Baixar PDF", file.read(), file_name="relatorio_ethica.pdf")
