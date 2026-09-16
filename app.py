"""Punto de entrada para probar los prompts del Taller 1 (Fase 3).

Uso:
    python app.py pedido --tracking TRK-1003
    python app.py pedido --tracking TRK-1003 --version 1   # forzar versión anterior
    python app.py devolucion --producto "Champú sólido natural"

Por defecto, siempre se usa la ÚLTIMA versión disponible del prompt en
prompts/<ejercicio>/vN.toml (ver prompt_loader.py), lo que permite dejar
trazabilidad de cómo fue mejorando el prompt sin tener que tocar código:
solo agrega un nuevo archivo vN+1.toml.

Modelo: se usa Groq (API compatible con OpenAI) para correr un modelo
open-source (por defecto openai/gpt-oss-20b) de forma gratuita, tal como
sugiere el enunciado del taller.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from prompt_loader import list_versions, load_prompt

# La consola de Windows usa cp1252 por defecto y las respuestas del modelo
# contienen emojis, lo que haria fallar print() con UnicodeEncodeError.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Se aceptan ambas convenciones: .env.local (como en prompt-engineering-sample)
# y .env. La primera que defina una variable gana.
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def get_client() -> Groq:
    """Crea el cliente de Groq, con un mensaje claro si falta la API key."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit(
            "Falta GROQ_API_KEY.\n"
            "1. Crea una key gratis en https://console.groq.com/keys\n"
            "2. Copia .env.example a .env (o .env.local) y pega tu key."
        )
    return Groq(api_key=api_key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corre los prompts del Taller 1 - Fase 3")
    subparsers = parser.add_subparsers(dest="exercise", required=True)

    pedido_parser = subparsers.add_parser("pedido", help="Ejercicio 1: estado de pedido")
    pedido_parser.add_argument("--tracking", required=True, help="Número de seguimiento, ej. TRK-1001")
    pedido_parser.add_argument("--version", type=int, default=None, help="Forzar una versión específica del prompt")

    devolucion_parser = subparsers.add_parser("devolucion", help="Ejercicio 2: proceso de devolución")
    devolucion_parser.add_argument("--producto", required=True, help="Nombre del producto (busqueda parcial, sin importar tildes)")
    devolucion_parser.add_argument("--version", type=int, default=None, help="Forzar una versión específica del prompt")

    return parser.parse_args()


def _fill_template(template: str, **values: str) -> str:
    """Reemplaza placeholders {nombre} sin usar str.format, ya que los
    prompts contienen ejemplos con JSON literal (con llaves) que romperían
    str.format."""
    result = template
    for key, value in values.items():
        result = result.replace("{" + key + "}", value)
    return result


def _load_json(name: str) -> dict:
    with (DATA_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def run_pedido(tracking_number: str, version: int | None) -> None:
    prompt_data = load_prompt("pedido", version)
    pedidos = _load_json("pedidos.json")

    user_message = _fill_template(
        prompt_data["prompts"]["instruction_prompt"],
        tracking_number=tracking_number,
        pedidos_json=json.dumps(pedidos, ensure_ascii=False, indent=2),
    )
    _call_and_report("pedido", prompt_data, user_message, identifier=tracking_number)


def _normalize(text: str) -> str:
    """Minusculas y sin tildes, para poder buscar sin pelear con el teclado."""
    descompuesto = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def _find_producto(query: str, productos: dict) -> str:
    """Busca un producto por coincidencia parcial, ignorando tildes y mayusculas."""
    objetivo = _normalize(query)
    coincidencias = [nombre for nombre in productos if objetivo in _normalize(nombre)]

    if len(coincidencias) == 1:
        return coincidencias[0]

    disponibles = "\n  - ".join(productos)
    if not coincidencias:
        raise SystemExit(f"No encontre '{query}'. Productos disponibles:\n  - {disponibles}")
    opciones = "\n  - ".join(coincidencias)
    raise SystemExit(f"'{query}' es ambiguo. Coincide con:\n  - {opciones}")


def run_devolucion(producto: str, version: int | None) -> None:
    prompt_data = load_prompt("devolucion", version)
    productos = _load_json("productos.json")
    producto = _find_producto(producto, productos)

    user_message = _fill_template(
        prompt_data["prompts"]["instruction_prompt"],
        producto=producto,
        producto_json=json.dumps(productos[producto], ensure_ascii=False, indent=2),
    )
    _call_and_report("devolucion", prompt_data, user_message, identifier=producto)


def _call_and_report(exercise: str, prompt_data: dict, user_message: str, identifier: str) -> None:
    role_prompt = prompt_data["prompts"].get("role_prompt", "").strip()
    version = prompt_data["_resolved_version"]

    messages = []
    if role_prompt:
        messages.append({"role": "system", "content": role_prompt})
    messages.append({"role": "user", "content": user_message})

    print(f"--- Ejercicio: {exercise} | Prompt version: v{version} ({prompt_data['_source_file']}) ---")
    print(f"Versiones disponibles: {list_versions(exercise)}")
    print(f"Modelo: {DEFAULT_MODEL}\n")

    response = get_client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0.3,
    )
    output = response.choices[0].message.content

    print("=== Respuesta del modelo ===")
    print(output)

    OUTPUTS_DIR.mkdir(exist_ok=True)
    output_file = OUTPUTS_DIR / f"{exercise}_v{version}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{'=' * 60}\n[{timestamp}] {exercise} v{version} | consulta: {identifier}\n{'=' * 60}\n{output}\n\n"
    with output_file.open("a", encoding="utf-8") as f:
        f.write(entry)
    print(f"\n(Agregado a {output_file})")


def main() -> None:
    args = parse_args()
    if args.exercise == "pedido":
        run_pedido(args.tracking, args.version)
    elif args.exercise == "devolucion":
        run_devolucion(args.producto, args.version)


if __name__ == "__main__":
    main()
