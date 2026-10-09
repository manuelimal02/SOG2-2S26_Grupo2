-- 1. Conteos
SELECT
    (SELECT count(*) FROM res_partner)     AS total_contactos,
    (SELECT count(*) FROM product_template) AS total_productos;

-- 2. Clientes cargados por el bot 
SELECT p.id, p.name,
        CASE WHEN p.is_company THEN 'company' ELSE 'person' END AS company_type,
        p.email, p.phone, p.street, p.street2, p.city, s.name AS state, p.zip,
        COALESCE(c.name->>'es_GT', c.name->>'en_US') AS country,
        p.vat AS tax_id, p.website, p.ref AS reference, p.create_date
FROM res_partner p
LEFT JOIN res_country_state s ON s.id = p.state_id
LEFT JOIN res_country c ON c.id = p.country_id
ORDER BY p.id DESC
LIMIT 20;

-- 3. Productos cargados por el bot
SELECT t.id, COALESCE(t.name->>'es_GT', t.name->>'en_US') AS name, t.type,
        t.default_code AS internal_reference, pp.barcode,
        t.list_price AS sales_price, t.weight, t.create_date
FROM product_template t
LEFT JOIN product_product pp ON pp.product_tmpl_id = t.id
ORDER BY t.id DESC
LIMIT 20;

-- 4. Clientes con sus empresas relacionadas y etiquetas
SELECT p.id, p.name,
        CASE WHEN p.is_company THEN 'company' ELSE 'person' END AS company_type,
        par.name AS related_company,
        p.email, p.phone, p.street, p.street2, p.city, s.name AS state, p.zip,
        COALESCE(c.name->>'es_GT', c.name->>'en_US') AS country,
        p.vat AS tax_id, p.website,
        (SELECT string_agg(COALESCE(cat.name->>'es_GT', cat.name->>'en_US'), ', ')
            FROM res_partner_res_partner_category_rel r
            JOIN res_partner_category cat ON cat.id = r.category_id
            WHERE r.partner_id = p.id) AS tags,
        p.ref AS reference, p.comment AS notes, p.create_date
    FROM res_partner p
LEFT JOIN res_partner par ON par.id = p.parent_id
LEFT JOIN res_country_state s ON s.id = p.state_id
LEFT JOIN res_country c ON c.id = p.country_id
ORDER BY p.id DESC
LIMIT 20;

-- 5. Productos con sus descripciones, costos y cantidades a la mano
SELECT t.id,
        (SELECT d.module || '.' || d.name FROM ir_model_data d
            WHERE d.model = 'product.template' AND d.res_id = t.id LIMIT 1) AS external_id,
        COALESCE(t.name->>'es_GT', t.name->>'en_US') AS name,
        t.type AS product_type,
        t.default_code AS internal_reference,
        pp.barcode,
        t.list_price AS sales_price,
        pp.standard_price->>'1' AS cost,
        t.weight,
        COALESCE(t.description_sale->>'es_GT', t.description_sale->>'en_US') AS sales_description,
        (SELECT COALESCE(SUM(q.quantity), 0) FROM stock_quant q
            JOIN stock_location l ON l.id = q.location_id AND l.usage = 'internal'
            JOIN product_product p2 ON p2.id = q.product_id
            WHERE p2.product_tmpl_id = t.id) AS cantidad_a_la_mano,
        t.is_published AS esta_publicado,
        t.create_date
FROM product_template t
LEFT JOIN product_product pp ON pp.product_tmpl_id = t.id
ORDER BY t.id DESC
LIMIT 20;