// Простая версия дашборда
const RFMDashboard = () => {
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const [activeTab, setActiveTab] = React.useState('overview');
    
    // Эффект для имитации загрузки данных
    React.useEffect(() => {
      // Симулируем загрузку
      setTimeout(() => {
        setLoading(false);
      }, 2000);
      
      // Попытка загрузить данные с сервера
      fetch('/api/rfm-data')
        .then(response => {
          if (!response.ok) {
            throw new Error('Не удалось загрузить данные');
          }
          return response.json();
        })
        .then(data => {
          console.log('Данные успешно загружены:', data);
        })
        .catch(err => {
          console.error('Ошибка загрузки данных:', err);
          setError('Не удалось загрузить данные: ' + err.message);
        });
    }, []);
    
    // Интерфейс загрузки
    if (loading) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mb-4"></div>
            <p className="text-gray-600">Загрузка данных...</p>
          </div>
        </div>
      );
    }
    
    // Интерфейс ошибки
    if (error) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
          <div className="bg-white rounded-lg shadow p-6 max-w-md">
            <h2 className="text-red-500 text-lg font-bold mb-2">Ошибка</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Попробовать снова
            </button>
          </div>
        </div>
      );
    }
    
    // Основной интерфейс
    return (
      <div className="bg-gray-50 min-h-screen">
        {/* Верхняя панель */}
        <div className="bg-white shadow">
          <div className="container mx-auto px-4 py-3 flex justify-between items-center">
            <h1 className="text-xl font-bold">RFM Pro - Личный кабинет</h1>
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-full hover:bg-gray-100">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38"/>
                </svg>
              </button>
              <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
                <span className="ml-2">Пользователь</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Вкладки */}
        <div className="container mx-auto px-4 py-6">
          <div className="mb-6 bg-white rounded-lg shadow p-1 flex">
            {['overview', 'segments', 'customers', 'reports'].map(tab => (
              <button 
                key={tab}
                className={`py-2 px-4 rounded ${activeTab === tab ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab === 'overview' ? 'Обзор' : 
                 tab === 'segments' ? 'Сегменты' : 
                 tab === 'customers' ? 'Клиенты' : 'Отчеты'}
              </button>
            ))}
          </div>
          
          {/* Карточка с уведомлением */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-blue-600 mb-2">Дашборд успешно загружен!</h2>
            <p className="mb-4">
              Базовая версия дашборда работает корректно. Для полной функциональности необходимо
              имплементировать все компоненты и подключить реальные данные.
            </p>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-bold mb-2">Рекомендации:</h3>
              <ul className="list-disc pl-5">
                <li>Проверьте API-запросы к серверу для получения данных</li>
                <li>Используйте упрощенные компоненты вместо сложных библиотек</li>
                <li>Постепенно добавляйте функциональность, тестируя каждый шаг</li>
              </ul>
            </div>
          </div>
          
          {/* Пример простой карточки с метриками */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {['Всего клиентов', 'Средний чек', 'Общая выручка', 'Средняя частота'].map((title, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-4">
                <div className="text-gray-500 text-sm mb-2">{title}</div>
                <div className="text-2xl font-bold">
                  {index === 0 ? '24' : 
                   index === 1 ? '₽2,851' : 
                   index === 2 ? '₽68,420' : '2.3'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };