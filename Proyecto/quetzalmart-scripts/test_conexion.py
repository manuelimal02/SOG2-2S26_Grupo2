"""
test_conexion.py
Persona 2 - Luis - Modulo Empleados y Compras

Prueba la conexion a Odoo (usando el conexion.py real del equipo,
funcion conectar_odoo()) y verifica permisos sobre los modelos
que se van a usar: hr.employee, hr.department, hr.job,
purchase.order y product.product.

Uso: python test_conexion.py
"""

from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD


def main():
    uid, models = conectar_odoo()

    modelos_a_probar = [
        "hr.employee",
        "hr.department",
        "hr.job",
        "purchase.order",
        "product.product",
    ]

    print("\n--- Permisos ---")
    for modelo in modelos_a_probar:
        puede_leer = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            modelo, "check_access_rights",
            ["read"], {"raise_exception": False}
        )
        puede_crear = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            modelo, "check_access_rights",
            ["create"], {"raise_exception": False}
        )
        print(f"{modelo:20s} lectura={puede_leer}  creacion={puede_crear}")

    print("\n--- Estado actual en Odoo ---")
    for modelo in modelos_a_probar:
        total = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, modelo, "search_count", [[]])
        print(f"{modelo:20s} registros existentes: {total}")


if __name__ == "__main__":
    main()