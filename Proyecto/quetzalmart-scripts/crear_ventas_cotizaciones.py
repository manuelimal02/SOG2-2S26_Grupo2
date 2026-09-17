# 03_crear_ventas_cotizaciones.py
import random
from datetime import datetime, timedelta
from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

uid, models = conectar_odoo()

# --- Obtener clientes existentes ---
clientes_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search',
    [[['customer_rank', '>', 0]]]
)
print(f"Clientes encontrados: {len(clientes_ids)}")

# --- Obtener productos existentes ---
productos_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'product.product', 'search',
    [[]]
)
print(f"Productos encontrados: {len(productos_ids)}")

if not clientes_ids or not productos_ids:
    raise Exception("No hay clientes o productos. Corre primero 01 y 02.")


def fecha_aleatoria():
    """Genera una fecha aleatoria en los últimos 6 meses."""
    dias_atras = random.randint(0, 180)
    fecha = datetime.now() - timedelta(days=dias_atras)
    return fecha.strftime('%Y-%m-%d %H:%M:%S')


def generar_lineas_orden():
    """Genera entre 1 y 4 líneas de producto aleatorias, sin repetir producto en la misma orden."""
    cantidad_lineas = random.randint(1, 4)
    productos_elegidos = random.sample(productos_ids, min(cantidad_lineas, len(productos_ids)))

    lineas = []
    for producto_id in productos_elegidos:
        cantidad = random.randint(1, 10)
        lineas.append((0, 0, {
            'product_id': producto_id,
            'product_uom_qty': cantidad,
        }))
    return lineas


def crear_orden(es_cotizacion=False):
    """Crea una orden de venta. Si es_cotizacion=True, la deja en borrador. Si no, la confirma."""
    cliente_id = random.choice(clientes_ids)
    fecha = fecha_aleatoria()

    orden_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'sale.order', 'create',
        [{
            'partner_id': cliente_id,
            'date_order': fecha,
            'order_line': generar_lineas_orden(),
        }]
    )

    if not es_cotizacion:
        # Confirmar la orden (pasa de "cotización" a "venta")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'action_confirm',
            [[orden_id]]
        )

    return orden_id


# --- Crear 20 cotizaciones (quedan en borrador) ---
print("\n--- Creando cotizaciones ---")
cotizaciones_creadas = []
for i in range(20):
    orden_id = crear_orden(es_cotizacion=True)
    cotizaciones_creadas.append(orden_id)
    print(f"Cotización {i+1}/20 creada (ID: {orden_id})")

# --- Crear 150 ventas (confirmadas) ---
print("\n--- Creando ventas confirmadas ---")
ventas_creadas = []
for i in range(150):
    orden_id = crear_orden(es_cotizacion=False)
    ventas_creadas.append(orden_id)
    print(f"Venta {i+1}/150 creada y confirmada (ID: {orden_id})")

print(f"\nTotal cotizaciones creadas: {len(cotizaciones_creadas)}")
print(f"Total ventas confirmadas creadas: {len(ventas_creadas)}")