import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Solee Energia Solar",
    page_icon="☀️",
    layout="centered"
)

# --- ESTILIZAÇÃO CSS (CORES DA EMPRESA) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    div.stButton > button {
        background-color: #FF8C00; /* Laranja Solee */
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #e07b00;
        color: white;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #2E7D32; /* Verde Economia */
    }

    h1 {
        color: #FF8C00;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO E LOGO ---
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Tenta carregar a imagem 'logo.png' que deve estar no GitHub
    try:
        st.image("logo.png", use_column_width=True) 
    except:
        st.write("☀️") # Mostra um sol se não achar a logo

with col_title:
    st.title("Simulador Solee Energia Solar")
    st.caption("Ferramenta de Vendas - Cálculo de Economia")

st.divider()

# --- INPUTS (ENTRADA DE DADOS ZERADA) ---
with st.container():
    st.subheader("📝 Insira os dados da Fatura")
    st.write("Preencha os campos abaixo com os dados do cliente:")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        # value=None ou retirar o value faz começar zerado/vazio
        consumo_medio = st.number_input("1️⃣ Consumo Médio (kWh)", min_value=0.0, step=10.0, format="%.2f")
        tipo_ligacao = st.selectbox("3️⃣ Tipo de Ligação", ["Monofásico", "Trifásico"])

    with col_input2:
        valor_ilum_pub = st.number_input("2️⃣ Ilum. Pública (R$)", min_value=0.0, step=1.0, format="%.2f")
        desconto_pct = st.number_input("4️⃣ Desconto Oferecido (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f")

st.write("") # Espaçamento

# --- BOTÃO DE CÁLCULO ---
calcular = st.button("CALCULAR ECONOMIA AGORA 🚀")

if calcular:
    # Validação simples para não calcular zerado
    if consumo_medio <= 0:
        st.warning("⚠️ Por favor, insira um valor de Consumo Médio (kWh) maior que zero para calcular.")
    else:
        # --- PARÂMETROS E LÓGICA ---
        tarifa_equatorial = 1.077
        tarifa_fio_b_nominal = 0.224272
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
        st.divider()
        st.markdown("### 📊 Resultado da Simulação")

        # Métricas Principais
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Fatura Atual (Sem Solar)", f"R$ {total_sem_gd:.2f}")
        col_res2.metric("Fatura SOLEE (Estimada)", f"R$ {custo_total_com_gd:.2f}", delta=f"- {economia_pct:.1f}% de Redução", delta_color="inverse")
        col_res3.metric("💰 Economia Mensal", f"R$ {economia_reais:.2f}")

        # Gráfico Comparativo
        st.write("")
        st.caption("Comparativo visual de custos:")
        dados_grafico = pd.DataFrame({
            "Situação": ["Pagando Equatorial", "Pagando Solee"],
            "Valor Total (R$)": [total_sem_gd, custo_total_com_gd]
        })
        st.bar_chart(dados_grafico.set_index("Situação"), color="#FF8C00")

        # Detalhamento
        with st.expander("🔎 Ver Detalhes da Nova Fatura (Composição)"):
            st.info(f"""
            **Como fica o pagamento:**
            
            1. **Boleto Locadora (Solee):** R$ {valor_locadora:.2f}
               *(Referente a {consumo_para_compensar:.0f} kWh compensados com {desconto_pct}% de desconto)*
            
            2. **Fatura Equatorial:** R$ {total_fatura_equatorial:.2f}
               *(Referente ao custo de disponibilidade de {custo_disponibilidade}kWh, iluminação pública e taxas de uso da rede)*
               
            **Total Geral:** R$ {custo_total_com_gd:.2f}
            """)
        
        st.success("✅ Simulação pronta para apresentar ao cliente!")
