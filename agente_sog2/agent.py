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

herramientas_analisis = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[os.path.abspath(RUTA_MCP_SERVER)],
        ),
        timeout=30,
    ),
)

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
3. Resume los resultados en 2-4 oraciones. Menciona un nombre de archivo
   de gráfico SOLO si la herramienta lo devolvió explícitamente en el
   campo "grafico" de su respuesta. Si la herramienta no devolvió ese
   campo, no existe ningún gráfico para esa consulta — no inventes un
   nombre de archivo bajo ninguna circunstancia.
4. Si la pregunta no corresponde a ningún análisis disponible, dilo con
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
    tools=[herramientas_analisis],
)