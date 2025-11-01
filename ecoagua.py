import streamlit as st
from fpdf import FPDF

class Apartamento:
    def __init__(self, moradores, banheira=False, atividades_extra=[], maquinas_lavar=0, uso_maquinas_mensal=0):
        self.moradores = moradores
        self.banheira = banheira
        self.atividades_extra = atividades_extra
        self.maquinas_lavar = maquinas_lavar
        self.uso_maquinas_mensal = uso_maquinas_mensal

    def consumo_mensal(self):
        base = self.moradores * 154 * 30  # litros/mês
        if self.banheira:
            base += 300 * 4
        for atividade in self.atividades_extra:
            base += atividade
        base += self.maquinas_lavar * self.uso_maquinas_mensal * 135  # máquina de lavar
        return base / 1000  # m³

class Predio:
    def __init__(self, apartamentos, areas_comuns, consumo_real_m3, valor_m3):
        self.apartamentos = apartamentos
        self.areas_comuns = areas_comuns
        self.consumo_real_m3 = consumo_real_m3
        self.valor_m3 = valor_m3

    def consumo_total_estimado(self):
        consumo_apartamentos = sum([ap.consumo_mensal() for ap in self.apartamentos])
        consumo_areas = self.calcular_consumo_areas_comuns()
        return consumo_apartamentos + consumo_areas

    def calcular_consumo_areas_comuns(self):
        consumo = 0
        for area, dados in self.areas_comuns.items():
            m2 = dados['metragem']
            freq = dados['frequencia']
            consumo += m2 * 5 * freq
        return consumo / 1000

    def relatorio(self):
        estimado = self.consumo_total_estimado()
        economia = self.consumo_real_m3 - estimado
        valor_estimado = estimado * self.valor_m3
        valor_real = self.consumo_real_m3 * self.valor_m3
        valor_economia = economia * self.valor_m3

        return {
            "Consumo estimado (m³)": f"{estimado:.2f}",
            "Consumo real (m³)": f"{self.consumo_real_m3:.2f}",
            "Diferença (m³)": f"{economia:.2f}",
            "Valor estimado (R$)": f"{valor_estimado:.2f}",
            "Valor real (R$)": f"{valor_real:.2f}",
            "Economia possível (R$)": f"{valor_economia:.2f}"
        }

def gerar_pdf(relatorio, nome_cliente, endereco_cliente, contato_cliente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Relatório de Consumo - EcoAgua", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    if nome_cliente:
        pdf.cell(200, 10, txt=f"Cliente / Condomínio: {nome_cliente}", ln=True)
    if endereco_cliente:
        pdf.cell(200, 10, txt=f"Endereço: {endereco_cliente}", ln=True)
    if contato_cliente:
        pdf.cell(200, 10, txt=f"Contato: {contato_cliente}", ln=True)

    pdf.ln(10)
    for chave, valor in relatorio.items():
        linha = f"{chave}: {valor}"
        pdf.cell(200, 10, txt=linha, ln=True)

    return pdf.output(dest='S').encode('latin-1')

# Interface Streamlit
st.title("🌿 EcoAgua - Simulador de Consumo de Água")

# Dados do cliente
nome_cliente = st.text_input("🏢 Nome do Cliente / Condomínio")
endereco_cliente = st.text_input("📍 Endereço")
contato_cliente = st.text_input("📞 Nome e telefone de contato")

valor_m3 = st.number_input("💧 Valor do m³ cobrado pela prestadora (R$)", min_value=0.0)
consumo_real = st.number_input("📄 Consumo real do prédio (m³)", min_value=0.0)
qtd_apts = st.number_input("🏢 Quantidade de apartamentos", min_value=1, step=1)

apartamentos = []
for i in range(qtd_apts):
    st.subheader(f"Apartamento {i+1}")
    moradores = st.number_input(f"👨‍👩‍👧‍👦 Moradores no apt {i+1}", min_value=1, step=1, key=f"moradores_{i}")
    banheira = st.checkbox(f"🛁 Possui banheira de hidromassagem?", key=f"banheira_{i}")
    atividades_extra = []
    if st.checkbox(f"⚙️ Possui atividades extras que consomem água?", key=f"extra_{i}"):
        qtd_atividades = st.number_input("Quantas atividades extras?", min_value=1, step=1, key=f"qtd_extra_{i}")
        for j in range(qtd_atividades):
            litros = st.number_input(f"Consumo da atividade {j+1} (litros/mês)", min_value=0, step=1, key=f"atividade_{i}_{j}")
            atividades_extra.append(litros)
    maquinas_lavar = st.number_input("🧺 Quantidade de máquinas de lavar roupa", min_value=0, step=1, key=f"maquinas_{i}")
    uso_maquinas_mensal = st.number_input("🔁 Lavagens por mês", min_value=0, step=1, key=f"uso_maquinas_{i}")
    apt = Apartamento(moradores, banheira, atividades_extra, maquinas_lavar, uso_maquinas_mensal)
    apartamentos.append(apt)

st.subheader("🏞️ Áreas Comuns")
areas_comuns = {}
for area in ["quintal", "garagem", "área social", "área de lazer", "área da piscina"]:
    metragem = st.number_input(f"Metragem da {area} (m²)", min_value=0.0, key=f"metragem_{area}")
    freq = st.number_input(f"Frequência de lavagem da {area} (vezes/semana)", min_value=0, step=1, key=f"freq_{area}")
    areas_comuns[area] = {"metragem": metragem, "frequencia": freq}

if st.button("📊 Gerar Relatório"):
    predio = Predio(apartamentos, areas_comuns, consumo_real, valor_m3)
    relatorio = predio.relatorio()
    st.success("✅ Relatório gerado com sucesso!")
    for chave, valor in relatorio.items():
        st.write(f"**{chave}**: {valor}")

    pdf_bytes = gerar_pdf(relatorio, nome_cliente, endereco_cliente, contato_cliente)
    st.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_bytes,
        file_name="relatorio_ecoagua.pdf",
        mime="application/pdf"
    )