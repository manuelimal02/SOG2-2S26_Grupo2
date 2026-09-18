"""
Modulo Empleados y Compras

Crea 60 materiales (productos) que usa cada sucursal de QuetzalMart,


Requisito: al menos 60 materiales, verificables por
consulta a base de datos.

"""

from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

# Categorias de materiales tipicas de un supermercado en expansion
CATEGORIAS_MATERIALES = {
    "Limpieza y Suministros": [
        "Desinfectante multiusos 1L", "Jabon liquido para manos 1L",
        "Bolsas plasticas para basura", "Papel higienico institucional",
        "Papel toalla industrial", "Trapeador industrial",
        "Escoba industrial", "Guantes de limpieza",
        "Detergente en polvo 5kg", "Cloro industrial 1 galon",
    ],
    "Empaque y Embalaje": [
        "Bolsas plasticas para compras", "Cajas de carton reforzado",
        "Cinta adhesiva de embalaje", "Papel film plastico",
        "Etiquetas adhesivas de precio", "Bandejas de unicel",
        "Rollos de papel kraft", "Sellos plasticos para bolsas",
        "Cajas plegables medianas", "Cajas plegables grandes",
    ],
    "Equipo de Bodega": [
        "Estanteria metalica industrial", "Tarimas de plastico",
        "Carretilla de carga", "Bascula digital industrial",
        "Lector de codigo de barras", "Impresora de etiquetas",
        "Refrigerador industrial", "Congelador industrial",
        "Contenedor plastico apilable", "Termometro de refrigeracion",
    ],
    "Suministros de Oficina": [
        "Resma de papel bond", "Cartuchos de tinta impresora",
        "Engrapadora de oficina", "Caja de lapiceros",
        "Folder tamano carta", "Calculadora de escritorio",
        "Rollo de papel para caja registradora", "Sello de recibido",
        "Libreta de notas", "Clip metalico caja",
    ],
    "Uniformes y Seguridad": [
        "Uniforme de cajero", "Uniforme de bodega",
        "Chaleco reflectante", "Guantes de seguridad industrial",
        "Casco de seguridad", "Botas de seguridad",
        "Mascarilla desechable caja", "Gel antibacterial 1L",
        "Extintor portatil", "Botiquin de primeros auxilios",
    ],
    "Insumos de Punto de Venta": [
        "Rollo de bolsas para caja", "Caja registradora portatil",
        "Lector de tarjetas de pago", "Base para exhibidor de caja",
        "Rotulo de precios promocionales", "Cesta de compras plastica",
        "Carrito de compras", "Divisor de banda transportadora",
        "Soporte para bolsas reciclables", "Letrero de sucursal",
    ],
}


def material_existe(models, uid, nombre):
    existentes = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "product.product", "search",
        [[["name", "=", nombre]]]
    )
    return bool(existentes)


def main():
    uid, models = conectar_odoo()

    total_materiales = sum(len(v) for v in CATEGORIAS_MATERIALES.values())
    print(f"\nSe crearan hasta {total_materiales} materiales (agrupados en "
          f"{len(CATEGORIAS_MATERIALES)} categorias)...\n")

    total_creados = 0
    for categoria, materiales in CATEGORIAS_MATERIALES.items():
        print(f"Categoria: {categoria}")
        for nombre in materiales:
            nombre_completo = f"[MAT] {nombre}"

            if material_existe(models, uid, nombre_completo):
                print(f"  Ya existe, se omite: {nombre_completo}")
                continue

            producto_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "product.product", "create",
                [{
                    "name": nombre_completo,
                    "type": "consu",
                    "purchase_ok": True,
                    "sale_ok": False,
                    "categ_id": 1,  # categoria "All" por defecto de Odoo
                }]
            )
            total_creados += 1
            print(f"  Material creado: {nombre_completo} (id={producto_id})")

    print(f"\nListo. {total_creados} materiales nuevos creados en esta corrida.")

    total_en_odoo = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "product.product", "search_count",
        [[["name", "like", "[MAT]"]]]
    )
    print(f"Total de materiales con prefijo [MAT] en Odoo ahora: {total_en_odoo}")


if __name__ == "__main__":
    main()