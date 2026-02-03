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

# --- ESTILO CSS (VISUAL LIMPO E MODERNO) ---
st.markdown("""
    <style>
    /* Layout Mobile */
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 5rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Botão Principal */
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
    
    /* Box de Resultado Principal */
    .result-box {
        background-color: #fff;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #2E7D32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Estilo do Extrato Simplificado */
    .statement-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 16px;
    }
    .statement-label { color: #333; font-weight: 500; }
    .statement-value { font-weight: bold; color: #000; }
    .discount-tag { 
        background-color: #e8f5e9; 
        color: #2E7D32; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-size: 13px; 
        font-weight: bold;
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
    st.markdown("<h1 style='margin-top: 0px; color: #FF8C00;'>Simulador Solee</h1>", unsafe_allow_html=True)
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

        # 2. CÁLCULO SEM GD (ANTES)
        custo_energia_sem_gd = consumo_medio * tarifa_equatorial
        total_sem_gd = custo_energia_sem_gd + valor_ilum_pub

        # 3. CÁLCULO COM GD (DEPOIS)
        consumo_para_compensar = max(0, consumo_medio - custo_disponibilidade)
        
        # Lógica Solee
        tarifa_base_locadora = tarifa_equatorial - tarifa_fio_b_nominal
        tarifa_locadora_final = tarifa_base_locadora * (1 - (desconto_pct / 100))
        
        valor_bruto_energia_locadora = consumo_para_compensar * tarifa_base_locadora
        valor_locadora = consumo_para_compensar * tarifa_locadora_final
        desconto_em_reais_solee = valor_bruto_energia_locadora - valor_locadora
        
        # Lógica Equatorial
        valor_disponibilidade = custo_disponibilidade * tarifa_equatorial
        custo_fio_b_efetivo = consumo_para_compensar * fator_custo_fio_b
        total_fatura_equatorial = valor_disponibilidade + valor_ilum_pub + custo_fio_b_efetivo

        # Totais
        custo_total_com_gd = valor_locadora + total_fatura_equatorial
        economia_reais = total_sem_gd - custo_total_com_gd
        economia_pct = (economia_reais / total_sem_gd) * 100 if total_sem_gd > 0 else 0
        
        # Percentuais para o "Raio-X"
        total_taxas = total_fatura_equatorial
        pct_taxas = (total_taxas / custo_total_com_gd) * 100
        pct_energia = 100 - pct_taxas

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
        st.markdown("<h3 style='text-align: center; color: #333;'>Resultado da Análise</h3>", unsafe_allow_html=True)

        # 1. CARD PRINCIPAL (LIMPO)
        st.markdown(f"""
        <div class="result-box">
            <h4 style="margin:0; color: #555; font-weight: normal;">Economia Mensal</h4>
            <h1 style="margin: 5px 0; color: #2E7D32; font-size: 42px;">R$ {economia_reais:.2f}</h1>
            <p style="margin:0; font-size: 16px;">📉 Redução de <b>{economia_pct:.1f}%</b> na conta total</p>
        </div>
        """, unsafe_allow_html=True)

        # 2. COMPARATIVO LADO A LADO
        col_ant, col_dep = st.columns(2)
        col_ant.metric("🔴 Pagaria Hoje", f"R$ {total_sem_gd:.2f}")
        col_dep.metric("🟢 Vai Pagar", f"R$ {custo_total_com_gd:.2f}")

        # 3. MEMÓRIA DE CÁLCULO (SIMPLIFICADA E DIRETA)
        st.write("")
        with st.expander("🔎 Entenda os Valores (Raio-X da Fatura)", expanded=True):
            
            st.markdown("#### 1. Onde você ganha (Energia)")
            st.markdown(f"""
            <div class="statement-row">
                <span class="statement-label">Preço Normal da Energia</span>
                <span class="statement-value" style="color: #555; text-decoration: line-through;">R$ {valor_bruto_energia_locadora:.2f}</span>
            </div>
            <div class="statement-row">
                <span class="statement-label">✅ Seu Desconto Solee ({desconto_pct}%)</span>
                <span class="discount-tag">- R$ {desconto_em_reais_solee:.2f}</span>
            </div>
            <div class="statement-row" style="background-color: #f9f9f9; padding-left: 10px; border-radius: 5px;">
                <span class="statement-label" style="font-weight:bold;">= Energia com Desconto</span>
                <span class="statement-value" style="color: #2E7D32;">R$ {valor_locadora:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.markdown("#### 2. O que é Obrigatório (Impostos/Taxas)")
            st.markdown(f"""
            <div class="statement-row">
                <span class="statement-label">Mínimo da Equatorial + Fio B</span>
                <span class="statement-value">R$ {(valor_disponibilidade + custo_fio_b_efetivo):.2f}</span>
            </div>
            <div class="statement-row">
                <span class="statement-label">Iluminação Pública</span>
                <span class="statement-value">R$ {valor_ilum_pub:.2f}</span>
            </div>
            <div class="statement-row" style="background-color: #f9f9f9; padding-left: 10px; border-radius: 5px;">
                <span class="statement-label" style="font-weight:bold;">= Total Taxas</span>
                <span class="statement-value" style="color: #d32f2f;">R$ {total_fatura_equatorial:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.info(f"""
            **Resumo da sua nova fatura:**
            
            De tudo que você vai pagar (**R$ {custo_total_com_gd:.2f}**):
            * ⚡ **{pct_energia:.0f}%** é Energia (Com o desconto da Solee).
            * 🏛️ **{pct_taxas:.0f}%** são Taxas Obrigatórias (Equatorial/Prefeitura).
            
            *Tarifa Equatorial considerada: R$ {tarifa_equatorial:.3f}*
            """)
