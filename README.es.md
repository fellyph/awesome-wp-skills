# Awesome WordPress Agent Skills

[English](README.md) · [Español](README.es.md) · [Português do Brasil](README.pt-BR.md)

[![Validate repository](https://github.com/fellyph/awesome-wp-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/fellyph/awesome-wp-skills/actions/workflows/validate.yml)

Una selección de habilidades para agentes e integraciones MCP para quienes desarrollan con WordPress. Temas, plugins, bloques, accesibilidad, rendimiento, diseño, pruebas y constructores de sitios, reunidos en un solo lugar.

El buen desarrollo con WordPress también se nutre del ecosistema web. Esta lista incluye tanto conocimientos específicos de WordPress como herramientas generales con una aplicación práctica en WordPress.

## Contenido

- [Empieza aquí](#empieza-aquí)
- [Habilidades de WordPress](#habilidades-de-wordpress)
- [Habilidades de diseño y frontend](#habilidades-de-diseño-y-frontend)
- [Habilidades de accesibilidad, rendimiento y calidad](#habilidades-de-accesibilidad-rendimiento-y-calidad)
- [Habilidades de pruebas y seguridad](#habilidades-de-pruebas-y-seguridad)
- [Servidores e integraciones MCP](#servidores-e-integraciones-mcp)
- [Combinaciones sugeridas](#combinaciones-sugeridas)
- [Cómo contribuir](#cómo-contribuir)

## Empieza aquí

Una **habilidad para agentes** reúne instrucciones para realizar tareas en un archivo `SKILL.md`, a veces acompañado de scripts y referencias. Un **servidor MCP** permite que un agente acceda a herramientas o datos externos. Se complementan: una habilidad puede orientar una revisión, mientras que un servidor MCP proporciona mediciones del navegador o acceso al sitio. Consulta el [formato Agent Skills](https://agentskills.io/home) y la [introducción a MCP](https://modelcontextprotocol.io/docs/getting-started/intro).

Este repositorio es un directorio de enlaces, no un paquete para instalar. Elige las habilidades que necesites y sigue las instrucciones de sus proyectos de origen. Por ejemplo, si tienes Node.js/npm, la [CLI de Skills](https://github.com/vercel-labs/skills) permite ejecutar:

```sh
npx skills add WordPress/agent-skills --skill wp-block-themes
npx skills add addyosmani/web-quality-skills --skill accessibility
```

Para Impeccable, sigue su [guía de instalación](https://impeccable.style/). Las integraciones MCP tienen sus propios requisitos de autenticación, entorno de ejecución y cliente; los comandos anteriores no las instalan.

**Selección:** fuentes primarias públicas, responsables identificables, funcionalidad documentada y un caso de uso concreto en WordPress. La inclusión es una recomendación editorial, no una certificación ni un respaldo de los proveedores. La documentación de las fuentes se comprobó el **5 de septiembre de 2026**; no se probaron las instalaciones ni las integraciones en funcionamiento. Consulta las [notas de investigación](SOURCES.md) para conocer el alcance, las migraciones y las exclusiones.

<!-- skills:start -->

## Habilidades de WordPress

Estas habilidades proceden de la colección [WordPress/agent-skills](https://github.com/WordPress/agent-skills), que sigue recibiendo mantenimiento. El antiguo repositorio [Automattic/agent-skills](https://github.com/Automattic/agent-skills) está archivado y remite a ella. Comprueba los requisitos de versión del proyecto de origen antes de utilizarlas.

### Orientación del proyecto

- [wordpress-router](https://github.com/WordPress/agent-skills/blob/trunk/skills/wordpress-router/SKILL.md) — Identifica el tipo de proyecto y dirige el trabajo al flujo de WordPress adecuado.
- [wp-project-triage](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-project-triage/SKILL.md) — Examina la estructura del repositorio, las herramientas, las pruebas y los indicios de versiones antes de realizar cambios.

### Temas, bloques e interactividad

- [wp-block-themes](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-themes/SKILL.md) — Crea temas de bloques y resuelve problemas con estilos globales, plantillas y modificaciones del editor del sitio.
- [wp-block-development](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-development/SKILL.md) — Desarrolla bloques personalizados con registro, contenido guardado, renderizado y procesos de actualización fiables.
- [wp-patterns](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-patterns/SKILL.md) — Crea patrones de bloques reutilizables con ajustes preestablecidos del tema, marcado accesible y un registro correcto.
- [wp-interactivity-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-interactivity-api/SKILL.md) — Añade comportamiento interactivo a los bloques mediante directivas, estado, acciones y módulos de scripts de WordPress.

### Plugins y API

- [wp-plugin-development](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-plugin-development/SKILL.md) — Orienta la estructura de plugins, sus ajustes, el tratamiento de datos, las comprobaciones de seguridad y la preparación de versiones.
- [wp-rest-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-rest-api/SKILL.md) — Diseña endpoints REST con esquemas, autorización, validación de entradas y respuestas predecibles.
- [wp-abilities-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-abilities-api/SKILL.md) — Registra habilidades de WordPress que los clientes pueden descubrir y utilizar con los permisos adecuados.
- [wp-plugin-directory-guidelines](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-plugin-directory-guidelines/SKILL.md) — Revisa nombres, licencias, distribución y monetización según las directrices del directorio de plugins de WordPress.org.

### Operaciones y entornos de desarrollo

- [wp-wpcli-and-ops](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-wpcli-and-ops/SKILL.md) — Gestiona tareas de administración y mantenimiento mediante WP-CLI, incluidas migraciones y operaciones multisitio.
- [wp-phpstan](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-phpstan/SKILL.md) — Configura el análisis estático de PHP para WordPress, los tipos del framework y las líneas base para código existente.
- [wp-playground](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-playground/SKILL.md) — Selecciona flujos de Playground para ejecución local, vistas previas en el navegador, instantáneas y depuración.
- [blueprint](https://github.com/WordPress/agent-skills/blob/trunk/skills/blueprint/SKILL.md) — Crea y valida entornos reproducibles de Playground mediante Blueprint JSON y recursos incluidos.

## Habilidades de diseño y frontend

- [Impeccable](https://github.com/pbakaus/impeccable) — **Paul Bakaus.** Habilidad y comandos de diseño para tipografía, composición, color, movimiento y textos de interfaz. Útil para temas, páginas de destino y pantallas de plugins. [Sitio web](https://impeccable.style/).
- [wpds](https://github.com/WordPress/agent-skills/blob/trunk/skills/wpds/SKILL.md) — **WordPress.** Crea interfaces con componentes, tokens y patrones de interacción del sistema de diseño de WordPress.
- [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) — **Anthropic.** Crea composiciones y componentes con identidad propia que pueden servir de base para temas personalizados y secciones de páginas.
- [Web Design Guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md) — **Vercel.** Revisa el código de interfaces para mejorar formularios accesibles, estados de foco, movimiento, localización y detalles de experiencia de usuario.

## Habilidades de accesibilidad, rendimiento y calidad

Las siguientes habilidades de calidad web son mantenidas por **Addy Osmani** como una [colección no oficial e independiente de la tecnología utilizada](https://github.com/addyosmani/web-quality-skills), no como un producto de Google.

- [Accessibility](https://github.com/addyosmani/web-quality-skills/blob/main/skills/accessibility/SKILL.md) — Revisa la navegación con teclado, el HTML semántico, el contraste y la compatibilidad con tecnologías de asistencia en las páginas renderizadas y el código fuente.
- [Performance](https://github.com/addyosmani/web-quality-skills/blob/main/skills/performance/SKILL.md) — Mide los cuellos de botella de carga y ejecución en recursos, renderizado, JavaScript, fuentes y caché.
- [Core Web Vitals](https://github.com/addyosmani/web-quality-skills/blob/main/skills/core-web-vitals/SKILL.md) — Investiga LCP, INP y CLS para detectar comportamientos de temas y plugins que perjudican el rendimiento del frontend.
- [Web Quality Audit](https://github.com/addyosmani/web-quality-skills/blob/main/skills/web-quality-audit/SKILL.md) — Coordina una revisión más amplia del rendimiento, la accesibilidad, el SEO técnico y las buenas prácticas del navegador.
- [SEO](https://github.com/addyosmani/web-quality-skills/blob/main/skills/seo/SKILL.md) — Revisa la capacidad de rastreo, los metadatos, los encabezados y los datos estructurados de las páginas que el sitio realmente renderiza.
- [Best Practices](https://github.com/addyosmani/web-quality-skills/blob/main/skills/best-practices/SKILL.md) — Comprueba la compatibilidad entre navegadores, los errores de ejecución, las dependencias y los fundamentos de seguridad web.
- [wp-performance](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-performance/SKILL.md) — **WordPress.** Mide los cuellos de botella del backend en consultas, caché, tareas programadas y peticiones remotas. Complementa las revisiones de rendimiento en el navegador.
- [a11y-debugging](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/skills/a11y-debugging/SKILL.md) — **Chrome DevTools.** Audita y depura la accesibilidad mediante el árbol de accesibilidad de DevTools, verificaciones de Lighthouse, seguimiento del foco y contraste de color. Requiere Chrome DevTools MCP.

## Habilidades de pruebas y seguridad

- [Web App Testing](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md) — **Anthropic.** Utiliza scripts de Playwright en Python para probar interfaces locales, capturar pantallas e inspeccionar los registros del navegador.
- [Security Audit](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md) — **Cloudflare.** Coordina el análisis de código y la validación independiente de los hallazgos. Requiere soporte para subagentes en paralelo y Node.js; complementa la revisión específica de WordPress.

<!-- skills:end -->

## Servidores e integraciones MCP

Estas herramientas proporcionan acceso a funciones externas. Algunas se ejecutan localmente, otras son plugins de WordPress y otras son servicios alojados. Sigue la documentación enlazada para conocer la configuración y las condiciones de acceso actuales.

### WordPress y constructores de sitios

| Integración | Responsable / tipo | Caso de uso en WordPress y requisitos |
| --- | --- | --- |
| [WordPress MCP Adapter](https://github.com/WordPress/mcp-adapter) | WordPress · plugin/adaptador | Expone habilidades registradas a clientes MCP. Requiere WordPress 6.9+ y PHP 7.4+; las acciones disponibles dependen de las habilidades expuestas. |
| [WordPress.com MCP](https://wordpress.com/support/mcp/) | Automattic · servicio alojado | Conecta asistentes con el contenido y los ajustes del sitio. Requiere autenticación y un sitio de WordPress.com o conectado mediante Jetpack que cumpla los requisitos; se aplican límites según el plan. |
| [Elementor MCP](https://github.com/elementor/elementor/tree/main/docs/atomic-builder/mcp) | Elementor · integración oficial · **beta** | Crea páginas nativas de Elementor y trabaja con los ajustes de diseño del sitio. Anunciado con [Elementor 4.3 beta](https://github.com/orgs/elementor/discussions/37152); requiere configuración por parte de un administrador y los elementos Pro necesitan Pro. |
| [EMCP Tools](https://github.com/msrbuilds/elementor-mcp) | msrbuilds · plugin comunitario | Añade herramientas de estructura, widgets y plantillas de Elementor mediante WordPress MCP Adapter. Requiere WordPress 6.9+ y PHP 8.1+; es independiente de la integración oficial de Elementor. |

### Pruebas en el navegador, depuración y contexto de diseño

| Integración | Responsable / tipo | Caso de uso en WordPress y requisitos |
| --- | --- | --- |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Microsoft · servidor de navegador | Prueba pantallas de administración, formularios y comportamiento del frontend mediante automatización del navegador. Las instantáneas de accesibilidad permiten interactuar; no constituyen una auditoría completa de accesibilidad. |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Chrome DevTools · servidor de navegador | Registra trazas de rendimiento e inspecciona peticiones, mensajes de consola y páginas renderizadas. Requiere una versión compatible de Node.js y Chrome. |
| [Context7](https://github.com/upstash/context7) | Upstash · servidor/servicio de documentación | Recupera documentación de bibliotecas para trabajos de frontend y herramientas de desarrollo. La cobertura varía según la biblioteca; una clave de API amplía los límites de uso. |
| [Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server) | Figma · servicio de diseño | Proporciona contexto de diseño para temas, bloques y composiciones de constructores de sitios. Los accesos remoto y de escritorio tienen distintos requisitos de licencia de usuario y límites de uso. |

## Combinaciones sugeridas

Son puntos de partida, no paquetes probados. Selecciona las herramientas según el trabajo que vayas a realizar.

| Objetivo | Prueba esta combinación |
| --- | --- |
| Crear un tema de bloques | wp-block-themes + wp-patterns + Impeccable + Accessibility |
| Desarrollar un plugin | wp-plugin-development + wp-rest-api + wp-phpstan + Web App Testing |
| Investigar un sitio lento | wp-performance + Core Web Vitals + Chrome DevTools MCP |
| Trabajar con Elementor | Elementor MCP (beta) o EMCP Tools + Accessibility + Performance |
| Crear una demo reproducible | wp-playground + blueprint + Playwright MCP |
| Implementar un diseño | Figma MCP + wpds o Frontend Design + Web Design Guidelines |

## Cómo contribuir

¿Has encontrado una habilidad o integración útil? Lee [CONTRIBUTING.md](CONTRIBUTING.md). Incluye su fuente primaria, responsable, caso de uso en WordPress y cualquier requisito de versión beta, plan o entorno de ejecución. Mantén alineadas las tres ediciones de idiomas.

Esta colección comenzó con Impeccable, las habilidades de temas de bloques de WordPress y la habilidad de accesibilidad de Addy Osmani. Gracias a quienes mantienen estos recursos y los ponen a disposición de la comunidad.

## Licencia

El texto original de este directorio está disponible bajo la [licencia MIT](LICENSE). Los proyectos enlazados conservan sus propias licencias.
