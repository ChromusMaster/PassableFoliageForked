> Build 2.2.2: Fabric 26.2/26.3 and NeoForge 26.2 stable; NeoForge 26.3 beta is opt-in.
> See [BUILDING_WINDOWS.md](BUILDING_WINDOWS.md) for the build matrix, strict warnings and output layout.
> Latest build fixes and validation: [REVISAO_2.2.2.md](REVISAO_2.2.2.md).
> Initial port review: [REVISAO_2.2.md](REVISAO_2.2.md).

# Passable Foliage Forked

Mod version: **2.2.2**

Minecraft Java: **26.2 / 26.3**

## About

Passable Foliage Forked allows players and entities to move through leaves and any other blocks included in the `passablefoliage:passables` tag. Movement through foliage still has configurable effects such as reduced speed, sounds and fall-damage reduction. The mod also adjusts pathfinding and provides the Leaf Walker enchantment.

This project is a fork of [Passable Foliage](https://github.com/Snownee/PassableFoliage), originally created by Snownee and released under the MIT License.

This fork is independently maintained and is not affiliated with or endorsed by the original author. The technical mod ID and resource namespace remain `passablefoliage` to preserve compatibility with existing worlds and to prevent the original mod and this fork from being loaded together.

## Requirements

| Component | Version |
| --- | --- |
| Minecraft Java | 26.2 or 26.3 (separate builds) |
| Java | JDK 25 for building; Java 25 for running |
| Fabric Loader | 0.19.5 or newer |
| Fabric API | 0.158.0+26.2 / 0.161.0+26.3 |
| NeoForge | 26.2.0.88 stable / 26.3.0.58-beta experimental |
| Environment | Client and server |

Install the JAR matching both Minecraft and your modloader. Fabric API is required only for Fabric. Quilt has not been validated in this revision. Client and server should use matching configuration values.

## Features

- Removes collision from leaves and blocks included in the mod tag.
- Can restrict passable foliage to players only.
- Configurable horizontal and vertical movement speed inside foliage.
- Reduces and limits fall damage when landing in leaves.
- Plays configurable impact and movement sounds.
- Allows pathfinding entities to recognize foliage as an open path.
- Includes the Leaf Walker enchantment for walking on top of foliage.
- Includes the `headHitter` option, which preserves collision when approaching foliage from below.
- Hides an entity's name tag only while the entity is fully inside foliage.

## Changes in 2.2.2

- Declare Gson explicitly for test compilation and execution on every loader.
- Include main compilation artifacts in the bytecode contract test classpath.
- Consolidate verification dependencies/tasks in `gradle/verification.gradle`.

## Changes in 2.2.1

- Exclude obsolete source/resource locations when updating an existing checkout.
- Verify the selected Java source layout before compilation.
- Enable Java 25 native access in every Gradle launcher.
- Use the contextual, non-deprecated NeoForge sound API.
- Keep strict warnings, including JVM `[warning]` diagnostics.

## Changes in 2.2

- Separate builds and project caches by loader, Minecraft version and mod version.
- NeoForge entrypoint, registry lifecycle and native resource conditions.
- Strict warning gates, build logs, timing profiles and artifact hashes.
- Correct playerOnly effects/pathfinding and the inverted fall damage multiplier.
- Reuse collision suppression counters and skip unnecessary name-tag queries.
- Keep version-specific recipe datagen APIs isolated.

## Changes in 2.1

- Updated the project target from Minecraft Java 26.2 to 26.3.
- Updated Fabric Loader to 0.19.5 and Fabric API to 0.161.0+26.3.
- Kept Java 25, Loom 1.17.19 and the existing Gradle 9.7.0 wrapper.
- Updated the resource-pack metadata to Minecraft 26.3 format 97.1 using `min_format` and `max_format`.
- Removed stale datagen cache metadata from Minecraft 26.1.2 while preserving the generated data files.
- Reviewed the mod's current mixin/API touch points for the 26.3 port without compiling the project; no speculative Java rewrites were applied.

## Changes in 2.0

- Updated from Minecraft 26.1.2 to Minecraft Java 26.2.
- Updated to Fabric Loader 0.19.3, Fabric API 0.158.0, Loom 1.17.19, Gradle 9.7.0 and Java 25.
- Removed the Kiwi dependency because no Minecraft 26.2-compatible release was available.
- Replaced Kiwi registration and resource conditions with native Fabric and vanilla APIs.
- Replaced the old YAML configuration with `config/passablefoliage.json`.
- Added automatic migration of known values from `config/passablefoliage-common.yaml`. The old file is not deleted.
- Added strict parsing, type and range validation, and a 64 KiB configuration size limit.
- Added atomic configuration writes to reduce the risk of partially written files.
- Fixed the inverted name-tag visibility check.
- Fixed foliage slowdown still being applied while `alwaysLeafWalking` was enabled.
- Preserved loaded configuration values when the configuration file cannot be created.
- Protected temporary collision suppression with `try/finally` blocks.
- Removed an `INFO` log from the entity movement hot path.
- Removed unnecessary access to Minecraft internals and the Access Widener.
- Updated resource formats, datagen and tag APIs for Minecraft 26.2.
- Replaced dynamic build-plugin versions with exact versions.
- Enabled reproducible archives and added checksum verification to the Gradle Wrapper.
- Removed development leftovers and binaries that were not required to build the mod.

## Configuration

The `config/passablefoliage.json` file is created the first time the game starts with the mod installed.

| Option | Default | Range or purpose |
| --- | ---: | --- |
| `fallDamageMultiplier` | `0.5` | From 0 to 1 |
| `fallDamageThreshold` | `20` | From 5 to 255 blocks |
| `speedMultiplierHorizontal` | `0.9` | From 0 to 1 |
| `speedMultiplierVertical` | `0.9` | From 0 to 1 |
| `modifyPathFinding` | `true` | Adjusts entity pathfinding |
| `playerOnly` | `false` | Restricts passable foliage to players |
| `alwaysNotViewBlocking` | `true` | Prevents foliage from blocking vision |
| `alwaysLeafWalking` | `false` | Applies the Leaf Walker effect to all entities |
| `headHitter` | `false` | Preserves collision when approaching from below |
| `sounds.playerOnly` | `false` | Restricts foliage sounds to players |
| `sounds.volume` | `1.0` | From 0 to 10 |
| `leafWalkerEnabled` | `true` | Enables the enchantment and its recipe |

Out-of-range values are clamped. If the file is invalid, the mod keeps it unchanged, reports the problem in the log and uses safe defaults for that session.

## Building

Detailed instructions for Windows 10 and Visual Studio Code are available in [BUILDING_WINDOWS.md](BUILDING_WINDOWS.md).

From PowerShell in the project directory:

```powershell
.\Build.ps1 -Mode partial
.\Build.ps1 -Clean
```

Artifacts: `build/<Modloader>/<MinecraftVersion>/<ModVersion>/`.
The default matrix builds Fabric 26.2, Fabric 26.3 and NeoForge 26.2.
NeoForge 26.3 requires explicit beta opt-in. See the build guide and revision
report for validation limits and runtime checks.

## License

MIT. See [LICENSE](LICENSE).
