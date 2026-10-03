import time

from conexion import conectar_odoo
from config import (
    ODOO_DB,
    ODOO_PASSWORD,
    ODOO_URL,
)


INTERVALO_SEGUNDOS = 15

ASUNTO_MARKETING = (
    "Gracias por tu compra en QuetzalMart | "
    "10% de descuento en tu próxima visita"
)

CORREO_QUETZALMART = (
    "QuetzalMart <quetzalmart.g2@gmail.com>"
)

NOMBRE_PLANTILLA = (
    "QuetzalMart - Marketing Post Compra"
)

CODIGO_DESCUENTO = "VIP10"

URL_TIENDA = f"{ODOO_URL.rstrip('/')}/shop"

uid, models = conectar_odoo()



def construir_html():
    return f"""
    <div style="
        margin:0;
        padding:30px 10px;
        background-color:#f3f5f4;
        font-family:Arial, Helvetica, sans-serif;
    ">

        <div style="
            max-width:680px;
            margin:0 auto;
            background-color:#ffffff;
            border-radius:12px;
            overflow:hidden;
            border:1px solid #e1e5e2;
        ">

            <!-- ENCABEZADO -->
            <div style="
                background-color:#0f5132;
                color:#ffffff;
                text-align:center;
                padding:35px 25px;
            ">

                <div style="
                    font-size:34px;
                    font-weight:bold;
                    margin-bottom:8px;
                ">
                    QuetzalMart
                </div>

                <div style="
                    font-size:15px;
                    color:#e6f2eb;
                ">
                    Comprometidos al trabajo bien hecho.
                </div>

            </div>


            <!-- CONTENIDO -->
            <div style="
                padding:35px 35px 20px 35px;
            ">

                <h1 style="
                    margin:0;
                    text-align:center;
                    color:#18392a;
                    font-size:28px;
                ">
                    ¡Gracias por tu compra!
                </h1>

                <p style="
                    text-align:center;
                    color:#666666;
                    font-size:16px;
                    line-height:1.6;
                    margin-top:15px;
                ">
                    Gracias por confiar en
                    <strong>QuetzalMart</strong>.
                    Esperamos que disfrutes tu compra.
                </p>

                <p style="
                    text-align:center;
                    color:#666666;
                    font-size:16px;
                    line-height:1.6;
                ">
                    Queremos seguir acompañándote,
                    por eso tenemos un beneficio
                    especial para tu próxima visita.
                </p>


                <!-- PROMOCIÓN -->
                <div style="
                    margin:30px 0;
                    padding:30px 20px;
                    background-color:#20252f;
                    border-radius:12px;
                    text-align:center;
                    color:#ffffff;
                ">

                    <div style="
                        font-size:13px;
                        letter-spacing:2px;
                        font-weight:bold;
                        color:#dfc078;
                    ">
                        OFERTA EXCLUSIVA
                    </div>

                    <div style="
                        margin-top:12px;
                        font-size:40px;
                        font-weight:bold;
                        color:#ffffff;
                    ">
                        10% DE DESCUENTO
                    </div>

                    <p style="
                        font-size:16px;
                        color:#eeeeee;
                        margin:15px 0;
                    ">
                        Utiliza este código en tu
                        próxima compra:
                    </p>

                    <div style="
                        display:inline-block;
                        padding:14px 30px;
                        background-color:#ffffff;
                        border:2px dashed #dfc078;
                        border-radius:8px;
                        color:#20252f;
                        font-size:26px;
                        font-weight:bold;
                        letter-spacing:3px;
                    ">
                        {CODIGO_DESCUENTO}
                    </div>

                    <p style="
                        margin-top:16px;
                        margin-bottom:0;
                        font-size:13px;
                        color:#cccccc;
                    ">
                        Ingresa el código durante
                        el proceso de compra.
                    </p>

                </div>


                <!-- BENEFICIOS -->
                <table
                    width="100%"
                    cellpadding="0"
                    cellspacing="0"
                    style="
                        margin:25px 0;
                        text-align:center;
                    "
                >
                    <tr>

                        <td style="
                            width:33%;
                            padding:12px;
                            color:#245c3c;
                            font-weight:bold;
                            font-size:14px;
                        ">
                            ENVÍOS<br>
                            RÁPIDOS
                        </td>

                        <td style="
                            width:33%;
                            padding:12px;
                            color:#245c3c;
                            font-weight:bold;
                            font-size:14px;
                        ">
                            OFERTAS<br>
                            EXCLUSIVAS
                        </td>

                        <td style="
                            width:33%;
                            padding:12px;
                            color:#245c3c;
                            font-weight:bold;
                            font-size:14px;
                        ">
                            COMPRA<br>
                            EN LÍNEA
                        </td>

                    </tr>
                </table>


                <p style="
                    text-align:center;
                    color:#555555;
                    font-size:16px;
                    line-height:1.6;
                ">
                    Descubre alimentos, bebidas
                    y productos esenciales para
                    tu día a día.
                </p>


                <!-- BOTÓN -->
                <div style="
                    text-align:center;
                    margin:30px 0;
                ">

                    <a
                        href="{URL_TIENDA}"
                        style="
                            display:inline-block;
                            background-color:#167044;
                            color:#ffffff;
                            text-decoration:none;
                            padding:15px 32px;
                            border-radius:8px;
                            font-size:16px;
                            font-weight:bold;
                        "
                    >
                        Volver a QuetzalMart
                    </a>

                </div>


                <p style="
                    text-align:center;
                    font-size:13px;
                    color:#888888;
                ">
                    Código promocional:
                    <strong>{CODIGO_DESCUENTO}</strong>
                </p>

            </div>


            <!-- PIE -->
            <div style="
                background-color:#edf3ef;
                padding:25px;
                text-align:center;
            ">

                <div style="
                    color:#17452f;
                    font-size:17px;
                    font-weight:bold;
                ">
                    QuetzalMart
                </div>

                <p style="
                    margin:8px 0 0 0;
                    color:#6d756f;
                    font-size:13px;
                ">
                    Ciudad de Guatemala, Guatemala
                </p>

                <p style="
                    margin:8px 0 0 0;
                    color:#8a8a8a;
                    font-size:12px;
                ">
                    Este correo fue enviado
                    automáticamente como seguimiento
                    a tu compra.
                </p>

            </div>

        </div>

    </div>
    """


def obtener_modelo_id(nombre_modelo):
    registros = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "ir.model",
        "search_read",
        [[
            ["model", "=", nombre_modelo]
        ]],
        {
            "fields": ["id"],
            "limit": 1,
        },
    )

    if not registros:
        raise Exception(
            f"No se encontró el modelo: {nombre_modelo}"
        )

    return registros[0]["id"]


def obtener_o_crear_plantilla():

    modelo_crm_id = obtener_modelo_id(
        "crm.lead"
    )

    body_html = construir_html()

    plantillas = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "mail.template",
        "search",
        [[
            [
                "name",
                "=",
                NOMBRE_PLANTILLA,
            ]
        ]],
        {
            "limit": 1
        },
    )

    if plantillas:

        plantilla_id = plantillas[0]

        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "mail.template",
            "write",
            [
                [plantilla_id],
                {
                    "subject":
                        ASUNTO_MARKETING,

                    "email_from":
                        CORREO_QUETZALMART,

                    "email_to":
                        "{{ object.email_from }}",

                    "body_html":
                        body_html,
                },
            ],
        )

        print(
            f"Plantilla existente actualizada "
            f"correctamente: {plantilla_id}"
        )

        return plantilla_id

    plantilla_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "mail.template",
        "create",
        [{
            "name":
                NOMBRE_PLANTILLA,

            "model_id":
                modelo_crm_id,

            "subject":
                ASUNTO_MARKETING,

            "email_from":
                CORREO_QUETZALMART,

            "email_to":
                "{{ object.email_from }}",

            "body_html":
                body_html,
        }],
    )

    print(
        f"Plantilla creada correctamente: "
        f"{plantilla_id}"
    )

    return plantilla_id


def obtener_datos_orden(orden_id):

    resultado = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "sale.order",
        "read",
        [[orden_id]],
        {
            "fields": [
                "name",
                "partner_id",
                "amount_total",
                "invoice_ids",
                "state",
                "website_id",
            ]
        },
    )

    if not resultado:
        return None

    return resultado[0]

def factura_esta_pagada(orden):

    factura_ids = orden.get(
        "invoice_ids",
        []
    )

    if not factura_ids:
        return False

    facturas = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "account.move",
        "read",
        [factura_ids],
        {
            "fields": [
                "name",
                "state",
                "payment_state",
                "move_type",
            ]
        },
    )

    for factura in facturas:

        es_factura_cliente = (
            factura["move_type"]
            == "out_invoice"
        )

        esta_publicada = (
            factura["state"]
            == "posted"
        )

        esta_pagada = (
            factura["payment_state"]
            == "paid"
        )

        if (
            es_factura_cliente
            and esta_publicada
            and esta_pagada
        ):
            return True

    return False


def obtener_cliente(partner_id):

    resultado = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "res.partner",
        "read",
        [[partner_id]],
        {
            "fields": [
                "name",
                "email",
                "phone",
            ]
        },
    )

    if not resultado:
        return None

    return resultado[0]


# =========================================================
# CRM
# =========================================================

def obtener_o_crear_oportunidad(
    orden,
    cliente,
):

    nombre = (
        f"Compra Web - {orden['name']}"
    )

    oportunidades = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "crm.lead",
        "search",
        [[
            [
                "name",
                "=",
                nombre,
            ],
            [
                "partner_id",
                "=",
                cliente["id"],
            ],
        ]],
        {
            "limit": 1
        },
    )

    if oportunidades:

        oportunidad_id = (
            oportunidades[0]
        )

        print(
            f"CRM: oportunidad existente "
            f"(ID {oportunidad_id})"
        )

        return oportunidad_id

    # Crear nueva
    descripcion = (
        f"Compra realizada desde la tienda "
        f"web de QuetzalMart. "
        f"Pedido {orden['name']}. "
        f"Total Q{orden['amount_total']:.2f}. "
        f"Pago confirmado."
    )

    oportunidad_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "crm.lead",
        "create",
        [{
            "name":
                nombre,

            "type":
                "opportunity",

            "partner_id":
                cliente["id"],

            "email_from":
                cliente.get("email"),

            "phone":
                cliente.get("phone"),

            "expected_revenue":
                orden["amount_total"],

            "probability":
                100,

            "description":
                descripcion,
        }],
    )

    print(
        f"CRM: oportunidad creada "
        f"(ID {oportunidad_id})"
    )

    return oportunidad_id


def correo_ya_enviado(
    oportunidad_id,
):

    cantidad = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "mail.message",
        "search_count",
        [[
            [
                "model",
                "=",
                "crm.lead",
            ],
            [
                "res_id",
                "=",
                oportunidad_id,
            ],
            [
                "subject",
                "=",
                ASUNTO_MARKETING,
            ],
        ]],
    )

    return cantidad > 0


# =========================================================
# ENVIAR CORREO
# =========================================================

def enviar_correo(
    plantilla_id,
    oportunidad_id,
):

    mail_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "mail.template",
        "send_mail",
        [
            [plantilla_id],
            oportunidad_id,
        ],
        {
            "force_send": True,
            "raise_exception": True,
        },
    )

    return mail_id



def obtener_ordenes_web_confirmadas():

    return models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "sale.order",
        "search",
        [[
            [
                "state",
                "=",
                "sale",
            ],
            [
                "website_id",
                "!=",
                False,
            ],
        ]],
    )


plantilla_id = (
    obtener_o_crear_plantilla()
)


ordenes_existentes = set(
    obtener_ordenes_web_confirmadas()
)

procesadas = set()


print()
print("=" * 50)
print("AUTOMATIZACIÓN POST-COMPRA QUETZALMART")
print("=" * 50)

print(
    f"Plantilla de marketing: "
    f"{plantilla_id}"
)

print(
    f"Órdenes web existentes ignoradas: "
    f"{len(ordenes_existentes)}"
)

print(
    f"Código promocional: "
    f"{CODIGO_DESCUENTO}"
)

print(
    f"Intervalo de revisión: "
    f"{INTERVALO_SEGUNDOS} segundos"
)

print()
print("Esperando nuevas compras...")
print()

while True:

    try:

        ordenes_actuales = (
            obtener_ordenes_web_confirmadas()
        )

        nuevas = [
            orden_id
            for orden_id
            in ordenes_actuales

            if (
                orden_id
                not in ordenes_existentes

                and orden_id
                not in procesadas
            )
        ]

        for orden_id in nuevas:

            orden = obtener_datos_orden(
                orden_id
            )

            if not orden:
                continue

            print()
            print("-" * 50)

            print(
                f"Nueva compra detectada: "
                f"{orden['name']}"
            )

            print(
                f"Total de la compra: "
                f"Q {orden['amount_total']:.2f}"
            )

            # -------------------------------------
            # Esperar factura
            # -------------------------------------

            if not factura_esta_pagada(
                orden
            ):

                print(
                    "La factura todavía no "
                    "está pagada."
                )

                print(
                    "Esperando confirmación "
                    "del pago..."
                )

                continue

            print(
                "Factura pagada detectada."
            )

            # -------------------------------------
            # Cliente
            # -------------------------------------

            partner_id = (
                orden["partner_id"][0]
            )

            cliente = obtener_cliente(
                partner_id
            )

            if not cliente:

                print(
                    "No fue posible obtener "
                    "el cliente."
                )

                procesadas.add(
                    orden_id
                )

                continue

            print(
                f"Cliente: "
                f"{cliente['name']}"
            )


            if not cliente.get("email"):

                print(
                    "El cliente no tiene "
                    "correo electrónico."
                )

                print(
                    "No se puede enviar "
                    "la campaña."
                )

                procesadas.add(
                    orden_id
                )

                continue

            print(
                f"Correo: "
                f"{cliente['email']}"
            )

            oportunidad_id = (
                obtener_o_crear_oportunidad(
                    orden,
                    cliente,
                )
            )


            if correo_ya_enviado(
                oportunidad_id
            ):

                print(
                    "El correo promocional "
                    "ya fue enviado anteriormente."
                )

                procesadas.add(
                    orden_id
                )

                continue

            # -------------------------------------
            # Enviar marketing
            # -------------------------------------

            print(
                "Enviando correo "
                "promocional..."
            )

            mail_id = enviar_correo(
                plantilla_id,
                oportunidad_id,
            )

            print()
            print(
                "CORREO PROMOCIONAL "
                "ENVIADO CORRECTAMENTE"
            )

            print(
                f"Mail ID: {mail_id}"
            )

            print(
                f"Orden: {orden['name']}"
            )

            print(
                f"Cliente: "
                f"{cliente['name']}"
            )

            print(
                f"Correo: "
                f"{cliente['email']}"
            )

            print(
                f"Total: "
                f"Q {orden['amount_total']:.2f}"
            )

            print(
                f"Cupón enviado: "
                f"{CODIGO_DESCUENTO}"
            )

            print("-" * 50)

            procesadas.add(
                orden_id
            )

    except KeyboardInterrupt:

        print()
        print(
            "Automatización detenida "
            "por el usuario."
        )

        break

    except Exception as error:

        print()
        print(
            "ERROR DURANTE LA "
            "AUTOMATIZACIÓN:"
        )

        print(error)

        print(
            "Se volverá a intentar "
            f"en {INTERVALO_SEGUNDOS} segundos."
        )

    time.sleep(
        INTERVALO_SEGUNDOS
    )