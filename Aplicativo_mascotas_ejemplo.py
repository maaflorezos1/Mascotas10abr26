#Importar las librerias necesarias
import streamlit as st
import pandas as pd
from pandasql import sqldf
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

#Vamos a crear el dataframe con los datos de ejemplo mascotas
df_mascotas = pd.read_csv('mascotas_completa.csv', sep=";", encoding="latin-1")

# Renombrar columna para facilitar
df_mascotas.rename(columns={'Gasto última consulta': 'Gasto_ultima_consulta'}, inplace=True)

# Eliminar filas con valores NaN (columnas incompletas o vacías)
df_mascotas = df_mascotas.dropna()

# Calcular días desde última revisión
df_mascotas['ultima_revision'] = pd.to_datetime(df_mascotas['ultima_revision'], format='%d/%m/%Y')
df_mascotas['dias_desde_revision'] = (datetime(2026, 4, 21) - df_mascotas['ultima_revision']).dt.days

# Consulta 1: Cantidad total de id (mascotas)
df_total_mascotas = sqldf("SELECT COUNT(id) AS total_mascotas FROM df_mascotas")

# Consulta 2: Cantidad de id total por departamento
df_mascotas_por_departamento = sqldf("SELECT departamento, COUNT(id) AS cantidad_mascotas FROM df_mascotas GROUP BY departamento")

# Consulta 3: Cantidad de id total por ciudad
df_mascotas_por_ciudad = sqldf("SELECT ciudad, COUNT(id) AS cantidad_mascotas FROM df_mascotas GROUP BY ciudad")

# Consulta 4: Listado de especie ordenadas por cantidad de id, de mayor a menor
df_especies_por_cantidad = sqldf("SELECT especie, COUNT(id) AS cantidad_mascotas FROM df_mascotas GROUP BY especie ORDER BY cantidad_mascotas DESC")

# Consulta 5: Cantidad de id con estado "Enfermo" en columna estado_salud
df_mascotas_enfermas = sqldf("SELECT COUNT(id) AS cantidad_enfermas FROM df_mascotas WHERE estado_salud = 'Enfermo'")

# Consulta 6: Top 5 de id con estado "Enfermo" por especie
df_top5_enfermas_por_especie = sqldf("SELECT especie, COUNT(id) AS cantidad_enfermas FROM df_mascotas WHERE estado_salud = 'Enfermo' GROUP BY especie ORDER BY cantidad_enfermas DESC LIMIT 5")

# Consulta 7: Top 7 mascotas con más días desde revisión
df_top7_dias_revision = sqldf("SELECT nombre, dias_desde_revision FROM df_mascotas ORDER BY dias_desde_revision DESC LIMIT 7")

# Consulta 8: Porcentaje de id con estado 't' en columna vacunacion_al_dia
df_porcentaje_vacunados = sqldf("SELECT (COUNT(CASE WHEN vacunacion_al_dia = 't' THEN 1 END) * 100.0 / COUNT(*)) AS porcentaje_vacunados FROM df_mascotas")

# Consulta 9: Costo total de Gasto última consulta
df_costo_total_consultas = sqldf("SELECT SUM(Gasto_ultima_consulta) AS costo_total FROM df_mascotas")

# Consulta 10: Top 5 mascotas con mayor Gasto última consulta
df_top5_gasto_consulta = sqldf("SELECT nombre, Gasto_ultima_consulta FROM df_mascotas ORDER BY Gasto_ultima_consulta DESC LIMIT 5")

# Estilos CSS
st.markdown("""
<style>
    body {
        background-color: #f0f8ff;
        font-family: 'Arial', sans-serif;
        font-size: 18px;
    }
    .stButton>button {
        background-color: #4682b4;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 15px;
        font-size: 16px;
        margin: 0 5px;
    }
    .stButton>button:hover {
        background-color: #32cd32;
    }
    .metric {
        background-color: #e6f3ff;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 2px solid #4682b4;
        margin: 10px auto;
        width: 80%;
    }
    h1, h2, h3 {
        color: #2e8b57;
        font-weight: bold;
        text-align: center;
    }
    .plotly-graph-div {
        border-radius: 10px;
        border: 2px solid #4682b4;
    }
    .plotly-graph-div:hover {
        border-color: #32cd32;
    }
    .dataframe {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Menú centrado
st.markdown("<h1 style='text-align: center;'>🐶 Aplicativo de Mascotas 🐱</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("🏠 Página de Inicio"):
        st.session_state.page = "home"
with col2:
    if st.button("📊 Sección 1"):
        st.session_state.page = "section1"
with col3:
    if st.button("🩺 Sección 2"):
        st.session_state.page = "section2"

if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.markdown("## **🏠 Página de Inicio**")
    st.markdown("<div class='metric'><h2>Total de Mascotas</h2><h1>{}</h1></div>".format(df_total_mascotas['total_mascotas'].iloc[0]), unsafe_allow_html=True)
    st.write("**Análisis detallado:** El dataframe contiene un total de {} mascotas registradas después de limpiar los datos. Esta cifra representa la base de datos completa de mascotas en el sistema, lo que permite un análisis integral de la población animal atendida. Es fundamental mantener este número actualizado para una gestión eficiente de los recursos veterinarios y el seguimiento de la salud de las mascotas.".format(df_total_mascotas['total_mascotas'].iloc[0]))

elif st.session_state.page == "section1":
    st.markdown("## **📊 Sección 1: Distribución por Ubicación y Especies**")
    
    st.markdown("### **🐾 Mascotas por Departamento**")
    fig1 = px.bar(df_mascotas_por_departamento.sort_values('cantidad_mascotas', ascending=False), x='departamento', y='cantidad_mascotas', color='departamento')
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1)
    st.write("**Análisis detallado:** Cundinamarca y Valle del Cauca lideran con el mayor número de mascotas registradas, lo que indica una alta concentración en estas regiones. Esto puede deberse a factores como densidad poblacional urbana y acceso a servicios veterinarios. Es importante considerar estrategias de distribución de recursos para equilibrar la atención en áreas con menor representación.")
    
    st.markdown("### **🏙️ Mascotas por Ciudad (Horizontal)**")
    fig2 = px.bar(df_mascotas_por_ciudad.sort_values('cantidad_mascotas', ascending=False), x='cantidad_mascotas', y='ciudad', orientation='h', color='ciudad')
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2)
    st.write("**Análisis detallado:** Cali y Bogotá destacan como las ciudades con más mascotas, reflejando su estatus como centros urbanos principales. El gráfico horizontal facilita la comparación visual, mostrando cómo la urbanización influye en la tenencia de mascotas. Recomendamos monitorear tendencias para anticipar necesidades futuras en salud animal.")
    
    st.markdown("### **🦎 Especies por Cantidad (Horizontal)**")
    fig_especies = px.bar(df_especies_por_cantidad, x='cantidad_mascotas', y='especie', orientation='h', color='especie')
    fig_especies.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_especies)
    st.write("**Análisis detallado:** Los conejos predominan como la especie más común, seguidos de aves y peces. Esta distribución sugiere preferencias culturales o ambientales en la tenencia de mascotas. Entender estas tendencias ayuda a adaptar servicios veterinarios especializados y promover la adopción responsable según la demanda.")

elif st.session_state.page == "section2":
    st.markdown("## **🩺 Sección 2: Salud y Costos**")
    
    st.markdown("### **🤒 Cantidad de Mascotas Enfermas**")
    st.markdown("<div class='metric'><h2>Mascotas Enfermas</h2><h1>{}</h1></div>".format(df_mascotas_enfermas['cantidad_enfermas'].iloc[0]), unsafe_allow_html=True)
    st.write("**Análisis detallado:** Un total de {} mascotas se encuentran en estado enfermo, representando aproximadamente el {}% del total. Esta cifra destaca la importancia de revisiones periódicas y campañas de prevención. Identificar patrones en enfermedades puede ayudar a implementar protocolos de salud más efectivos.".format(df_mascotas_enfermas['cantidad_enfermas'].iloc[0], round(df_mascotas_enfermas['cantidad_enfermas'].iloc[0] / df_total_mascotas['total_mascotas'].iloc[0] * 100, 2)))
    
    st.markdown("### **📈 Top 5 Especies con Más Mascotas Enfermas**")
    fig3 = px.pie(df_top5_enfermas_por_especie, names='especie', values='cantidad_enfermas', title='Distribución de Mascotas Enfermas por Especie')
    fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3)
    st.write("**Análisis detallado:** Las aves y conejos concentran la mayoría de los casos enfermos, lo que podría indicar vulnerabilidades específicas por especie. Este patrón sugiere la necesidad de investigaciones sobre factores ambientales o genéticos que afectan a estas especies, permitiendo intervenciones preventivas más precisas.")
    
    st.markdown("### **⏰ Top 7 Mascotas con Más Días desde Revisión**")
    styled_df = df_top7_dias_revision.style.apply(lambda x: ['background-color: #f0f0f0' if i % 2 == 0 else '' for i in range(len(x))], axis=0).set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold')]}])
    st.dataframe(styled_df)
    st.write("**Análisis detallado:** Estas mascotas requieren atención inmediata, ya que el tiempo transcurrido desde su última revisión supera los estándares recomendados. Priorizar revisiones para estos animales puede prevenir complicaciones de salud y reducir costos futuros en tratamientos.")
    
    st.markdown("### **💉 Porcentaje de Mascotas Vacunadas**")
    total = df_total_mascotas['total_mascotas'].iloc[0]
    porcentaje = df_porcentaje_vacunados['porcentaje_vacunados'].iloc[0]
    vacunados = int(total * porcentaje / 100)
    no_vacunados = total - vacunados
    fig4 = px.pie(names=['Vacunados', 'No Vacunados'], values=[vacunados, no_vacunados], title='Estado de Vacunación')
    fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig4)
    st.write("**Análisis detallado:** Solo el {}% de las mascotas están al día con sus vacunas, dejando un {}% vulnerable a enfermedades prevenibles. Esta brecha resalta la necesidad de campañas de vacunación masivas y educación a los dueños sobre la importancia de mantener el calendario vacunal.")
    
    st.markdown("### **💰 Costo Total de Últimas Consultas**")
    st.markdown("<div class='metric'><h2>Costo Total</h2><h1>${:,}</h1></div>".format(df_costo_total_consultas['costo_total'].iloc[0]), unsafe_allow_html=True)
    st.write("**Análisis detallado:** El costo total de las últimas consultas asciende a ${:,}, reflejando la inversión en salud animal. Analizar estos gastos por especie o región puede optimizar presupuestos y identificar áreas donde se pueden reducir costos mediante prevención.")
    
    st.markdown("### **📊 Top 5 Mascotas con Mayor Gasto en Última Consulta**")
    fig5 = px.bar(df_top5_gasto_consulta, x='nombre', y='Gasto_ultima_consulta', color='nombre')
    fig5.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig5)
    st.write("**Análisis detallado:** Estas mascotas incurrieron en los gastos más altos, posiblemente debido a tratamientos especializados. Revisar estos casos puede proporcionar insights sobre enfermedades costosas y estrategias para mitigar riesgos financieros asociados con la salud de mascotas.")



