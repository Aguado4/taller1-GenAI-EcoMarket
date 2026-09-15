# Fase 2 — Evaluación de Fortalezas, Limitaciones y Riesgos Éticos

## Fortalezas

- **Preguntas repetitivas resueltas de forma eficiente.** Como se indicó
  en la introducción del caso, las preguntas repetitivas son las que más
  tiempo consumen hoy en EcoMarket. Estas se pueden guardar como
  respuestas predefinidas en una knowledge base, y darle al modelo una
  herramienta para elegir la respuesta correcta entre las ya existentes
  en vez de generarla desde cero. Esto ahorra tokens (ni siquiera hay que
  generar texto nuevo) y hace la respuesta más consistente.
- **Disponibilidad 24/7**, respondiendo todo el día y toda la noche sin
  depender de horarios de un equipo humano.

## Limitaciones

- Hay casos en los que los clientes quieren hablar con un humano, o
  tienen situaciones más complicadas que un modelo con información
  limitada y sin mucha complejidad no puede resolver bien.
- Esto se puede resolver dándole al modelo una **herramienta de
  escalamiento** que le pase el caso a un agente humano de EcoMarket
  cuando detecte que no puede o no debe responderlo solo.

## Riesgos éticos

- **Alucinaciones.** Sí puede tener, aunque es poco probable si se le dan
  al modelo *constraints* que lo obliguen a responder únicamente con base
  en la información entregada, ya sea vía RAG o con una knowledge base
  local (el mismo enfoque de contexto-en-el-prompt que se usa en la Fase 3
  de este repositorio).
- **Sesgo.** Puede tener sesgos que sean inherentes al modelo elegido
  (Gemini 2.5 Flash).
- **Privacidad de datos.** La información sensible se podría eliminar de
  los registros si se van a llevar logs, o directamente no guardar logs
  del contenido de las sesiones. En su lugar, registrar solo métricas que
  no hablen de datos personales, como satisfacción y latencia.
- **Impacto laboral.** El objetivo no sería reemplazar al equipo de
  servicio al cliente que ya existe, sino empoderarlo: aumentar su
  productividad para que puedan enfocarse en otras funciones y en trabajo
  más productivo (de desarrollo, por ejemplo) en vez de responder
  preguntas repetitivas. Al empoderar al equipo actual, se reduce la
  necesidad de reclutar más agentes de servicio al cliente.
