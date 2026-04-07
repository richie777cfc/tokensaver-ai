"""Generic fallback plugin for non-Flutter repositories."""

from __future__ import annotations

from dataclasses import dataclass

from tokensaver.core.helpers import (
    ENV_PATTERNS,
    NODE_API_PATTERN,
    PYTHON_API_PATTERN,
    REACT_ROUTE_PATTERN,
    add_api_file_entry,
    all_code_files,
    build_module_graph_artifact,
    finalize_api_files,
    finalize_route_files,
    match_with_lines,
    meta,
    module_name_for_file,
    timestamp,
)
from tokensaver.core.models import ArtifactResult, BuildContext


@dataclass(frozen=True)
class GenericPlugin:
    name: str = "generic"
    frameworks: set[str] = frozenset({"react", "nextjs", "node", "python", "unknown", "rust", "go", "android_native"})

    def build_artifacts(self, ctx: BuildContext) -> list[ArtifactResult]:
        return [
            build_module_graph(ctx),
            build_api_index(ctx),
            build_route_index(ctx),
            build_config_index(ctx),
        ]


def build_module_graph(ctx: BuildContext) -> ArtifactResult:
    return build_module_graph_artifact(ctx.root, ctx.scan.framework, ArtifactResult)


def build_api_index(ctx: BuildContext) -> ArtifactResult:
    api_files = {}
    source_files = set()
    endpoint_count = 0

    for file_path in all_code_files(ctx.root):
        if "test" in file_path.parts:
            continue
        content = file_path.read_text(errors="ignore")
        rel_path = str(file_path.relative_to(ctx.root))
        module = module_name_for_file(ctx.root, file_path)

        if file_path.suffix == ".py":
            for _, method, path in match_with_lines(content, PYTHON_API_PATTERN, method_group=1, path_group=2):
                if add_api_file_entry(api_files, rel_path=rel_path, module=module, path=path, name="", method=method.upper()):
                    endpoint_count += 1
                source_files.add(file_path)
        elif file_path.suffix in {".js", ".ts", ".jsx", ".tsx"}:
            for _, method, path in match_with_lines(content, NODE_API_PATTERN, method_group=1, path_group=2):
                if add_api_file_entry(api_files, rel_path=rel_path, module=module, path=path, name="", method=method.upper()):
                    endpoint_count += 1
                source_files.add(file_path)

    payload = {
        "_meta": {
            **meta(ctx.root, "api_index_v1", source_files),
            "entry_schema": ["path", "name", "method"],
            "group_schema": ["file", "module", "entries"],
        },
        "files": finalize_api_files(api_files),
    }
    return ArtifactResult(
        name="api_index",
        file_name="API_INDEX.json",
        payload=payload,
        source_files=source_files,
        entity_count=endpoint_count,
    )


def build_route_index(ctx: BuildContext) -> ArtifactResult:
    routes = {}
    source_files = set()

    if ctx.scan.framework == "nextjs":
        for base_name in ("app", "pages"):
            base_dir = ctx.root / base_name
            if not base_dir.exists():
                continue
            for file_path in all_code_files(base_dir):
                rel_path = file_path.relative_to(base_dir)
                route = "/" + "/".join(rel_path.with_suffix("").parts)
                route = route.replace("/page", "").replace("/index", "") or "/"
                routes[route] = {
                    "path": route,
                    "source": [{"file": str(file_path.relative_to(ctx.root))}],
                    "usage_count": 1,
                    "navigated_from": [],
                }
                source_files.add(file_path)
    else:
        for file_path in all_code_files(ctx.root):
            if "test" in file_path.parts:
                continue
            if file_path.suffix not in {".js", ".jsx", ".ts", ".tsx"}:
                continue
            content = file_path.read_text(errors="ignore")
            rel_path = str(file_path.relative_to(ctx.root))
            for line_no, route_path in match_with_lines(content, REACT_ROUTE_PATTERN, value_group=1):
                routes[route_path] = {
                    "path": route_path,
                    "source": [{"file": rel_path, "line": line_no}],
                    "usage_count": 1,
                    "navigated_from": [],
                }
                source_files.add(file_path)

    payload = {
        "_meta": {
            "generated_at": timestamp(),
            "extractor": "route_index_v1",
            "entry_schema": ["path", "screen", "usage_count", "aliases", "navigated_from"],
            "group_schema": ["file", "entries"],
        },
        "files": finalize_route_files(routes),
    }
    return ArtifactResult(
        name="route_index",
        file_name="ROUTE_INDEX.json",
        payload=payload,
        source_files=source_files,
        entity_count=len(routes),
    )


def build_config_index(ctx: BuildContext) -> ArtifactResult:
    keys = {}
    source_files = set()

    for file_path in all_code_files(ctx.root):
        if "test" in file_path.parts:
            continue
        content = file_path.read_text(errors="ignore")
        rel_path = str(file_path.relative_to(ctx.root))
        file_has_keys = False

        for extractor, pattern in ENV_PATTERNS:
            for line_no, key in match_with_lines(content, pattern, value_group=1):
                entry = keys.setdefault(
                    key,
                    {
                        "name": key,
                        "types": set(),
                        "references": [],
                        "extractor": extractor,
                        "confidence": 0.95,
                    },
                )
                entry["references"].append({"file": rel_path, "line": line_no})
                file_has_keys = True

        if file_has_keys:
            source_files.add(file_path)

    payload = {
        "_meta": meta(ctx.root, "config_index_v1", source_files),
        "config_keys": [
            {
                "name": item["name"],
                "types": sorted(item["types"]) if item["types"] else ["unknown"],
                "references": item["references"],
                "source": item["references"],
                "extractor": item["extractor"],
                "confidence": item["confidence"],
            }
            for item in sorted(keys.values(), key=lambda value: value["name"])
        ],
    }
    return ArtifactResult(
        name="config_index",
        file_name="CONFIG_INDEX.json",
        payload=payload,
        source_files=source_files,
        entity_count=len(keys),
    )


GENERIC_PLUGIN = GenericPlugin()
