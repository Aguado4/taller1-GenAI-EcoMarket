# Taller 1 — EcoMarket: Optimización de Atención al Cliente con IA Generativa

Entrega completa del Taller Práctico #1 (ver [`Taller 1.pdf`](./Taller%201.pdf)),
estructurada en sus tres fases.

| Fase | Entregable |
|---|---|
| 1 — Selección y justificación del modelo | [`respuestas/fase1_seleccion_modelo.md`](./respuestas/fase1_seleccion_modelo.md) |
| 2 — Fortalezas, limitaciones y riesgos éticos | [`respuestas/fase2_fortalezas_riesgos.md`](./respuestas/fase2_fortalezas_riesgos.md) |
| 3 — Ingeniería de prompts | [`respuestas/fase3_ingenieria_prompts.md`](./respuestas/fase3_ingenieria_prompts.md) + código de este repositorio (`prompts/`, `app.py`) |

## Estructura del repositorio

```
taller 1 genAI/
├── Taller 1.pdf                          # Enunciado original
├── respuestas/
│   ├── fase1_seleccion_modelo.md         # Fase 1
│   ├── fase2_fortalezas_riesgos.md       # Fase 2
│   └── fase3_ingenieria_prompts.md       # Fase 3: historial de versiones + hallazgos
├── data/
│   ├── pedidos.json                      # "Base de datos" de prueba: 10 pedidos
│   └── productos.json                    # Catálogo con política de devolución por producto
├── prompts/
│   ├── pedido/                           # v1 (básico) ... v6 (grounding + few-shot + nombre del cliente)
│   └── devolucion/                       # v1 (básico) ... v4 (grounding + few-shot)
├── outputs/                              # Se genera al correr app.py (evidencia de las corridas, una por versión)
├── prompt_loader.py                      # Resuelve automáticamente la última versión del prompt
├── app.py                                # CLI de la Fase 3
├── requirements.txt
└── .env.example
```

## Fase 3 — Cómo ejecutarlo

### 1. Instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate          # Windows (en macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 2. Configurar la API key

Usamos [Groq](https://console.groq.com/keys) porque ofrece inferencia
gratuita y muy rápida de modelos **open-source**, tal como permite el
enunciado ("pueden usar un modelo open-source sin ningún problema, con el
fin de evidenciar el impacto de los prompts").

El modelo por defecto es **`openai/gpt-oss-20b`**, un modelo de pesos
abiertos bajo licencia Apache 2.0.

1. Crea una cuenta gratuita en https://console.groq.com/keys y genera una API key.
2. Copia `.env.example` a `.env` y pega tu key:

```bash
cp .env.example .env
```

```
GROQ_API_KEY="tu-api-key-de-groq"
GROQ_MODEL="openai/gpt-oss-20b"
```

> También se acepta un archivo `.env.local` (la convención del repositorio
> `prompt-engineering-sample` de Real Python en el que se basa este proyecto).
> Ambos archivos están en `.gitignore`, así que tu key nunca se sube al repo.

> Groq va retirando modelos antiguos. Si el modelo por defecto deja de
> existir (error `model_not_found`), lista los disponibles en tu cuenta con:
>
> ```bash
> python -c "import app; print(*sorted(m.id for m in app.get_client().models.list().data), sep='\n')"
> ```
>
> y cambia `GROQ_MODEL` por uno de esa lista.

### 3. Ejecutar los ejercicios

**Ejercicio 1 — Estado de pedido:**

```bash
python app.py pedido --tracking TRK-1003     # pedido retrasado
python app.py pedido --tracking TRK-1002     # pedido entregado
python app.py pedido --tracking TRK-7777     # no existe: prueba anti-alucinación
```

**Ejercicio 2 — Devolución de producto:**

```bash
python app.py devolucion --producto "mochila"     # sí se puede devolver
python app.py devolucion --producto "champu"      # higiene: no se puede
python app.py devolucion --producto "snack"       # perecedero: no se puede
```

La búsqueda de producto es parcial y no distingue tildes ni mayúsculas, así
que `champu` encuentra "Champú sólido natural". Si el texto es ambiguo o no
existe, el programa lista las opciones disponibles.

**Comparar versiones de un prompt:**

```bash
python app.py pedido --tracking TRK-1003 --version 1    # línea base
python app.py pedido --tracking TRK-1003 --version 2    # mejorado
```

Sin `--version`, siempre se usa la versión más alta disponible. Cada corrida
se agrega (append) a `outputs/<ejercicio>_v<version>.txt`, con un
separador y timestamp por corrida — un solo archivo por versión que
acumula todas las pruebas hechas contra esa versión.

## Versionamiento y trazabilidad de prompts

Cada ejercicio tiene su carpeta en `prompts/` con archivos `v1.toml`,
`v2.toml`, `v3.toml`… `prompt_loader.py` escanea la carpeta y **usa
automáticamente el número más alto**, salvo que se fuerce otro con
`--version`.

Para iterar un prompt sin perder el historial:

1. Copia el archivo de la versión más reciente (`v2.toml` → `v3.toml`).
2. Edita `v3.toml` con tu mejora.
3. Documenta en su bloque `[meta]` qué técnica aplicaste y por qué.
4. Corre `python app.py <ejercicio> ...` — usará `v3` automáticamente.

No hay que tocar `app.py` para agregar una versión. Como el relleno de
plantillas solo sustituye los placeholders que el archivo realmente
contiene, una versión puede omitir `{pedidos_json}` (como hace `pedido/v1`)
para servir de línea base sin contexto.

## Técnicas de prompt engineering aplicadas

Ver [`respuestas/fase3_ingenieria_prompts.md`](./respuestas/fase3_ingenieria_prompts.md)
para el historial completo de versiones y los hallazgos de cada una
(incluida una regresión real detectada y corregida en `pedido`). Como
referencia general, `prompt-engineering-sample/README.md` (carpeta
hermana a este repo) tiene más ejemplos de role prompting, delimitadores,
few-shot, chain-of-thought y salida estructurada.

La estructura del proyecto (prompts en archivos de configuración separados
del código, y las técnicas de few-shot, delimitadores y chain-of-thought)
está inspirada en el tutorial de Real Python
[Practical Prompt Engineering](https://realpython.com/practical-prompt-engineering/).
