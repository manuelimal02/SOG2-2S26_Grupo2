# 03b_completar_ventas.py
import random
from datetime import datetime, timedelta
from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

uid, models = conectar_odoo()

clientes_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search',
    [[['customer_rank', '>', 0]]]
)

productos_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'product.product', 'search',
    [[]]
)

def fecha_aleatoria():
    dias_atras = random.randint(0, 180)
    fecha = datetime.now() - timedelta(days=dias_atras)
    return fecha.strftime('%Y-%m-%d %H:%M:%S')

def generar_lineas_orden():
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

def crear_venta_confirmada():
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
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'sale.order', 'action_confirm',
        [[orden_id]]
    )
    return orden_id

# --- Completar las 66 ventas faltantes (85 a 150) ---
FALTANTES = 66
print(f"--- Creando las {FALTANTES} ventas faltantes ---")
ventas_creadas = []
for i in range(FALTANTES):
    orden_id = crear_venta_confirmada()
    ventas_creadas.append(orden_id)
    print(f"Venta faltante {i+1}/{FALTANTES} creada y confirmada (ID: {orden_id})")

print(f"\nTotal de ventas completadas en esta corrida: {len(ventas_creadas)}")