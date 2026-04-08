# Published Results

Benchmark date: April 7, 2026

These snapshots publish exact TokenSaver benchmark outputs from anonymized real-world repositories. Public fixture suite results are tracked separately in CI — see the fixture suite section in [README.md](../README.md).

`Files` in the summary table come from the full repo scan. `Source Tokens` and `Compression` use the artifact covered-set union from `repo.union_source_tokens`. Those covered-set totals may differ from full scan totals because artifact source accounting follows extractor source sets rather than the top-level scan summary.

## Summary

| Repo | Framework | Plugin | Files | Source Tokens | Bundle Tokens | Compression |
|------|-----------|--------|------:|-------------:|-------------:|------------:|
| Confidential Flutter App A | `flutter` | `flutter` | 10,264 | 8,510,170 | 157,867 | **53.91x** |
| Confidential Flutter App B | `flutter` | `flutter` | 105 | 222,337 | 2,882 | **77.15x** |
| Confidential React Native App A | `react_native` | `react_native` | 896 | 804,476 | 28,466 | **28.26x** |
| Confidential React Native App B | `react_native` | `react_native` | 570 | 71,748 | 5,063 | **14.17x** |
| Confidential Node Backend A | `node` | `generic` | 32 | 19,998 | 5,498 | **3.64x** |
| Confidential Next.js App A | `nextjs` | `nextjs` | 59 | 18,747 | 1,999 | **9.38x** |
| Confidential Android App A | `android_native` | `android_native` | 2,255 | 4,427,242 | 2,180,896 | **2.03x** |
| Confidential iOS App A | `ios_swift` | `ios_swift` | 2,449 | 5,903,230 | 84,544 | **69.82x** |

## Confidential Flutter App A

- Framework: `flutter`
- Plugin: `flutter`
- Runtime: `47.75s`
- Full scan: `10,264` files, `16,067,711` tokens
- Covered-set compression: `8,510,170 -> 157,867` tokens (`53.91x`)

Artifact ratios:

- `project_summary`: `7.13x`
- `module_graph`: `86.39x`
- `api_index`: `2.80x`
- `route_index`: `51.54x`
- `config_index`: `22.16x`

## Confidential Flutter App B

- Framework: `flutter`
- Plugin: `flutter`
- Runtime: `1.05s`
- Full scan: `105` files, `262,077` tokens
- Covered-set compression: `222,337 -> 2,882` tokens (`77.15x`)

Artifact ratios:

- `project_summary`: `4.08x`
- `module_graph`: `196.22x`
- `api_index`: `18.72x`

## Confidential React Native App A

- Framework: `react_native`
- Plugin: `react_native`
- Runtime: `14.35s`
- Full scan: `896` files, `806,286` tokens
- Covered-set compression: `804,476 -> 28,466` tokens (`28.26x`)

Artifact ratios:

- `project_summary`: `5.49x`
- `module_graph`: `53.57x`
- `api_index`: `26.53x`
- `route_index`: `41.40x`

## Confidential React Native App B

- Framework: `react_native`
- Plugin: `react_native`
- Runtime: `19.68s`
- Full scan: `570` files, `483,093` tokens
- Covered-set compression: `71,748 -> 5,063` tokens (`14.17x`)

Artifact ratios:

- `project_summary`: `3.17x`
- `api_index`: `16.64x`
- `route_index`: `28.81x`
- `config_index`: `5.99x`

## Confidential Node Backend A

- Framework: `node`
- Plugin: `generic`
- Runtime: `0.07s`
- Full scan: `32` files, `21,447` tokens
- Covered-set compression: `19,998 -> 5,498` tokens (`3.64x`)

Artifact ratios:

- `project_summary`: `5.70x`
- `module_graph`: `23.41x`
- `api_index`: `8.67x`
- `route_index`: `5.88x`
- `config_index`: `1.36x`

## Confidential Next.js App A

- Framework: `nextjs`
- Plugin: `nextjs`
- Runtime: `0.12s`
- Full scan: `59` files, `92,293` tokens
- Covered-set compression: `18,747 -> 1,999` tokens (`9.38x`)

Artifact ratios:

- `project_summary`: `3.47x`
- `module_graph`: `26.65x`
- `route_index`: `47.39x`

## Confidential Android App A

- Framework: `android_native`
- Plugin: `android_native`
- Runtime: `16.31s`
- Full scan: `2,255` files, `3,631,975` tokens
- Covered-set compression: `4,427,242 -> 2,180,896` tokens (`2.03x`)

Artifact ratios:

- `module_graph`: `26.61x`
- `api_index`: `42.76x`
- `route_index`: `110.34x`
- `config_index`: `0.64x`

## Confidential iOS App A

- Framework: `ios_swift`
- Plugin: `ios_swift`
- Runtime: `11.43s`
- Full scan: `2,449` files, `5,994,964` tokens
- Covered-set compression: `5,903,230 -> 84,544` tokens (`69.82x`)

Artifact ratios:

- `module_graph`: `89.25x`
- `api_index`: `24.08x`
- `route_index`: `33.69x`
- `config_index`: `27.56x`
