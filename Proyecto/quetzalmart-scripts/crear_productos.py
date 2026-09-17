# 02_crear_productos.py
import requests
import base64
from conexion import conectar_odoo
from config import ODOO_DB, ODOO_PASSWORD, PEXELS_API_KEY

uid, models = conectar_odoo()

# Lista de productos: (nombre, término de búsqueda en Pexels, precio_venta, costo)
productos = [
    ("Arroz 1lb", "rice bag", 8.50, 5.00),
    ("Frijol negro 1lb", "black beans", 9.00, 5.50),
    ("Azúcar blanca 2lb", "sugar bag", 10.00, 6.00),
    ("Aceite vegetal 1L", "cooking oil bottle", 22.00, 15.00),
    ("Harina de trigo 2lb", "flour bag", 12.00, 7.50),
    ("Pasta espagueti 500g", "spaghetti pasta", 9.50, 5.50),
    ("Sal de mesa 1lb", "salt", 4.50, 2.50),
    ("Café molido 500g", "ground coffee", 35.00, 22.00),
    ("Agua embotellada 1L", "water bottle", 6.00, 3.00),
    ("Bebida gaseosa de cola 2L", "cola soda bottle", 15.00, 9.00),
    ("Jugo de naranja 1L", "orange juice carton", 14.00, 8.50),
    ("Leche entera 1L", "milk carton", 11.00, 6.50),
    ("Té helado 500ml", "iced tea bottle", 8.00, 4.50),
    ("Bebida energética 250ml", "energy drink can", 12.00, 7.00),
    ("Jabón de barra", "bar soap", 5.50, 3.00),
    ("Detergente en polvo 1kg", "laundry detergent powder", 28.00, 18.00),
    ("Cloro 1L", "bleach bottle", 10.00, 6.00),
    ("Papel higiénico paquete", "toilet paper pack", 32.00, 20.00),
    ("Shampoo 400ml", "shampoo bottle", 45.00, 28.00),
    ("Pasta dental 100ml", "toothpaste tube", 18.00, 10.00),
    ("Pan de molde", "sliced bread loaf", 16.00, 9.50),
    ("Galletas dulces paquete", "cookies package", 13.00, 7.50),
    ("Papas fritas bolsa", "potato chips bag", 14.50, 8.00),
    ("Cereal de maíz caja", "corn cereal box", 27.00, 17.00),
    ("Manzanas 1lb", "apples", 10.00, 6.00),
    ("Bananos 1lb", "bananas", 5.00, 2.50),
    ("Tomates 1lb", "tomatoes", 8.00, 4.50),
    ("Cebollas 1lb", "onions", 6.50, 3.50),
]

def buscar_imagen_pexels(termino_busqueda):
    """Busca en Pexels y devuelve la imagen en base64, o None si falla."""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={termino_busqueda}&per_page=1"

    respuesta = requests.get(url, headers=headers)
    if respuesta.status_code != 200:
        print(f"Error al buscar '{termino_busqueda}': {respuesta.status_code}")
        return None

    datos = respuesta.json()
    if not datos.get("photos"):
        print(f"Sin resultados para '{termino_busqueda}'")
        return None

    imagen_url = datos["photos"][0]["src"]["medium"]
    imagen_respuesta = requests.get(imagen_url)

    if imagen_respuesta.status_code == 200:
        return base64.b64encode(imagen_respuesta.content).decode('utf-8')
    return None


ids_creados = []

for nombre, termino, precio_venta, costo in productos:
    print(f"Procesando: {nombre}...")

    imagen_b64 = buscar_imagen_pexels(termino)

    datos_producto = {
        'name': nombre,
        'list_price': precio_venta,
        'standard_price': costo,
        'sale_ok': True,
        'purchase_ok': True,
        'type': 'consu',  # producto consumible/almacenable
    }

    if imagen_b64:
        datos_producto['image_1920'] = imagen_b64

    producto_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.template', 'create',
        [datos_producto]
    )
    ids_creados.append(producto_id)
    print(f"Creado (ID: {producto_id}) {'con imagen' if imagen_b64 else 'SIN imagen'}")

print(f"\nTotal de productos creados: {len(ids_creados)}")