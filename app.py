import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA (MOBILE FRIENDLY) ---
st.set_page_config(
    page_title="Simulador Solee",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILO CSS OTIMIZADO PARA CELULAR ---
st.markdown("""
    <style>
    /* Remove margens excessivas do topo para celular */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    
    /* Esconde menu e rodapé padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Botão Grande e Chamativo (Fácil de clicar com o dedo) */
    div.stButton > button {
        background-color: #FF8C00; /* Laranja Solee */
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
    
    /* Ajuste de tamanho de fontes para leitura no celular */
    h1 { font-size: 1.8rem !important; }
    h3 { font-size: 1.3rem !important; }
    p, label { font-size: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
# Usamos colunas, mas travamos a largura da imagem para não estourar no celular
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        # width=100 garante que no celular ela fique pequena e elegante (não gigante)
        st.image("logo.png", width=100) 
    except:
        st.write("☀️")

with col_title:
    st.markdown("<h1 style='margin-top: -10px; color: #FF8C00;'>Simulador Solee</h1>", unsafe_allow_html=True)
    st.caption("Cálculo de Economia Solar")

st.write("---")

# --- INPUTS (CAMPOS EM BRANCO) ---
st.markdown("### 📝 Dados da Fatura")

# value=None deixa o campo vazio. placeholder mostra o texto cinza de exemplo.
consumo_medio = st.number_input(
    "1️⃣ Consumo Médio (kWh)", 
    min_value=0.0, 
    value=None, 
    placeholder="Ex: 480"
)

valor_ilum_pub = st.number_input(
    "2️⃣ Ilum. Pública (R$)", 
    min_value=0.0, 
    value=None, 
    placeholder="Ex: 48.00",
    format="%.2f"
)

col_tipo, col_desc = st.columns(2)
with col_tipo:
    tipo_ligacao = st.selectbox("3️⃣ Ligação", ["Monofásico", "Trifásico"], index=1)

with col_desc:
    desconto_pct = st.number_input(
        "4️⃣ Desconto (%)", 
        min_value=0.0, 
        max_value=100.0, 
        value=None, 
        placeholder="Ex: 15"
    )

st.write("") # Espaço para o dedo não bater errado

# --- BOTÃO DE CÁLCULO ---
calcular = st.button("CALCULAR AGORA 🚀")

if calcular:
    # Validação: Verifica se os campos estão preenchidos (não são None)
    if consumo_medio is None or valor_ilum_pub is None or desconto_pct is None:
        st.error("⚠️ Por favor, preencha todos os campos numéricos para calcular.")
    else:
        # --- LÓGICA DE CÁLCULO ---
        tarifa_equatorial = 1.077
        tarifa_fio_b_nominal = 0.224272
        fator_custo_fio_b = 0.15065 
        custo_disponibilidade = 100 if tipo_ligacao == "Trifásico" else 30

        # Cenário SEM GD
        custo_energia_sem_gd = consumo_medio * tarifa_equatorial
        total_sem_gd = custo_energia_sem_gd + valor_ilum_pub

        # Cenário COM GD
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

        # --- RESULTADOS (MOBILE FRIENDLY) ---
        st.write("---")
        st.markdown("<h3 style='text-align: center; color: #2E7D32;'>🎉 Economia Encontrada!</h3>", unsafe_allow_html=True)

        # Container Verde para destacar o resultado final
        st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #2E7D32; text-align: center;">
            <p style="margin:0; font-size: 14px; color: #555;">O cliente vai economizar:</p>
            <h2 style="margin:0; color: #2E7D32; font-size: 32px;">R$ {economia_reais:.2f}</h2>
            <p style="margin:0; font-weight: bold; color: #2E7D32;">({economia_pct:.1f}% a menos)</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        # Detalhamento Simplificado (Comparativo Lado a Lado)
        col_antes, col_depois = st.columns(2)
        with col_antes:
            st.metric("🔴 Paga Hoje", f"R$ {total_sem_gd:.0f}")
        with col_depois:
            st.metric("🟢 Vai Pagar", f"R$ {custo_total_com_gd:.0f}")

        # Gráfico (Removemos detalhes desnecessários para caber na tela)
        chart_data = pd.DataFrame({
            "Cenário": ["Hoje", "Com Solee"],
            "Valor": [total_sem_gd, custo_total_com_gd]
        })
        st.bar_chart(chart_data.set_index("Cenário"), color="#FF8C00")
        
        # Botão Expander para quem quer ver os centavos (não polui a tela principal)
        with st.expander("Ver composição exata dos valores"):
            st.write(f"**Boleto Solee:** R$ {valor_locadora:.2f}")
            st.write(f"**Conta Equatorial:** R$ {total_fatura_equatorial:.2f}")
            st.caption(f"Base: Consumo {consumo_medio}kWh | Disp. {custo_disponibilidade}kWh")
