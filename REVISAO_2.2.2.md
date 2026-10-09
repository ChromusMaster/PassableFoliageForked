# Correção da configuração de testes — 2.2.2

## Resultado dos logs enviados da versão 2.2.1

| Alvo | Resultado observado |
|---|---|
| Fabric 26.2 | `partialCheck` aprovado em 20,547 s, zero warnings |
| Fabric 26.3 | `partialCheck` aprovado em 17,234 s, zero warnings |
| NeoForge 26.2 | `compileJava` e `processResources` aprovados; `compileTestJava` falhou por ausência de Gson |
| NeoForge 26.3 | Sem nova execução: o ZIP contém somente os testes isolados incluídos na entrega anterior |

Ambos os Fabric compilaram os testes e executaram a verificação das 16
assinaturas de Mixins e as regressões de `SuppressionDepth`. As exclusões das
14 localizações obsoletas funcionaram nos três builds executados. Não foram
enviados resultados de empacotamento de JARs nem de execução no jogo.

## Causa e correção

`MixinContractTest` importa `com.google.gson.JsonParser`, mas Gson não estava
declarado como dependência dos testes. Fabric o disponibilizava indiretamente;
no NeoForge, o classpath de testes não incluía essa dependência. O erro estava
na configuração entregue, não no ambiente Windows do usuário.

As dependências e tarefas de verificação foram reunidas em
`gradle/verification.gradle`, aplicado pelo `build.gradle` principal:

- `testImplementation 'com.google.code.gson:gson:2.14.0'`, versão presente nos
  metadados oficiais dos dois Minecraft alvo; disponível ao compilar e executar
  os testes, sem embutir Gson no JAR do mod.
- O classpath de `mixinContractTest` inclui o classpath de compilação principal,
  permitindo ler as classes do Minecraft selecionadas pelo loader. A tarefa
  apenas inspeciona bytecode; não inicializa o jogo.
- Diretório de trabalho da tarefa definido explicitamente na raiz do projeto,
  onde está o JSON de configuração dos Mixins.
- Preservados `-Xlint:all -Werror`, `--warning-mode=fail`, testes de regressão,
  acesso nativo Java 25 e estrutura de saídas por alvo.

## Validação e limites

O mesmo `gradle/verification.gradle` foi aplicado em projetos Gradle Java
isolados para os quatro alvos. Os testes foram recompilados com JDK 25 e
warnings como erros e executados contra classes principais anteriormente
compiladas e o cliente vanilla de cada versão. Essa verificação valida a
configuração dos testes; não equivale a executar os plugins Fabric/NeoForge
nem a gerar um JAR final. Os resultados estão em
`docs/validation-2.2.2-tests.json` e os logs em
`build/<Loader>/<Minecraft>/2.2.2/logs/test-wiring/`.

Os quatro cenários isolados passaram sem warnings: 16 assinaturas de Mixins
verificadas por alvo e regressões de `SuppressionDepth` aprovadas. Os nove testes
Python também passaram. Um controle negativo, removendo Gson do classpath de
testes, reproduziu o erro original; sua falha é intencional e está identificada
em `logs/negative-no-gson/`.

Os logs reais enviados foram preservados em `docs/user-validation-2.2.1/`.
O resultado da revisão 2.2.1 permanece histórico; a versão 2.2.2 ainda precisa
passar pelo build completo e pelos testes em cliente e servidor.

## Comandos

Após substituir os arquivos do projeto:

```powershell
.\Build.ps1 -Mode partial
.\Build.ps1 -Clean
```

O padrão executa os três alvos estáveis. Para executar também o alvo NeoForge
26.3 beta:

```powershell
.\Build.ps1 -Loader NeoForge -Minecraft 26.3 -IncludeBeta -Mode partial
.\Build.ps1 -Loader NeoForge -Minecraft 26.3 -IncludeBeta -Clean
```

Os arquivos de log históricos não demonstram uma nova execução: confira
`mod_version`, `mode`, `started_utc` e `status` no `result.json` da pasta com
data e hora. Só utilize JARs de uma execução completa aprovada.
