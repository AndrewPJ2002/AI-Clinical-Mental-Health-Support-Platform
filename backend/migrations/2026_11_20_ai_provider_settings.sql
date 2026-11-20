-- Apply after deploying the AI settings feature. Keep the encryption key in the backend secret store.
CREATE TABLE IF NOT EXISTS ai_provider_settings (
    id BIGINT PRIMARY KEY CHECK (id = 1),
    provider VARCHAR(50) NOT NULL DEFAULT 'openai' CHECK (provider = 'openai'),
    model VARCHAR(150) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    encrypted_api_key TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
