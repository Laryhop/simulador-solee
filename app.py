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

# --- ESTILO CSS (CORRIGIDO E OTIMIZADO) ---
st.markdown("""
    <style>
    /* Layout Mobile */
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 5rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    div.stButton > button {
        background-color: #FF8C00;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        padding: 15px 24px;
        width: 100%;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #e07b00;
        transform: translateY(-2px);
    }
    
    .result-box {
        background-color: #262730; 
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444; 
        border-left: 8px solid #2E7D32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        text-align: center;
        margin-bottom: 25px;
    }
    
    .annual-box {
        background-color: #1E1E1E;
        border: 1px solid #FF8C00;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    h1 { color: #FF8C00 !important; }
    h3 { color: #FAFAFA !important; }
    p { color: #E0E0E0 !important; }
    
    /* Estilo Geral das Linhas do Extrato */
    .statement-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #444; 
        font-size: 16px;
    }
    .statement-label { color: #E0E0E0; font-weight: 500; }
    .statement-value { font-weight: bold; color: #FFFFFF; }
    
    .discount-tag { 
        background-color: #1B5E20; 
        color: #A5D6A7; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-size: 13px; 
        font-weight: bold;
        border: 1px solid #2E7D32;
    }
    
    /* CORREÇÃO DO BOX DE COMPARAÇÃO */
    .duelo-box {
        background-color: #333; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 15px;
        border: 1px solid #444;
    }
    
    .duelo-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .impacto-box {
        background-color: #3d3e47;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-top: 10px;
        border: 1px solid #FF8C00;
    }
    
    .streamlit-expanderContent {
        background-color: #262730;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo.png", width=80) 
    except:
        st.write("☀️")
with col_title:
    st.markdown("<h1 style='margin-top: 0px;'>Simulador Solee</h1>", unsafe_allow_html=True)
    st.caption("Cálculo Oficial de Economia")

st.write("---")

# --- INPUTS ---
st.markdown("### 📝 Dados da Fatura")

consumo_medio = st.number_input("1️⃣ Consumo Médio (kWh)", min_value=0.0, value=None, placeholder="Ex: 480")
valor_ilum_pub = st.number_input("2️⃣ Ilum. Pública (R$)", min_value=0.0, value=None, placeholder="Ex: 48.00", format="%.2f")

col_tipo, col_desc = st.columns(2)
with col_tipo:
    tipo_ligacao = st.selectbox("3️⃣ Ligação", ["Monofásico", "Trifásico"], index=1)
with col_desc:
    desconto_pct = st.number_input("4️⃣ Desconto (%)", min_value=0.0, max_value=100.0, value=None, placeholder="Ex: 15")

st.write("") 

# --- CÁLCULO ---
if st.button("CALCULAR ECONOMIA 🚀"):
    
    if consumo_medio is None or valor_ilum_pub is None or desconto_pct is None:
        st.error("⚠️ Por favor, preencha todos os campos.")
    else:
        # 1. PARÂMETROS
        tarifa_equatorial = 1.077
        tarifa_fio_b_nominal = 0.224272
        fator_custo_fio_b = 0.15065 
        custo_disponibilidade = 100 if tipo_ligacao == "Trifásico" else 30

        # 2. CÁLCULO
        custo_energia_sem_gd = consumo_medio * tarifa_equatorial
        total_sem_gd = custo_energia_sem_gd + valor_ilum_pub

        consumo_para_compensar = max(0, consumo_medio - custo_disponibilidade)
        
        tarifa_base_locadora = tarifa_equatorial - tarifa_fio_b_nominal
        tarifa_locadora_final = tarifa_base_locadora * (1 - (desconto_pct / 100))
        
        # Valores Comparativos
        custo_energia_se_fosse_equatorial = consumo_para_compensar * tarifa_equatorial
        valor_locadora = consumo_para_compensar * tarifa_locadora_final
        
        desconto_em_reais_solee = custo_energia_se_fosse_equatorial - valor_locadora
        
        # Porcentagem de Impacto Real
        if custo_energia_se_fosse_equatorial > 0:
            pct_desconto_efetivo = ((custo_energia_se_fosse_equatorial - valor_locadora) / custo_energia_se_fosse_equatorial) * 100
        else:
            pct_desconto_efetivo = 0

        # Taxas Equatorial
        valor_disponibilidade = custo_disponibilidade * tarifa_equatorial
        custo_fio_b_efetivo = consumo_para_compensar * fator_custo_fio_b
        total_fatura_equatorial = valor_disponibilidade + valor_ilum_pub + custo_fio_b_efetivo

        # Totais Finais
        custo_total_com_gd = valor_locadora + total_fatura_equatorial
        economia_reais = total_sem_gd - custo_total_com_gd
        economia_anual = economia_reais * 12
        economia_pct = (economia_reais / total_sem_gd) * 100 if total_sem_gd > 0 else 0
        
        # --- AUTO-SCROLL ---
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
        st.markdown("<h3 style='text-align: center;'>Resultado da Análise</h3>", unsafe_allow_html=True)

        # CARD MENSAL
        st.markdown(f"""
        <div class="result-box">
            <h4 style="margin:0; color: #BBB; font-weight: normal;">Economia Mensal</h4>
            <h1 style="margin: 5px 0; color: #4CAF50; font-size: 42px;">R$ {economia_reais:.2f}</h1>
            <p style="margin:0; font-size: 16px; color: #EEE;">📉 Redução de <b>{economia_pct:.1f}%</b> na conta</p>
        </div>
        """, unsafe_allow_html=True)

        # CARD ANUAL
        st.markdown(f"""
        <div class="annual-box">
            <span style="color: #FF8C00; font-weight: bold; font-size: 14px;">PROJEÇÃO DE 1 ANO</span><br>
            <span style="color: #FFF; font-size: 24px; font-weight: bold;">R$ {economia_anual:.2f}</span><br>
            <span style="color: #888; font-size: 12px;">economizados em 12 meses</span>
        </div>
        """, unsafe_allow_html=True)

        col_ant, col_dep = st.columns(2)
        col_ant.metric("🔴 Pagaria Hoje", f"R$ {total_sem_gd:.2f}")
        col_dep.metric("🟢 Vai Pagar", f"R$ {custo_total_com_gd:.2f}")

        # DETALHAMENTO (LAYOUT CORRIGIDO)
        st.write("")
        with st.expander("🔎 Entenda os Valores (Raio-X)", expanded=False):
            
            st.markdown("#### 1. Duelo de Tarifas (Energia)")
            
            # Box de Comparação Reestruturado
            st.markdown(f"""
            <div class="duelo-box">
                <p style="margin:0 0 10px 0; font-size:14px; color:#AAA;">Comparativo do custo da energia ({consumo_para_compensar:.0f} kWh):</p>
                
                <div class="duelo-row" style="border-bottom: 1px solid #555; padding-bottom: 8px;">
                    <span style="color: #FFF;">🔴 Na Equatorial</span>
                    <span style="color: #FF5252; font-weight: bold;">R$ {custo_energia_se_fosse_equatorial:.2f}</span>
                </div>
                
                <div class="duelo-row" style="padding-top: 8px;">
                    <span style="color: #FFF;">🟢 Na Solee</span>
                    <span style="color: #66BB6A; font-weight: bold;">R$ {valor_locadora:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Box de Impacto separado para não quebrar layout
            st.markdown(f"""
            <div class="impacto-box">
                <span style="color: #FFF; font-size: 14px;">⚡ Desconto Efetivo na Energia: </span>
                <br>
                <span style="color: #FF8C00; font-size: 22px; font-weight: bold;">{pct_desconto_efetivo:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

            st.info(f"""
            **💡 Explicação para o Cliente:**
            Embora o desconto no contrato seja de {desconto_pct}%, a **economia real** na compra da energia é muito maior ({pct_desconto_efetivo:.0f}%) porque a Solee retira custos (como o Fio B) que a Equatorial cobraria cheios.
            """)

            st.write("")
            st.markdown("#### 2. O que é Obrigatório (Taxas)")
            st.markdown(f"""
            <div class="statement-row">
                <span class="statement-label">Mínimo Equatorial + Fio B</span>
                <span class="statement-value">R$ {(valor_disponibilidade + custo_fio_b_efetivo):.2f}</span>
            </div>
            <div class="statement-row">
                <span class="statement-label">Iluminação Pública</span>
                <span class="statement-value">R$ {valor_ilum_pub:.2f}</span>
            </div>
            <div class="statement-row" style="background-color: #333; padding: 5px 10px; border-radius: 5px; margin-top: 5px;">
                <span class="statement-label" style="font-weight:bold; color: #FFF;">= Total Taxas</span>
                <span class="statement-value" style="color: #EF5350;">R$ {total_fatura_equatorial:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        # RODAPÉ
        st.write("")
        st.info(f"ℹ️ Cálculos baseados na Tarifa Equatorial de R$ {tarifa_equatorial:.3f}. Os valores aproximados e condicionados ao tipo de sistema e taxas de disponibilidade e iluminação pública.")
