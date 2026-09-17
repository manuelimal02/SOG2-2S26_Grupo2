# Punto 4: Segmentación de clientes
# Punto 5: Análisis de correlación

import os
import pandas as pd
import numpy as np
import psycopg2
from dotenv import load_dotenv
from scipy.stats import pearsonr, chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")


# -------------------------------------------------------------------
# CONEXIÓN Y EXTRACCIÓN (mismo patrón que el ETL del equipo)
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
# PUNTO 4: SEGMENTACIÓN DE CLIENTES
# -------------------------------------------------------------------

# 4.a Agrupar por edad y analizar patrones de compra
def segmentacion_por_edad(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa a los clientes en rangos de edad y calcula sus patrones de compra."""
    bins = [17, 25, 35, 45, 55, 65, 100]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]
    df["rango_edad"] = pd.cut(df["edad"], bins=bins, labels=labels)

    resumen = (
        df.groupby("rango_edad", observed=True)
        .agg(
            clientes=("id_cliente", "count"),
            venta_total_prom=("venta_total", "mean"),
            n_compras_prom=("n_compras", "mean"),
            monto_compra_prom=("monto_compra", "mean"),
        )
        .round(2)
        .reset_index()
    )
    print("\n--- 4.a Patrones de compra por rango de edad ---")
    print(resumen)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=resumen, x="rango_edad", y="venta_total_prom", ax=ax, color="#4C72B0")
    ax.set_title("Venta total promedio por rango de edad")
    ax.set_xlabel("Rango de edad")
    ax.set_ylabel("Venta total promedio")
    fig.tight_layout()
    fig.savefig("grafico_venta_por_edad.png", dpi=150)
    plt.close(fig)

    return resumen


# 4.b Comparar comportamiento de compra entre géneros
def comparacion_por_genero(df: pd.DataFrame) -> pd.DataFrame:
    """Compara métricas de compra entre clientes de género femenino y masculino."""
    resumen = (
        df.groupby("genero")
        .agg(
            clientes=("id_cliente", "count"),
            venta_total_prom=("venta_total", "mean"),
            n_compras_prom=("n_compras", "mean"),
            monto_compra_prom=("monto_compra", "mean"),
        )
        .round(2)
        .reset_index()
    )
    resumen["genero"] = resumen["genero"].map({1: "Femenino", 0: "Masculino"})
    print("\n--- 4.b Comparación de comportamiento por género ---")
    print(resumen)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(data=resumen, x="genero", y="venta_total_prom", hue="genero", ax=ax, palette="Set2", legend=False)
    ax.set_title("Venta total promedio por género")
    ax.set_xlabel("Género")
    ax.set_ylabel("Venta total promedio")
    fig.tight_layout()
    fig.savefig("grafico_venta_por_genero.png", dpi=150)
    plt.close(fig)

    return resumen


# 4.c Agrupar por boletín y vale, analizar patrones de compra
def segmentacion_boletin_vale(df: pd.DataFrame) -> pd.DataFrame:
    """Analiza patrones de compra según suscripción a boletín y uso de vales."""
    resumen = (
        df.groupby(["boletin", "vale"])
        .agg(
            clientes=("id_cliente", "count"),
            venta_total_prom=("venta_total", "mean"),
            n_compras_prom=("n_compras", "mean"),
        )
        .round(2)
        .reset_index()
    )
    resumen["boletin"] = resumen["boletin"].map({1: "Sí", 0: "No"})
    resumen["vale"] = resumen["vale"].map({1: "Sí", 0: "No"})
    print("\n--- 4.c Patrones de compra por Boletín y Vale ---")
    print(resumen)
    return resumen


# -------------------------------------------------------------------
# PUNTO 5: ANÁLISIS DE CORRELACIÓN
# -------------------------------------------------------------------

# 5.a Relación entre venta total y edad
def correlacion_venta_edad(df: pd.DataFrame) -> float:
    """Calcula la correlación de Pearson entre venta_total y edad."""
    r, p_valor = pearsonr(df["edad"], df["venta_total"])
    print(f"\n--- 5.a Correlación venta_total vs edad ---")
    print(f"Coeficiente de Pearson: {r:.3f} (p-valor: {p_valor:.4f})")

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=df, x="edad", y="venta_total", ax=ax,
        scatter_kws={"alpha": 0.3, "s": 15}, line_kws={"color": "red"},
    )
    ax.set_title(f"Venta total vs Edad (r = {r:.3f})")
    fig.tight_layout()
    fig.savefig("grafico_correlacion_edad_venta.png", dpi=150)
    plt.close(fig)

    return r


# 5.b Correlación entre género y método de pago preferido
def correlacion_genero_metodopago(df: pd.DataFrame):
    """Evalúa la asociación entre género y método de pago usando chi-cuadrado y V de Cramér."""
    tabla = pd.crosstab(df["genero"], df["metodo_pago"])
    tabla.index = tabla.index.map({1: "Femenino", 0: "Masculino"})
    tabla.columns = tabla.columns.map({0: "Efectivo", 1: "Tarjeta Crédito", 2: "Tarjeta Débito"})

    chi2, p_valor, gl, _ = chi2_contingency(tabla)
    n = tabla.values.sum()
    cramers_v = np.sqrt(chi2 / (n * (min(tabla.shape) - 1)))

    print("\n--- 5.b Correlación género vs método de pago ---")
    print(tabla)
    print(f"Chi2: {chi2:.2f}, p-valor: {p_valor:.4f}, V de Cramér: {cramers_v:.3f}")

    fig, ax = plt.subplots(figsize=(7, 5))
    tabla_pct = tabla.div(tabla.sum(axis=1), axis=0) * 100
    tabla_pct.plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
    ax.set_title("Distribución de método de pago por género")
    ax.set_ylabel("% de clientes")
    ax.legend(title="Método de pago", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig("grafico_genero_metodopago.png", dpi=150)
    plt.close(fig)

    return chi2, p_valor, cramers_v


# 5.c Correlación entre clientes que usan boletín y vale
def correlacion_boletin_vale(df: pd.DataFrame):
    """Evalúa la asociación entre uso de boletín y uso de vale (variables binarias)."""
    tabla = pd.crosstab(df["boletin"], df["vale"])
    chi2, p_valor, gl, _ = chi2_contingency(tabla)

    # Coeficiente Phi (caso especial de Cramér's V para tablas 2x2)
    n = tabla.values.sum()
    phi = np.sqrt(chi2 / n)

    print("\n--- 5.c Correlación Boletín vs Vale ---")
    print(tabla)
    print(f"Chi2: {chi2:.2f}, p-valor: {p_valor:.4f}, Coeficiente Phi: {phi:.3f}")

    return chi2, p_valor, phi


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

    # Punto 4
    segmentacion_por_edad(df)
    comparacion_por_genero(df)
    segmentacion_boletin_vale(df)

    # Punto 5
    correlacion_venta_edad(df)
    correlacion_genero_metodopago(df)
    correlacion_boletin_vale(df)


if __name__ == "__main__":
    main()