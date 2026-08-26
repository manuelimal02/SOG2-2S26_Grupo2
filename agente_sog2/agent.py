"""
Agente conversacional - Práctica 1 SOG2 (Persona 5)
----------------------------------------------------
Agente construido con Google ADK, conectado al modelo Gemini
(gemini-2.5-flash / gemini-2.5-flash-lite) y al MCPServer del proyecto
(mcp_server/server.py), que expone como herramientas los análisis de
los puntos 2 al 6 del enunciado (exploratorio, tendencias, segmentación
y correlación) ya definidos por Persona 2, 3 y 4 sobre la base de datos
de Persona 1 en Supabase.

Ejecución local para pruebas (desde la raíz del proyecto):
    adk web
o bien:
    adk run agente_sog2
"""

import os
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types
from mcp import StdioServerParameters

# El .env vive en la raíz del proyecto (mismo archivo que usa el MCPServer),
# con DATABASE_URL, GOOGLE_API_KEY y GOOGLE_GENAI_USE_VERTEXAI.
RUTA_ENV = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(RUTA_ENV, override=True)

# Ruta absoluta al server.py del MCPServer, para que ADK pueda lanzarlo
# como subproceso vía stdio sin importar desde dónde se ejecute `adk web`.
RUTA_MCP_SERVER = os.path.join(
    os.path.dirname(__file__), "..", "mcp_server", "server.py"
)
# Carpeta donde el MCPServer guarda los .png que genera (ver mcp_server/server.py).
CARPETA_GRAFICOS = os.path.join(
    os.path.dirname(__file__), "..", "mcp_server", "graficos"
)

herramientas_analisis = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[os.path.abspath(RUTA_MCP_SERVER)],
        ),
        timeout=30,
    ),
)


async def mostrar_grafico(nombre_archivo: str, tool_context: ToolContext) -> dict:
    """Muestra en el chat, como imagen, un gráfico que ya haya generado
    otra herramienta de análisis. Úsala INMEDIATAMENTE después de cualquier
    herramienta que haya devuelto un campo "grafico" en su resultado,
    pasándole solo el nombre del archivo (ej. "distribucion_mes.png"),
    para que el usuario lo vea directamente en el chat en vez de tener
    que buscarlo manualmente en la carpeta del proyecto.

    Args:
        nombre_archivo: nombre del archivo .png (sin ruta), tal como
            aparece al final del campo "grafico" que devolvió la otra tool.
    """
    nombre_archivo = os.path.basename(nombre_archivo)
    ruta = os.path.join(CARPETA_GRAFICOS, nombre_archivo)

    if not os.path.isfile(ruta):
        return {
            "mostrado": False,
            "error": f"No se encontró el archivo {nombre_archivo} en {CARPETA_GRAFICOS}.",
        }

    with open(ruta, "rb") as f:
        datos_png = f.read()

    await tool_context.save_artifact(
        filename=nombre_archivo,
        artifact=genai_types.Part(
            inline_data=genai_types.Blob(mime_type="image/png", data=datos_png)
        ),
    )
    return {"mostrado": True, "archivo": nombre_archivo}


INSTRUCCIONES = """
Eres el asistente de análisis de datos de una empresa que vende en línea
y también ahora en tienda física. Tu trabajo es responder, en español y
en lenguaje claro para un gerente no técnico, preguntas sobre:

- Estadísticas básicas de las ventas (punto 2).
- Tendencias de ventas por mes, navegador, método de pago, boletín y
  vale (punto 3).
- Segmentación de clientes por edad, género, boletín y vale (punto 4).
- Correlaciones entre venta/edad, género/método de pago y boletín/vale
  (punto 5).

Reglas:
1. Usa SIEMPRE las herramientas disponibles para obtener datos reales
   de la base de datos; nunca inventes cifras.
2. Si la pregunta puede resolverse con más de una herramienta, usa todas
   las que hagan falta antes de responder.
3. Si el resultado de una herramienta incluye un campo "grafico" (ej.
   "distribucion_mes.png"), DEBES llamar inmediatamente a la herramienta
   mostrar_grafico con ese nombre de archivo, ANTES de responder al
   usuario. Así el gráfico aparece directamente en el chat y el usuario
   no tiene que ir a buscarlo manualmente a ninguna carpeta.
4. Resume los resultados en 2-4 oraciones. Si ya mostraste el gráfico con
   mostrar_grafico, no repitas el nombre del archivo en el texto — solo
   describe lo que muestra. Si una herramienta no devolvió ningún campo
   "grafico", no inventes que existe un gráfico para esa consulta.
5. Si la pregunta no corresponde a ningún análisis disponible, dilo con
   claridad en vez de adivinar.
"""

root_agent = Agent(
    name="sog2_agente_analista",
    model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    description=(
        "Agente conversacional que responde consultas de análisis de ventas "
        "(exploratorio, tendencias, segmentación y correlación) para el "
        "informe de Sistemas Organizacionales y Gerenciales 2."
    ),
    instruction=INSTRUCCIONES,
    tools=[herramientas_analisis, mostrar_grafico],
)
