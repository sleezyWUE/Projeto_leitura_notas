import os
import io
from datetime import datetime
import streamlit as st
import pandas as pd

DATABASE_FILE = "Captura_Notas_Fiscais.csv"

st.set_page_config(
    page_title="Management Audit Panel",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Painel de Controle e Auditoria Fiscal")
st.markdown("Módulo administrativo para consolidação de despesas e exportação de relatórios.")
st.markdown("---")

if os.path.exists(DATABASE_FILE) and os.path.getsize(DATABASE_FILE) > 100:
    df = pd.read_csv(DATABASE_FILE)
    
    df["transaction_id"] = df["transaction_id"].astype(str)
    df["fiscal_id"] = df["fiscal_id"].fillna("NONE").astype(str)
    df["extracted_total_value"] = df["extracted_total_value"].fillna("0.00").astype(str)

    rename_rules = {
        "transaction_id": "ID Transação",
        "timestamp": "Data/Hora Envio",
        "employee_name": "Funcionário",
        "file_path": "Caminho do Arquivo",
        "user_description": "Categoria da Despesa",
        "headcount": "Qtd Pessoas",
        "extracted_emission_date": "Data Emissão (IA)",
        "extracted_total_value": "Valor Total (IA)",
        "fiscal_id": "ID Fiscal / Autenticação"
    }
    
    df_display = df.rename(columns=rename_rules)
    final_order = [
        "ID Transação", "Data/Hora Envio", "Funcionário", "Caminho do Arquivo", 
        "Categoria da Despesa", "Qtd Pessoas", "Data Emissão (IA)", 
        "Valor Total (IA)", "ID Fiscal / Autenticação"
    ]
    df_display = df_display[final_order]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Notas Capturadas", len(df))
    
    try:
        v_clean = df["extracted_total_value"].str.replace("R$", "", regex=False).str.strip()
        total_gasto = pd.to_numeric(v_clean, errors='coerce').sum()
        if pd.isna(total_gasto) or total_gasto > 100000000:
            col2.metric("Volume Financeiro Auditado", "R$ 0.00")
        else:
            col2.metric("Volume Financeiro Auditado", f"R$ {total_gasto:,.2f}")
    except Exception:
        col2.metric("Volume Financeiro Auditado", "R$ 0.00")
        
    non_fiscal_count = len(df[df["fiscal_id"].str.upper() == "NONE"])
    col3.metric("Documentos Não-Fiscais", non_fiscal_count)

    st.subheader("Registros Sincronizados no Sistema")
    st.dataframe(df_display, use_container_width=True)

    st.markdown("---")
    st.subheader("Exportação de Relatório Executivo")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_display.to_excel(writer, index=False, sheet_name='Auditoria Despesas')
    
    st.download_button(
        label="📥 Baixar Planilha Oficial do Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"Relatorio_Auditoria_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
else:
    st.info("Nenhum registro de despesa armazenado na base de dados até o momento.")
