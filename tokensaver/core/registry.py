"""Plugin registry for TokenSaver."""

from __future__ import annotations

from tokensaver.core.plugin_api import TokenSaverPlugin
from tokensaver.plugins.flutter import FLUTTER_PLUGIN
from tokensaver.plugins.generic import GENERIC_PLUGIN
from tokensaver.plugins.react_native import REACT_NATIVE_PLUGIN

PLUGINS: tuple[TokenSaverPlugin, ...] = (
    FLUTTER_PLUGIN,
    REACT_NATIVE_PLUGIN,
    GENERIC_PLUGIN,
)


def get_plugin(framework: str) -> TokenSaverPlugin:
    for plugin in PLUGINS:
        if framework in plugin.frameworks:
            return plugin
    return GENERIC_PLUGIN
