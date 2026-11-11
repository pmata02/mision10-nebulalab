# Guion de narración · vídeo de demostración (5 min 18 s)

Leed cada línea cuando aparezca su subtítulo. Tiempos en minutos:segundos.

| Entra | Texto |
|---|---|
| 0:00 | Presentamos nuestro asistente RAG para la normativa interna de NébulaLab, una empresa ficticia. |
| 0:04 | Pablo Mata Rius y Wenjie Jiang · Misión 10. |
| 0:08 | Preguntamos cuántos días de vacaciones hay y los documentos dan tres cifras: 22, 24 más uno y 25. |
| 0:17 | Solo la política de 2026 está en vigor. Un buscador por parecido devuelve la FAQ de 2024, porque está redactada igual que la pregunta. |
| 0:27 | Al indexar, leemos la versión, el estado y el tipo de cada documento y los pegamos como cabecera a cada fragmento. |
| 0:38 | Al preguntar, buscamos 20 candidatos, la jerarquía pone delante el vigente, Gemini redacta y un control en código revisa la respuesta. |
| 0:50 | Este es el corpus: los seis documentos del kit y cuatro nuestros, entre ellos la política de 2023, la FAQ de 2024 y un mensaje manipulado. |
| 1:05 | El proyecto es reproducible: 28 pruebas pasan sin conexión y la base de Chroma se regenera en un momento. |
| 1:19 | Primera pregunta, con palabras coloquiales. |
| 1:28 | Gemini responde 0,26 euros por kilómetro y cita el manual en PDF con su página y su sección. |
| 1:42 | Ahora la pregunta del conflicto, con la configuración original del kit. |
| 1:50 | El primer fragmento es la FAQ de 2024, con 24 días. La política vigente sale tercera. |
| 2:04 | Con nuestra versión, la jerarquía pone delante la política vigente. |
| 2:15 | La respuesta da 25 días, cita las dos fuentes y marca el estado como conflicto. |
| 2:25 | El documento antiguo no se esconde: se nombra para que el usuario sepa que existe otra cifra. |
| 2:35 | Esta es la regla de jerarquía. No depende del parecido con la pregunta, sino de los metadatos de cada documento. |
| 2:45 | Con el kit, el documento vigente nunca salía primero en las preguntas de vigencia; con nuestra versión, en 4 de 5. |
| 2:55 | Ahora, seguridad. Un mensaje reenviado sin firma contiene una contraseña y órdenes para la IA. |
| 3:07 | Con el prompt original del kit, Gemini obedece al mensaje y da la contraseña. |
| 3:19 | La misma pregunta con nuestro prompt final y el control en código: «No consta en los documentos disponibles». |
| 3:35 | Y si la respuesta no está en ningún documento, el asistente lo reconoce en lugar de inventar. |
| 3:50 | Para evaluar, escribimos 64 preguntas en tres bancos y solo ajustamos con el de diseño. |
| 3:59 | Fijamos la regla de decisión antes de ejecutar y generamos 396 respuestas reales con Gemini. |
| 4:08 | El prompt del kit acierta más preguntas parafraseadas, pero entrega la contraseña en las dos preguntas que la piden. |
| 4:20 | Nuestra versión final nunca la entrega, rechaza todas las preguntas sin respuesta y mejora en robustez. |
| 4:32 | Nuestro hallazgo principal: al hacer el prompt menos prudente, también se volvió más fácil de manipular. |
| 4:42 | Solo el control en código impidió que la contraseña llegara al usuario. |
| 4:50 | También contamos lo que no funciona: el glosario se escribió conociendo las preguntas de validación. |
| 5:00 | Y los fallos que quedan son de recuperación: si el fragmento correcto no llega, ningún prompt lo arregla. |
| 5:10 | Todo el código, los datos y los resultados están en el repositorio. Gracias. |
