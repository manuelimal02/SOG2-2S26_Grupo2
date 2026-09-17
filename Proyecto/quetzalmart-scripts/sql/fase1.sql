-- Consulta 1 - Ver todas las ventas confirmadas (con cliente y total)
SELECT 
    so.id,
    so.name AS numero_orden,
    rp.name AS cliente,
    so.date_order AS fecha,
    so.amount_total AS total,
    so.state AS estado
FROM sale_order so
JOIN res_partner rp ON so.partner_id = rp.id
WHERE so.state = 'sale'
ORDER BY so.date_order DESC;

-- Consulta 2 - Ver todas las cotizaciones (borrador)

SELECT 
    so.id,
    so.name AS numero_orden,
    rp.name AS cliente,
    so.date_order AS fecha,
    so.amount_total AS total,
    so.state AS estado
FROM sale_order so
JOIN res_partner rp ON so.partner_id = rp.id
WHERE so.state = 'draft'
ORDER BY so.date_order DESC;

-- Consulta 3 - Conteo total

SELECT 
    state,
    COUNT(*) AS cantidad
FROM sale_order
GROUP BY state;

-- Consulta 4 - Verificar facturas

SELECT 
    am.id,
    am.name AS numero_factura,
    rp.name AS cliente,
    am.invoice_date AS fecha,
    am.amount_total AS total,
    am.state AS estado
FROM account_move am
JOIN res_partner rp ON am.partner_id = rp.id
WHERE am.move_type = 'out_invoice'
ORDER BY am.invoice_date DESC;

-- Conteo de facturas

SELECT COUNT(*) AS total_facturas
FROM account_move
WHERE move_type = 'out_invoice' AND state = 'posted';