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
    # Убедимся, что есть столбец 'Месяц' для графиков
    if 'Месяц' not in df.columns:
        df['Месяц'] = df['Дата'].dt.month
    return df

df = load_data()

# Современный, привлекающий внимание, но ненавязчивый стиль
st.markdown(
    """
    <style>
    /* Фон приложения */
    .stApp {
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        background-attachment: fixed;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background-color: rgba(255, 255, 255, 0.97);
        z-index: -1;
    }

    /* Заголовки */
    h1 {
        color: #4c1d95;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #7e22ce, #4c1d95);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    h2, h3 {
        color: #5b21b6;
        font-weight: 600;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f3ff 0%, #ffffff 100%);
        border-right: 1px solid #e9d5ff;
    }

    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #7e22ce 0%, #8b5cf6 100%);
        color: white;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        border: none;
        box-shadow: 0 4px 12px rgba(126, 34, 206, 0.25);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(126, 34, 206, 0.35);
    }

    /* Улучшенный стиль для таблиц (через Pandas .style) */
    table {
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.95em;
        min-width: 100%;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    thead tr {
        background-color: #7e22ce;
        color: #ffffff;
        text-align: left;
        font-weight: 600;
    }
    th, td {
        padding: 12px 15px;
        text-align: right;
    }
    tbody tr {
        border-bottom: 1px solid #e0e0e0;
    }
    tbody tr:nth-of-type(even) {
        background-color: #faf5ff;
    }
    tbody tr:last-of-type {
        border-bottom: 2px solid #7e22ce;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Заголовок
st.title("📺 Анализ стоимости промоутинга на телевидении")
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
selected_time_slots = st.sidebar.multiselect("Временной диапазон", time_slots, default=time_slots)

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

# Функция для стилизации таблиц
def style_dataframe(df, highlight_cols=None):
    if highlight_cols is None:
        highlight_cols = []
    
    styler = df.style
    
    # Форматирование числовых столбцов
    numeric_cols = df.select_dtypes(include=['number']).columns
    styler = styler.format({col: "{:,.0f}" if col in ['Стоимость_руб'] else 
                           "{:.2f}" for col in numeric_cols})
    
    # Зебра-раскраска
    styler = styler.set_table_styles([
        {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#faf5ff')]},
        {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#ffffff')]},
        {'selector': 'thead', 'props': [('background-color', '#7e22ce'), ('color', 'white'), ('font-weight', 'bold')]},
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [('text-align', 'right')]},
    ], overwrite=False)
    
    # Дополнительное выделение ключевых столбцов (если нужно)
    if highlight_cols:
        styler = styler.highlight_max(subset=highlight_cols, color='#ede9fe')
    
    return styler

with tab1:
    st.header("Обычная таблица данных")
    st.write(style_dataframe(df.head(100)).to_html(), unsafe_allow_html=True)

with tab2:
    st.header("Фильтрованная таблица")
    st.write(style_dataframe(filtered_df.head(100)).to_html(), unsafe_allow_html=True)
    st.info(f"Всего записей после фильтрации: {len(filtered_df)}")

with tab3:
    st.header("Стилизованная таблица")
    styled_df = filtered_df.head(100).copy()
    # Добавим подсветку максимальной стоимости
    st.write(style_dataframe(styled_df, highlight_cols=['Стоимость_руб']).to_html(), unsafe_allow_html=True)

with tab4:
    st.header("Сводная таблица")
    
    col1, col2 = st.columns(2)
    with col1:
        pivot_index = st.selectbox("Строки", ['Канал', 'Временной_слот', 'Тип_программы', 'Тип_рекламодателя'], key='pivot1')
    with col2:
        pivot_columns = st.selectbox("Столбцы", ['Временной_слот', 'Канал', 'Тип_программы', 'Тип_рекламодателя'], key='pivot2')
    
    pivot_df = filtered_df.pivot_table(
        values='Стоимость_руб', 
        index=pivot_index, 
        columns=pivot_columns, 
        aggfunc='mean',
        fill_value=0
    )
    
    # Стилизация сводной таблицы
    pivot_styler = pivot_df.style.format("{:.0f}") \
        .background_gradient(cmap="Blues", axis=None) \
        .set_properties(**{'text-align': 'center'}) \
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#7e22ce'), ('color', 'white')]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ])
    
    st.write(pivot_styler.to_html(), unsafe_allow_html=True)
    
    # Статистика по каналам
    st.subheader("Статистика по стоимости")
    stats_df = filtered_df.groupby('Канал').agg({
        'Стоимость_руб': ['mean', 'median', 'min', 'max'],
        'Рейтинг': 'mean',
        'CPT_руб': 'mean'
    }).round(2)
    
    stats_df.columns = ['Средняя стоимость', 'Медиана', 'Минимум', 'Максимум', 'Средний рейтинг', 'Средний CPT']
    st.write(style_dataframe(stats_df).to_html(), unsafe_allow_html=True)

# Вкладка с графиками остаётся без изменений (логика та же)
with tab5:
    st.header("Графики и визуализации")
    
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
                  color='Стоимость_руб', color_continuous_scale='Purples')
    st.plotly_chart(fig1, use_container_width=True)
    
    # График 2: Стоимость по каналам
    st.subheader("2. Сравнение стоимости по каналам")
    channel_cost = filtered_df.groupby('Канал')['Стоимость_руб'].mean().sort_values(ascending=False).reset_index()
    fig2 = px.bar(channel_cost, x='Канал', y='Стоимость_руб',
                  title='Средняя стоимость рекламы по каналам',
                  labels={'Стоимость_руб': 'Средняя стоимость (₽)', 'Канал': 'Телеканал'},
                  color='Стоимость_руб', color_continuous_scale='Purples')
    st.plotly_chart(fig2, use_container_width=True)
    
    # График 3: Зависимость стоимости от рейтинга
    st.subheader("3. Корреляция между рейтингом и стоимостью")
    sample_df = filtered_df.sample(min(1000, len(filtered_df)))
    fig3 = px.scatter(sample_df, 
                      x='Рейтинг', y='Стоимость_руб',
                      color='Временной_слот', size='Длительность_сек',
                      title='Зависимость стоимости от рейтинга программы',
                      labels={'Стоимость_руб': 'Стоимость (₽)', 'Рейтинг': 'Рейтинг программы'},
                      hover_data=['Канал', 'Тип_программы'])
    st.plotly_chart(fig3, use_container_width=True)
    
    # График 4: Динамика по месяцам
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
        aggfunc='mean',
        fill_value=0
    )
    fig5 = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Purples',
        text=heatmap_data.values.round(0),
        texttemplate='%{text:,.0f}',
        textfont={"size": 10}
    ))
    fig5.update_layout(title='Средняя стоимость рекламы: Канал × Временной слот')
    st.plotly_chart(fig5, use_container_width=True)
    
    # График 6: Длительность
    st.subheader("6. Влияние длительности ролика на стоимость")
    duration_cost = filtered_df.groupby('Длительность_сек')['Стоимость_руб'].mean().reset_index()
    fig6 = px.bar(duration_cost, x='Длительность_сек', y='Стоимость_руб',
                  title='Зависимость стоимости от длительности ролика',
                  labels={'Стоимость_руб': 'Средняя стоимость (₽)', 'Длительность_сек': 'Длительность (сек)'},
                  color='Стоимость_руб', color_continuous_scale='Purples')
    st.plotly_chart(fig6, use_container_width=True)
    
    # График 7: CPT по рекламодателям
    st.subheader("7. Эффективность (CPT) по типам рекламодателей")
    advertiser_cpt = filtered_df.groupby('Тип_рекламодателя')['CPT_руб'].mean().sort_values().reset_index()
    fig7 = px.bar(advertiser_cpt, x='CPT_руб', y='Тип_рекламодателя',
                  title='Средний CPT по типам рекламодателей',
                  labels={'CPT_руб': 'CPT (₽)', 'Тип_рекламодателя': 'Тип рекламодателя'},
                  orientation='h', color='CPT_руб', color_continuous_scale='Purples')
    st.plotly_chart(fig7, use_container_width=True)

# Экспорт
st.sidebar.markdown("---")
if st.sidebar.button("📥 Экспорт отфильтрованных данных"):
    filtered_df.to_excel('filtered_tv_advertising_data.xlsx', index=False)
    st.sidebar.success("✅ Данные экспортированы!")
