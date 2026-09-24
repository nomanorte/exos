# Contribuir a EXOS

Gracias por querer mejorar EXOS. Cualquier persona puede abrir un Issue o un Pull Request;
esta guía te ahorra ida y vuelta.

## Qué se acepta

- **Errores reproducibles**: algo que no funciona como dice la documentación.
- **Mejoras a la documentación**: explicaciones que confundían, pasos que faltaban.
- **Mejoras pequeñas y acotadas** a los guardianes, scripts o instrucciones.
- **Propuestas grandes**: primero un Issue (ver abajo), nunca un PR sorpresa.

## Qué no entra

- Datos personales, secretos, historiales de alumnos o contenido de programas privados.
- Cambios que dependan de un proveedor concreto sin dejarlo como adaptador opcional.
- Reglas del sistema modificadas sin explicar el contexto, la consecuencia y la recomendación
  (`exos/CONGELADO.md` protege esas zonas).

## Cómo proponerlo

1. **Busca antes** si ya existe un Issue o un PR equivalente.
2. **Abre un Issue** que cuente el problema y el resultado que esperas. Para un cambio grande,
   espera a que el mantenedor confirme que encaja antes de escribir código.
3. **Trabaja en una rama o fork** y abre un PR hacia `main`. Explica qué cambia, por qué, cómo lo
   comprobaste y si toca datos, instrucciones o compatibilidad. Mantén los cambios acotados: un
   PR, una idea.
4. **Enciende los guardianes** en tu copia con `bash exos/scripts/bootstrap.sh`: paran un
   guardado que rompe las reglas y te dicen por qué. La CI vuelve a ejecutarlos en el PR, pero
   no sustituye la revisión humana.

## Qué pasa después

Cada contribución se lee y se responde. Si entra, **se publica en la siguiente release**, no en
el momento: EXOS se actualiza solo por versiones oficiales, que reúnen una tanda de cambios
probados en conjunto (excepto un fallo de seguridad, que sale como parche). Un Issue o un PR no
garantiza incorporación ni fecha; la publicación de una versión es decisión del mantenedor.
Quien contribuye aparece en el historial del repositorio y se le menciona en las notas de la
release donde entra su cambio.

## Trato y seguridad

Al participar aceptas el [Código de conducta](CODE_OF_CONDUCT.md). Para una vulnerabilidad o una
filtración, sigue [SECURITY.md](SECURITY.md): **no** uses un Issue público.
