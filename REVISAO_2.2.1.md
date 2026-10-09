# Correção dos builds — 2.2.1

## Causas observadas nos logs enviados

1. Fontes Fabric do layout antigo em `src/main/java` estavam sendo compiladas
   junto às novas fontes em `src/fabric`. Isso causava classes duplicadas no
   Fabric e referências Fabric ausentes no NeoForge. A receita antiga também
   continuava selecionada. `clean` não remove arquivos-fonte obsoletos.
2. O launcher Python iniciava o Wrapper sem habilitar acesso nativo. O Java 25
   emitia warnings de `native-platform`, corretamente reprovados pelo gate.
3. As duas chamadas compartilhadas a `BlockState.getSoundType()` usavam uma API
   obsoleta no Minecraft modificado pelo NeoForge. Esta foi uma falha do port
   2.2 que a compilação anterior contra Minecraft vanilla não detectou.

## Correções

- `gradle/source-layout.gradle` seleciona os diretórios do loader e da versão e
  exclui 14 localizações obsoletas conhecidas de fontes/recursos. Arquivos locais
  não são apagados. As exclusões usam caminhos exatos, preservando os novos
  arquivos de mesmo nome nas pastas do loader.
- `verifySourceLayout` detecta duplicatas antes de `compileJava` e
  `processResources`; registra quantos fontes selecionou e quantas localizações
  obsoletas estavam presentes.
- Python, `gradlew`, `gradlew.bat` e a JVM Gradle recebem
  `--enable-native-access=ALL-UNNAMED`. O acesso necessário é habilitado;
  os warnings continuam tratados como erros.
- `PlatformSound` tem implementação por loader. NeoForge usa
  `IBlockStateExtension.getSoundType(level, pos, entity)`, respeitando mundo,
  posição e entidade. Fabric mantém `BlockState.getSoundType()`.
- O gate também reconhece diagnósticos JVM no formato `[warning]`.
- A versão passa a 2.2.1, mantendo saídas em
  `build/<Modloader>/<Minecraft>/<ModVersion>/`.

## Validação realizada

| Verificação | Resultado e escopo |
|---|---|
| Testes Python | 9 aprovados, incluindo warnings e argumentos do launcher |
| Seleção de fontes e recursos | 4 alvos, cada um em pasta limpa e sobreposição do projeto original: seleção idêntica; Gradle com `--warning-mode=fail` |
| Compilação parcial Java | `PassableFoliage.java` e `PlatformSound.java` compilados nos 4 alvos com JDK 25, `-Xlint:all -Werror`; zero diagnósticos |
| Gradle com Java 25 e acesso nativo | `verifySourceLayout` aprovado no harness Java isolado; zero warnings |

Fabric selecionou 30 fontes Java por versão; NeoForge selecionou 24. As
compilações parciais usaram o cliente vanilla oficial da versão correspondente,
a API do loader e classes comuns já compiladas da revisão anterior. Não foram
usados stubs. Os logs estão em `build/<Loader>/<Minecraft>/2.2.1/logs/` e os
resultados detalhados em `docs/validation-summary.json`.

**Limite da validação:** não foi certificado um build completo com o Minecraft
transformado pelos plugins, nem a aplicação de Mixins ou execução no jogo.
O ambiente de validação anterior bloqueou a inicialização de socket Unix do Loom
e a identificação do executável Java no NeoForm. A compilação direta não
substitui esses passos. O relatório da revisão 2.2 permanece como histórico em
`docs/validation-2.2.json`.

## Compilar no Windows

Substitua os arquivos pelo conteúdo deste pacote e execute com JDK 25 e Python
3.10+:

```powershell
.\Build.ps1 -Mode partial
.\Build.ps1 -Clean
```

O padrão inclui Fabric 26.2, Fabric 26.3 e NeoForge 26.2. NeoForge 26.3 permanece
beta e exige `-IncludeBeta`. Use apenas JARs de uma execução completa cujo
`result.json` indique `status: passed`. Uma validação parcial não certifica JARs
antigos. As versões de dependências permanecem fixadas nas mesmas versões da
revisão 2.2; este hotfix corrige os erros enviados.
