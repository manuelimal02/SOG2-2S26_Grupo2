"""
MCPServer - Práctica 1 SOG2
---------------------------
Expone como "tools" MCP la misma lógica de análisis que ya construyeron
Persona 2 (exploratorio), Persona 3 (tendencias) y Persona 4 (segmentación
y correlación), pero en vez de imprimir en consola o guardar solo en disco,
devuelve resultados estructurados (dict/JSON) para que el agente de
Google ADK los pueda leer y responder al usuario en lenguaje natural.

Cada tool:
  1. Se conecta a la base de datos (Supabase / Postgres) usando DATABASE_URL.
  2. Ejecuta exactamente la misma consulta/lógica pandas que el resto del
     equipo ya definió para ese punto del enunciado.
  3. Devuelve un diccionario con los resultados (y, cuando aplica, la ruta
     del gráfico .png generado) para que el agente los use en su respuesta.

Ejecución local para pruebas:
    python server.py
Conexión desde el agente ADK: ver agente_sog2/agent.py
"""

import os
import pandas as pd
import numpy as np
import psycopg2
from dotenv import load_dotenv
from scipy.stats import pearsonr, chi2_contingency

from mcp.server.fastmcp import FastMCP

# -------------------------------------------------------------------
# Configuración e inicialización
# -------------------------------------------------------------------
# El .env vive en la raíz del proyecto (un nivel arriba de mcp_server/),
# para que tanto este servidor como el agente ADK lean las mismas
# variables (DATABASE_URL, GOOGLE_API_KEY).
RUTA_ENV = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(RUTA_ENV, override=True)

# Carpeta donde se guardan los gráficos generados por las tools,
# para poder adjuntarlos luego al informe final.
CARPETA_GRAFICOS = os.path.join(os.path.dirname(__file__), "graficos")
os.makedirs(CARPETA_GRAFICOS, exist_ok=True)

mcp = FastMCP("sog2-analisis-ventas")

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
METODO_PAGO = {0: "Efectivo / Contra entrega", 1: "Tarjeta de Crédito", 2: "Tarjeta de Débito"}
NAVEGADOR = {0: "Tienda Física", 1: "Navegador 1", 2: "Navegador 2", 3: "Navegador 3", 4: "Navegador 4"}
SI_NO = {0: "No", 1: "Sí"}


def _conectar_bd():
    """Conecta a la base de datos en Supabase (Postgres)."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "No se encontró DATABASE_URL en el .env. Verifica que el archivo "
            "esté en la raíz del proyecto y contenga la cadena de conexión de Supabase."
        )
    return psycopg2.connect(database_url)


def _obtener_datos() -> pd.DataFrame:
    """Obtiene todos los registros de la tabla 'ventas'."""
    conexion = _conectar_bd()
    try:
        df = pd.read_sql("SELECT * FROM ventas;", conexion)
    finally:
        conexion.close()
    return df


def _ruta_grafico(nombre_archivo: str) -> str:
    return os.path.join(CARPETA_GRAFICOS, nombre_archivo)


# =====================================================================
# PUNTO 2 · ANÁLISIS EXPLORATORIO  (lógica de Persona 2)
# =====================================================================

@mcp.tool()
def obtener_estadisticas_basicas() -> dict:
    """Calcula media, mediana y moda de edad, venta_total, n_compras,
    monto_compra y tiempo. Úsala cuando pregunten por estadísticas
    generales, promedios, medianas o valores más frecuentes."""
    df = _obtener_datos()
    columnas = ["edad", "venta_total", "n_compras", "monto_compra", "tiempo"]
    resumen = pd.DataFrame({
        "media": df[columnas].mean(),
        "mediana": df[columnas].median(),
        "moda": df[columnas].apply(lambda col: col.mode().iloc[0]),
    }).round(2)
    return {"estadisticas_basicas": resumen.reset_index().rename(columns={"index": "variable"}).to_dict("records")}


def _distribucion_por(df, columna_grupo, mapeo, titulo, archivo):
    df = df.copy()
    df["grupo"] = df[columna_grupo].map(mapeo) if mapeo else df[columna_grupo]
    resumen = df.groupby("grupo")["venta_total"].sum()
    if mapeo:
        resumen = resumen.reindex(list(mapeo.values()))
    resumen = resumen.reset_index()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=resumen, x="grupo", y="venta_total", hue="grupo", ax=ax, palette="Set2", legend=False)
    ax.set_title(titulo)
    ax.set_ylabel("Venta total")
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    ruta = _ruta_grafico(archivo)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return resumen.to_dict("records"), ruta


@mcp.tool()
def distribucion_ventas_por_mes() -> dict:
    """Distribución de la venta total agrupada por mes. Úsala cuando
    pregunten cómo se distribuyen las ventas a lo largo del año."""
    df = _obtener_datos()
    df["mes"] = pd.to_datetime(df["fecha_compra"]).dt.month.map(MESES)
    datos, ruta = _distribucion_por(df, "mes", None, "Distribución de ventas por mes", "distribucion_mes.png")
    return {"distribucion_por_mes": datos, "grafico": ruta}


@mcp.tool()
def distribucion_ventas_por_metodo_pago() -> dict:
    """Distribución de la venta total agrupada por método de pago
    (efectivo, tarjeta de crédito, tarjeta de débito)."""
    df = _obtener_datos()
    datos, ruta = _distribucion_por(df, "metodo_pago", METODO_PAGO,
                                     "Distribución de ventas por método de pago", "distribucion_metodopago.png")
    return {"distribucion_por_metodo_pago": datos, "grafico": ruta}


@mcp.tool()
def distribucion_ventas_por_navegador() -> dict:
    """Distribución de la venta total agrupada por navegador usado
    (incluye 'Tienda Física' para ventas presenciales)."""
    df = _obtener_datos()
    datos, ruta = _distribucion_por(df, "navegador", NAVEGADOR,
                                     "Distribución de ventas por navegador", "distribucion_navegador.png")
    return {"distribucion_por_navegador": datos, "grafico": ruta}


@mcp.tool()
def distribucion_ventas_por_boletin() -> dict:
    """Distribución de la venta total agrupada por si el cliente está
    suscrito o no al boletín."""
    df = _obtener_datos()
    datos, ruta = _distribucion_por(df, "boletin", SI_NO,
                                     "Distribución de ventas por suscripción a Boletín", "distribucion_boletin.png")
    return {"distribucion_por_boletin": datos, "grafico": ruta}


@mcp.tool()
def distribucion_ventas_por_vale() -> dict:
    """Distribución de la venta total agrupada por si el cliente usó
    o no un vale de descuento."""
    df = _obtener_datos()
    datos, ruta = _distribucion_por(df, "vale", SI_NO,
                                     "Distribución de ventas por uso de Vale", "distribucion_vale.png")
    return {"distribucion_por_vale": datos, "grafico": ruta}


# =====================================================================
# PUNTO 3 · ANÁLISIS DE TENDENCIAS  (lógica de Persona 3)
# =====================================================================

@mcp.tool()
def meses_mayor_menor_venta() -> dict:
    """Identifica el mes con mayor y el mes con menor venta total del año.
    Úsala cuando pregunten en qué mes se vendió más o menos."""
    df = _obtener_datos()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_num"] = df["fecha_compra"].dt.month
    resumen = df.groupby("mes_num")["venta_total"].sum().reindex(range(1, 13)).reset_index()
    resumen["mes"] = resumen["mes_num"].map(MESES)
    fila_mayor = resumen.loc[resumen["venta_total"].idxmax()]
    fila_menor = resumen.loc[resumen["venta_total"].idxmin()]
    return {
        "ventas_por_mes": resumen[["mes", "venta_total"]].to_dict("records"),
        "mes_mayor_venta": {"mes": fila_mayor["mes"], "venta_total": round(float(fila_mayor["venta_total"]), 2)},
        "mes_menor_venta": {"mes": fila_menor["mes"], "venta_total": round(float(fila_menor["venta_total"]), 2)},
    }


@mcp.tool()
def navegador_mas_menos_utilizado() -> dict:
    """Identifica el navegador más y el menos utilizado por los clientes,
    contando el número de registros (compras) por navegador."""
    df = _obtener_datos()
    df["navegador_label"] = df["navegador"].map(NAVEGADOR)
    resumen = df.groupby("navegador_label").size().reindex(list(NAVEGADOR.values())).reset_index(name="cantidad")
    fila_mayor = resumen.loc[resumen["cantidad"].idxmax()]
    fila_menor = resumen.loc[resumen["cantidad"].idxmin()]
    return {
        "uso_por_navegador": resumen.to_dict("records"),
        "navegador_mas_usado": {"navegador": fila_mayor["navegador_label"], "cantidad": int(fila_mayor["cantidad"])},
        "navegador_menos_usado": {"navegador": fila_menor["navegador_label"], "cantidad": int(fila_menor["cantidad"])},
    }


@mcp.tool()
def ventas_por_metodo_pago() -> dict:
    """Calcula cantidad y monto total de ventas pagadas en efectivo/contra
    entrega frente a tarjeta de crédito y débito."""
    df = _obtener_datos()
    df["metodo_pago_label"] = df["metodo_pago"].map(METODO_PAGO)
    resumen = df.groupby("metodo_pago_label")["venta_total"].sum().reindex(list(METODO_PAGO.values())).reset_index()
    cantidad_efectivo = int((df["metodo_pago"] == 0).sum())
    total_efectivo = float(resumen.loc[resumen["metodo_pago_label"] == "Efectivo / Contra entrega", "venta_total"].iloc[0])
    return {
        "ventas_por_metodo_pago": resumen.to_dict("records"),
        "efectivo_contra_entrega": {"cantidad_ventas": cantidad_efectivo, "total_vendido": round(total_efectivo, 2)},
    }


@mcp.tool()
def meses_mayor_uso_boletin() -> dict:
    """Identifica en qué meses del año se usó más el boletín de descuentos."""
    df = _obtener_datos()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_num"] = df["fecha_compra"].dt.month
    resumen = df[df["boletin"] == 1].groupby("mes_num").size().reindex(range(1, 13), fill_value=0).reset_index(name="cantidad")
    resumen["mes"] = resumen["mes_num"].map(MESES)
    fila_mayor = resumen.loc[resumen["cantidad"].idxmax()]
    return {
        "uso_boletin_por_mes": resumen[["mes", "cantidad"]].to_dict("records"),
        "mes_mayor_uso_boletin": {"mes": fila_mayor["mes"], "cantidad": int(fila_mayor["cantidad"])},
    }


@mcp.tool()
def meses_mayor_uso_vale() -> dict:
    """Identifica en qué meses del año se usaron más los vales de descuento."""
    df = _obtener_datos()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_num"] = df["fecha_compra"].dt.month
    resumen = df[df["vale"] == 1].groupby("mes_num").size().reindex(range(1, 13), fill_value=0).reset_index(name="cantidad")
    resumen["mes"] = resumen["mes_num"].map(MESES)
    fila_mayor = resumen.loc[resumen["cantidad"].idxmax()]
    return {
        "uso_vale_por_mes": resumen[["mes", "cantidad"]].to_dict("records"),
        "mes_mayor_uso_vale": {"mes": fila_mayor["mes"], "cantidad": int(fila_mayor["cantidad"])},
    }


# =====================================================================
# PUNTO 4 · SEGMENTACIÓN DE CLIENTES  (lógica de Persona 4)
# =====================================================================

@mcp.tool()
def segmentacion_por_edad() -> dict:
    """Agrupa a los clientes en rangos de edad (18-25, 26-35, ... 66+) y
    calcula venta total promedio, número de compras y monto promedio
    por rango. Úsala para preguntas sobre patrones de compra por edad."""
    df = _obtener_datos()
    bins = [17, 25, 35, 45, 55, 65, 100]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]
    df["rango_edad"] = pd.cut(df["edad"], bins=bins, labels=labels)
    resumen = (
        df.groupby("rango_edad", observed=True)
        .agg(clientes=("id_cliente", "count"), venta_total_prom=("venta_total", "mean"),
             n_compras_prom=("n_compras", "mean"), monto_compra_prom=("monto_compra", "mean"))
        .round(2).reset_index()
    )
    resumen["rango_edad"] = resumen["rango_edad"].astype(str)
    return {"segmentacion_por_edad": resumen.to_dict("records")}


@mcp.tool()
def comparacion_por_genero() -> dict:
    """Compara venta total promedio, número de compras y monto promedio
    entre clientes de género femenino y masculino."""
    df = _obtener_datos()
    resumen = (
        df.groupby("genero")
        .agg(clientes=("id_cliente", "count"), venta_total_prom=("venta_total", "mean"),
             n_compras_prom=("n_compras", "mean"), monto_compra_prom=("monto_compra", "mean"))
        .round(2).reset_index()
    )
    resumen["genero"] = resumen["genero"].map({1: "Femenino", 0: "Masculino"})
    return {"comparacion_por_genero": resumen.to_dict("records")}


@mcp.tool()
def segmentacion_boletin_vale() -> dict:
    """Agrupa a los clientes por combinación de suscripción a boletín y
    uso de vale, mostrando cuántos clientes hay en cada grupo y su
    venta/compras promedio."""
    df = _obtener_datos()
    resumen = (
        df.groupby(["boletin", "vale"])
        .agg(clientes=("id_cliente", "count"), venta_total_prom=("venta_total", "mean"),
             n_compras_prom=("n_compras", "mean"))
        .round(2).reset_index()
    )
    resumen["boletin"] = resumen["boletin"].map({1: "Sí", 0: "No"})
    resumen["vale"] = resumen["vale"].map({1: "Sí", 0: "No"})
    return {"segmentacion_boletin_vale": resumen.to_dict("records")}


# =====================================================================
# PUNTO 5 · ANÁLISIS DE CORRELACIÓN  (lógica de Persona 4)
# =====================================================================

@mcp.tool()
def correlacion_venta_edad() -> dict:
    """Calcula la correlación de Pearson entre la edad del cliente y su
    venta total, para saber si a mayor edad compran más o menos. Genera
    y guarda un gráfico de dispersión con línea de tendencia."""
    df = _obtener_datos()
    r, p_valor = pearsonr(df["edad"], df["venta_total"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=df, x="edad", y="venta_total", ax=ax,
        scatter_kws={"alpha": 0.3, "s": 15}, line_kws={"color": "red"},
    )
    ax.set_title(f"Venta total vs Edad (r = {r:.3f})")
    fig.tight_layout()
    ruta = _ruta_grafico("correlacion_edad_venta.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)

    return {
        "coeficiente_pearson": round(float(r), 3),
        "p_valor": round(float(p_valor), 4),
        "interpretacion": (
            "Correlación positiva" if r > 0.1 else
            "Correlación negativa" if r < -0.1 else
            "Sin correlación relevante"
        ),
        "grafico": ruta,
    }


@mcp.tool()
def correlacion_genero_metodopago() -> dict:
    """Evalúa si existe asociación entre el género del cliente y el
    método de pago preferido, usando chi-cuadrado y V de Cramér. Genera
    y guarda un gráfico de barras apiladas con la distribución (%)."""
    df = _obtener_datos()
    tabla = pd.crosstab(df["genero"], df["metodo_pago"])
    tabla.index = tabla.index.map({1: "Femenino", 0: "Masculino"})
    tabla.columns = tabla.columns.map({0: "Efectivo", 1: "Tarjeta Crédito", 2: "Tarjeta Débito"})
    chi2, p_valor, _, _ = chi2_contingency(tabla)
    n = tabla.values.sum()
    cramers_v = float(np.sqrt(chi2 / (n * (min(tabla.shape) - 1))))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5))
    tabla_pct = tabla.div(tabla.sum(axis=1), axis=0) * 100
    tabla_pct.plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
    ax.set_title("Distribución de método de pago por género")
    ax.set_ylabel("% de clientes")
    ax.legend(title="Método de pago", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    ruta = _ruta_grafico("correlacion_genero_metodopago.png")
    fig.savefig(ruta, dpi=150)
    plt.close(fig)

    return {
        "tabla_cruzada": tabla.reset_index().to_dict("records"),
        "chi2": round(float(chi2), 2),
        "p_valor": round(float(p_valor), 4),
        "cramers_v": round(cramers_v, 3),
        "grafico": ruta,
    }


@mcp.tool()
def correlacion_boletin_vale() -> dict:
    """Evalúa si existe asociación entre usar boletín y usar vale de
    descuento (variables binarias), usando chi-cuadrado y coeficiente Phi."""
    df = _obtener_datos()
    tabla = pd.crosstab(df["boletin"], df["vale"])
    chi2, p_valor, _, _ = chi2_contingency(tabla)
    n = tabla.values.sum()
    phi = float(np.sqrt(chi2 / n))
    return {
        "chi2": round(float(chi2), 2),
        "p_valor": round(float(p_valor), 4),
        "coeficiente_phi": round(phi, 3),
    }


if __name__ == "__main__":
    # Transporte stdio: así lo consume el agente ADK vía StdioServerParameters.
    mcp.run(transport="stdio")