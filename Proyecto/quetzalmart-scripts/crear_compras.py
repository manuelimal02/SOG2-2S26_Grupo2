"""
Modulo Empleados y Compras

Version idempotente: es seguro correr este script varias veces.
Cada vez que corre:
  1. Ajusta la politica de facturacion de los materiales [MAT] a
     "facturar sobre cantidad pedida" (no requiere recepcion previa).
  2. Factura y postea cualquier orden ya confirmada que quedo sin
     factura (repara corridas anteriores que hayan fallado aqui).
  3. Completa proveedores, compras confirmadas+facturadas y RFQ
     hasta llegar a las metas (10 proveedores, 100 confirmadas, 20 RFQ).

Uso: python crear_compras.py
"""

import random
import xmlrpc.client
from datetime import date
from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

META_COMPRAS_CONFIRMADAS = 100
META_RFQ_SIN_CONFIRMAR = 20

PROVEEDORES = [
    "Distribuidora Central de Guatemala",
    "Suministros Industriales del Norte",
    "Comercializadora San Cristobal",
    "Proveedora Quetzal S.A.",
    "Insumos y Equipos del Pacifico",
    "Distribuidora La Union",
    "Grupo Comercial Atitlan",
    "Suministros Metropolitanos",
    "Comercializadora Xela",
    "Distribuidora Puerto Barrios",
]


def get_or_create_proveedor(models, uid, nombre):
    existentes = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "res.partner", "search", [[["name", "=", nombre]]]
    )
    if existentes:
        return existentes[0]
    pid = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "res.partner", "create",
        [{"name": nombre, "company_type": "company", "supplier_rank": 1}]
    )
    print(f"  Proveedor creado: {nombre} (id={pid})")
    return pid


def get_materiales(models, uid):
    ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "product.product", "search", [[["name", "like", "[MAT]"]]]
    )
    if len(ids) < 5:
        raise RuntimeError("Hay menos de 5 materiales. Corre primero crear_materiales.py")
    return ids


def ajustar_politica_facturacion(models, uid, materiales_ids):
    """
    Cambia purchase_method a 'purchase' (facturar sobre cantidad pedida)
    en los templates de los materiales [MAT], para no depender de una
    recepcion de bodega antes de poder facturar.
    """
    productos = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "product.product", "read", [materiales_ids], {"fields": ["product_tmpl_id"]}
    )
    template_ids = list({p["product_tmpl_id"][0] for p in productos})

    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "product.template", "write",
        [template_ids, {"purchase_method": "purchase"}]
    )
    print(f"Politica de facturacion ajustada en {len(template_ids)} materiales "
          f"(ahora se facturan sobre cantidad pedida, sin requerir recepcion).")


def crear_orden(models, uid, proveedor_id, materiales_ids):
    n_lineas = random.randint(2, 5)
    productos = random.sample(materiales_ids, n_lineas)
    lineas = []
    for prod_id in productos:
        cantidad = random.randint(5, 50)
        precio = round(random.uniform(15, 450), 2)
        lineas.append((0, 0, {
            "product_id": prod_id,
            "product_qty": cantidad,
            "price_unit": precio,
        }))
    orden_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "purchase.order", "create",
        [{"partner_id": proveedor_id, "order_line": lineas}]
    )
    return orden_id


def facturar_y_postear(models, uid, orden_id):
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "action_create_invoice", [[orden_id]])
    except xmlrpc.client.Fault as e:
        if "allow_none" not in str(e):
            raise
    orden = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "purchase.order", "read", [[orden_id]], {"fields": ["invoice_ids"]}
    )[0]
    factura_ids = orden["invoice_ids"]
    if factura_ids:
        # La factura necesita fecha de factura asignada antes de poder postearse
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move", "write",
            [factura_ids, {"invoice_date": date.today().isoformat()}]
        )
        try:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "account.move", "action_post", [factura_ids])
        except xmlrpc.client.Fault as e:
            if "allow_none" not in str(e):
                raise
    return factura_ids


def reparar_facturas_en_borrador(models, uid):
    """
    Busca facturas de proveedor (account.move, move_type=in_invoice) que
    hayan quedado en estado borrador de corridas anteriores (por ejemplo,
    antes de que se corrigiera lo de la fecha de factura) y las postea.
    """
    draft_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "account.move", "search",
        [[["move_type", "=", "in_invoice"], ["state", "=", "draft"]]]
    )
    if not draft_ids:
        return

    print(f"\nReparando {len(draft_ids)} facturas de proveedor que quedaron en borrador...")
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "account.move", "write",
        [draft_ids, {"invoice_date": date.today().isoformat()}]
    )
    reparadas = 0
    for fid in draft_ids:
        try:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "account.move", "action_post", [[fid]])
            reparadas += 1
        except xmlrpc.client.Fault as e:
            if "allow_none" not in str(e):
                print(f"  Factura id={fid}: no se pudo postear -> {e}")
            else:
                reparadas += 1
    print(f"  {reparadas}/{len(draft_ids)} facturas reparadas y posteadas.")


def main():
    uid, models = conectar_odoo()

    print("\nCreando/verificando proveedores...")
    proveedor_ids = [get_or_create_proveedor(models, uid, nombre) for nombre in PROVEEDORES]

    materiales_ids = get_materiales(models, uid)
    print(f"{len(materiales_ids)} materiales disponibles.")

    ajustar_politica_facturacion(models, uid, materiales_ids)
    reparar_facturas_en_borrador(models, uid)

    # --- Paso 1: limpiar ordenes viejas que quedaron "congeladas" sin poder
    # facturarse (creadas ANTES de corregir la politica de facturacion).
    # Se cancelan y se eliminan; el Paso 2 las vuelve a crear desde cero,
    # ya con la politica correcta desde el momento de creacion.
    atascadas_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "purchase.order", "search",
        [[["state", "=", "purchase"], ["invoice_status", "!=", "invoiced"]]]
    )
    if atascadas_ids:
        print(f"\nLimpiando {len(atascadas_ids)} compras viejas que quedaron "
              f"sin poder facturarse (se recrean desde cero)...")

        # button_cancel a veces responde None, lo cual el XML-RPC de Odoo 18
        # no puede serializar y lanza un Fault aunque la cancelacion SI se
        # haya aplicado en el servidor. Por eso se llama uno por uno,
        # ignorando ese error especifico, y luego se verifica el estado real.
        for oid in atascadas_ids:
            try:
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "button_cancel", [[oid]])
            except xmlrpc.client.Fault as e:
                if "allow_none" not in str(e):
                    print(f"  Orden id={oid}: error real al cancelar -> {e}")

        canceladas_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "purchase.order", "search",
            [[["id", "in", atascadas_ids], ["state", "=", "cancel"]]]
        )
        print(f"  {len(canceladas_ids)}/{len(atascadas_ids)} ordenes quedaron canceladas. Eliminando...")

        for oid in canceladas_ids:
            try:
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "unlink", [[oid]])
            except xmlrpc.client.Fault as e:
                if "allow_none" not in str(e):
                    print(f"  Orden id={oid}: error real al eliminar -> {e}")

        restantes = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "purchase.order", "search_count",
            [[["id", "in", canceladas_ids]]]
        )
        print(f"  {len(canceladas_ids) - restantes}/{len(canceladas_ids)} ordenes eliminadas correctamente.")

    # --- Paso 2: completar compras confirmadas+facturadas hasta la meta ---
    n_confirmadas_ok = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "search_count",
        [[["state", "=", "purchase"], ["invoice_status", "=", "invoiced"]]]
    )
    faltantes = META_COMPRAS_CONFIRMADAS - n_confirmadas_ok
    if faltantes > 0:
        print(f"\nYa hay {n_confirmadas_ok} compras confirmadas y facturadas. "
              f"Creando {faltantes} mas para llegar a {META_COMPRAS_CONFIRMADAS}...")
        for i in range(1, faltantes + 1):
            proveedor_id = random.choice(proveedor_ids)
            orden_id = crear_orden(models, uid, proveedor_id, materiales_ids)
            try:
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "button_confirm", [[orden_id]])
            except xmlrpc.client.Fault as e:
                if "allow_none" not in str(e):
                    print(f"  Compra nueva (id={orden_id}): fallo al confirmar -> {e}")
                    continue
            try:
                facturar_y_postear(models, uid, orden_id)
                if i % 10 == 0:
                    print(f"  {i}/{faltantes} nuevas compras confirmadas y facturadas...")
            except Exception as e:
                print(f"  Compra nueva (id={orden_id}): fallo -> {e}")
    else:
        print(f"\nYa hay {n_confirmadas_ok} compras confirmadas y facturadas (meta {META_COMPRAS_CONFIRMADAS} cumplida).")

    # --- Paso 3: completar RFQ sin confirmar hasta la meta ---
    n_rfq = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "search_count",
        [[["state", "in", ["draft", "sent"]]]]
    )
    faltantes_rfq = META_RFQ_SIN_CONFIRMAR - n_rfq
    if faltantes_rfq > 0:
        print(f"\nYa hay {n_rfq} RFQ sin confirmar. Creando {faltantes_rfq} mas "
              f"para llegar a {META_RFQ_SIN_CONFIRMAR}...")
        for _ in range(faltantes_rfq):
            proveedor_id = random.choice(proveedor_ids)
            crear_orden(models, uid, proveedor_id, materiales_ids)
    else:
        print(f"\nYa hay {n_rfq} RFQ sin confirmar (meta {META_RFQ_SIN_CONFIRMAR} cumplida).")

    # --- Resumen final ---
    total_confirmadas = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "search_count",
        [[["state", "=", "purchase"], ["invoice_status", "=", "invoiced"]]]
    )
    total_rfq = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "purchase.order", "search_count",
        [[["state", "in", ["draft", "sent"]]]]
    )
    total_facturas_proveedor = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "account.move", "search_count",
        [[["move_type", "=", "in_invoice"], ["state", "=", "posted"]]]
    )
    print("\n--- Resumen final ---")
    print(f"Compras confirmadas y facturadas: {total_confirmadas} / {META_COMPRAS_CONFIRMADAS}")
    print(f"RFQ sin confirmar:                 {total_rfq} / {META_RFQ_SIN_CONFIRMAR}")
    print(f"Facturas de proveedor validadas:   {total_facturas_proveedor}")


if __name__ == "__main__":
    main()