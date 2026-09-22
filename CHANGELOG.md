# Changelog

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
