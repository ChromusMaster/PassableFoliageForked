#!/usr/bin/env python3
"""Sequential, logged Gradle matrix; any diagnostic warning fails the target."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
WARNING = re.compile(r"(?:\bwarning\s*:|(?:^|\s|\[)WARN(?:\s|\]|:)|\[warning\]|^\s*WARNING\b|^\s*[1-9]\d*\s+warnings?\b|Deprecated Gradle features were used)", re.I)


def properties(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    return values


def targets(loader: str, minecraft: str, beta: bool) -> list[tuple[str, str]]:
    result = []
    for platform in (['Fabric', 'NeoForge'] if loader == 'All' else [loader]):
        for mc in (['26.2', '26.3'] if minecraft == 'All' else [minecraft]):
            if platform == 'NeoForge' and mc == '26.3' and not beta:
                if loader != 'All' and minecraft != 'All':
                    raise ValueError('NeoForge 26.3 requires --include-beta; it is not a stable release.')
                continue
            result.append((platform, mc))
    return result


def run_target(loader: str, mc: str, version: str, mode: str, clean: bool, beta: bool) -> bool:
    output = ROOT / 'build' / loader / mc / version
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') + '-' + uuid.uuid4().hex[:8]
    logdir = output / 'logs' / stamp
    logdir.mkdir(parents=True)
    # Invoke the wrapper JAR directly: identical wrapper/distribution validation on
    # Windows and Linux, no shell parsing and no dependency on executable bits.
    java = str(Path(os.environ['JAVA_HOME']) / 'bin' / ('java.exe' if os.name == 'nt' else 'java')) if os.environ.get('JAVA_HOME') else 'java'
    command = [java, '--enable-native-access=ALL-UNNAMED', '-Dfile.encoding=UTF-8', '-cp', str(ROOT / 'gradle/wrapper/gradle-wrapper.jar'),
               'org.gradle.wrapper.GradleWrapperMain',
               '--project-cache-dir', str(output / '.gradle'),
               '--no-daemon', '--console=plain', '--warning-mode=fail', '--stacktrace', '--info', '--profile',
               f'-Pmodloader={loader}', f'-Pminecraft_version={mc}', f'-Pmod_version={version}']
    if beta:
        command.append('-Pallow_beta=true')
    if clean:
        command.append('clean')
    command.append('partialCheck' if mode == 'partial' else 'build')
    report = {'loader': loader, 'minecraft': mc, 'mod_version': version, 'mode': mode,
              'started_utc': stamp, 'command': command, 'warnings': [], 'status': 'running'}
    start = time.monotonic()
    exit_code = 1
    print(f'\n=== {loader} / {mc} / {version} ({mode}) ===', flush=True)
    process = None
    try:
        with (logdir / 'build.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding='utf-8', errors='replace')
            assert process.stdout is not None
            for line in process.stdout:
                log.write(line)
                log.flush()
                print(line, end='', flush=True)
                if WARNING.search(line):
                    report['warnings'].append(line.rstrip())
            exit_code = process.wait()
    except (OSError, KeyboardInterrupt) as error:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        report['exception'] = str(error) or 'Interrupted by user'
        if isinstance(error, KeyboardInterrupt):
            exit_code = 130
    finally:
        report.update(exit_code=exit_code, elapsed_seconds=round(time.monotonic() - start, 3),
                      status='passed' if exit_code == 0 and not report['warnings'] else 'failed')
        artifacts = []
        if report['status'] == 'passed' and mode == 'full':
            for path in sorted(output.glob('*.jar')):
                artifacts.append({'name': path.name, 'bytes': path.stat().st_size,
                                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            if not artifacts:
                report['status'] = 'failed'
                report['exception'] = 'Gradle returned success but no JAR was produced in the target directory.'
        report['artifacts'] = artifacts
        (logdir / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        (output / 'last-build.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"{report['status'].upper()}: {loader} {mc}; {len(report['warnings'])} warning(s); {report['elapsed_seconds']} s")
    if exit_code == 130:
        raise KeyboardInterrupt
    return report['status'] == 'passed'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loader', choices=['All', 'Fabric', 'NeoForge'], default='All')
    parser.add_argument('--minecraft', choices=['All', '26.2', '26.3'], default='All')
    parser.add_argument('--mode', choices=['partial', 'full'], default='full')
    parser.add_argument('--include-beta', action='store_true')
    parser.add_argument('--clean', action='store_true')
    args = parser.parse_args()
    version = properties(ROOT / 'gradle.properties')['mod_version']
    if not re.fullmatch(r'[0-9A-Za-z][0-9A-Za-z.+_-]*', version):
        parser.error('Unsafe mod_version in gradle.properties')
    try:
        matrix = targets(args.loader, args.minecraft, args.include_beta)
    except ValueError as error:
        parser.error(str(error))
    success = True
    try:
        for loader, mc in matrix:
            success = run_target(loader, mc, version, args.mode, args.clean, args.include_beta) and success
    except KeyboardInterrupt:
        return 130
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
