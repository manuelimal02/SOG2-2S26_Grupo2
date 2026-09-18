-- ============================================================
-- fase2_empleados_compras.sql
-- Persona 2 - Luis - Modulo Empleados y Compras
-- Proyecto Unico SOG2 - QuetzalMart
--
-- Consultas SQL sobre la base de datos INTERNA de Odoo (PostgreSQL).
-- Verifican los requisitos de Empleados y Compras del enunciado.
-- ============================================================


-- ------------------------------------------------------------
-- 1. EMPLEADOS: total cargado (requisito: al menos 35)
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_empleados
FROM hr_employee
WHERE active = true;


-- 1.1 Detalle de empleados con su cargo y departamento
SELECT
    e.id,
    e.name                      AS empleado,
    (SELECT value FROM jsonb_each_text(j.name) LIMIT 1) AS cargo,
    (SELECT value FROM jsonb_each_text(d.name) LIMIT 1) AS departamento,
    e.work_email
FROM hr_employee e
LEFT JOIN hr_job j        ON e.job_id = j.id
LEFT JOIN hr_department d ON e.department_id = d.id
WHERE e.active = true
ORDER BY d.name, j.name, e.name;


-- ------------------------------------------------------------
-- 2. CARGOS: total (requisito: al menos 6)
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_cargos
FROM hr_job;

-- 2.1 Detalle: cuantos empleados tiene cada cargo
SELECT
    (SELECT value FROM jsonb_each_text(j.name) LIMIT 1) AS cargo,
    COUNT(e.id)         AS empleados_en_este_cargo
FROM hr_job j
LEFT JOIN hr_employee e ON e.job_id = j.id AND e.active = true
GROUP BY j.name
ORDER BY empleados_en_este_cargo DESC;


-- ------------------------------------------------------------
-- 3. DEPARTAMENTOS: total (requisito: al menos 5)
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_departamentos
FROM hr_department;

-- 3.1 Detalle: cuantos empleados tiene cada departamento
SELECT
    (SELECT value FROM jsonb_each_text(d.name) LIMIT 1) AS departamento,
    COUNT(e.id)         AS empleados_en_este_departamento
FROM hr_department d
LEFT JOIN hr_employee e ON e.department_id = d.id AND e.active = true
GROUP BY d.name
ORDER BY empleados_en_este_departamento DESC;


-- ------------------------------------------------------------
-- 4. COMPRAS: total confirmadas (requisito: al menos 100)
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_compras_confirmadas
FROM purchase_order
WHERE state = 'purchase';

-- 4.1 Detalle de las compras confirmadas: proveedor, fecha, total
SELECT
    po.id,
    po.name                    AS numero_orden,
    rp.name                    AS proveedor,
    po.date_order               AS fecha_orden,
    po.amount_total              AS total,
    po.invoice_status
FROM purchase_order po
JOIN res_partner rp ON po.partner_id = rp.id
WHERE po.state = 'purchase'
ORDER BY po.date_order DESC;


-- 4.2 Cotizaciones a proveedores (RFQ, sin confirmar)
SELECT COUNT(*) AS total_rfq_cotizaciones_proveedores
FROM purchase_order
WHERE state IN ('draft', 'sent');


-- ------------------------------------------------------------
-- 5. MATERIALES: total cargado (requisito: al menos 60)
--    Se identifican por el prefijo [MAT] en el nombre.
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_materiales
FROM product_template
WHERE name::text ILIKE '%[MAT]%';

-- 5.1 Detalle de los materiales
SELECT
    pt.id,
    (SELECT value FROM jsonb_each_text(pt.name) LIMIT 1) AS material,
    pt.type              AS tipo_producto
FROM product_template pt
WHERE pt.name::text ILIKE '%[MAT]%'
ORDER BY pt.name;


-- ------------------------------------------------------------
-- 6. FACTURAS DE PROVEEDOR: total validadas (comprueba
--    "facturas correspondientes" de las 100 compras)
-- ------------------------------------------------------------
SELECT COUNT(*) AS total_facturas_proveedor_validadas
FROM account_move
WHERE move_type = 'in_invoice'
  AND state = 'posted';

-- 6.1 Detalle de facturas de proveedor con su orden de compra origen
SELECT
    am.id,
    am.name                 AS numero_factura,
    am.invoice_origin       AS orden_compra_origen,
    am.invoice_date,
    am.amount_total,
    am.state
FROM account_move am
WHERE am.move_type = 'in_invoice'
  AND am.state = 'posted'
ORDER BY am.invoice_date DESC;


-- ------------------------------------------------------------
-- 7. RESUMEN GENERAL (una sola consulta con todo, para
--    mostrar rapido el dia de la calificacion)
-- ------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM hr_employee WHERE active = true)              AS empleados,
    (SELECT COUNT(*) FROM hr_job)                                       AS cargos,
    (SELECT COUNT(*) FROM hr_department)                                AS departamentos,
    (SELECT COUNT(*) FROM purchase_order WHERE state = 'purchase')      AS compras_confirmadas,
    (SELECT COUNT(*) FROM purchase_order WHERE state IN ('draft','sent')) AS cotizaciones_rfq,
    (SELECT COUNT(*) FROM product_template WHERE name::text ILIKE '%[MAT]%') AS materiales,
    (SELECT COUNT(*) FROM account_move WHERE move_type = 'in_invoice' AND state = 'posted') AS facturas_proveedor;