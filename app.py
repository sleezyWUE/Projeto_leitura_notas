import os
import csv
from datetime import datetime
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==============================================================================
# 1. INITIALIZATION & CORE CONFIGURATIONS
# ==============================================================================

DATABASE_FILE = "Captura_Notas_Fiscais.csv"

# Força a criação do arquivo CSV com cabeçalhos caso ele não exista no servidor em nuvem
if not os.path.exists(DATABASE_FILE) or os.path.getsize(DATABASE_FILE) == 0:
    with open(DATABASE_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "transaction_id", 
            "timestamp", 
            "employee_name",
            "file_path", 
            "user_description", 
            "headcount", 
            "extracted_emission_date", 
            "extracted_total_value",
            "fiscal_id"
        ])

# Busca a credencial de forma segura e oculta nas configurações do Streamlit Cloud
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

CATEGORIES = [
    "ÁGUA", "ALMOÇO", "CAFÉ DA MANHÃ", "CARGA", "COMBUSTÍVEL", "CRÉDITO",
    "ENVIO DE MATERIAL", "ESTACIONAMENTO", "FARMÁCIA", "FERRAMENTAS",
    "HOTEL", "JANTA", "LAVAGEM CARRO", "LAVANDERIA",
    "MATERIAL DE ESCRITÓRIO", "MATERIAL OBRA", "MERCADO", "OUTROS",
    "PASSAGEM", "PEÇAS CARRO", "PEDÁGIO", "REEMBOLSO", "SAQUE",
    "TAXA DE SAQUE", "UBER"
]

if "form_key" not in st.session_state:
    st.session_state.form_key = 0

# ==============================================================================
# 2. APPLICATION INTERFACE (FRONT-END)
# ==============================================================================

st.set_page_config(
    page_title="Data Capture System - Expense Control",
    page_icon="🧾",
    layout="centered"
)

st.title("Sistema de Captura e Auditoria de Despesas")
st.markdown("---")

st.subheader("1. Informações Operacionais")

with st.form(key=f"expense_form_{st.session_state.form_key}", clear_on_submit=True):
    
    employee_name = st.text_input("Nome do Funcionário", placeholder="Digite seu nome completo")
    user_description = st.selectbox("Finalidade do Gasto / Descrição", options=CATEGORIES, index=1)
    headcount = st.number_input("Quantidade de Beneficiários (Pessoas)", min_value=1, value=1, step=1)

    st.subheader("2. Digitalização do Comprovante")
    captured_file = st.file_uploader("Insira ou tire a foto do cupom fiscal", type=["png", "jpg", "jpeg"])

    submit_button = st.form_submit_button("Processar Documento e Sincronizar", type="primary")

# ==============================================================================
# 3. CORE PROCESSING PIPELINE
# ==============================================================================

if submit_button:
    if not employee_name:
        st.error("Erro: O campo 'Nome do Funcionário' é obrigatório.")
    elif not captured_file:
        st.error("Erro: Nenhuma imagem detectada para processamento.")
    else:
        with st.spinner("Executando pipeline de extração por Visão Computacional..."):
            try:
                # Carrega a imagem direto na memória RAM (evita problemas de permissão de escrita em nuvem)
                img_payload = Image.open(captured_file)
                current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Define o caminho virtual para manter a integridade da tabela
                virtual_file_path = f"MEM_STREAM/rec_{current_timestamp}.png"

                # Inicialização do motor LLM multimodal estável
                llm_engine = genai.GenerativeModel('gemini-2.5-flash')
                
                extraction_prompt = (
                    "Analyze the attached document. Extract the emission date, the final total value, "
                    "and any official Brazilian fiscal identification number such as NFC-e number, NFS-e number, "
                    "or Chave de Acesso. If no official fiscal identification sequence is found on the document, "
                    "return 'NONE' for FISCAL_ID.\n\n"
                    "Return the extracted information strictly in plain text formatting exactly as the template below, "
                    "with no markdown tags, no notes, and no additional text:\n"
                    "DATE: DD/MM/YYYY\n"
                    "VALUE: 00.00\n"
                    "FISCAL_ID: TEXT"
                )

                # Executa a inferência diretamente com o arquivo em memória
                inference_response = llm_engine.generate_content([extraction_prompt, img_payload])
                raw_output = inference_response.text
                
                extracted_date = "N/A"
                extracted_value = "N/A"
                fiscal_id = "NONE"
                
                for line in raw_output.split("\n"):
                    if "DATE:" in line:
                        extracted_date = line.replace("DATE:", "").strip()
                    if "VALUE:" in line:
                        extracted_value = line.replace("VALUE:", "").strip()
                    if "FISCAL_ID:" in line:
                        fiscal_id = line.replace("FISCAL_ID:", "").strip()

                if fiscal_id.upper() == "NONE" or fiscal_id == "":
                    fiscal_display = "Sem Cupom Fiscal (Documento Não-Fiscal)"
                else:
                    fiscal_display = fiscal_id

                transaction_id = f"TX-{current_timestamp}"

                # Persistência estruturada apenas dos dados textuais no arquivo CSV
                with open(DATABASE_FILE, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        transaction_id,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        employee_name,
                        virtual_file_path,
                        user_description,
                        headcount,
                        extracted_date,
                        extracted_value,
                        fiscal_id
                    ])

                st.success(f"Transação {transaction_id} processada e gravada com sucesso.")
                
                st.markdown("### Resumo da Última Extração Auditada")
                st.info(
                    f"**Funcionário:** {employee_name}  \n"
                    f"**Categoria:** {user_description}  \n"
                    f"**Identificação Fiscal:** {fiscal_display}  \n"
                    f"**Data de Emissão:** {extracted_date}  \n"
                    f"**Valor Total:** R$ {extracted_value}"
                )
                
                # Reseta o formulário limpando os inputs automaticamente para a próxima nota
                st.session_state.form_key += 1
                st.rerun()

            except Exception as ex:
                st.error(f"Falha na execução do pipeline: {str(ex)}")
