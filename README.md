# 🧾 Sistema Unificado de Captura, Auditoria e Consolidação de Despesas

Aplicações web desenvolvidas em **Python** e **Streamlit**, integradas à API de Inteligência Artificial Multimodal **Google Gemini 2.5 Flash**. O ecossistema automatiza completamente o fluxo de prestação de contas, extração de dados fiscais por visão computacional e auditoria gerencial de despesas corporativas.

---

## 🚀 Funcionalidades Principais

O sistema foi unificado em uma única plataforma dividida por abas de usabilidade, garantindo centralização de dados:

*   **📲 Módulo do Funcionário (Captura):** Interface limpa e responsiva para que colaboradores em campo insiram seu nome, selecionem a categoria do gasto e façam o upload ou tirem a foto do cupom fiscal.
*   **🔒 Painel Administrativo (Gerência):** Área restrita por barreira de autenticação (Senha master: `caetevisual`). Exibe métricas consolidadas (Total de Notas, Volume Financeiro Auditado, Qtd de Documentos Não-Fiscais), tabela de registros sincronizados em tempo real e exportação do relatório oficial em formato nativo do Excel (`.xlsx`).

---

## 🧠 Escaneamento Cognitivo (IA Multimodal vs OCR Tradicional)

Diferente dos sistemas de OCR legados que dependem de regras rígidas de programação e falham com imagens de baixa qualidade, este projeto utiliza **Inteligência Artificial Multimodal**:
1. **Compreensão de Contexto:** O modelo lê os pixels da imagem e compreende a semântica de um documento fiscal brasileiro, localizando com precisão campos como *Data de Emissão*, *Valor Total* e sequências complexas como a *Chave de Acesso (NFC-e/NFS-e)*.
2. **Resiliência a Ruídos:** Capaz de extrair dados com exatidão mesmo de cupons fiscais amassados, rasurados, com sombras ou fotos tiradas em ambientes externos sob iluminação precária.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3
*   **Interface Web (Front-End/Back-End):** Streamlit
*   **Engine de IA:** Google Generative AI (Gemini 2.5 Flash)
*   **Manipulação de Dados:** Pandas
*   **Geração de Relatórios:** Openpyxl

---

## 📂 Estrutura do Repositório

```text
├── app.py                      # Código-fonte unificado (Funcionário + Painel Gerencial)
├── requirements.txt            # Dependências e bibliotecas do ecossistema Python
├── Captura_Notas_Fiscais.csv   # Base de dados estruturada local (Gerada automaticamente)
└── README.md                   # Documentação oficial do projeto# Projeto_leitura_notas
