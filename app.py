import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Загрузка данных
@st.cache_data
def load_data():
    df = pd.read_excel('tv_advertising_data.xlsx')
    df['Дата'] = pd.to_datetime(df['Дата'])
    return df

df = load_data()

# Элегантный стиль
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.95);
        z-index: -1;
    }
    h1, h2, h3 {
        color: #667eea;
        font-weight: 600;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #667eea30;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Заголовок
st.title("📺 Анализ стоимости спонсорской рекламы на телевидении")
st.markdown("Интерактивный дашборд для анализа факторов, формирующих стоимость рекламы.")

# Боковая панель для фильтров
st.sidebar.header("Фильтры")

# Фильтр по дате
date_range = st.sidebar.date_input("Выберите диапазон дат", [df['Дата'].min(), df['Дата'].max()])
start_date, end_date = date_range

# Фильтр по каналу
channels = df['Канал'].unique()
selected_channels = st.sidebar.multiselect("Каналы", channels, default=channels)

# Фильтр по временному слоту
time_slots = df['Временной_слот'].unique()
selected_time_slots = st.sidebar.multiselect("Временные слоты", time_slots, default=time_slots)

# Фильтр по типу программы
program_types = df['Тип_программы'].unique()
selected_program_types = st.sidebar.multiselect("Типы программ", program_types, default=program_types)

# Фильтр по типу рекламодателя
advertiser_types = df['Тип_рекламодателя'].unique()
selected_advertiser_types = st.sidebar.multiselect("Типы рекламодателей", advertiser_types, default=advertiser_types)

# Применение фильтров
filtered_df = df[
    (df['Дата'] >= pd.to_datetime(start_date)) &
    (df['Дата'] <= pd.to_datetime(end_date)) &
    (df['Канал'].isin(selected_channels)) &
    (df['Временной_слот'].isin(selected_time_slots)) &
    (df['Тип_программы'].isin(selected_program_types)) &
    (df['Тип_рекламодателя'].isin(selected_advertiser_types))
]

# Вкладки
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Обычная таблица", 
    "Фильтрованная таблица", 
    "Стилизованная таблица", 
    "Сводная таблица", 
    "Графики и анализ"
])

with tab1:
    st.header("Обычная таблица данных")
    st.dataframe(df.head(100))

with tab2:
    st.header("Фильтрованная таблица")
    st.dataframe(filtered_df.head(100))
    st.info(f"Всего записей после фильтрации: {len(filtered_df)}")

with tab3:
    st.header("Стилизованная таблица")
    st.markdown("""
    <style>
    .dataframe th {
        background-color: #667eea;
        color: white;
        font-weight: bold;
    }
    .dataframe td {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Форматирование числовых столбцов
    styled_df = filtered_df.head(100).copy()
    st.dataframe(styled_df)

with tab4:
    st.header("Сводная таблица")
    
    # Выбор параметров для сводной таблицы
    col1, col2 = st.columns(2)
    with col1:
        pivot_index = st.selectbox("Строки", ['Канал', 'Временной_слот', 'Тип_программы', 'Тип_рекламодателя'])
    with col2:
        pivot_columns = st.selectbox("Столбцы", ['Временной_слот', 'Канал', 'Тип_программы', 'Тип_рекламодателя'])
    
    # Сводная таблица: средняя стоимость
    pivot_df = filtered_df.pivot_table(
        values='Стоимость_руб', 
        index=pivot_index, 
        columns=pivot_columns, 
        aggfunc='mean'
    )
    st.dataframe(pivot_df.style.format("{:.0f}"))
    
    # Дополнительная статистика
    st.subheader("Статистика по стоимости")
    stats_df = filtered_df.groupby('Канал').agg({
        'Стоимость_руб': ['mean', 'median', 'min', 'max'],
        'Рейтинг': 'mean',
        'CPT_руб': 'mean'
    }).round(2)
    st.dataframe(stats_df)

with tab5:
    st.header("Графики и визуализации")
    
    # Ключевые метрики
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Средняя стоимость", f"{filtered_df['Стоимость_руб'].mean():,.0f} ₽")
    with col2:
        st.metric("Средний рейтинг", f"{filtered_df['Рейтинг'].mean():.2f}")
    with col3:
        st.metric("Средний CPT", f"{filtered_df['CPT_руб'].mean():.2f} ₽")
    with col4:
        st.metric("Всего контрактов", f"{len(filtered_df):,}")
    
    st.markdown("---")
    
    # График 1: Стоимость по временным слотам
    st.subheader("1. Зависимость стоимости от временного слота")
    time_slot_cost = filtered_df.groupby('Временной_слот')['Стоимость_руб'].mean().reset_index()
    fig1 = px.bar(time_slot_cost, x='Временной_слот', y='Стоимость_руб',
                  title='Средняя стоимость рекламы по временным слотам',
                  labels={'Стоимость_руб': 'Средняя стоимость (₽)', 'Временной_слот': 'Временной слот'},
                  color='Стоимость_руб', color_continuous_scale='Viridis')
    st.plotly_chart(fig1, use_container_width=True)
    
    # График 2: Стоимость по каналам
    st.subheader("2. Сравнение стоимости по каналам")
    channel_cost = filtered_df.groupby('Канал')['Стоимость_руб'].mean().sort_values(ascending=False).reset_index()
    fig2 = px.bar(channel_cost, x='Канал', y='Стоимость_руб',
                  title='Средняя стоимость рекламы по каналам',
                  labels={'Стоимость_руб': 'Средняя стоимость (₽)', 'Канал': 'Телеканал'},
                  color='Стоимость_руб', color_continuous_scale='Blues')
    st.plotly_chart(fig2, use_container_width=True)
    
    # График 3: Зависимость стоимости от рейтинга
    st.subheader("3. Корреляция между рейтингом и стоимостью")
    fig3 = px.scatter(filtered_df.sample(min(1000, len(filtered_df))), 
                      x='Рейтинг', y='Стоимость_руб',
                      color='Временной_слот', size='Длительность_сек',
                      title='Зависимость стоимости от рейтинга программы',
                      labels={'Стоимость_руб': 'Стоимость (₽)', 'Рейтинг': 'Рейтинг программы'},
                      hover_data=['Канал', 'Тип_программы'])
    st.plotly_chart(fig3, use_container_width=True)
    
    # График 4: Динамика стоимости по месяцам
    st.subheader("4. Сезонность стоимости рекламы")
    monthly_cost = filtered_df.groupby('Месяц')['Стоимость_руб'].mean().reset_index()
    month_names = {1: 'Янв', 2: 'Фев', 3: 'Мар', 4: 'Апр', 5: 'Май', 6: 'Июн',
                   7: 'Июл', 8: 'Авг', 9: 'Сен', 10: 'Окт', 11: 'Ноя', 12: 'Дек'}
    monthly_cost['Месяц_название'] = monthly_cost['Месяц'].map(month_names)
    fig4 = px.line(monthly_cost, x='Месяц_название', y='Стоимость_руб',
                   title='Сезонность стоимости рекламы по месяцам',
                   labels={'Стоимость_руб': 'Средняя стоимость (₽)', 'Месяц_название': 'Месяц'},
                   markers=True)
    st.plotly_chart(fig4, use_container_width=True)
    
    # График 5: Тепловая карта
    st.subheader("5. Тепловая карта: Канал vs Временной слот")
    heatmap_data = filtered_df.pivot_table(
        values='Стоимость_руб',
        index='Канал',
        columns='Временной_слот',
        aggfunc='mean'
    )
    fig5 = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn_r',
        text=heatmap_data.values.round(0),
        texttemplate='%{text:,.0f}',
        textfont={"size": 10}
    ))
    fig5.update_layout(title='Средняя стоимость рекламы: Канал × Временной слот')
    st.plotly_chart(fig5, use_container_width=True)
    
    # График 6: Распределение по длительности
    st.subheader("6. Влияние длительности ролика на стоимость")
    duration_cost = filtered_df.groupby('Длительность_сек')['Стоимость_руб'].mean().reset_index()
    fig6 = px.bar(duration_cost, x='Длительность_сек', y='Стоимость_руб',
                  title='Зависимость стоимости от длительности ролика',
                  labels={'Стоимость_руб': 'Средняя стоимость (₽)', 'Длительность_сек': 'Длительность (сек)'},
                  color='Стоимость_руб', color_continuous_scale='Reds')
    st.plotly_chart(fig6, use_container_width=True)
    
    # График 7: CPT по типам рекламодателей
    st.subheader("7. Эффективность (CPT) по типам рекламодателей")
    advertiser_cpt = filtered_df.groupby('Тип_рекламодателя')['CPT_руб'].mean().sort_values().reset_index()
    fig7 = px.bar(advertiser_cpt, x='CPT_руб', y='Тип_рекламодателя',
                  title='Средний CPT по типам рекламодателей',
                  labels={'CPT_руб': 'CPT (₽)', 'Тип_рекламодателя': 'Тип рекламодателя'},
                  orientation='h', color='CPT_руб', color_continuous_scale='Purples')
    st.plotly_chart(fig7, use_container_width=True)

# Экспорт в Excel
st.sidebar.markdown("---")
if st.sidebar.button("📥 Экспорт отфильтрованных данных"):
    filtered_df.to_excel('filtered_tv_advertising_data.xlsx', index=False)
    st.sidebar.success("✅ Данные экспортированы!")
