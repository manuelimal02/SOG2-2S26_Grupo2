# Punto 2: Análisis exploratorio

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
METODO_PAGO = {0: "Efectivo", 1: "Tarjeta de Crédito", 2: "Tarjeta de Débito"}
NAVEGADOR = {0: "Tienda Física", 1: "Navegador 1", 2: "Navegador 2", 3: "Navegador 3", 4: "Navegador 4"}
SI_NO = {0: "No", 1: "Sí"}


# -------------------------------------------------------------------
# 2.a OBTENER LOS DATOS DE LA BASE DE DATOS
# -------------------------------------------------------------------
def conectar_bd():
    """Conecta a la base de datos en Supabase."""
    load_dotenv()
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
# 2.b ESTADÍSTICAS BÁSICAS (media, mediana, moda)
# -------------------------------------------------------------------
def estadisticas_basicas(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula media, mediana y moda para las variables numéricas."""
    columnas_numericas = ["edad", "venta_total", "n_compras", "monto_compra", "tiempo"]

    resumen = pd.DataFrame({
        "media": df[columnas_numericas].mean(),
        "mediana": df[columnas_numericas].median(),
        "moda": df[columnas_numericas].apply(lambda col: col.mode().iloc[0]),
    }).round(2)

    print("\n--- 2.b Estadísticas básicas (variables numéricas) ---")
    print(resumen)
    return resumen


# -------------------------------------------------------------------
# 2.c VISUALIZACIONES DE DISTRIBUCIÓN DE VENTAS
# -------------------------------------------------------------------
def _grafico_barras(resumen: pd.DataFrame, x: str, y: str, titulo: str, ylabel: str, archivo: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=resumen, x=x, y=y, hue=x, ax=ax, palette="Set2", legend=False)
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(archivo, dpi=150)
    plt.close(fig)
    print(f"Gráfico guardado: {archivo}")


def distribucion_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de ventas por mes."""
    df = df.copy()
    df["mes"] = pd.to_datetime(df["fecha_compra"]).dt.month.map(MESES)

    resumen = (
        df.groupby("mes", sort=False)["venta_total"].sum()
        .reindex(list(MESES.values()))
        .reset_index()
    )
    print("\n--- 2.c Distribución de ventas por mes ---")
    print(resumen)
    _grafico_barras(resumen, "mes", "venta_total", "Distribución de ventas por mes",
                     "Venta total", "grafico_ventas_por_mes.png")
    return resumen


def distribucion_por_metodopago(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de ventas por método de pago."""
    df = df.copy()
    df["metodo_pago_label"] = df["metodo_pago"].map(METODO_PAGO)

    resumen = df.groupby("metodo_pago_label")["venta_total"].sum().reset_index()
    print("\n--- 2.c Distribución de ventas por método de pago ---")
    print(resumen)
    _grafico_barras(resumen, "metodo_pago_label", "venta_total", "Distribución de ventas por método de pago",
                     "Venta total", "grafico_ventas_por_metodopago.png")
    return resumen


def distribucion_por_navegador(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de ventas por navegador."""
    df = df.copy()
    df["navegador_label"] = df["navegador"].map(NAVEGADOR)

    resumen = df.groupby("navegador_label")["venta_total"].sum().reset_index()
    print("\n--- 2.c Distribución de ventas por navegador ---")
    print(resumen)
    _grafico_barras(resumen, "navegador_label", "venta_total", "Distribución de ventas por navegador",
                     "Venta total", "grafico_ventas_por_navegador.png")
    return resumen


def distribucion_por_boletin(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de ventas por suscripción a boletín."""
    df = df.copy()
    df["boletin_label"] = df["boletin"].map(SI_NO)

    resumen = df.groupby("boletin_label")["venta_total"].sum().reset_index()
    print("\n--- 2.c Distribución de ventas por Boletín ---")
    print(resumen)
    _grafico_barras(resumen, "boletin_label", "venta_total", "Distribución de ventas por suscripción a Boletín",
                     "Venta total", "grafico_ventas_por_boletin.png")
    return resumen


def distribucion_por_vale(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de ventas por uso de vale."""
    df = df.copy()
    df["vale_label"] = df["vale"].map(SI_NO)

    resumen = df.groupby("vale_label")["venta_total"].sum().reset_index()
    print("\n--- 2.c Distribución de ventas por Vale ---")
    print(resumen)
    _grafico_barras(resumen, "vale_label", "venta_total", "Distribución de ventas por uso de Vale",
                     "Venta total", "grafico_ventas_por_vale.png")
    return resumen


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

    estadisticas_basicas(df)

    distribucion_por_mes(df)
    distribucion_por_metodopago(df)
    distribucion_por_navegador(df)
    distribucion_por_boletin(df)
    distribucion_por_vale(df)


if __name__ == "__main__":
    main()
