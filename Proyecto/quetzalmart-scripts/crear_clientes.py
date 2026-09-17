# 01_crear_clientes.py
from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD

uid, models = conectar_odoo()

clientes = [
    ("María Fernanda López", "maria.lopez@example.com", "5511-2233", "Guatemala"),
    ("Carlos Roberto Méndez", "carlos.mendez@example.com", "5522-3344", "Mixco"),
    ("Ana Lucía Pérez", "ana.perez@example.com", "5533-4455", "Antigua Guatemala"),
    ("José Miguel Ramírez", "jose.ramirez@example.com", "5544-5566", "Villa Nueva"),
    ("Gabriela Sofía Castillo", "gabriela.castillo@example.com", "5555-6677", "Guatemala"),
    ("Luis Fernando García", "luis.garcia@example.com", "5566-7788", "Chimaltenango"),
    ("Daniela Alejandra Morales", "daniela.morales@example.com", "5577-8899", "Escuintla"),
    ("Ricardo Antonio Vásquez", "ricardo.vasquez@example.com", "5588-9900", "Guatemala"),
    ("Paola Andrea Herrera", "paola.herrera@example.com", "5599-0011", "Mixco"),
    ("Sergio Iván Rodríguez", "sergio.rodriguez@example.com", "5600-1122", "Villa Nueva"),
    ("Karen Michelle Ortiz", "karen.ortiz@example.com", "5611-2233", "Guatemala"),
    ("Diego Alejandro Cruz", "diego.cruz@example.com", "5622-3344", "Antigua Guatemala"),
    ("Fernanda Isabel Aguilar", "fernanda.aguilar@example.com", "5633-4455", "Chimaltenango"),
    ("Andrés Felipe Soto", "andres.soto@example.com", "5644-5566", "Escuintla"),
    ("Valeria Nicole Ramos", "valeria.ramos@example.com", "5655-6677", "Guatemala"),
    ("Mario Alberto Juárez", "mario.juarez@example.com", "5666-7788", "Mixco"),
    ("Claudia Patricia Reyes", "claudia.reyes@example.com", "5677-8899", "Villa Nueva"),
    ("Óscar Eduardo Chávez", "oscar.chavez@example.com", "5688-9900", "Guatemala"),
]

ids_creados = []

for nombre, email, telefono, ciudad in clientes:
    partner_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'create',
        [{
            'name': nombre,
            'email': email,
            'phone': telefono,
            'city': ciudad,
            'customer_rank': 1,
        }]
    )
    ids_creados.append(partner_id)
    print(f"Cliente creado: {nombre} (ID: {partner_id})")

print(f"\nTotal de clientes creados: {len(ids_creados)}")