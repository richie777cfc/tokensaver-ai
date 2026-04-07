# Contributing

## Development

Run the local smoke check before opening a change:

```bash
python3 scripts/release_smoke.py
```

Run unit tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Privacy

Do not commit:

- private benchmark manifests
- raw local suite outputs
- confidential repo names
- local absolute paths

Before committing, run the leak scan included in `scripts/release_smoke.py`.

## Benchmarks

Use `benchmarks/manifest.example.json` as the public example.

Private local manifests belong under:

- `benchmarks/local/manifest.private.json`

That directory is gitignored on purpose.
