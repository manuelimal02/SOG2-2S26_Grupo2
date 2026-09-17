# 04_crear_facturas.py
import os
import re
import requests
from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD, ODOO_URL, ODOO_EMAIL

uid, models = conectar_odoo()

CARPETA_FACTURAS = "facturas_pdf"
os.makedirs(CARPETA_FACTURAS, exist_ok=True)

# --- Login HTTP con manejo de CSRF ---
sesion = requests.Session()
pagina_login = sesion.get(f"{ODOO_URL}/web/login")
match = re.search(r'name="csrf_token" value="([^"]+)"', pagina_login.text)

if not match:
    raise Exception("No se pudo encontrar el token CSRF en la página de login")

csrf_token = match.group(1)

sesion.post(f"{ODOO_URL}/web/login", data={
    'login': ODOO_EMAIL,
    'password': ODOO_PASSWORD,
    'csrf_token': csrf_token,
})

verificacion = sesion.get(f"{ODOO_URL}/web")
if 'login' in verificacion.url:
    raise Exception("⚠️ El login HTTP falló, revisa usuario/password en config.py")
print("✅ Login HTTP exitoso, sesión autenticada correctamente")


def descargar_pdf_factura(factura_id, nombre_archivo):
    url = f"{ODOO_URL}/report/pdf/account.report_invoice_with_payments/{factura_id}"
    respuesta = sesion.get(url, timeout=30)
    if respuesta.status_code == 200 and respuesta.headers.get('Content-Type') == 'application/pdf':
        with open(nombre_archivo, 'wb') as f:
            f.write(respuesta.content)
        return True
    return False


ventas_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'sale.order', 'search',
    [[['state', '=', 'sale']]],
    {'limit': 100}
)
print(f"Ventas confirmadas encontradas: {len(ventas_ids)}")

META_FACTURAS = 50
facturas_creadas = []

for venta_id in ventas_ids:
    if len(facturas_creadas) >= META_FACTURAS:
        break

    orden = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'sale.order', 'read',
        [[venta_id]],
        {'fields': ['name', 'partner_id', 'date_order', 'order_line', 'invoice_ids']}
    )[0]

    if orden['invoice_ids']:
        print(f"⏭️  Venta {orden['name']} ya tiene factura (ID {orden['invoice_ids'][0]}), se salta.")
        continue

    partner_id = orden['partner_id'][0]
    fecha_factura = orden['date_order'][:10]

    lineas_orden = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'sale.order.line', 'read',
        [orden['order_line']],
        {'fields': ['product_id', 'product_uom_qty', 'price_unit']}
    )

    lineas_factura = []
    for linea in lineas_orden:
        lineas_factura.append((0, 0, {
            'product_id': linea['product_id'][0],
            'quantity': linea['product_uom_qty'],
            'price_unit': linea['price_unit'],
        }))

    factura_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'account.move', 'create',
        [{
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_date': fecha_factura,
            'invoice_origin': orden['name'],
            'invoice_line_ids': lineas_factura,
        }]
    )

    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'account.move', 'action_post',
        [[factura_id]]
    )

    facturas_creadas.append(factura_id)
    print(f"[{len(facturas_creadas)}/{META_FACTURAS}] Factura creada y validada (ID: {factura_id}) a partir de venta {orden['name']}")

    nombre_archivo = f"{CARPETA_FACTURAS}/factura_{factura_id}.pdf"
    if descargar_pdf_factura(factura_id, nombre_archivo):
        print(f"    → PDF guardado: {nombre_archivo}")
    else:
        print(f"No se pudo descargar el PDF de la factura {factura_id}")

print(f"\nTotal de facturas nuevas creadas, validadas y exportadas: {len(facturas_creadas)}")