# Fase 3 — Aplicación de la Ingeniería de Prompts

Esta fase se entrega como código ejecutable (ver [README](../README.md) para
correrlo) más este documento, que resume el historial de versiones y los
hallazgos de probarlas. La evidencia completa de cada corrida está en
[`../outputs/`](../outputs).

## Historial de versiones

### Ejercicio 1 — Solicitud de pedido

| Versión | Qué agrega |
|---|---|
| v1 | El "prompt básico" literal del PDF ("Dame el estado del pedido {tracking_number}"), sin datos ni rol. |
| v2 | El "prompt mejorado" literal del PDF (rol + pide fecha, link y disculpa si hay retraso) + la base de datos de pedidos. |
| v3 | v2 + dos reglas de grounding: no inventar datos que no estén en el JSON, y no repetir nombres/valores técnicos del JSON tal cual (evita fugas como `en_transito` o `retrasado: true`). |
| v4 | v3 + few-shot con 4 casos sintéticos (en tránsito, entregado, retrasado, cancelado) + instrucción de no usar emojis. |
| v5 | Corrige una regresión encontrada en v4 (ver más abajo): agrega un 5º ejemplo few-shot que combina "entregado" y "retrasado" a la vez. |
| v6 | v5 + instrucción explícita de dirigirse al cliente por su nombre. |

### Ejercicio 2 — Devolución de producto

| Versión | Qué agrega |
|---|---|
| v1 | Línea base sin rol: se le pasan los datos del producto y se pregunta directamente si se puede devolver. |
| v2 | Rol de agente amable + instrucción basada en el desafío del PDF (distinguir perecederos/higiene, responder con empatía). |
| v3 | v2 + las mismas dos reglas de grounding que pedido/v3. |
| v4 | v3 + few-shot con un caso "sí se puede devolver" y uno "no se puede devolver" + sin emojis. |

La personalización por nombre de cliente **no aplica a este ejercicio**:
`data/productos.json` es un catálogo de productos, no tiene ningún dato
del cliente que hace la consulta, así que no hay nada que personalizar ahí.

## Comentario del último ejemplo: la regresión de v4 → v5

Al probar v4 contra un caso más complejo que los del enunciado —un pedido
que ya está **entregado** pero que además llegó **retrasado**
(`TRK-1010`: `estado: entregado`, `retrasado: true`, con
`motivo_retraso`)—, el modelo dejó de disculparse y de explicar el motivo
del retraso. Solo decía que el pedido ya había sido entregado, ignorando
por completo el retraso.

Esto incumple directamente un requisito explícito del enunciado ("si el
pedido está retrasado, ofrece una disculpa y una breve explicación").

La causa es un efecto secundario de los propios ejemplos few-shot de v4:
sus 4 ejemplos trataban "entregado" y "retrasado" como categorías
separadas y excluyentes (un ejemplo para cada estado, nunca los dos a la
vez), y el modelo generalizó mal a partir de ese patrón, asumiendo que si
el pedido ya se entregó, el retraso deja de ser relevante.

La corrección en v5 fue agregar un quinto ejemplo few-shot que combina
ambos estados explícitamente, mostrando que un pedido puede estar
entregado y retrasado al mismo tiempo, y que en ese caso también
corresponde disculparse. Al volver a probar `TRK-1010` con v5, la
respuesta sí incluye la disculpa y el motivo del retraso.

Esto es evidencia concreta de que el few-shot, si no cubre las
combinaciones reales de los datos (no solo los estados por separado, sino
también cómo se combinan), puede introducir regresiones en vez de solo
mejoras: el modelo no solo aprende el formato de los ejemplos, también
aprende (incorrectamente, en este caso) qué categorías son mutuamente
excluyentes.

## Conclusiones generales

Después de la v2, la calidad de las respuestas ya era bastante buena: el
"prompt mejorado" del propio enunciado, con solo agregarle la base de
datos, cumplía los tres requisitos explícitos del PDF (fecha estimada,
enlace de rastreo, disculpa si hay retraso) de forma consistente. Las
versiones siguientes (v3, v4, v5, v6) no cambiaron el comportamiento base,
sino que lo fueron refinando: primero cerrando fugas de información
interna y alucinaciones, luego con few-shot para forzar más consistencia
en el formato de salida, corrigiendo la regresión que ese mismo few-shot
introdujo, y por último agregando personalización con el nombre del
cliente.

Esto tiene una implicación práctica de costo: si el presupuesto de tokens
es muy ajustado, **v2 es una alternativa razonable**. Es mucho más simple
(sin few-shot, sin reglas adicionales) y ya cubre lo esencial que pide el
enunciado. Las versiones v3 en adelante consumen más tokens por
solicitud (el few-shot de v4/v5/v6 agrega varios ejemplos completos a
cada prompt) a cambio de mayor robustez frente a casos que un modelo sin
esas reglas explícitas no maneja igual de bien (fugas de datos internos,
alucinaciones, inconsistencia de tono). La elección entre usar v2 o v6 en
producción es, en el fondo, un trade-off entre costo/latencia y
robustez/consistencia.
