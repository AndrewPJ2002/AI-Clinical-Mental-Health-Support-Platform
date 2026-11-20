-- Apply once to add configurable OpenAI moderation category handling.
CREATE TABLE IF NOT EXISTS moderation_category_settings (
    id BIGSERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(150) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium'
        CHECK (severity IN ('low', 'medium', 'high')),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO moderation_category_settings (category, label, severity, is_enabled) VALUES
    ('harassment', 'Harassment', 'medium', TRUE),
    ('harassment_threatening', 'Threatening harassment', 'high', FALSE),
    ('hate', 'Hate', 'medium', FALSE),
    ('hate_threatening', 'Threatening hate', 'high', FALSE),
    ('illicit', 'Illicit content', 'medium', FALSE),
    ('illicit_violent', 'Violent illicit content', 'medium', TRUE),
    ('self_harm', 'Self-harm', 'high', TRUE),
    ('self_harm_intent', 'Self-harm intent', 'high', TRUE),
    ('self_harm_instructions', 'Self-harm instructions', 'high', TRUE),
    ('sexual', 'Sexual content', 'medium', FALSE),
    ('sexual_minors', 'Sexual content involving minors', 'high', FALSE),
    ('violence', 'Violence', 'medium', TRUE),
    ('violence_graphic', 'Graphic violence', 'high', FALSE)
ON CONFLICT (category) DO NOTHING;
