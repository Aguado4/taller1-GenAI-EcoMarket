"""Utilidades para cargar automáticamente la última versión de un prompt.

Convención de versionamiento:
    prompts/<ejercicio>/v1.toml
    prompts/<ejercicio>/v2.toml
    prompts/<ejercicio>/v3.toml   <- se detecta automáticamente al agregarlo

Para iterar un prompt, simplemente copia el archivo de la versión más alta,
súbele el número y edita su contenido. El código siempre usará la versión
con el número más alto salvo que se indique --version explícitamente.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
VERSION_PATTERN = re.compile(r"^v(\d+)\.toml$")


def list_versions(exercise: str) -> list[int]:
    """Devuelve las versiones disponibles (números) para un ejercicio, ordenadas."""
    exercise_dir = PROMPTS_DIR / exercise
    if not exercise_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta de prompts: {exercise_dir}")

    versions = []
    for file in exercise_dir.iterdir():
        match = VERSION_PATTERN.match(file.name)
        if match:
            versions.append(int(match.group(1)))
    if not versions:
        raise FileNotFoundError(f"No hay prompts versionados (vN.toml) en {exercise_dir}")
    return sorted(versions)


def latest_version(exercise: str) -> int:
    """Devuelve el número de versión más alto disponible para un ejercicio."""
    return list_versions(exercise)[-1]


def load_prompt(exercise: str, version: int | None = None) -> dict:
    """Carga el archivo TOML de un ejercicio.

    Si `version` es None, se usa automáticamente la versión más alta
    disponible (trazabilidad de mejoras sin tener que tocar código).
    """
    resolved_version = version if version is not None else latest_version(exercise)
    prompt_path = PROMPTS_DIR / exercise / f"v{resolved_version}.toml"

    if not prompt_path.exists():
        available = list_versions(exercise)
        raise FileNotFoundError(
            f"No existe {prompt_path}. Versiones disponibles para '{exercise}': {available}"
        )

    with prompt_path.open("rb") as f:
        data = tomllib.load(f)

    data["_resolved_version"] = resolved_version
    data["_source_file"] = str(prompt_path)
    return data
