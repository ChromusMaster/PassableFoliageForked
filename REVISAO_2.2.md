# Revisão 2.2 — Passable Foliage Forked

Data: 09/10/2026. Base: ZIP enviado pelo usuário, branch 26.3, mod 2.1.
A versão dos novos fontes é 2.2 para distinguir esta revisão dos JARs anteriores.

## Resultado e limites

**Os fontes dos quatro alvos passaram em compilação Java direta com JDK 25,
`--release 25 -Xlint:all -Werror`, sem diagnósticos.** Foram utilizados os JARs
reais de Minecraft, Fabric API/Loader e NeoForge/FML, sem stubs de APIs.
A validação foi parcial: não houve empacotamento final nem inicialização do jogo.

| Verificação | Fabric 26.2 | Fabric 26.3 | NeoForge 26.2 | NeoForge 26.3 beta |
|---|---|---|---|---|
| Java direto, fontes + testes | Passou | Passou | Passou | Passou |
| 16 assinaturas de injeção contra Minecraft vanilla | Passou | Passou | Passou | Passou |
| Regressões do contador por thread | Passou | Passou | Passou | Passou |
| processResources / buildInfo via Gradle | Não executado: Loom bloqueado | Não executado: Loom bloqueado | Passou | Passou |
| Build Gradle completo / JAR instalável | Não validado | Não validado | Não validado | Não validado |
| Teste dentro do Minecraft | Não executado | Não executado | Não executado | Não executado |

Os nove testes Python do controlador e dos recursos também passaram. Incluem
reprovação quando o processo retorna sucesso mas emite warning, preservação de
código de erro, exclusão de beta por padrão, ausência de JARs declarados em
validação parcial e equivalência das condições de dados entre loaders.

O teste de assinatura usa bytecode real, sem carregar classes do jogo. Ele
**não aplica os Mixins** nem cobre transformações feitas por NeoForge ou outros
mods. A compilação NeoForge direta usou Minecraft vanilla + APIs do loader;
a geração e compilação contra o Minecraft *patchado* permanecem pendentes.

## Bloqueios encontrados neste ambiente

- Fabric/Loom 1.17.19: `CurrentPlatform.isUnixDomainSocketsSupported` falhou com
  `SocketException: Operation not permitted`, durante a configuração do plugin.
  A falha ocorreu antes da compilação do mod. A tentativa registrada foi Fabric
  26.3; o mesmo bloqueio de inicialização impede validar o pipeline 26.2 aqui.
- NeoForge/NeoForm Runtime 2.0.31: preparação do Minecraft 26.2 terminou com
  `NoSuchElementException` em `NeoFormEngine`, linha 120. O código dessa linha
  usa `ProcessHandle.current().info().command().orElseThrow()`; a informação do
  executável não foi disponibilizada neste ambiente. Não houve erro Java do mod
  nessa etapa. Não foi repetido o mesmo pipeline completo para o alvo beta.

Não houve alteração de dependências para contornar essas restrições, remoção de
warnings ou uso de classes falsas para produzir uma aprovação artificial.
Os logs de falha e os logs das verificações aprovadas acompanham os fontes.

## Organização do build

Antes: projeto único Fabric 26.3, `build/libs`, versão 2.1, nomes de JAR sem
Minecraft/loader e `-Xlint:-processing`; sem `-Werror`. O histórico Git continha
26.2 com APIs diferentes, mas a árvore ativa não compilava ambas as versões.

Agora: `build/<Modloader>/<MinecraftVersion>/<ModVersion>/`. O JAR e o JAR de
fontes ficam diretamente na pasta da versão. Classes, recursos, temporários,
relatórios e logs ficam abaixo dela. O script fornece `--project-cache-dir`
antes da inicialização de Gradle para isolar o cache local de cada alvo.
Os caches globais de downloads e ferramentas continuam compartilhados no
`GRADLE_USER_HOME`; não são copiados ao pacote de fontes.

O script executa os alvos sequencialmente, usa no máximo dois workers Gradle,
heap Gradle de até 2 GiB e evita paralelismo entre projetos. Isso limita o build;
não é uma promessa de consumo total máximo de 2 GiB, pois ferramentas-filhas
podem criar outros processos. Não impõe limite de recursos ao Minecraft.

O modo completo registra hashes SHA-256, duração, código de saída, comando,
versões e todos os warnings detectados. `clean` preserva logs, cache local e
mundos de desenvolvimento do alvo. Outros alvos não são apagados.

## Correções e justificativas

1. **Assinatura de Mixin incorreta em 26.2.** `isViewBlocking` em 26.2 recebe
   `BlockGetter, BlockPos`; em 26.3 recebe também `AABB`. O adaptador agora é
   específico por versão em `src/version`. Esse erro não aparece no javac porque
   o alvo está declarado em uma anotação; foi detectado na inspeção de bytecode.
2. **playerOnly inconsistente.** Mobs podiam receber efeitos da folhagem e
   considerar folhas um caminho aberto mesmo quando sua colisão era sólida.
   Efeitos e alteração de pathfinding agora respeitam essa opção. Consultas
   auxiliares de headHitter também são dispensadas para esses mobs.
3. **Multiplicador de dano invertido.** O código usava `1 - fallDamageMultiplier`,
   contrário ao texto da configuração. Agora usa o próprio multiplicador:
   0 significa nenhum dano e 1 significa o dano calculado sem essa redução.
   O limite/threshold existente foi preservado; a física de queda não foi refeita.
4. **Alocações no caminho de colisão.** O ThreadLocal removia e recriava o array
   contador ao encerrar cada escopo. Agora reutiliza um pequeno contador por
   thread, sem referências a mundo ou entidades. Verifica overflow/underflow e
   mantém o `try/finally`. Blocos não passáveis retornam antes de acessar o contador.
5. **Consultas de renderização desnecessárias.** Entidades sem name tag não
   consultam blocos para decidir se o nome deve ser ocultado. Um fluxo vazio de
   estados não é mais interpretado como entidade totalmente dentro de folhas.
6. **Sons redundantes.** A marcação já existente de entidade dentro da folhagem
   impede repetir sons para vários blocos no mesmo tick. Volume zero dispensa
   o cálculo/emissão. Verificação de encantamento também é dispensada depois
   de os efeitos daquele tick já terem sido aplicados.
7. **Pathfinding frágil.** Removida a dependência de captura de variáveis locais
   `CAPTURE_FAILSOFT`, que poderia deixar a correção falhar apenas com warning.
   O hook usa parâmetros estáveis do método e continua com `defaultRequire: 1`.
8. **Cache de colisão inadequado.** Removido o Mixin que alterava o cache apenas
   em seu construtor, antes de as tags normalmente estarem carregadas, sem
   acompanhar recargas. As verificações dinâmicas permanecem nos métodos de
   estado; a flag compartilhada do bloco é `volatile` para visibilidade entre threads.
9. **Migração YAML.** Um booleano inválido em uma propriedade não cancela mais
   toda a migração: é tratado como os valores numéricos inválidos, com aviso,
   mantendo o valor padrão daquela propriedade e preservando os demais valores.
10. **Avisos de classpath.** Anotações JetBrains e Error Prone foram declaradas
    como dependências apenas de compilação. Os warnings de classes externas não
    foram desativados; `-Xlint:all -Werror` permanece ativo.
11. **Recursos por loader/versão.** Fabric e NeoForge têm metadados e condições
    próprias para encantamento, receita e advancement. `pack.mcmeta` cobre os
    formatos reais de recursos e dados informados por cada `version.json` do jogo:
    88.0–107.1 em 26.2 e 97.1–121.0 em 26.3. A compatibilidade declarada não se
    estende a outras versões de Minecraft.
12. **Portabilidade e CI.** Launcher Unix com LF, regras de finais de linha,
    matriz de CI, logs e artifacts. O workflow antigo executava `publish` sem
    repositório de publicação configurado; agora produz artifacts de release
    revisáveis, sem simular uma publicação em GitHub Packages.

Não houve benchmark dentro do jogo. As reduções descritas são de trabalho e
alocações identificáveis no código, sem percentuais prometidos. Não foi alterado
shader nem pipeline de GPU; não há redução de GPU medida ou garantida.

## NeoForge

Foram adicionados entrypoint `@Mod`, registro via `DeferredRegister`, atualização
de tags respeitando `shouldUpdateStaticData()` e condições `ICondition` nativas.
Não existe dependência Fabric no código compartilhado ou no alvo NeoForge.
A configuração JSON existente é mantida; o loader fornece o diretório correto.

Versões fixadas a partir do repositório oficial, consultado em 09/10/2026:

| Alvo | Loader | Situação |
|---|---|---|
| Fabric 26.2 | Loader 0.19.5 / API 0.158.0+26.2 | Incluído no padrão |
| Fabric 26.3 | Loader 0.19.5 / API 0.161.0+26.3 | Incluído no padrão |
| NeoForge 26.2 | 26.2.0.88 | Release estável; incluído no padrão |
| NeoForge 26.3 | 26.3.0.58-beta | Experimental; requer opt-in |

“Release estável” descreve a classificação do loader, não certifica este port.

Fontes consultadas:
- https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml
- https://github.com/NeoForgeMDKs/MDK-26.2-ModDevGradle
- https://github.com/NeoForgeMDKs/MDK-26.3-ModDevGradle
- https://docs.neoforged.net/docs/resources/server/conditions/
- https://github.com/neoforged/NeoFormRuntime/blob/main/src/main/java/net/neoforged/neoform/runtime/engine/NeoFormEngine.java
- `version.json` dos clientes oficiais Minecraft 26.2 e 26.3; SHA-1 dos downloads
  conferido com o manifesto oficial da Mojang.

## Próxima validação local

1. Execute `.\Build.ps1 -Mode partial`; após aprovação, `.\Build.ps1 -Clean`.
2. Teste cada JAR no cliente e no servidor dedicado correspondentes. Mantenha
   as configurações de cliente e servidor coerentes; esta revisão não adiciona
   sincronização automática de configuração.
3. Verifique travessia, playerOnly, headHitter, Leaf Walker ligado/desligado,
   passagem agachado, sons, queda com multiplicadores 0/0.5/1, passageiros,
   fluidos, neve e blocos de outros mods no tag de passáveis.
4. Teste `/reload` e reconexão, conferindo as tags e ausência de erros de Mixins.

O ZIP contém fontes, testes, documentação, wrapper e evidências. Não contém
JARs antigos do mod, diretório Git, mundos ou caches locais da máquina de origem.
Não substitui arquivos da instalação do Minecraft.
