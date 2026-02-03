import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Solee",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILO CSS (CORREÇÃO DE LOGO + LAYOUT) ---
st.markdown("""
    <style>
    /* 1. Aumentar margem do topo para a logo não cortar */
    .block-container {
        padding-top: 4rem !important; /* Mais espaço no topo */
        padding-bottom: 5rem;
    }
    
    /* 2. Remover elementos padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. Botão Grande e Chamativo */
    div.stButton > button {
        background-color: #FF8C00;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        padding: 15px 24px;
        width: 100%;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #e07b00;
        transform: translateY(-2px);
    }
    
    /* 4. Títulos e Texto Mobile */
    h1 { font-size: 1.8rem !important; }
    h3 { font-size: 1.3rem !important; }
    
    /* 5. Card de Resultado Fixo */
    .result-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #2E7D32;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        # width=80 garante que ela apareça inteira sem cortar
        st.image("logo.png", width=80) 
    except:
        st.write("☀️")

with col_title:
    st.markdown("<h1 style='margin-top: 0px; color: #FF8C00;'>Simulador Solee</h1>", unsafe_allow_html=True)
    st.caption("Cálculo Oficial de Economia")

st.write("---")

# --- INPUTS ---
st.markdown("### 📝 Dados da Fatura")

consumo_medio = st.number_input(
    "1️⃣ Consumo Médio (kWh)", 
    min_value=0.0, value=None, placeholder="Digite o consumo..."
)

valor_ilum_pub = st.number_input(
    "2️⃣ Ilum. Pública (R$)", 
    min_value=0.0, value=None, placeholder="Digite o valor em R$...", format="%.2f"
)

col_tipo, col_desc = st.columns(2)
with col_tipo:
    tipo_ligacao = st.selectbox("3️⃣ Ligação", ["Monofásico", "Trifásico"], index=1)

with col_desc:
    desconto_pct = st.number_input(
        "4️⃣ Desconto (%)", 
        min_value=0.0, max_value=100.0, value=None, placeholder="Ex: 15"
    )

st.write("") 

# --- CÁLCULO ---
if st.button("CALCULAR ECONOMIA 🚀"):
    
    # Validação
    if consumo_medio is None or valor_ilum_pub is None or desconto_pct is None:
        st.error("⚠️ Por favor, preencha todos os campos para calcular.")
    else:
        # --- PARÂMETROS ---
        tarifa_equatorial = 1.077
        tarifa_fio_b_nominal = 0.224272
        fator_custo_fio_b = 0.15065 
        custo_disponibilidade = 100 if tipo_ligacao == "Trifásico" else 30

        # SEM GD
        custo_energia_sem_gd = consumo_medio * tarifa_equatorial
        total_sem_gd = custo_energia_sem_gd + valor_ilum_pub

        # COM GD
        consumo_para_compensar = max(0, consumo_medio - custo_disponibilidade)
        
        # Locadora
        tarifa_base_locadora = tarifa_equatorial - tarifa_fio_b_nominal
        tarifa_locadora_final = tarifa_base_locadora * (1 - (desconto_pct / 100))
        valor_locadora = consumo_para_compensar * tarifa_locadora_final

        # Equatorial
        valor_disponibilidade = custo_disponibilidade * tarifa_equatorial
        custo_fio_b_efetivo = consumo_para_compensar * fator_custo_fio_b
        total_fatura_equatorial = valor_disponibilidade + valor_ilum_pub + custo_fio_b_efetivo

        # Totais
        custo_total_com_gd = valor_locadora + total_fatura_equatorial
        economia_reais = total_sem_gd - custo_total_com_gd
        economia_pct = (economia_reais / total_sem_gd) * 100 if total_sem_gd > 0 else 0

        # --- AUTO-SCROLL (SCRIPT PARA DESCER A TELA) ---
        # Isso força o navegador a descer até o fim da página onde está o resultado
        components.html(
            """
            <script>
                window.parent.document.querySelector('section.main').scrollTo({top: 1000, behavior: 'smooth'});
            </script>
            """, 
            height=0, width=0
        )

        # --- RESULTADOS ---
        st.write("---")
        st.markdown("<h3 style='text-align: center; color: #2E7D32;'>🎉 Resultado da Análise</h3>", unsafe_allow_html=True)

        # Card de destaque
        st.markdown(f"""
        <div class="result-box">
            <p style="margin:0; font-size: 16px; color: #555;">Economia Mensal Garantida</p>
            <h2 style="margin:5px 0; color: #2E7D32; font-size: 36px;">R$ {economia_reais:.2f}</h2>
            <p style="margin:0; font-weight: bold; color: #2E7D32; background-color: #fff; display: inline-block; padding: 2px 10px; border-radius: 10px;">
                📉 Redução de {economia_pct:.1f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Comparativo Simplificado
        col1, col2 = st.columns(2)
        col1.metric("🔴 Paga Hoje", f"R$ {total_sem_gd:.2f}")
        col2.metric("🟢 Com Solee", f"R$ {custo_total_com_gd:.2f}")

        # Gráfico Visual
        chart_data = pd.DataFrame({
            "Cenário": ["Atual", "Com Solee"],
            "Custo (R$)": [total_sem_gd, custo_total_com_gd]
        })
        st.bar_chart(chart_data.set_index("Cenário"), color="#FF8C00")

        # --- MEMÓRIA DE CÁLCULO DETALHADA ---
        st.write("")
        with st.expander("🔎 Ver Memória de Cálculo Detalhada (Explicação)"):
            st.markdown(f"""
            **1. Divisão do Consumo ({consumo_medio:.0f} kWh):**
            * **{custo_disponibilidade} kWh** ficam na Equatorial (Custo de Disponibilidade Obrigatório).
            * **{consumo_para_compensar:.0f} kWh** são injetados pela Solee (Energia Solar).

            ---
            
            **2. Composição da Nova Conta:**
            
            **A) Pagamento Equatorial (R$ {total_fatura_equatorial:.2f})**
            * Disponibilidade ({custo_disponibilidade} kWh x {tarifa_equatorial:.3f}): R$ {valor_disponibilidade:.2f}
            * Iluminação Pública: R$ {valor_ilum_pub:.2f}
            * Uso do Fio B (Taxa da rede sobre a energia solar): R$ {custo_fio_b_efetivo:.2f}
            
            **B) Boleto Solee (R$ {valor_locadora:.2f})**
            * Energia Solar ({consumo_para_compensar:.0f} kWh): 
            * *Tarifa aplicada com desconto:* R$ {tarifa_locadora_final:.4f}/kWh
            
            **Total (A + B) = R$ {custo_total_com_gd:.2f}**
            """)
            st.info("Cálculos baseados na Tarifa Equatorial de R$ 1,077.")
