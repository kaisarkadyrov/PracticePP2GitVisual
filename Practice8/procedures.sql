-- Процедура "вставка или обновление одного контакта"
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;

-- Процедура массовой вставки с проверкой корректности телефона
CREATE OR REPLACE PROCEDURE bulk_upsert_contacts(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE
    i INT := 1;
    invalid_data TEXT := '';
BEGIN
    IF array_length(p_names,1) <> array_length(p_phones,1) THEN
        RAISE EXCEPTION 'Names and phones arrays must have the same length';
    END IF;

    FOREACH i IN ARRAY generate_series(1,array_length(p_names,1)) LOOP
        IF p_phones[i] ~ '^\d{5,15}$' THEN  -- проверка телефона: только цифры, 5-15 символов
            CALL upsert_contact(p_names[i], p_phones[i]);
        ELSE
            invalid_data := invalid_data || p_names[i] || ':' || p_phones[i] || '; ';
        END IF;
    END LOOP;

    IF invalid_data <> '' THEN
        RAISE NOTICE 'Invalid contacts: %', invalid_data;
    END IF;
END;
$$;

-- Процедура удаления контакта по имени или телефону
CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts WHERE name = p_value OR phone = p_value;
END;
$$;