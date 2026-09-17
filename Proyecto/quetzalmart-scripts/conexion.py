# conexion.py
import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_EMAIL, ODOO_PASSWORD

def conectar_odoo():
    """
    Se conecta a Odoo vía XML-RPC y devuelve:
    - uid: el ID del usuario autenticado
    - models: el objeto para hacer llamadas a los modelos de Odoo
    """
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_EMAIL, ODOO_PASSWORD, {})

    if not uid:
        raise Exception("No se pudo autenticar. Revisa tus credenciales en config.py")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    print(f"Conectado a Odoo correctamente. UID: {uid}")
    return uid, models