# Fase 1 — Selección y Justificación del Modelo de IA

## ¿Qué tipo de modelo es el más adecuado?

Un modelo de lenguaje grande (LLM) de propósito general, sin fine-tuning.

Un modelo fine-tuned sería overkill para este caso de uso: hoy en día los
LLMs de propósito general tienen APIs muy flexibles y relativamente
baratas, y permiten hacer *harnessing* (afinar el prompt y darle
herramientas para tomar decisiones), lo cual es mucho más sencillo que
hacer un fine-tune completo de un modelo.

## ¿Por qué este modelo y no otro?

Usar un LLM de propósito general con buen prompting en vez de fine-tuning
ayuda en varios frentes:

- **Costos:** se evita el costo y tiempo de entrenamiento.
- **Flexibilidad:** si en algún momento se quiere cambiar de modelo, o
  aparece un caso de uso nuevo, no hay que reentrenar nada, solo ajustar
  el prompt.

## Arquitectura propuesta

La arquitectura depende mucho del tamaño del catálogo de EcoMarket:

- Si el catálogo es pequeño, se puede construir una *knowledge base*
  directamente en el prompt (el mismo enfoque que se usa en el código de
  la Fase 3 de este repositorio, inyectando los datos de pedidos y
  productos como contexto).
- Si el catálogo crece, esa knowledge base tendría que moverse a un
  sistema de recuperación externo (RAG) en vez de vivir completa en el
  prompt.

### Modelo específico propuesto

**Gemini 2.5 Flash**, porque:

- Da respuestas relativamente buenas para casos de uso sencillos donde
  todas las respuestas deben salir de una knowledge base.
- Es bastante barato.
- Se puede integrar a través de proveedores como **OpenRouter** o
  **Vercel AI Gateway**, lo que permite cambiar de modelo cuando se
  quiera sin reescribir la integración.

## Justificación

Lo que este modelo haría bien es responder las preguntas repetitivas que,
según el enunciado del caso, son las que más tiempo consumen hoy en
EcoMarket. Esas preguntas se pueden guardar como respuestas predefinidas
en la knowledge base, y darle al modelo herramientas para buscar y elegir
la respuesta correcta en vez de generarla desde cero, lo cual ahorra
tokens y hace la respuesta más consistente.

En cuanto a costo, escalabilidad y facilidad de integración: no hay
entrenamiento, el modelo se puede cambiar de proveedor fácilmente, y el
enfoque de prompt + herramientas escala simplemente agregando más datos o
más herramientas, sin tocar el modelo en sí.
