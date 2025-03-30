import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, Optional, Dict, List, Tuple


def rfm_analysis(
    data: pd.DataFrame,
    date_col: str,
    customer_col: str,
    amount_col: str,
    analysis_date: Optional[Union[str, dt.datetime]] = None,
    n_quantiles: int = 4,
    ranking_method: str = 'quantile',
    custom_intervals: Optional[Dict[str, List[float]]] = None,
    business_days_only: bool = False,
    segment_mapping: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Выполняет расширенный RFM-анализ на основе пользовательских данных.
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame с данными о транзакциях.
    date_col : str
        Название столбца с датами транзакций.
    customer_col : str
        Название столбца с идентификаторами клиентов.
    amount_col : str
        Название столбца с суммой транзакций.
    analysis_date : str or datetime, optional
        Дата, относительно которой рассчитывается Recency. 
        Если None, используется текущая дата.
    n_quantiles : int, default=4
        Количество квантилей для ранжирования.
    ranking_method : str, default='quantile'
        Метод ранжирования: 'quantile' для квантилей или 'fixed' для фиксированных интервалов.
    custom_intervals : dict, optional
        Пользовательские интервалы для ранжирования метрик при ranking_method='fixed'.
        Формат: {'R': [intervals], 'F': [intervals], 'M': [intervals]}.
    business_days_only : bool, default=False
        Учитывать только рабочие дни при расчете Recency.
    segment_mapping : dict, optional
        Словарь для маппинга RFM-сегментов. Если None, используется стандартная сегментация.
        
    Returns:
    --------
    Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]
        Кортеж из DataFrame с результатами RFM-анализа и словаря с дополнительной информацией.
    """
    # Валидация входных данных
    _validate_input_data(data, date_col, customer_col, amount_col)
    
    # Копирование данных во избежание изменения исходного DataFrame
    data_copy = data.copy()
    
    # Преобразование столбца с датами в datetime, если он еще не в этом формате
    if not pd.api.types.is_datetime64_any_dtype(data_copy[date_col]):
        try:
            data_copy[date_col] = pd.to_datetime(data_copy[date_col])
        except Exception as e:
            raise ValueError(f"Невозможно преобразовать столбец {date_col} в формат datetime: {str(e)}")
    
    # Устанавливаем дату анализа
    if analysis_date is None:
        current_date = dt.datetime.now()
    else:
        if isinstance(analysis_date, str):
            try:
                current_date = pd.to_datetime(analysis_date)
            except Exception as e:
                raise ValueError(f"Невозможно преобразовать analysis_date в формат datetime: {str(e)}")
        else:
            current_date = analysis_date
    
    # Рассчитываем метрики RFM
    rfm = _calculate_rfm_metrics(data_copy, customer_col, date_col, amount_col, current_date, business_days_only)
    
    # Присваиваем ранги для каждой метрики
    rfm = _assign_rfm_ranks(rfm, n_quantiles, ranking_method, custom_intervals)
    
    # Создаем RFM-сегменты
    rfm = _create_rfm_segments(rfm, segment_mapping)
    
    # Создаем дополнительную информацию для анализа
    additional_info = _create_additional_info(rfm)
    
    return rfm, additional_info


def _validate_input_data(data: pd.DataFrame, date_col: str, customer_col: str, amount_col: str) -> None:
    """Проверяет входные данные на корректность."""
    # Проверка наличия необходимых столбцов
    required_cols = [date_col, customer_col, amount_col]
    missing_cols = [col for col in required_cols if col not in data.columns]
    
    if missing_cols:
        raise ValueError(f"Отсутствуют следующие столбцы: {', '.join(missing_cols)}")
    
    # Проверка на пустые значения
    na_counts = data[required_cols].isna().sum()
    cols_with_na = [col for col, count in na_counts.items() if count > 0]
    
    if cols_with_na:
        warning_msg = f"Внимание: обнаружены пропущенные значения в столбцах: {', '.join(cols_with_na)}"
        print(warning_msg)
    
    # Проверка типа данных в столбце с суммой
    if not pd.api.types.is_numeric_dtype(data[amount_col]):
        try:
            # Пытаемся преобразовать к числовому типу
            pd.to_numeric(data[amount_col])
        except:
            raise ValueError(f"Столбец {amount_col} должен содержать числовые значения")
    
    # Проверка наличия отрицательных значений в столбце с суммой
    if (data[amount_col] < 0).any():
        print(f"Внимание: обнаружены отрицательные значения в столбце {amount_col}")
    
    # Проверка на минимальное количество данных
    if len(data) < 10:
        print("Внимание: слишком мало данных для надежного RFM-анализа")


def _calculate_rfm_metrics(data: pd.DataFrame, customer_col: str, date_col: str, 
                          amount_col: str, current_date: dt.datetime, 
                          business_days_only: bool) -> pd.DataFrame:
    """Рассчитывает базовые RFM-метрики."""
    # Расчет Recency
    if business_days_only:
        # Получаем максимальную дату для каждого клиента
        max_dates = data.groupby(customer_col)[date_col].max().reset_index()
        # Расчет рабочих дней между максимальной датой и текущей датой
        recency = max_dates.apply(
            lambda row: pd.bdate_range(start=row[date_col], end=current_date).shape[0] - 1, 
            axis=1
        )
        recency_df = pd.DataFrame({
            customer_col: max_dates[customer_col],
            'Recency': recency
        })
        
        # Объединяем с другими метриками
        rfm = data.groupby(customer_col).agg({
            customer_col: 'count',                             # Frequency
            amount_col: ['sum', 'mean', 'median', 'std']       # Monetary metrics
        })
        
        # Переименовываем столбцы
        rfm.columns = ['Frequency', 'Monetary_Sum', 'Monetary_Mean', 'Monetary_Median', 'Monetary_Std']
        rfm = rfm.reset_index()
        
        # Объединяем с Recency
        rfm = pd.merge(recency_df, rfm, on=customer_col)
        
    else:
        # Стандартный расчет всех метрик
        rfm = data.groupby(customer_col).agg({
            date_col: lambda x: (current_date - x.max()).days,  # Recency
            customer_col: 'count',                             # Frequency
            amount_col: ['sum', 'mean', 'median', 'std']       # Monetary metrics
        })
        
        # Переименовываем столбцы
        rfm.columns = ['Recency', 'Frequency', 'Monetary_Sum', 'Monetary_Mean', 'Monetary_Median', 'Monetary_Std']
        rfm = rfm.reset_index()
    
    # Основная метрика для Monetary - сумма
    rfm['Monetary'] = rfm['Monetary_Sum']
    
    # Обработка возможных ошибок в данных
    rfm['Recency'] = rfm['Recency'].clip(lower=0)  # Recency не может быть отрицательным
    rfm['Monetary_Std'] = rfm['Monetary_Std'].fillna(0)  # Заполняем NaN в стандартном отклонении
    
    return rfm


def _assign_rfm_ranks(rfm: pd.DataFrame, n_quantiles: int, 
                     ranking_method: str, custom_intervals: Optional[Dict[str, List[float]]]) -> pd.DataFrame:
    """Присваивает ранги для каждой RFM-метрики."""
    # Создаем копию DataFrame для работы
    rfm_ranked = rfm.copy()
    
    # Определяем метрики для ранжирования
    metrics = {
        'R': {'column': 'Recency', 'ascending': True},  # Для Recency меньшее значение лучше
        'F': {'column': 'Frequency', 'ascending': False},  # Для Frequency большее значение лучше
        'M': {'column': 'Monetary', 'ascending': False}  # Для Monetary большее значение лучше
    }
    
    # Присваиваем ранги для каждой метрики
    for metric_key, metric_info in metrics.items():
        column = metric_info['column']
        ascending = metric_info['ascending']
        
        # Обрабатываем исключения, когда квантильный метод не работает
        try:
            if ranking_method == 'quantile':
                # Метод квантилей
                labels = list(range(1, n_quantiles + 1))
                if not ascending:
                    labels = list(reversed(labels))
                    
                # Обработка случаев с одинаковыми значениями
                if rfm_ranked[column].nunique() < n_quantiles:
                    print(f"Предупреждение: в {column} меньше уникальных значений, чем требуемое количество квантилей ({n_quantiles}). "
                          f"Используем альтернативный метод ранжирования.")
                    rfm_ranked[f'{metric_key}_rank'] = pd.qcut(
                        rfm_ranked[column].rank(method='first'), 
                        q=n_quantiles, 
                        labels=labels,
                        duplicates='drop'
                    )
                else:
                    rfm_ranked[f'{metric_key}_rank'] = pd.qcut(
                        rfm_ranked[column], 
                        q=n_quantiles, 
                        labels=labels,
                        duplicates='drop'
                    )
                
            elif ranking_method == 'fixed':
                # Метод фиксированных интервалов
                if custom_intervals and metric_key in custom_intervals:
                    # Используем пользовательские интервалы
                    intervals = custom_intervals[metric_key]
                    if not ascending:
                        intervals = sorted(intervals, reverse=True)
                    
                    # Создаем ранги на основе интервалов
                    rfm_ranked[f'{metric_key}_rank'] = pd.cut(
                        rfm_ranked[column],
                        bins=[-float('inf')] + intervals + [float('inf')],
                        labels=list(range(1, len(intervals) + 2))
                    )
                else:
                    # Используем автоматически рассчитанные интервалы
                    min_val = rfm_ranked[column].min()
                    max_val = rfm_ranked[column].max()
                    step = (max_val - min_val) / n_quantiles
                    
                    intervals = [min_val + step * i for i in range(1, n_quantiles)]
                    if not ascending:
                        intervals = sorted(intervals, reverse=True)
                    
                    rfm_ranked[f'{metric_key}_rank'] = pd.cut(
                        rfm_ranked[column],
                        bins=[-float('inf')] + intervals + [float('inf')],
                        labels=list(range(1, n_quantiles + 1))
                    )
            else:
                raise ValueError(f"Неподдерживаемый метод ранжирования: {ranking_method}")
                
        except Exception as e:
            print(f"Ошибка при ранжировании {column}: {str(e)}. Используем альтернативный метод.")
            
            # Альтернативный метод ранжирования
            if rfm_ranked[column].nunique() <= 1:
                # Если все значения одинаковые, присваиваем средний ранг
                rfm_ranked[f'{metric_key}_rank'] = (n_quantiles + 1) // 2
            else:
                # Используем ранжирование по порядку
                ranks = rfm_ranked[column].rank(ascending=ascending, method='dense')
                max_rank = ranks.max()
                # Масштабируем ранги к диапазону от 1 до n_quantiles
                rfm_ranked[f'{metric_key}_rank'] = ((ranks - 1) / (max_rank - 1) * (n_quantiles - 1) + 1).round().astype(int)
    
    # Преобразуем ранги в целые числа
    for metric_key in metrics.keys():
        rfm_ranked[f'{metric_key}_rank'] = rfm_ranked[f'{metric_key}_rank'].astype(int)
    
    # Рассчитываем общий RFM-Score
    rfm_ranked['RFM_Score'] = rfm_ranked[['R_rank', 'F_rank', 'M_rank']].sum(axis=1)
    
    # Создаем RFM-комбинацию (строка из 3 цифр)
    rfm_ranked['RFM_Segment_Code'] = (
        rfm_ranked['R_rank'].astype(str) + 
        rfm_ranked['F_rank'].astype(str) + 
        rfm_ranked['M_rank'].astype(str)
    )
    
    return rfm_ranked


def _create_rfm_segments(rfm: pd.DataFrame, segment_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Создает сегменты клиентов на основе RFM-показателей."""
    # Создаем копию DataFrame
    rfm_segmented = rfm.copy()
    
    # Определяем сегменты на основе RFM-рангов, если не предоставлено пользовательское отображение
    if segment_mapping is None:
        # Создаем значения для сегментации
        rfm_segmented['R_Segment'] = pd.cut(
            rfm_segmented['R_rank'],
            bins=[0, 2, 4, 5],
            labels=['Давно', 'Недавно', 'Очень недавно'],
            include_lowest=True
        )
        
        rfm_segmented['F_Segment'] = pd.cut(
            rfm_segmented['F_rank'],
            bins=[0, 2, 4, 5],
            labels=['Редко', 'Часто', 'Очень часто'],
            include_lowest=True
        )
        
        rfm_segmented['M_Segment'] = pd.cut(
            rfm_segmented['M_rank'],
            bins=[0, 2, 4, 5],
            labels=['Низкая', 'Высокая', 'Очень высокая'],
            include_lowest=True
        )
        
        # Определяем основные сегменты клиентов
        conditions = [
            # Champions
            ((rfm_segmented['R_rank'] >= 3) & (rfm_segmented['F_rank'] >= 3) & (rfm_segmented['M_rank'] >= 3)),
            # Loyal Customers
            ((rfm_segmented['R_rank'] >= 3) & (rfm_segmented['F_rank'] >= 3) & (rfm_segmented['M_rank'] < 3)),
            # Potential Loyalists
            ((rfm_segmented['R_rank'] >= 3) & (rfm_segmented['F_rank'] < 3) & (rfm_segmented['M_rank'] >= 3)),
            # New Customers
            ((rfm_segmented['R_rank'] >= 3) & (rfm_segmented['F_rank'] < 3) & (rfm_segmented['M_rank'] < 3)),
            # At Risk
            ((rfm_segmented['R_rank'] < 3) & (rfm_segmented['F_rank'] >= 3) & (rfm_segmented['M_rank'] >= 3)),
            # Can't Lose Them
            ((rfm_segmented['R_rank'] < 3) & (rfm_segmented['F_rank'] >= 3) & (rfm_segmented['M_rank'] < 3)),
            # Lost
            ((rfm_segmented['R_rank'] < 3) & (rfm_segmented['F_rank'] < 3) & (rfm_segmented['M_rank'] < 3)),
            # Big Spenders
            ((rfm_segmented['R_rank'] < 3) & (rfm_segmented['F_rank'] < 3) & (rfm_segmented['M_rank'] >= 3)),
        ]
        
        choices = [
            'Чемпионы', 
            'Лояльные клиенты', 
            'Потенциально лояльные', 
            'Новые клиенты',
            'Под угрозой ухода', 
            'Нельзя потерять', 
            'Потерянные', 
            'Крупные покупатели'
        ]
        
        rfm_segmented['Customer_Segment'] = np.select(conditions, choices, default='Прочие')
    
    else:
        # Используем пользовательское отображение для создания сегментов
        rfm_segmented['Customer_Segment'] = rfm_segmented['RFM_Segment_Code'].map(
            segment_mapping).fillna('Прочие')
    
    return rfm_segmented


def _create_additional_info(rfm: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Создает дополнительную информацию для анализа."""
    # Расчет статистики по сегментам
    segment_stats = rfm.groupby('Customer_Segment').agg({
        'Recency': ['mean', 'median', 'count'],
        'Frequency': ['mean', 'median', 'sum'],
        'Monetary': ['mean', 'median', 'sum']
    })
    
    # Переименовываем столбцы
    segment_stats.columns = [f'{col[0]}_{col[1]}' for col in segment_stats.columns]
    segment_stats = segment_stats.reset_index()
    
    # Расчет распределения по сегментам
    segment_distribution = rfm['Customer_Segment'].value_counts().reset_index()
    segment_distribution.columns = ['Customer_Segment', 'Count']
    segment_distribution['Percentage'] = segment_distribution['Count'] / segment_distribution['Count'].sum() * 100
    
    # Возвращаем словарь с дополнительной информацией
    return {
        'segment_stats': segment_stats,
        'segment_distribution': segment_distribution
    }


def save_rfm_results(rfm: pd.DataFrame, output_path: str) -> None:
    """Сохраняет результаты RFM-анализа в CSV-файл."""
    try:
        rfm.to_csv(output_path, index=False)
        print(f"Результаты успешно сохранены в {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {str(e)}")


def visualize_rfm(rfm: pd.DataFrame, additional_info: Dict[str, pd.DataFrame], 
                 output_dir: Optional[str] = None) -> None:
    """Создает визуализации результатов RFM-анализа."""
    # Создаем базовые настройки для графиков
    plt.figure(figsize=(12, 10))
    plt.style.use('ggplot')
    
    # 1. Распределение клиентов по сегментам
    plt.subplot(2, 2, 1)
    segment_counts = additional_info['segment_distribution']
    # Сортируем по количеству для лучшей визуализации
    segment_counts = segment_counts.sort_values('Count', ascending=False)
    
    # Создаем горизонтальный bar plot
    sns.barplot(x='Count', y='Customer_Segment', data=segment_counts)
    plt.title('Распределение клиентов по сегментам')
    plt.tight_layout()
    
    # 2. Heatmap корреляции между RFM-метриками
    plt.subplot(2, 2, 2)
    corr_matrix = rfm[['Recency', 'Frequency', 'Monetary', 'RFM_Score']].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Корреляция между RFM-метриками')
    
    # 3. Scatter plot: Frequency vs Monetary с цветовой кодировкой по Recency
    plt.subplot(2, 2, 3)
    scatter = plt.scatter(rfm['Frequency'], rfm['Monetary'], 
                         c=rfm['Recency'], cmap='viridis', 
                         alpha=0.6, edgecolors='w', linewidth=0.5)
    plt.colorbar(scatter, label='Recency (дни)')
    plt.xlabel('Frequency (количество транзакций)')
    plt.ylabel('Monetary (сумма)')
    plt.title('Frequency vs Monetary по Recency')
    
    # 4. Boxplot для RFM-метрик по сегментам
    plt.subplot(2, 2, 4)
    
    # Создаем длинный формат данных для boxplot
    segments_to_plot = additional_info['segment_distribution']['Customer_Segment'].head(5).tolist()
    rfm_melt = rfm[rfm['Customer_Segment'].isin(segments_to_plot)].melt(
        id_vars=['Customer_Segment'],
        value_vars=['RFM_Score'],
        var_name='Метрика',
        value_name='Значение'
    )
    
    # Строим boxplot
    sns.boxplot(x='Customer_Segment', y='Значение', hue='Метрика', data=rfm_melt)
    plt.title('Распределение RFM-Score по топ-5 сегментам')
    plt.xticks(rotation=45)
    
    # Общие настройки и сохранение
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(f"{output_dir}/rfm_visualization.png", dpi=300)
        print(f"Визуализация сохранена в {output_dir}/rfm_visualization.png")
    
    plt.show()


# Пример использования
def example_usage():
    """Пример использования улучшенной функции RFM-анализа."""
    # Путь к файлу с данными
    file_path = "user_data.csv"
    
    # Загрузка данных
    try:
        data = pd.read_csv(file_path)
        print(f"Файл {file_path} успешно загружен. Количество строк: {len(data)}")
    except Exception as e:
        print(f"Ошибка при загрузке файла: {str(e)}")
        return
    
    # Переименование столбцов, если необходимо
    if 'TransactionDate' not in data.columns or 'CustomerID' not in data.columns or 'Amount' not in data.columns:
        # Пример переименования
        original_columns = data.columns.tolist()
        
        if len(original_columns) >= 3:
            data.columns = ['TransactionDate', 'CustomerID', 'Amount'] + original_columns[3:]
            print(f"Столбцы переименованы: {original_columns} -> {data.columns.tolist()}")
        else:
            print("Ошибка: в файле недостаточно столбцов для анализа")
            return
    
    # Преобразование даты в формат datetime
    try:
        data['TransactionDate'] = pd.to_datetime(data['TransactionDate'])
    except Exception as e:
        print(f"Ошибка при преобразовании столбца с датами: {str(e)}")
        print("Попробуйте указать формат даты, например: %Y-%m-%d")
        return
    
    # Пример пользовательских интервалов для ранжирования с фиксированными интервалами
    custom_intervals = {
        'R': [30, 90, 180],  # Интервалы для Recency в днях
        'F': [3, 5, 10],     # Интервалы для Frequency в количестве транзакций
        'M': [1000, 5000, 10000]  # Интервалы для Monetary в сумме
    }
    
    # Выполнение RFM-анализа с расширенными параметрами
    try:
        # Базовый вызов с параметрами по умолчанию
        # rfm_result, additional_info = rfm_analysis(
        #     data, 
        #     date_col='TransactionDate', 
        #     customer_col='CustomerID', 
        #     amount_col='Amount'
        # )
        
        # Пример вызова с расширенными параметрами
        rfm_result, additional_info = rfm_analysis(
            data, 
            date_col='TransactionDate', 
            customer_col='CustomerID', 
            amount_col='Amount',
            analysis_date='2025-03-30',  # Указываем конкретную дату для анализа
            n_quantiles=5,               # 5 квантилей вместо 4
            ranking_method='fixed',      # Используем фиксированные интервалы
            custom_intervals=custom_intervals,  # Пользовательские интервалы
            business_days_only=True      # Учитываем только рабочие дни
        )
        
        # Вывод результатов
        print("\nРезультаты RFM-анализа (первые 5 строк):")
        print(rfm_result.head())
        
        # Вывод статистики по сегментам
        print("\nСтатистика по сегментам:")
        print(additional_info['segment_stats'])
        
        # Вывод распределения по сегментам
        print("\nРаспределение клиентов по сегментам:")
        print(additional_info['segment_distribution'])
        
        # Сохранение результатов
        save_rfm_results(rfm_result, "rfm_results.csv")
        
        # Визуализация результатов
        visualize_rfm(rfm_result, additional_info, ".")
        
    except Exception as e:
        print(f"Ошибка при выполнении RFM-анализа: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    example_usage()