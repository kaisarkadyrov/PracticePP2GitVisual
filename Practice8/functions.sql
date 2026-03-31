DROP FUNCTION IF EXISTS get_contacts_by_pattern(text);
DROP FUNCTION IF EXISTS get_contacts_paginated(integer, integer);
DROP PROCEDURE IF EXISTS upsert_contact(text, text);
DROP PROCEDURE IF EXISTS bulk_upsert_contacts(text[], text[]);
DROP PROCEDURE IF EXISTS delete_contact(text);

-- Таблица
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL
);

-- Функции
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p text)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT c.name, c.phone FROM contacts c
                 WHERE c.name ILIKE '%' || p || '%'
                    OR c.phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit integer, p_offset integer) # offset сколько записей пропустить
RETURNS TABLE(id integer, name varchar, phone varchar)
AS $$
BEGIN   
    RETURN QUERY
    SELECT * FROM contacts
    ORDER BY id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
