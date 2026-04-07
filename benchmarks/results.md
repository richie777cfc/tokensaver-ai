# Published Results

Benchmark date: April 7, 2026

These snapshots publish exact TokenSaver benchmark outputs without committing full generated artifact bundles.

## Confidential Flutter App A

- Framework: `flutter`
- Plugin: `flutter`
- Runtime: `55.53s`
- Full scan: `10,264` files, `16,067,711` tokens
- Covered-set compression: `8,510,170 -> 157,466` tokens (`54.04x`)

Artifact ratios:

- `project_summary`: `7.22x`
- `module_graph`: `86.40x`
- `api_index`: `2.80x`
- `route_index`: `51.56x`
- `config_index`: `22.20x`

## Confidential React Native App B

- Framework: `react_native`
- Plugin: `react_native`
- Runtime: `16.76s`
- Full scan: `896` files, `806,286` tokens
- Covered-set compression: `804,476 -> 28,394` tokens (`28.33x`)

Artifact ratios:

- `project_summary`: `5.58x`
- `commands`: `1.07x`
- `module_graph`: `53.61x`
- `api_index`: `26.58x`
- `route_index`: `41.52x`
- `config_index`: `n/a`
