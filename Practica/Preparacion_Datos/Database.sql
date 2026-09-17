CREATE TABLE IF NOT EXISTS ventas (
    id_cliente      INTEGER PRIMARY KEY,
    edad            INTEGER NOT NULL,
    genero          SMALLINT NOT NULL,          -- 1: Femenino, 0: Masculino
    venta_total     NUMERIC(10, 2) NOT NULL,
    n_compras       INTEGER NOT NULL,
    fecha_compra    DATE NOT NULL,
    monto_compra    NUMERIC(10, 3) NOT NULL,
    metodo_pago     SMALLINT NOT NULL,           -- 0: Efectivo, 1: Tarjeta de Crédito, 2: Tarjeta de Débito
    tiempo          INTEGER NOT NULL,
    navegador       SMALLINT NOT NULL,           -- 0: Tienda Física, 1-4: Navegador 1 a 4
    boletin         SMALLINT NOT NULL,           -- 1: Sí, 0: No
    vale            SMALLINT NOT NULL,           -- 1: Sí, 0: No

    CONSTRAINT chk_genero CHECK (genero IN (0, 1)),
    CONSTRAINT chk_metodo_pago CHECK (metodo_pago IN (0, 1, 2)),
    CONSTRAINT chk_navegador CHECK (navegador IN (0, 1, 2, 3, 4)),
    CONSTRAINT chk_boletin CHECK (boletin IN (0, 1)),
    CONSTRAINT chk_vale CHECK (vale IN (0, 1))
);