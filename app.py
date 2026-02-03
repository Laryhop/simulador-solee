import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Solee",
    page_icon="☀️",
    layout="centered"
)

# --- ESTILIZAÇÃO CSS (CORES DA EMPRESA) ---
# Aqui definimos as cores. 
# Cor Primária (Botões/Destaques): #FF8C00 (Laranja Solar)
# Cor Fundo Secundário: #F0F2F6
st.markdown("""
    <style>
    /* Esconder menu padrão do Streamlit para parecer mais um App */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilo do Botão */
    div.stButton > button {
        background-color: #FF8C00;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #e07b00;
        color: white;
    }
    
    /* Estilo das Métricas */
    [data-testid="stMetricValue"] {
        font-size: 26px;
        color: #2E7D32; /* Verde Economia */
    }
    
    /* Card de Resultado */
    .result-card {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO E LOGO ---
col1, col2 = st.columns([1, 4])

with col1:
    # Tenta carregar a logo se ela existir, senão mostra um emoji
    try:
        st.image("logo.png", width=80) 
    except:
        st.write("☀️") 

with col2:
    st.title("Simulador SOLEE")
    st.caption("Ferramenta de Vendas - Energia Inteligente")

st.divider()

# --- INPUTS (ENTRADA DE DADOS) ---
with st.container():
    st.subheader("📝 Dados do Cliente")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        consumo_medio = st.number_input("Consumo Médio (kWh)", min_value=0.0, value=480.0, step=10.0)
        tipo_ligacao = st.selectbox("Tipo de Ligação", ["Monofásico", "Trifásico"], index=1) # Default Trifásico

    with col_input2:
        valor_ilum_pub = st.number_input("Ilum. Pública (R$)", min_value=0.0, value=48.0, step=1.0)
        desconto_pct = st.number_input("Desconto Oferecido (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)

# --- BOTÃO DE CÁLCULO ---
calcular = st.button("CALCULAR ECONOMIA 🚀")

if calcular:
    # --- PARÂMETROS E LÓGICA (IDÊNTICA À PLANILHA) ---
    tarifa_equatorial = 1.077
    tarifa_fio_b_nominal = 0.224272
    # Fator reverso extraído da planilha (29.51 / 195.91)
    fator_custo_fio_b = 0.15065 
    
    custo_disponibilidade = 100 if tipo_ligacao == "Trifásico" else 30

    # 1. Cenário SEM GD
    custo_energia_sem_gd = consumo_medio * tarifa_equatorial
    total_sem_gd = custo_energia_sem_gd + valor_ilum_pub

    # 2. Cenário COM GD
    consumo_para_compensar = max(0, consumo_medio - custo_disponibilidade)
    
    # Locadora
    tarifa_base_locadora = tarifa_equatorial - tarifa_fio_b_nominal
    tarifa_locadora_final = tarifa_base_locadora * (1 - (desconto_pct / 100))
    valor_locadora = consumo_para_compensar * tarifa_locadora_final

    # Equatorial (Novo)
    valor_disponibilidade = custo_disponibilidade * tarifa_equatorial
    custo_fio_b_efetivo = consumo_para_compensar * fator_custo_fio_b
    total_fatura_equatorial = valor_disponibilidade + valor_ilum_pub + custo_fio_b_efetivo

    # Totais
    custo_total_com_gd = valor_locadora + total_fatura_equatorial
    economia_reais = total_sem_gd - custo_total_com_gd
    economia_pct = (economia_reais / total_sem_gd) * 100 if total_sem_gd > 0 else 0

    # --- EXIBIÇÃO DOS RESULTADOS ---
    
    st.markdown("### 📊 Resultado da Simulação")

    # Métricas Principais (Destaque)
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Fatura Atual", f"R$ {total_sem_gd:.2f}")
    col_res2.metric("Fatura SOLEE", f"R$ {custo_total_com_gd:.2f}", delta=f"- {economia_pct:.1f}%", delta_color="inverse")
    col_res3.metric("Economia Mensal", f"R$ {economia_reais:.2f}")

    # Gráfico Comparativo Simples
    dados_grafico = pd.DataFrame({
        "Cenário": ["Sem Solee", "Com Solee"],
        "Valor (R$)": [total_sem_gd, custo_total_com_gd]
    })
    st.bar_chart(dados_grafico.set_index("Cenário"), color="#FF8C00")

    # Detalhamento (Expander)
    with st.expander("Ver Detalhes do Cálculo"):
        st.write(f"**⚡ Divisão da Nova Fatura:**")
        st.write(f"- Pagamento à Locadora: **R$ {valor_locadora:.2f}**")
        st.write(f"- Pagamento à Concessionária: **R$ {total_fatura_equatorial:.2f}**")
        st.write(f"*(Inclui Disp. {custo_disponibilidade}kWh + Ilum. Pub + Fio B)*")
        st.caption("Cálculos baseados nas tarifas vigentes da Equatorial.")

    # Call to Action
    st.success("✅ Simulação concluída! Tire um print ou apresente ao cliente.")
