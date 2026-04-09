"""Composite extractor for nested multi-app repositories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tokensaver.core.helpers import finalize_api_files, meta
from tokensaver.core.models import ArtifactResult, BuildContext
from tokensaver.scanner import scan_project
from tokensaver.workspaces import detect_workspace_components


@dataclass(frozen=True)
class WorkspacePlugin:
    name: str = "workspace"
    frameworks: set[str] = frozenset({"workspace"})

    def build_artifacts(self, ctx: BuildContext) -> list[ArtifactResult]:
        return [
            build_module_graph(ctx),
            build_api_index(ctx),
            build_route_index(ctx),
            build_config_index(ctx),
        ]


def _child_components(root: Path):
    return [item for item in detect_workspace_components(root) if item.root != root]


def _prefixed_path(prefix: str, value: str) -> str:
    if not prefix:
        return value
    if not value:
        return prefix
    return f"{prefix}/{value}"


def _prefix_refs(root: Path, project_root: Path, refs: list[dict]) -> list[dict]:
    prefix = str(project_root.relative_to(root))
    prefixed = []
    for ref in refs:
        item = dict(ref)
        item["file"] = _prefixed_path(prefix, ref["file"])
        prefixed.append(item)
    return prefixed


def _child_artifacts(ctx: BuildContext) -> list[tuple[Path, dict[str, ArtifactResult]]]:
    from tokensaver.core.registry import get_plugin

    results = []
    for component in _child_components(ctx.root):
        child_scan = scan_project(component.root)
        child_plugin = get_plugin(child_scan.framework)
        child_ctx = BuildContext(root=component.root, scan=child_scan)
        artifacts = {artifact.name: artifact for artifact in child_plugin.build_artifacts(child_ctx)}
        results.append((component.root, artifacts))
    return results


def build_module_graph(ctx: BuildContext) -> ArtifactResult:
    modules = []
    source_files: set[Path] = set()
    seen = set()

    for project_root, artifacts in _child_artifacts(ctx):
        prefix = str(project_root.relative_to(ctx.root))
        artifact = artifacts["module_graph"]
        source_files.update(artifact.source_files)
        for item in artifact.payload["modules"]:
            path = _prefixed_path(prefix, item["path"])
            if path in seen:
                continue
            seen.add(path)
            modules.append(
                {
                    **item,
                    "name": _prefixed_path(prefix, item["name"]),
                    "path": path,
                    "source": _prefix_refs(ctx.root, project_root, item.get("source", [])),
                }
            )

    payload = {
        "_meta": meta(ctx.root, "workspace_module_graph_v1", source_files),
        "modules": sorted(modules, key=lambda item: item["path"]),
    }
    return ArtifactResult(
        name="module_graph",
        file_name="MODULE_GRAPH.json",
        payload=payload,
        source_files=source_files,
        entity_count=len(modules),
    )


def build_api_index(ctx: BuildContext) -> ArtifactResult:
    grouped: dict[str, dict] = {}
    source_files: set[Path] = set()
    endpoint_count = 0

    for project_root, artifacts in _child_artifacts(ctx):
        prefix = str(project_root.relative_to(ctx.root))
        artifact = artifacts["api_index"]
        source_files.update(artifact.source_files)
        for file_path, module, entries in artifact.payload["files"]:
            prefixed_file = _prefixed_path(prefix, file_path)
            group = grouped.setdefault(
                prefixed_file,
                {"file": prefixed_file, "module": _prefixed_path(prefix, module), "entries": [], "seen": set()},
            )
            for entry in entries:
                row = tuple(entry)
                if row in group["seen"]:
                    continue
                group["seen"].add(row)
                group["entries"].append(entry)
                endpoint_count += 1

    payload = {
        "_meta": {
            **meta(ctx.root, "workspace_api_index_v1", source_files),
            "entry_schema": ["path", "name", "method"],
            "group_schema": ["file", "module", "entries"],
        },
        "files": finalize_api_files(grouped),
    }
    return ArtifactResult(
        name="api_index",
        file_name="API_INDEX.json",
        payload=payload,
        source_files=source_files,
        entity_count=endpoint_count,
    )


def build_route_index(ctx: BuildContext) -> ArtifactResult:
    grouped: dict[str, list[list]] = {}
    seen: dict[str, set[tuple]] = {}
    source_files: set[Path] = set()
    route_count = 0

    for project_root, artifacts in _child_artifacts(ctx):
        prefix = str(project_root.relative_to(ctx.root))
        artifact = artifacts["route_index"]
        source_files.update(artifact.source_files)
        for file_path, entries in artifact.payload["files"]:
            prefixed_file = _prefixed_path(prefix, file_path)
            bucket = grouped.setdefault(prefixed_file, [])
            bucket_seen = seen.setdefault(prefixed_file, set())
            for entry in entries:
                row = tuple(entry)
                if row in bucket_seen:
                    continue
                bucket_seen.add(row)
                bucket.append(entry)
                route_count += 1

    payload = {
        "_meta": meta(ctx.root, "workspace_route_index_v1", source_files),
        "files": [
            [file_path, sorted(entries, key=lambda row: row[0])]
            for file_path, entries in sorted(grouped.items())
        ],
    }
    payload["_meta"]["entry_schema"] = ["path", "screen", "usage_count", "aliases", "navigated_from"]
    payload["_meta"]["group_schema"] = ["file", "entries"]
    return ArtifactResult(
        name="route_index",
        file_name="ROUTE_INDEX.json",
        payload=payload,
        source_files=source_files,
        entity_count=route_count,
    )


def build_config_index(ctx: BuildContext) -> ArtifactResult:
    keys: dict[str, dict] = {}
    source_files: set[Path] = set()

    for project_root, artifacts in _child_artifacts(ctx):
        artifact = artifacts["config_index"]
        source_files.update(artifact.source_files)
        for item in artifact.payload["config_keys"]:
            entry = keys.setdefault(
                item["name"],
                {
                    "name": item["name"],
                    "types": set(),
                    "references": [],
                    "extractor": item["extractor"],
                    "confidence": item["confidence"],
                },
            )
            entry["types"].update(item.get("types", []))
            entry["references"].extend(_prefix_refs(ctx.root, project_root, item.get("references", [])))
            if item["confidence"] >= entry["confidence"]:
                entry["extractor"] = item["extractor"]
                entry["confidence"] = item["confidence"]

    payload = {
        "_meta": meta(ctx.root, "workspace_config_index_v1", source_files),
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


WORKSPACE_PLUGIN = WorkspacePlugin()
