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

# --- ESTILO CSS ---
st.markdown("""
    <style>
    /* 1. Ajuste de margem topo (Logo) */
    .block-container {
        padding-top: 4rem !important; 
        padding-bottom: 5rem;
    }
    
    /* 2. Remover menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. Botão Principal */
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
    
    /* 4. Textos Mobile */
    h1 { font-size: 1.8rem !important; }
    h3 { font-size: 1.3rem !important; }
    
    /* 5. Caixa de Resultado */
    .result-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #2E7D32;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* 6. Estilo para Tabelas de Detalhes */
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #eee;
        font-size: 14px;
    }
    .detail-row:last-child {
        border-bottom: none;
        font-weight: bold;
    }
    .detail-label { color: #555; }
    .detail-value { color: #000; font-weight: 500; }
    .detail-sub { font-size: 12px; color: #888; display: block; }
    .negative { color: #d32f2f; } /* Vermelho para descontos */
    .positive { color: #2E7D32; } /* Verde para valores positivos */
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
    
    if consumo_medio is None or valor_ilum_pub is None or desconto_pct is None:
        st.error("⚠️ Por favor, preencha todos os campos para calcular.")
    else:
        # --- 1. PARÂMETROS E TARIFAS ---
        tarifa_equatorial = 1.077
        tarifa_fio_b_nominal = 0.224272
        fator_custo_fio_b = 0.15065 
        custo_disponibilidade = 100 if tipo_ligacao == "Trifásico" else 30

        # --- 2. CÁLCULO SEM GD (HOJE) ---
        custo_energia_sem_gd = consumo_medio * tarifa_equatorial
        total_sem_gd = custo_energia_sem_gd + valor_ilum_pub

        # --- 3. CÁLCULO COM GD (SOLEE) ---
        consumo_para_compensar = max(0, consumo_medio - custo_disponibilidade)
        
        # A. LOCADORA (SOLEE)
        tarifa_base_locadora = tarifa_equatorial - tarifa_fio_b_nominal
        tarifa_locadora_final = tarifa_base_locadora * (1 - (desconto_pct / 100))
        
        # Valores Brutos e Líquidos Solee
        valor_bruto_energia_locadora = consumo_para_compensar * tarifa_base_locadora
        valor_locadora = consumo_para_compensar * tarifa_locadora_final
        desconto_em_reais_solee = valor_bruto_energia_locadora - valor_locadora
        
        # B. EQUATORIAL
        valor_disponibilidade = custo_disponibilidade * tarifa_equatorial
        custo_fio_b_efetivo = consumo_para_compensar * fator_custo_fio_b
        total_fatura_equatorial = valor_disponibilidade + valor_ilum_pub + custo_fio_b_efetivo

        # --- 4. TOTAIS E INDICADORES ---
        custo_total_com_gd = valor_locadora + total_fatura_equatorial
        economia_reais = total_sem_gd - custo_total_com_gd
        economia_pct = (economia_reais / total_sem_gd) * 100 if total_sem_gd > 0 else 0
        
        pct_fio_b = (custo_fio_b_efetivo / custo_total_com_gd) * 100
        pct_ilum = (valor_ilum_pub / custo_total_com_gd) * 100
        pct_disp = (valor_disponibilidade / custo_total_com_gd) * 100

        # --- AUTO-SCROLL ---
        components.html(
            """
            <script>
                window.parent.document.querySelector('section.main').scrollTo({top: 1000, behavior: 'smooth'});
            </script>
            """, 
            height=0, width=0
        )

        # --- EXIBIÇÃO RESULTADOS ---
        st.write("---")
        st.markdown("<h3 style='text-align: center; color: #2E7D32;'>🎉 Resultado da Análise</h3>", unsafe_allow_html=True)

        # Card Destaque
        st.markdown(f"""
        <div class="result-box">
            <p style="margin:0; font-size: 16px; color: #555;">Economia Mensal Garantida</p>
            <h2 style="margin:5px 0; color: #2E7D32; font-size: 36px;">R$ {economia_reais:.2f}</h2>
            <p style="margin:0; font-weight: bold; color: #2E7D32; background-color: #fff; display: inline-block; padding: 2px 10px; border-radius: 10px;">
                📉 Redução de {economia_pct:.1f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric("🔴 Paga Hoje", f"R$ {total_sem_gd:.2f}")
        col2.metric("🟢 Com Solee", f"R$ {custo_total_com_gd:.2f}")

        chart_data = pd.DataFrame({
            "Cenário": ["Atual", "Com Solee"],
            "Custo (R$)": [total_sem_gd, custo_total_com_gd]
        })
        st.bar_chart(chart_data.set_index("Cenário"), color="#FF8C00")

        # --- MEMÓRIA DE CÁLCULO DETALHADA ---
        st.write("")
        with st.expander("🔎 Ver Memória de Cálculo Detalhada (Completa)"):
            
            # BLOCO 1: SOLEE
            st.markdown("#### 1. Composição Solee (Energia)")
            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 10px; border-radius: 8px;">
                <div class="detail-row">
                    <span class="detail-label">Energia Compensada<br><span class="detail-sub">{consumo_para_compensar:.0f} kWh x R$ {tarifa_base_locadora:.4f} (Tarifa Base)</span></span>
                    <span class="detail-value">R$ {valor_bruto_energia_locadora:.2f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label" style="color:#d32f2f;">(-) Desconto Aplicado<br><span class="detail-sub">Desconto de {desconto_pct}% sobre a tarifa base</span></span>
                    <span class="detail-value negative">- R$ {desconto_em_reais_solee:.2f}</span>
                </div>
                <div class="detail-row" style="border-top: 1px solid #ddd; margin-top:5px;">
                    <span class="detail-label" style="font-weight:bold;">= Total a Pagar Solee</span>
                    <span class="detail-value" style="font-weight:bold;">R$ {valor_locadora:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")

            # BLOCO 2: EQUATORIAL
            st.markdown("#### 2. Taxas Obrigatórias (Equatorial)")
            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 10px; border-radius: 8px;">
                <div class="detail-row">
                    <span class="detail-label">Custo de Disponibilidade<br><span class="detail-sub">Mínimo obrigatório ({custo_disponibilidade} kWh)</span></span>
                    <span class="detail-value">R$ {valor_disponibilidade:.2f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Taxa Fio B<br><span class="detail-sub">Pelo uso da rede na energia injetada</span></span>
                    <span class="detail-value">R$ {custo_fio_b_efetivo:.2f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Iluminação Pública (CIP)<br><span class="detail-sub">Repasse municipal</span></span>
                    <span class="detail-value">R$ {valor_ilum_pub:.2f}</span>
                </div>
                <div class="detail-row" style="border-top: 1px solid #ddd; margin-top:5px;">
                    <span class="detail-label" style="font-weight:bold;">= Total a Pagar Equatorial</span>
                    <span class="detail-value" style="font-weight:bold;">R$ {total_fatura_equatorial:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")

            # BLOCO 3: RESUMO DE INDICADORES
            st.markdown("#### 3. Indicadores Financeiros")
            st.info(f"""
            **💰 Desconto Real:**
            O cliente deixa de pagar **R$ {desconto_em_reais_solee:.2f}** referente à energia que consumiu.
            Isso representa um desconto financeiro de **R$ {(tarifa_base_locadora - tarifa_locadora_final):.4f}** para cada kWh compensado.
            
            **📊 Para onde vai o dinheiro (Nova Fatura):**
            * **{pct_fio_b:.1f}%** são taxas de uso da rede (Fio B).
            * **{pct_disp:.1f}%** é custo de disponibilidade.
            * **{pct_ilum:.1f}%** é iluminação pública.
            * O restante refere-se à compra de energia com desconto.
            """)
        
        # --- INFORMAÇÃO FINAL DE RODAPÉ ---
        st.write("")
        st.info(f"ℹ️ Cálculos baseados na Tarifa Equatorial de R$ {tarifa_equatorial:.3f}")
