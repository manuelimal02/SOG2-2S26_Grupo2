"""
Modulo Empleados y Compras

Crea los 5 departamentos y 6 cargos (puestos de trabajo) que pide
el enunciado, antes de cargar los 35 empleados.


"""

from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

# 5 departamentos de trabajo para QuetzalMart
DEPARTAMENTOS = [
    "Ventas",
    "Compras y Logistica",
    "Recursos Humanos",
    "Bodega y Almacen",
    "Administracion y Finanzas",
]

# 6 cargos, cada uno asociado a un departamento (por nombre, arriba)
CARGOS = [
    {"name": "Gerente General",            "departamento": "Administracion y Finanzas"},
    {"name": "Cajero",                     "departamento": "Ventas"},
    {"name": "Auxiliar de Ventas",         "departamento": "Ventas"},
    {"name": "Encargado de Compras",       "departamento": "Compras y Logistica"},
    {"name": "Bodeguero",                  "departamento": "Bodega y Almacen"},
    {"name": "Auxiliar de Recursos Humanos", "departamento": "Recursos Humanos"},
]


def get_or_create_departamento(models, uid, nombre):
    """Busca el departamento por nombre; si no existe, lo crea. Devuelve su ID."""
    existentes = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.department", "search",
        [[["name", "=", nombre]]]
    )
    if existentes:
        return existentes[0]

    nuevo_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.department", "create",
        [{"name": nombre}]
    )
    print(f"  Departamento creado: {nombre} (id={nuevo_id})")
    return nuevo_id


def get_or_create_cargo(models, uid, nombre, departamento_id):
    """Busca el cargo por nombre; si no existe, lo crea asociado al departamento."""
    existentes = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.job", "search",
        [[["name", "=", nombre]]]
    )
    if existentes:
        return existentes[0]

    nuevo_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.job", "create",
        [{"name": nombre, "department_id": departamento_id}]
    )
    print(f"  Cargo creado: {nombre} (id={nuevo_id})")
    return nuevo_id


def main():
    uid, models = conectar_odoo()

    print("\nCreando departamentos...")
    dept_ids = {}
    for nombre in DEPARTAMENTOS:
        dept_ids[nombre] = get_or_create_departamento(models, uid, nombre)

    print("\nCreando cargos...")
    cargo_ids = {}
    for cargo in CARGOS:
        dep_id = dept_ids[cargo["departamento"]]
        cargo_ids[cargo["name"]] = get_or_create_cargo(models, uid, cargo["name"], dep_id)

    print(f"\nListo. {len(dept_ids)} departamentos y {len(cargo_ids)} cargos disponibles.")
    print("Departamentos:", list(dept_ids.keys()))
    print("Cargos:", list(cargo_ids.keys()))


if __name__ == "__main__":
    main()