-- Включение необходимых расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создание схемы для пользовательских данных
CREATE SCHEMA IF NOT EXISTS public;

-- Создаем enum типы
CREATE TYPE user_plan_type AS ENUM ('free', 'basic', 'pro');
CREATE TYPE file_status AS ENUM ('processing', 'completed', 'error');
CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'error');

-- Таблица пользователей
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    plan_type user_plan_type NOT NULL DEFAULT 'free',
    analysis_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_login TIMESTAMPTZ,
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Таблица загруженных файлов
CREATE TABLE public.uploaded_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    status file_status DEFAULT 'processing',
    error_message TEXT,
    upload_date TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT file_size_check CHECK (file_size > 0)
);

-- Таблица результатов RFM-анализа
CREATE TABLE public.rfm_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    file_id UUID REFERENCES public.uploaded_files(id) ON DELETE CASCADE,
    params JSONB NOT NULL,
    summary JSONB NOT NULL,
    recommendations JSONB,
    status analysis_status DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT valid_parameters CHECK (jsonb_typeof(params) = 'object'),
    CONSTRAINT valid_summary CHECK (jsonb_typeof(summary) = 'object')
);

-- Таблица истории действий пользователей
CREATE TABLE public.user_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT valid_action CHECK (action IN ('login', 'logout', 'file_upload', 'analysis_start', 'analysis_complete', 'plan_update'))
);

-- Индексы для оптимизации
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_uploaded_files_user_id ON public.uploaded_files(user_id);
CREATE INDEX idx_uploaded_files_status ON public.uploaded_files(status);
CREATE INDEX idx_rfm_analysis_user_id ON public.rfm_analysis(user_id);
CREATE INDEX idx_rfm_analysis_file_id ON public.rfm_analysis(file_id);
CREATE INDEX idx_rfm_analysis_status ON public.rfm_analysis(status);
CREATE INDEX idx_user_activity_log_user_id ON public.user_activity_log(user_id);
CREATE INDEX idx_user_activity_log_created_at ON public.user_activity_log(created_at);

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для обновления updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_uploaded_files_updated_at
    BEFORE UPDATE ON public.uploaded_files
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_rfm_analysis_updated_at
    BEFORE UPDATE ON public.rfm_analysis
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Функция для очистки старых данных бесплатных аккаунтов
CREATE OR REPLACE FUNCTION public.cleanup_free_accounts()
RETURNS void AS $$
BEGIN
    -- Удаление старых файлов
    DELETE FROM public.uploaded_files
    WHERE user_id IN (
        SELECT id FROM public.users WHERE plan_type = 'free'
    )
    AND upload_date < now() - INTERVAL '30 days';
    
    -- Удаление старых анализов
    DELETE FROM public.rfm_analysis
    WHERE user_id IN (
        SELECT id FROM public.users WHERE plan_type = 'free'
    )
    AND created_at < now() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Функция для синхронизации auth.users и public.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, name, password_hash)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'name', NEW.encrypted_password);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Триггер для синхронизации пользователей
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Представление для статистики пользователя
CREATE VIEW public.user_statistics AS
SELECT 
    u.id,
    u.email,
    u.name,
    u.plan_type,
    u.analysis_count,
    COUNT(DISTINCT f.id) as total_files,
    COUNT(DISTINCT r.id) as total_analyses,
    MAX(f.upload_date) as last_file_upload,
    MAX(r.created_at) as last_analysis_date
FROM public.users u
LEFT JOIN public.uploaded_files f ON u.id = f.user_id
LEFT JOIN public.rfm_analysis r ON u.id = r.user_id
GROUP BY u.id, u.email, u.name, u.plan_type, u.analysis_count;

-- Представление для последних анализов
CREATE VIEW public.recent_analyses AS
SELECT 
    r.id,
    r.user_id,
    u.name as user_name,
    f.filename,
    r.status,
    r.created_at,
    r.updated_at,
    r.summary->>'best_segment' as best_segment,
    r.summary->>'worst_segment' as worst_segment,
    (r.summary->>'average_rfm_score')::float as average_rfm_score
FROM public.rfm_analysis r
JOIN public.users u ON r.user_id = u.id
JOIN public.uploaded_files f ON r.file_id = f.id
ORDER BY r.created_at DESC;

-- Политики безопасности (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploaded_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rfm_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_activity_log ENABLE ROW LEVEL SECURITY;

-- Политики для users
CREATE POLICY "Users can view own data"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Политики для uploaded_files
CREATE POLICY "Users can view own files"
    ON public.uploaded_files FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own files"
    ON public.uploaded_files FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own files"
    ON public.uploaded_files FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own files"
    ON public.uploaded_files FOR DELETE
    USING (auth.uid() = user_id);

-- Политики для rfm_analysis
CREATE POLICY "Users can view own analyses"
    ON public.rfm_analysis FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
    ON public.rfm_analysis FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses"
    ON public.rfm_analysis FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own analyses"
    ON public.rfm_analysis FOR DELETE
    USING (auth.uid() = user_id);

-- Политики для user_activity_log
CREATE POLICY "Users can view their own activity logs"
    ON public.user_activity_log FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can insert activity logs"
    ON public.user_activity_log FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Функции для работы с данными
CREATE OR REPLACE FUNCTION get_user_analysis_stats(user_id UUID)
RETURNS TABLE (
    total_analyses BIGINT,
    completed_analyses BIGINT,
    total_files_size BIGINT,
    average_rfm_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_analyses,
        COUNT(*) FILTER (WHERE status = 'completed')::BIGINT as completed_analyses,
        COALESCE(SUM(f.file_size), 0)::BIGINT as total_files_size,
        COALESCE(AVG((summary->>'average_rfm_score')::FLOAT), 0) as average_rfm_score
    FROM public.rfm_analysis r
    LEFT JOIN public.uploaded_files f ON r.file_id = f.id
    WHERE r.user_id = $1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Функция для очистки старых файлов
CREATE OR REPLACE FUNCTION cleanup_old_files(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM public.uploaded_files
        WHERE status = 'completed'
        AND upload_date < NOW() - (days_old || ' days')::INTERVAL
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Создаем функцию для автоматической очистки
CREATE OR REPLACE FUNCTION schedule_cleanup()
RETURNS void AS $$
BEGIN
    PERFORM cleanup_old_files(30);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Создаем расписание для очистки
SELECT cron.schedule('0 0 * * *', $$SELECT schedule_cleanup()$$);

-- Комментарии к таблицам
COMMENT ON TABLE public.users IS 'Таблица пользователей системы';
COMMENT ON TABLE public.uploaded_files IS 'Таблица загруженных файлов';
COMMENT ON TABLE public.rfm_analysis IS 'Таблица результатов RFM-анализа';
COMMENT ON TABLE public.user_activity_log IS 'Таблица логов активности пользователей';

-- Комментарии к колонкам
COMMENT ON COLUMN public.users.email IS 'Email пользователя (уникальный)';
COMMENT ON COLUMN public.users.plan_type IS 'Тип тарифного плана пользователя';
COMMENT ON COLUMN public.uploaded_files.status IS 'Статус обработки файла';
COMMENT ON COLUMN public.rfm_analysis.status IS 'Статус выполнения анализа';
COMMENT ON COLUMN public.rfm_analysis.params IS 'Параметры анализа в формате JSON';
COMMENT ON COLUMN public.rfm_analysis.summary IS 'Общая статистика анализа в формате JSON';
COMMENT ON COLUMN public.rfm_analysis.recommendations IS 'Рекомендации по улучшению в формате JSON';
