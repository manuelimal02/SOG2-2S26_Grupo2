# Preparación de datos y Base de Datos

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# a. EXTRACCIÓN
def extraer_datos(ruta_csv: str) -> pd.DataFrame:
    #Lee el archivo .csv de Ventas Online 2021 y lo carga en un DataFrame de pandas.
    df = pd.read_csv(ruta_csv, sep=";")
    print(f"Se leyeron {df.shape[0]} filas y {df.shape[1]} columnas.")
    return df



# b. VERIFICACIÓN DE FALTANTES Y DUPLICADOS
def verificar_faltantes_y_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    # Verifica si hay valores nulos o filas duplicadas en el DataFrame.
    nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()
    print(f"Valores nulos totales: {nulos}")
    print(f"Filas duplicadas: {duplicados}")

    if nulos > 0:
        df = df.dropna()
        print("Se eliminaron filas con valores nulos.")

    if duplicados > 0:
        df = df.drop_duplicates()
        print("Se eliminaron filas duplicadas.")

    return df

# c. CORRECCIÓN DE TIPOS DE DATO
def corregir_tipos(df: pd.DataFrame) -> pd.DataFrame:
    # Corrige los tipos de dato según el csv.
    df["Id_cliente"] = df["Id_cliente"].astype(int)
    df["Edad"] = df["Edad"].astype(int)
    df["Genero"] = df["Genero"].astype(int)
    df["Venta_total"] = df["Venta_total"].astype(float)
    df["N_Compras"] = df["N_Compras"].astype(int)
    df["MontoCompra"] = df["MontoCompra"].astype(float)
    df["MetodoPago"] = df["MetodoPago"].astype(int)
    df["Tiempo"] = df["Tiempo"].astype(int)
    df["Navegador"] = df["Navegador"].astype(int)
    df["Boletin"] = df["Boletin"].astype(int)
    df["Vale"] = df["Vale"].astype(int)

    # FechaCompra viene como texto dd.mm.aa. Se convierte a datetime.
    df["FechaCompra"] = pd.to_datetime(df["FechaCompra"], format="%d.%m.%y")

    print("Tipos de dato corregidos según el enunciado:")
    print(df.dtypes)
    return df



# d. CARGA A LA BASE DE DATOS EN LA NUBE
def conectar_bd():
    # Conecta a la base de datos en Supabase.
    load_dotenv()
    conexion = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("Conexión a Supabase establecida.")
    return conexion


def cargar_datos(df: pd.DataFrame, conexion) -> None:
    # Carga los datos del DataFrame a la tabla 'ventas' en la base de datos.
    columnas = [
        "id_cliente", "edad", "genero", "venta_total", "n_compras",
        "fecha_compra", "monto_compra", "metodo_pago", "tiempo",
        "navegador", "boletin", "vale",
    ]

    registros = list(
        df[
            [
                "Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras",
                "FechaCompra", "MontoCompra", "MetodoPago", "Tiempo",
                "Navegador", "Boletin", "Vale",
            ]
        ].itertuples(index=False, name=None)
    )

    consulta = f"""
        INSERT INTO ventas ({", ".join(columnas)})
        VALUES %s
        ON CONFLICT (id_cliente) DO NOTHING
    """

    with conexion.cursor() as cursor:
        execute_values(cursor, consulta, registros)
    conexion.commit()
    print(f"Se insertaron (o ya existían) {len(registros)} registros en la tabla 'ventas'.")



# EJECUCIÓN DEL PROCESO ETL COMPLETO
def main():
    ruta_csv = "../Venta_online_c.csv"

    df = extraer_datos(ruta_csv)
    df = verificar_faltantes_y_duplicados(df)
    df = corregir_tipos(df)

    conexion = conectar_bd()
    try:
        cargar_datos(df, conexion)
    finally:
        conexion.close()
        print("Conexión cerrada.")


if __name__ == "__main__":
    main()