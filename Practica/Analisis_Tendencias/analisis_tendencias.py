# Punto 3: Análisis de tendencias

import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

METODO_PAGO = {
    0: "Efectivo / Contra entrega",
    1: "Tarjeta de Crédito",
    2: "Tarjeta de Débito"
}
NAVEGADOR = {
    0: "Tienda Física",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4"
}


# -------------------------------------------------------------------
# 3.a OBTENER LOS DATOS DE LA BASE DE DATOS
# -------------------------------------------------------------------
def conectar_bd():
    """Conecta a la base de datos en Supabase."""

    ruta_env = os.path.join(
        os.path.dirname(__file__),
        "..",
        ".env"
    )

    load_dotenv(ruta_env, override=True)

    conexion = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("Conexión a Supabase establecida.")
    return conexion

def obtener_datos(conexion) -> pd.DataFrame:
    """Obtiene todos los registros de la tabla 'ventas'."""
    query = "SELECT * FROM ventas;"
    df = pd.read_sql(query, conexion)
    print(f"Se obtuvieron {df.shape[0]} filas desde la base de datos.")
    return df


# -------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA GUARDAR GRÁFICAS
# -------------------------------------------------------------------
def _grafico_barras(resumen: pd.DataFrame, x: str, y: str, titulo: str, ylabel: str, archivo: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=resumen, x=x, y=y, hue=x, ax=ax, palette="Set2", legend=False)
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(archivo, dpi=150)
    plt.close(fig)
    print(f"Gráfico guardado: {archivo}")


# -------------------------------------------------------------------
# 3.b MESES CON MAYORES Y MENORES VENTAS
# -------------------------------------------------------------------
def meses_mayor_menor_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """Obtiene la venta total por mes e identifica el mes con mayor y menor venta."""
    df = df.copy()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_num"] = df["fecha_compra"].dt.month

    resumen = (
        df.groupby("mes_num")["venta_total"]
        .sum()
        .reindex(range(1, 13))
        .reset_index()
    )
    resumen["mes"] = resumen["mes_num"].map(MESES)

    print("\n--- 3.b Meses con mayores y menores ventas ---")
    print(resumen[["mes", "venta_total"]])

    fila_mayor = resumen.loc[resumen["venta_total"].idxmax()]
    fila_menor = resumen.loc[resumen["venta_total"].idxmin()]

    print(f"\nMes con MAYOR venta: {fila_mayor['mes']} - Q{fila_mayor['venta_total']:.2f}")
    print(f"Mes con MENOR venta: {fila_menor['mes']} - Q{fila_menor['venta_total']:.2f}")

    _grafico_barras(
        resumen,
        "mes",
        "venta_total",
        "Ventas totales por mes",
        "Venta total",
        "grafico_tendencia_ventas_por_mes.png"
    )

    return resumen[["mes", "venta_total"]]


# -------------------------------------------------------------------
# 3.c NAVEGADOR MÁS Y MENOS UTILIZADO
# -------------------------------------------------------------------
def navegador_mas_menos_utilizado(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta cuántas veces fue utilizado cada navegador."""
    df = df.copy()
    df["navegador_label"] = df["navegador"].map(NAVEGADOR)

    resumen = (
        df.groupby("navegador_label")
        .size()
        .reindex(list(NAVEGADOR.values()))
        .reset_index(name="cantidad")
    )

    print("\n--- 3.c Navegador más y menos utilizado ---")
    print(resumen)

    fila_mayor = resumen.loc[resumen["cantidad"].idxmax()]
    fila_menor = resumen.loc[resumen["cantidad"].idxmin()]

    print(f"\nMás utilizado: {fila_mayor['navegador_label']} - {fila_mayor['cantidad']} registros")
    print(f"Menos utilizado: {fila_menor['navegador_label']} - {fila_menor['cantidad']} registros")

    _grafico_barras(
        resumen,
        "navegador_label",
        "cantidad",
        "Uso de navegadores",
        "Cantidad de registros",
        "grafico_tendencia_navegadores.png"
    )

    return resumen


# -------------------------------------------------------------------
# 3.d TOTAL DE VENTAS PAGADAS EN EFECTIVO
# -------------------------------------------------------------------
def ventas_efectivo_contra_entrega(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el total vendido por método de pago
    y genera la gráfica para la sección 6.3.
    """
    df = df.copy()
    df["metodo_pago_label"] = df["metodo_pago"].map(METODO_PAGO)

    resumen = (
        df.groupby("metodo_pago_label")["venta_total"]
        .sum()
        .reindex(list(METODO_PAGO.values()))
        .reset_index()
    )

    print("\n--- 6.3 Ventas contra entrega o pago en efectivo ---")
    print(resumen)

    fila_efectivo = resumen[
        resumen["metodo_pago_label"] == "Efectivo / Contra entrega"
    ].iloc[0]

    cantidad_efectivo = df[df["metodo_pago"] == 0].shape[0]
    total_efectivo = fila_efectivo["venta_total"]

    print(f"\nCantidad de ventas en efectivo / contra entrega: {cantidad_efectivo}")
    print(f"Total vendido en efectivo / contra entrega: Q{total_efectivo:.2f}")

    _grafico_barras(
        resumen,
        "metodo_pago_label",
        "venta_total",
        "Ventas por método de pago",
        "Venta total",
        "grafico_tendencia_metodopago.png"
    )

    return resumen

# -------------------------------------------------------------------
# 3.e MESES CON MAYOR USO DE BOLETINES
# -------------------------------------------------------------------
def meses_mayor_uso_boletin(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta en qué meses se usó más el boletín."""
    df = df.copy()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_num"] = df["fecha_compra"].dt.month

    resumen = (
        df[df["boletin"] == 1]
        .groupby("mes_num")
        .size()
        .reindex(range(1, 13), fill_value=0)
        .reset_index(name="cantidad")
    )
    resumen["mes"] = resumen["mes_num"].map(MESES)

    print("\n--- 3.e Meses con mayor uso de boletines ---")
    print(resumen[["mes", "cantidad"]])

    fila_mayor = resumen.loc[resumen["cantidad"].idxmax()]
    print(f"\nMes con mayor uso de boletín: {fila_mayor['mes']} - {fila_mayor['cantidad']} registros")

    _grafico_barras(
        resumen,
        "mes",
        "cantidad",
        "Uso de boletín por mes",
        "Cantidad de registros",
        "grafico_tendencia_boletines_por_mes.png"
    )

    return resumen[["mes", "cantidad"]]


# -------------------------------------------------------------------
# 3.f MESES CON MAYOR USO DE VALES
# -------------------------------------------------------------------
def meses_mayor_uso_vale(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta en qué meses se usaron más los vales."""
    df = df.copy()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_num"] = df["fecha_compra"].dt.month

    resumen = (
        df[df["vale"] == 1]
        .groupby("mes_num")
        .size()
        .reindex(range(1, 13), fill_value=0)
        .reset_index(name="cantidad")
    )
    resumen["mes"] = resumen["mes_num"].map(MESES)

    print("\n--- 3.f Meses con mayor uso de vales ---")
    print(resumen[["mes", "cantidad"]])

    fila_mayor = resumen.loc[resumen["cantidad"].idxmax()]
    print(f"\nMes con mayor uso de vale: {fila_mayor['mes']} - {fila_mayor['cantidad']} registros")

    _grafico_barras(
        resumen,
        "mes",
        "cantidad",
        "Uso de vales por mes",
        "Cantidad de registros",
        "grafico_tendencia_vales_por_mes.png"
    )

    return resumen[["mes", "cantidad"]]


# -------------------------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------------------------
def main():
    conexion = conectar_bd()
    try:
        df = obtener_datos(conexion)
    finally:
        conexion.close()
        print("Conexión cerrada.")

    meses_mayor_menor_ventas(df)
    navegador_mas_menos_utilizado(df)
    ventas_efectivo_contra_entrega(df)
    meses_mayor_uso_boletin(df)
    meses_mayor_uso_vale(df)

if __name__ == "__main__":
    main()