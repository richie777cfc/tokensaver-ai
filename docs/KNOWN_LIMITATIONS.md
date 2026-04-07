# Known Limitations

TokenSaver is usable, but it is not omniscient. These are the current boundaries to keep in mind.

## Stack Coverage

First-class extractors currently exist for:

- Flutter
- React Native

Other stacks fall back to generic extraction. That path is useful, but lower confidence.

## Artifact Quality

- Some artifact types compress extremely well (`module_graph`, many route maps).
- Some artifact types are intentionally conservative and may have low compression ratios on small or simple repos.
- Generic stack support can produce `partial` benchmark status when major artifacts are empty or not applicable.

## Public Benchmarks

- Public fixture benchmarks are smoke tests, not performance leaderboards.
- Fixture repos are synthetic and intentionally small.
- Published ratios from fixture projects should be interpreted as contract verification, not product marketing claims.

## Stability

- The benchmark suite and public-export format are now documented and tested, but the overall project should still be treated as evolving.
- Users should expect improvements to extractor quality over time, especially for non-Flutter and non-React Native stacks.
