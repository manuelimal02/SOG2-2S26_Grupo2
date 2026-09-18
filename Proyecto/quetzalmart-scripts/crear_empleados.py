"""
Modulo Empleados y Compras

Carga 35 empleados en Odoo, distribuidos entre los 5 departamentos
y 6 cargos creados previamente con crear_departamentos_cargos.py.

Requisito : al menos 35 empleados, 6 cargos y
5 departamentos, verificables por consulta a base de datos.
"""

from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

# Distribucion de los 35 empleados por cargo (debe sumar 35)
# Cada cargo ya esta asociado a un departamento en Odoo (paso anterior)
DISTRIBUCION_POR_CARGO = {
    "Cajero": 8,
    "Auxiliar de Ventas": 7,
    "Bodeguero": 6,
    "Encargado de Compras": 5,
    "Auxiliar de Recursos Humanos": 5,
    "Gerente General": 4,
}

# 35 nombres completos de ejemplo para los empleados
NOMBRES = [
    "Maria Fernanda Lopez Garcia", "Carlos Alberto Perez Ramirez",
    "Ana Lucia Gonzalez Morales", "Jose Manuel Hernandez Cruz",
    "Luisa Fernanda Castillo Ruiz", "Diego Alejandro Ramos Vasquez",
    "Andrea Sofia Martinez Lopez", "Juan Pablo Gomez Estrada",
    "Karla Vanessa Rodriguez Diaz", "Erick Rene Chavez Morales",
    "Paola Ximena Solis Aguilar", "Mario Roberto Gutierrez Leon",
    "Daniela Alejandra Ortiz Reyes", "Kevin Estuardo Monzon Paz",
    "Silvia Patricia Herrera Cano", "Oscar Rolando Barrios Xitumul",
    "Gabriela Isabel Salazar Pineda", "Victor Hugo Marroquin Sical",
    "Claudia Marisol Tzul Ajanel", "Fernando Jose Calderon Recinos",
    "Wendy Roxana Ixcot Batz", "Hector Danilo Villatoro Mendez",
    "Lorena Beatriz Contreras Sandoval", "Marvin Estuardo Coj Tuy",
    "Ingrid Yesenia Pop Choc", "Byron Alexander Quiej Us",
    "Cristina Elizabeth Falla Escobar", "Edgar Rolando Sic Sunun",
    "Nancy Carolina Ajucum Chub", "Manuel de Jesus Rax Cumez",
    "Alejandra Patricia Xoc Sacbaja", "Rudy Armando Tot Caal",
    "Yesenia Guadalupe Chan Tavico", "Selvin Josue Say Cal",
    "Brenda Lissette Morataya Aguirre",
]


def get_ids(models, uid, nombre_cargo):
    """Devuelve (job_id, department_id) para un cargo dado."""
    job = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.job", "search_read",
        [[["name", "=", nombre_cargo]]],
        {"fields": ["id", "department_id"], "limit": 1}
    )
    if not job:
        raise RuntimeError(f"No se encontro el cargo '{nombre_cargo}'. "
                            f"Corre primero crear_departamentos_cargos.py")
    job_id = job[0]["id"]
    department_id = job[0]["department_id"][0]
    return job_id, department_id


def empleado_existe(models, uid, nombre):
    existentes = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.employee", "search",
        [[["name", "=", nombre]]]
    )
    return bool(existentes)


def main():
    uid, models = conectar_odoo()

    if sum(DISTRIBUCION_POR_CARGO.values()) != len(NOMBRES):
        raise RuntimeError("La distribucion por cargo no suma 35. Revisa las listas.")

    print("\nCargando empleados...")
    idx_nombre = 0
    total_creados = 0

    for cargo, cantidad in DISTRIBUCION_POR_CARGO.items():
        job_id, department_id = get_ids(models, uid, cargo)

        for _ in range(cantidad):
            nombre = NOMBRES[idx_nombre]
            idx_nombre += 1

            if empleado_existe(models, uid, nombre):
                print(f"  Ya existe, se omite: {nombre}")
                continue

            correo = nombre.lower().replace(" ", ".") + "@quetzalmart.com"

            emp_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "hr.employee", "create",
                [{
                    "name": nombre,
                    "job_id": job_id,
                    "department_id": department_id,
                    "work_email": correo,
                }]
            )
            total_creados += 1
            print(f"  Empleado creado: {nombre} - {cargo} (id={emp_id})")

    print(f"\nListo. {total_creados} empleados nuevos creados en esta corrida.")

    total_en_odoo = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "hr.employee", "search_count", [[]])
    print(f"Total de empleados existentes en Odoo ahora: {total_en_odoo}")


if __name__ == "__main__":
    main()