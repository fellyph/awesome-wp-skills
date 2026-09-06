# Awesome WordPress Agent Skills

[English](README.md) · [Español](README.es.md) · [Português do Brasil](README.pt-BR.md)

[![Validate repository](https://github.com/fellyph/awesome-wp-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/fellyph/awesome-wp-skills/actions/workflows/validate.yml)

Uma seleção de skills para agentes e integrações MCP para quem desenvolve com WordPress. Temas, plugins, blocos, acessibilidade, desempenho, design, testes e construtores de sites em um só lugar.

Um bom desenvolvimento com WordPress aproveita todo o ecossistema da web. Esta lista reúne tanto conhecimentos específicos de WordPress quanto ferramentas gerais com aplicação prática no WordPress.

## Conteúdo

- [Comece aqui](#comece-aqui)
- [Skills de WordPress](#skills-de-wordpress)
- [Skills de design e frontend](#skills-de-design-e-frontend)
- [Skills de acessibilidade, desempenho e qualidade](#skills-de-acessibilidade-desempenho-e-qualidade)
- [Skills de testes e segurança](#skills-de-testes-e-segurança)
- [Servidores e integrações MCP](#servidores-e-integrações-mcp)
- [Combinações sugeridas](#combinações-sugeridas)
- [Como contribuir](#como-contribuir)

## Comece aqui

Uma **skill para agentes** reúne instruções para uma tarefa em um arquivo `SKILL.md`, às vezes com scripts e referências. Um **servidor MCP** dá ao agente acesso a ferramentas ou dados externos. Eles se complementam: uma skill pode orientar uma revisão, enquanto um servidor MCP fornece medições do navegador ou acesso ao site. Consulte o [formato Agent Skills](https://agentskills.io/home) e a [introdução ao MCP](https://modelcontextprotocol.io/docs/getting-started/intro).

Este repositório é um diretório de links, não um pacote para instalar. Escolha as skills de que precisa nos projetos de origem e siga suas instruções de configuração. Por exemplo, com Node.js/npm disponível, a [Skills CLI](https://github.com/vercel-labs/skills) permite executar:

```sh
npx skills add WordPress/agent-skills --skill wp-block-themes
npx skills add addyosmani/web-quality-skills --skill accessibility
```

Para o Impeccable, siga o [guia de instalação](https://impeccable.style/). As integrações MCP têm requisitos próprios de autenticação, ambiente de execução e cliente; os comandos acima não as instalam.

**Critérios de seleção:** fontes primárias públicas, responsáveis identificáveis, funcionalidades documentadas e uma aplicação concreta no WordPress. A inclusão é uma recomendação editorial, não uma certificação nem um endosso do fornecedor. A documentação das fontes foi verificada em **5 de setembro de 2026**; as instalações e integrações em funcionamento não foram testadas. Consulte as [notas da pesquisa](SOURCES.md) para saber mais sobre o escopo, as migrações e as exclusões.

<!-- skills:start -->

## Skills de WordPress

Estas skills fazem parte da coleção [WordPress/agent-skills](https://github.com/WordPress/agent-skills), que continua sendo mantida. O antigo repositório [Automattic/agent-skills](https://github.com/Automattic/agent-skills) está arquivado e aponta para ela. Confira os requisitos de versão no projeto de origem antes de usar.

### Entendendo o projeto

- [wordpress-router](https://github.com/WordPress/agent-skills/blob/trunk/skills/wordpress-router/SKILL.md) — Identifica o tipo de projeto e direciona o trabalho para o fluxo de desenvolvimento WordPress adequado.
- [wp-project-triage](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-project-triage/SKILL.md) — Analisa a estrutura do repositório, as ferramentas, os testes e os indícios de versão antes de fazer alterações.

### Temas, blocos e interatividade

- [wp-block-themes](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-themes/SKILL.md) — Cria temas de blocos e resolve problemas com estilos globais, modelos e personalizações que se sobrepõem às configurações no Editor do site.
- [wp-block-development](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-development/SKILL.md) — Desenvolve blocos personalizados com registro, salvamento de conteúdo, renderização e processos de atualização confiáveis.
- [wp-patterns](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-patterns/SKILL.md) — Cria padrões de blocos reutilizáveis com predefinições do tema, marcação acessível e registro correto.
- [wp-interactivity-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-interactivity-api/SKILL.md) — Adiciona comportamento interativo aos blocos com diretivas, estado, ações e módulos de script do WordPress.

### Plugins e APIs

- [wp-plugin-development](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-plugin-development/SKILL.md) — Orienta a estrutura de plugins, configurações, tratamento de dados, verificações de segurança e preparação de versões.
- [wp-rest-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-rest-api/SKILL.md) — Projeta endpoints REST com esquemas, autorização, validação de entrada e respostas previsíveis.
- [wp-abilities-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-abilities-api/SKILL.md) — Registra habilidades do WordPress que podem ser descobertas e as conecta a clientes com as permissões adequadas.
- [wp-plugin-directory-guidelines](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-plugin-directory-guidelines/SKILL.md) — Revisa nomes, licenciamento, distribuição e monetização conforme as diretrizes do Diretório de plugins do WordPress.org.

### Operações e ambientes de desenvolvimento

- [wp-wpcli-and-ops](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-wpcli-and-ops/SKILL.md) — Cuida da administração e manutenção com WP-CLI, incluindo migrações e tarefas em redes multisite.
- [wp-phpstan](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-phpstan/SKILL.md) — Configura a análise estática de PHP para WordPress, os tipos do framework e as linhas de base para problemas já existentes no código.
- [wp-playground](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-playground/SKILL.md) — Seleciona fluxos de trabalho do Playground para execução local, prévias no navegador, snapshots e depuração.
- [blueprint](https://github.com/WordPress/agent-skills/blob/trunk/skills/blueprint/SKILL.md) — Cria e valida ambientes reproduzíveis do Playground com Blueprint JSON e recursos incluídos no pacote.

## Skills de design e frontend

- [Impeccable](https://github.com/pbakaus/impeccable) — **Paul Bakaus.** Skill de design e comandos para tipografia, layout, cores, movimento e textos de interface. Útil para temas, páginas de destino e telas de plugins. [Site](https://impeccable.style/).
- [wpds](https://github.com/WordPress/agent-skills/blob/trunk/skills/wpds/SKILL.md) — **WordPress.** Cria interfaces com componentes, tokens e padrões de interação do WordPress Design System.
- [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) — **Anthropic.** Cria layouts e componentes com identidade própria que podem orientar temas personalizados e seções de páginas.
- [Web Design Guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md) — **Vercel.** Revisa o código de interfaces quanto a formulários acessíveis, estados de foco, movimento, localização e detalhes de experiência do usuário.

## Skills de acessibilidade, desempenho e qualidade

As skills de qualidade web abaixo são mantidas por **Addy Osmani** como uma [coleção não oficial e independente de tecnologias](https://github.com/addyosmani/web-quality-skills), não como um produto do Google.

- [Accessibility](https://github.com/addyosmani/web-quality-skills/blob/main/skills/accessibility/SKILL.md) — Revisa a navegação por teclado, o HTML semântico, o contraste e o suporte a tecnologias assistivas nas páginas renderizadas e no código-fonte.
- [Performance](https://github.com/addyosmani/web-quality-skills/blob/main/skills/performance/SKILL.md) — Mede gargalos de carregamento e execução em recursos, renderização, JavaScript, fontes e cache.
- [Core Web Vitals](https://github.com/addyosmani/web-quality-skills/blob/main/skills/core-web-vitals/SKILL.md) — Investiga LCP, INP e CLS para identificar comportamentos de temas e plugins que prejudicam o desempenho do frontend.
- [Web Quality Audit](https://github.com/addyosmani/web-quality-skills/blob/main/skills/web-quality-audit/SKILL.md) — Coordena uma revisão mais ampla de desempenho, acessibilidade, SEO técnico e boas práticas para navegadores.
- [SEO](https://github.com/addyosmani/web-quality-skills/blob/main/skills/seo/SKILL.md) — Revisa as condições de rastreamento, os metadados, os títulos e os dados estruturados nas páginas que o site de fato renderiza.
- [Best Practices](https://github.com/addyosmani/web-quality-skills/blob/main/skills/best-practices/SKILL.md) — Verifica a compatibilidade com navegadores, erros de execução, dependências e fundamentos de segurança web.
- [wp-performance](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-performance/SKILL.md) — **WordPress.** Mede gargalos de backend em consultas, cache, tarefas agendadas e requisições remotas. Complementa as revisões de desempenho no navegador.
- [a11y-debugging](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/skills/a11y-debugging/SKILL.md) — **Chrome DevTools.** Audita e depura a acessibilidade usando a árvore de acessibilidade do DevTools, verificações do Lighthouse, rastreamento de foco e contraste de cores. Requer o Chrome DevTools MCP.

## Skills de testes e segurança

- [Web App Testing](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md) — **Anthropic.** Usa scripts Python com Playwright para testar interfaces locais, capturar telas e analisar registros do navegador.
- [Security Audit](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md) — **Cloudflare.** Coordena a análise de código e a validação independente dos resultados. Requer suporte a subagentes em paralelo e Node.js; complementa a revisão específica de WordPress.

<!-- skills:end -->

## Servidores e integrações MCP

Os itens abaixo dão acesso a ferramentas. Alguns são executados localmente, outros são plugins de WordPress e outros são serviços hospedados. Siga a documentação de cada um para conferir a configuração e os critérios atuais de acesso.

### WordPress e construtores de sites

| Integração | Responsável / tipo | Aplicação no WordPress e requisitos |
| --- | --- | --- |
| [WordPress MCP Adapter](https://github.com/WordPress/mcp-adapter) | WordPress · plugin/adaptador | Expõe habilidades registradas a clientes MCP. Requer WordPress 6.9+ e PHP 7.4+; as ações disponíveis dependem das habilidades expostas. |
| [WordPress.com MCP](https://wordpress.com/support/mcp/) | Automattic · serviço hospedado | Conecta assistentes ao conteúdo e às configurações do site. Requer um site elegível no WordPress.com ou conectado ao Jetpack e autenticação; há limites conforme o plano. |
| [Elementor MCP](https://github.com/elementor/elementor/tree/main/docs/atomic-builder/mcp) | Elementor · integração oficial · **beta** | Cria páginas nativas do Elementor e trabalha com as configurações de design do site. Anunciado com o [Elementor 4.3 beta](https://github.com/orgs/elementor/discussions/37152); requer configuração por um administrador, e os elementos Pro precisam do Pro. |
| [EMCP Tools](https://github.com/msrbuilds/elementor-mcp) | msrbuilds · plugin da comunidade | Adiciona ferramentas de estrutura, widgets e modelos do Elementor por meio do WordPress MCP Adapter. Requer WordPress 6.9+ e PHP 8.1+; é separado da integração oficial do Elementor. |

### Testes no navegador, depuração e contexto de design

| Integração | Responsável / tipo | Aplicação no WordPress e requisitos |
| --- | --- | --- |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Microsoft · servidor de navegador | Testa telas administrativas, formulários e comportamentos do frontend com automação de navegador. Snapshots de acessibilidade permitem a interação; não constituem uma auditoria completa de acessibilidade. |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Chrome DevTools · servidor de navegador | Registra rastros de desempenho e analisa requisições, a saída do console e páginas renderizadas. Requer uma versão compatível do Node.js e o Chrome. |
| [Context7](https://github.com/upstash/context7) | Upstash · servidor/serviço de documentação | Obtém documentação de bibliotecas para o trabalho com frontend e ferramentas. A cobertura varia por biblioteca; uma chave de API aumenta os limites de uso. |
| [Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server) | Figma · serviço de design | Fornece contexto de design para temas, blocos e layouts de construtores. O acesso remoto e pelo aplicativo desktop têm requisitos de licença por usuário e limites de uso diferentes. |

## Combinações sugeridas

Estas combinações são pontos de partida, não pacotes testados. Selecione as ferramentas conforme o trabalho.

| Objetivo | Experimente combinar |
| --- | --- |
| Criar um tema de blocos | wp-block-themes + wp-patterns + Impeccable + Accessibility |
| Desenvolver um plugin | wp-plugin-development + wp-rest-api + wp-phpstan + Web App Testing |
| Investigar um site lento | wp-performance + Core Web Vitals + Chrome DevTools MCP |
| Trabalhar com Elementor | Elementor MCP (beta) ou EMCP Tools + Accessibility + Performance |
| Criar uma demonstração reproduzível | wp-playground + blueprint + Playwright MCP |
| Implementar um design | Figma MCP + wpds ou Frontend Design + Web Design Guidelines |

## Como contribuir

Encontrou uma skill ou integração útil? Leia [CONTRIBUTING.md](CONTRIBUTING.md). Inclua a fonte primária, o responsável, a aplicação no WordPress e eventuais requisitos de versão beta, plano ou ambiente de execução. Mantenha as três versões de idioma alinhadas.

Esta coleção começou com o Impeccable, as skills para temas de blocos do WordPress e a skill de acessibilidade de Addy Osmani. Agradecemos às pessoas que mantêm esses recursos disponíveis.

## Licença

O texto original deste diretório está disponível sob a [Licença MIT](LICENSE). Os projetos vinculados mantêm suas próprias licenças.
