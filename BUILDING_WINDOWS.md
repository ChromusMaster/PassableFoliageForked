# Compilação / Building — Passable Foliage Forked 2.2.3

Requisitos: **JDK 25**, `JAVA_HOME` apontando para esse JDK, **Python 3.10+**
e internet para baixar o Gradle e as dependências. O Gradle Wrapper verifica o
SHA-256 da distribuição. Não é necessário instalar Gradle separadamente.

Extraia preferencialmente em uma pasta nova. Ao atualizar uma pasta existente,
substitua todos os arquivos do pacote. A versão 2.2.1 exclui da compilação as
localizações obsoletas conhecidas de fontes e recursos do layout anterior, sem
apagá-las. `verifySourceLayout` informa a contagem e reprova outras duplicatas.
Não reutilize JARs de builds antigos.
Abra o terminal na pasta que contém `Build.ps1` e `gradlew.bat`.

## Windows / PowerShell

Validação parcial dos três alvos estáveis, sem gerar JAR nem iniciar Minecraft:

```powershell
.\Build.ps1 -Mode partial
```

Compilação completa, sequencial, dos três alvos estáveis:

```powershell
.\Build.ps1 -Clean
```

Compilar somente um alvo:

```powershell
.\Build.ps1 -Loader Fabric -Minecraft 26.2 -Clean
.\Build.ps1 -Loader Fabric -Minecraft 26.3 -Clean
.\Build.ps1 -Loader NeoForge -Minecraft 26.2 -Clean
```

NeoForge 26.3 ainda é **beta**. A inclusão é explícita:

```powershell
.\Build.ps1 -Loader NeoForge -Minecraft 26.3 -IncludeBeta -Mode partial
.\Build.ps1 -Loader NeoForge -Minecraft 26.3 -IncludeBeta -Clean
```

## Linux, macOS e Windows com Python

```bash
python scripts/build.py --mode partial
python scripts/build.py --clean
python scripts/build.py --loader NeoForge --minecraft 26.3 --include-beta --mode partial
```

O script usa o mesmo Gradle Wrapper, sem shell intermediário, preserva o código de
saída, continua os outros alvos após falha e retorna erro se qualquer alvo falhar.
Interrupção por Ctrl+C encerra o processo e registra falha; não inicia outro alvo.

## Organização de saídas

| Alvo | Diretório |
|---|---|
| Fabric 26.2 | `build/Fabric/26.2/2.2.3/` |
| Fabric 26.3 | `build/Fabric/26.3/2.2.3/` |
| NeoForge 26.2 | `build/NeoForge/26.2/2.2.3/` |
| NeoForge 26.3 beta | `build/NeoForge/26.3/2.2.3/` |

Dentro de cada diretório ficam o JAR do mod, JAR de fontes, `classes/`, `resources/`,
`generated/`, `tmp/`, `reports/`, `.gradle/`, `run/`, `build-info.json`,
`last-build.json` e `logs/<data-hora-UTC-id>/`. Pastas só aparecem quando a tarefa
correspondente as utiliza. O JAR do mod fica diretamente na pasta da versão,
por exemplo `PassableFoliageForked-fabric-26.2-2.2.3.jar`.

`clean` limpa apenas o alvo escolhido e preserva seus logs, cache local e mundos
em `run/`. Os caches globais de distribuição/dependências do Gradle continuam no
`GRADLE_USER_HOME`, compartilhados para não duplicar downloads e grandes arquivos.
Nenhum cache, mundo ou binário antigo é parte dos fontes entregues.

## Logs e warnings

- `build.log`: stdout + stderr completos, incluindo `--info` e `--stacktrace`.
- `result.json`: comando, alvo, duração, código de saída, warnings, resultado e
  hashes SHA-256 dos JARs produzidos por uma compilação completa aprovada.
- `last-build.json`: resultado da tentativa mais recente, inclusive falhas.
- `build-info.json`: versões de Java, Gradle, Minecraft, mod e dependências do alvo.
- `reports/profile/`: perfil HTML de tempo das tarefas gerado por `--profile`.
- Java usa `-Xlint:all -Werror`; Gradle usa `--warning-mode=fail`.
- Os launchers Python, Windows e Unix habilitam acesso nativo para o Gradle no Java 25.
- O script reprova também linhas de diagnóstico `WARNING`, `WARN`, `[warning]` e `warning:`.
  Não ignora warnings de dependências ou plugins. Uma falha deve ser investigada,
  não contornada desativando essas opções.

O Gradle pode ter criado um JAR antes de uma reprovação por warning do plugin.
Use **somente** JARs de uma execução cujo `result.json` tenha `status: passed`.
Uma validação parcial aprovada não gera nem valida um JAR antigo nessa pasta.

## Gradle direto e IDE

```powershell
.\gradlew.bat partialCheck -Pmodloader=Fabric -Pminecraft_version=26.2 --project-cache-dir build/Fabric/26.2/2.2.3/.gradle
.\gradlew.bat build -Pmodloader=NeoForge -Pminecraft_version=26.2 --project-cache-dir build/NeoForge/26.2/2.2.3/.gradle
```

Sem parâmetros, Gradle usa Fabric 26.3. O script `Build.ps1`/`build.py` é a entrada
recomendada para a matriz e para capturar logs completos e warnings externos.
O script também define `--project-cache-dir` antes de iniciar Gradle; sem essa
opção, uma invocação direta usa o cache padrão `.gradle` da raiz.
Não execute dois builds simultaneamente para o mesmo alvo. Na IDE selecione um
alvo por vez nas propriedades do Gradle e recarregue o projeto.

## Fontes e testes

- `src/main`: comportamento compartilhado.
- `src/version`: adaptadores de assinatura de Mixins para cada versão do Minecraft.
- `src/fabric`: integração Fabric, datagen e adaptadores de API em `26.2`/`26.3`.
- `src/neoforge`: inicialização, registros, condições e metadados NeoForge.
- `src/generated/resources`: dados de referência Fabric.
- `src/neoforge/resources/data`: equivalentes NeoForge com condições próprias.
- `src/test`: regressões Java (`regressionTest`) e contratos de assinatura de Mixins
  (`mixinContractTest`), ambos executados por `partialCheck` e `check`.
- `prepareAdvancements`: gera o critério de desbloqueio no formato do Minecraft selecionado.
- `verifyAdvancementResources`: valida o advancement processado, critérios e recompensa;
  obrigatório em `partialCheck`, `check` e `jar`.
- `tests`: testes do controlador de compilação (`python -m unittest discover -s tests -v`).

O teste de integração opcional `tests/test_resource_build.py` usa um Gradle instalado
indicado por `GRADLE_TEST_COMMAND` (array JSON de argumentos). Ele executa o
processamento de recursos e cria JARs de teste contendo apenas recursos, sem
plugins Minecraft. O build normal sempre executa `verifyAdvancementResources`.

As condições dos JSONs Fabric e NeoForge devem permanecer equivalentes; os testes
verificam isso. Compilação parcial não inicia o jogo e não garante que os Mixins
se apliquem em runtime. Testar cliente e servidor dedicado, /reload, encantamento,
playerOnly, headHitter, fluidos, neve, sons e queda continua necessário.

## Correção 2.2.3

Veja [REVISAO_2.2.3.md](REVISAO_2.2.3.md) para as causas dos erros enviados,
as correções e o escopo exato da validação parcial. A integração de som NeoForge
usa a API contextual com mundo, posição e entidade; Fabric mantém sua API nativa.

## English quick start

Install JDK 25 and Python 3.10+. Run `python scripts/build.py --mode partial` for
compilation/resource/regression checks or `python scripts/build.py --clean` to
build all stable targets. Output: `build/<Loader>/<Minecraft>/<ModVersion>/`.
NeoForge 26.3 requires `--include-beta`. Warnings fail the build; inspect per-run
logs and use only artifacts from a `passed` full build. Runtime testing is separate.
