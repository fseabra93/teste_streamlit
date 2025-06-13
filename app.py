import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import os

# --- Configuração da Página e Título ---
st.set_page_config(
    page_title="Assistente de Documento",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Assistente Especialista")
st.caption("Faça perguntas sobre o documento e eu responderei com base no seu conteúdo.")

# --- Configuração da API Key na Barra Lateral ---
st.sidebar.header("Configurações")
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = st.sidebar.text_input("Sua Chave de API do Gemini", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro ao configurar com a API do Gemini: {e}")
        st.stop()
else:
    st.info("Por favor, insira sua chave de API do Gemini na barra lateral para começar.")
    st.stop()

# --- Função para carregar e extrair texto do PDF local ---
# @st.cache_data é ESSENCIAL para performance. Ele garante que o PDF
# seja lido e processado apenas UMA VEZ.
@st.cache_data
def carregar_texto_pdf_local(caminho_do_arquivo):
    """Lê um arquivo PDF local e retorna seu conteúdo como texto."""
    if not os.path.exists(caminho_do_arquivo):
        st.error(f"Arquivo não encontrado em: {caminho_do_arquivo}")
        return None
    try:
        with fitz.open(caminho_do_arquivo) as doc:
            texto_completo = ""
            for page in doc:
                texto_completo += page.get_text()
        return texto_completo
    except Exception as e:
        st.error(f"Não foi possível ler o PDF local: {e}")
        return None

# --- Lógica Principal ---

# 1. DEFINA O NOME DO SEU ARQUIVO PDF AQUI
NOME_DO_ARQUIVO_PDF = "Lic_Computacao_Metodologia-Pesquisa-Cientifica.pdf"  # <--- MUDE AQUI PARA O NOME DO SEU ARQUIVO

# 2. Carrega o texto do PDF (usando o cache)
texto_do_pdf = carregar_texto_pdf_local(NOME_DO_ARQUIVO_PDF)


# 3. Mostra a interface de perguntas apenas se o PDF foi carregado com sucesso
if texto_do_pdf:
    st.header("Faça sua pergunta sobre o documento")

    prompt_usuario = st.text_area(
        "Sua pergunta:",
        height=100,
        placeholder="Ex: Qual é o principal tópico do documento?"
    )

    if st.button("Enviar Pergunta"):
        if not prompt_usuario:
            st.warning("Por favor, digite uma pergunta.")
        else:
            # Montando o Prompt para o Gemini
            prompt_para_gemini = f"""
            Com base EXCLUSIVAMENTE no seguinte texto extraído de um documento, responda à pergunta do usuário.
            Se a resposta não estiver contida no texto, diga claramente: "Não encontrei essa informação no documento.".
            Não utilize nenhum conhecimento externo.

            --- TEXTO DO DOCUMENTO ---
            {texto_do_pdf}
            -------------------------

            --- PERGUNTA DO USUÁRIO ---
            {prompt_usuario}
            """

            try:
                with st.spinner("Analisando o documento e preparando sua resposta..."):
                    response = model.generate_content(prompt_para_gemini)

                st.subheader("Resposta:")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar a resposta: {e}")
else:
    st.warning("O PDF não pôde ser carregado. Verifique o nome do arquivo e se ele está na pasta correta.")


# --- Rodapé ---
st.markdown("---")
st.markdown("Feito com ❤️ usando [Streamlit](https://streamlit.io) e [Gemini](https://ai.google.dev/).")