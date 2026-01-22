import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Функция для генерации данных о спонсорской рекламе на ТВ
def generate_tv_advertising_data(num_records=5000):
    data = []
    start_date = datetime(2023, 1, 1)
    
    # Справочники
    channels = ['Первый канал', 'Россия 1', 'НТВ', 'ТНТ', 'СТС', 'Пятый канал', 'Рен ТВ', 'Матч ТВ']
    program_types = ['Новости', 'Сериал', 'Развлекательное шоу', 'Спортивная передача', 
                     'Документальный фильм', 'Ток-шоу', 'Кино', 'Утреннее шоу']
    time_slots = ['Утро (06:00-09:00)', 'День (09:00-18:00)', 'Прайм-тайм (18:00-23:00)', 'Ночь (23:00-06:00)']
    advertiser_types = ['FMCG', 'Автомобили', 'Финансы', 'Телекоммуникации', 'Ритейл', 'Фармацевтика', 'Технологии']
    ad_durations = [10, 15, 20, 30, 45, 60]  # секунды
    
    for i in range(num_records):
        date = start_date + timedelta(days=random.randint(0, 365))
        channel = random.choice(channels)
        program_type = random.choice(program_types)
        time_slot = random.choice(time_slots)
        advertiser_type = random.choice(advertiser_types)
        duration = random.choice(ad_durations)
        
        # Базовая стоимость зависит от времени
        base_cost = {
            'Утро (06:00-09:00)': 50000,
            'День (09:00-18:00)': 80000,
            'Прайм-тайм (18:00-23:00)': 200000,
            'Ночь (23:00-06:00)': 30000
        }[time_slot]
        
        # Коэффициенты для каналов
        channel_multiplier = {
            'Первый канал': 1.5,
            'Россия 1': 1.4,
            'НТВ': 1.3,
            'ТНТ': 1.1,
            'СТС': 1.0,
            'Пятый канал': 0.8,
            'Рен ТВ': 0.9,
            'Матч ТВ': 1.2
        }[channel]
        
        # Рейтинг программы (влияет на стоимость)
        rating = round(random.uniform(1.0, 15.0), 2)
        
        # Охват аудитории (тысяч человек)
        audience_reach = int(rating * random.randint(50000, 200000) / 10)
        
        # Расчет стоимости
        cost = int(base_cost * channel_multiplier * (duration / 30) * (1 + rating / 10) * random.uniform(0.9, 1.1))
        
        # CPT (Cost Per Thousand) - стоимость за тысячу зрителей
        cpt = round(cost / (audience_reach / 1000), 2) if audience_reach > 0 else 0
        
        # День недели
        weekday = date.strftime('%A')
        is_weekend = weekday in ['Saturday', 'Sunday']
        
        # Сезонность (выше в праздничные месяцы)
        month = date.month
        seasonal_factor = 1.2 if month in [11, 12, 1] else 1.0
        cost = int(cost * seasonal_factor)
        
        data.append({
            'Дата': date.date(),
            'Канал': channel,
            'Тип_программы': program_type,
            'Временной_слот': time_slot,
            'Длительность_сек': duration,
            'Рейтинг': rating,
            'Охват_аудитории_тыс': audience_reach,
            'Тип_рекламодателя': advertiser_type,
            'Стоимость_руб': cost,
            'CPT_руб': cpt,
            'День_недели': weekday,
            'Выходной': is_weekend,
            'Месяц': month
        })
    
    return pd.DataFrame(data)

# Генерация данных
print("Генерация данных о спонсорской рекламе на ТВ...")
df = generate_tv_advertising_data(num_records=5000)

# Сохранение в XLSX
df.to_excel('tv_advertising_data.xlsx', index=False)

print(f"Данные сохранены в tv_advertising_data.xlsx")
print(f"Всего записей: {len(df)}")
print(f"\nПример данных:")
print(df.head())
print(f"\nСтатистика по стоимости:")
print(df['Стоимость_руб'].describe())
