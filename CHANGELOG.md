# Changelog

## 2.2.1

- Corrected duplicate sources and obsolete Fabric resource selection after extracting over the old layout.
- Added a source layout verification task without deleting legacy user files.
- Enabled native access in Python, Windows and Unix launchers for Java 25.
- Replaced NeoForge deprecated sound calls with its contextual sound API.
- Preserved warning-as-error checks and included JVM bracketed warning diagnostics.
- Partially compiled changed classes for all four targets; see REVISAO_2.2.1.md for limitations.

## 2.2

- Added segmented Fabric and NeoForge builds, logs, profiles and strict warning gates.
- Added the NeoForge port and performance/stability fixes described in REVISAO_2.2.md.

## 2.1

- Ported the project metadata and dependencies to Minecraft Java 26.3.
- Updated Fabric Loader to 0.19.5 and Fabric API to 0.161.0+26.3.
- Retained Java 25, Loom 1.17.19 and the Gradle 9.7.0 wrapper.
- Updated `pack.mcmeta` to resource pack format 97.1 using `min_format` and `max_format`.
- Removed stale Minecraft 26.1.2 datagen cache files while retaining generated resources.
- Performed a static compatibility review only; the project was intentionally not compiled or executed.

## 2.0

- Ported the mod to Minecraft Java 26.2 and Java 25.
- Updated Fabric Loader, Fabric API, Loom and Gradle.
- Removed the Kiwi dependency and replaced its configuration, registration and resource-condition features with native implementations.
- Added migration from the old YAML configuration to JSON.
- Fixed the inverted name-tag visibility check.
- Fixed foliage slowdown while `alwaysLeafWalking` was enabled.
- Preserved loaded values when the configuration file cannot be created.
- Ensured temporary collision state is restored if an intercepted call throws an exception.
- Removed excessive logging from entity movement processing.
- Updated datagen, tags and resource formats for Minecraft 26.2.
- Removed unnecessary binaries and development files from the source package.
- Pinned dependency versions and added checksum verification for the Gradle distribution.
- Preserved Fabric and Quilt support on both client and server.
- Established independent fork branding and versioning as Passable Foliage Forked 2.0.
- Fixed archive naming without relying on Loom tasks before they are registered.
