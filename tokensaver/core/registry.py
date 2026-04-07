"""Plugin registry for TokenSaver."""

from __future__ import annotations

from tokensaver.core.plugin_api import TokenSaverPlugin
from tokensaver.plugins.flutter import FLUTTER_PLUGIN
from tokensaver.plugins.generic import GENERIC_PLUGIN
from tokensaver.plugins.go_mod import GO_PLUGIN
from tokensaver.plugins.nextjs import NEXTJS_PLUGIN
from tokensaver.plugins.python_web import PYTHON_WEB_PLUGIN
from tokensaver.plugins.react_native import REACT_NATIVE_PLUGIN
from tokensaver.plugins.spring_boot import SPRING_BOOT_PLUGIN

PLUGINS: tuple[TokenSaverPlugin, ...] = (
    FLUTTER_PLUGIN,
    REACT_NATIVE_PLUGIN,
    NEXTJS_PLUGIN,
    PYTHON_WEB_PLUGIN,
    SPRING_BOOT_PLUGIN,
    GO_PLUGIN,
    GENERIC_PLUGIN,
)


def get_plugin(framework: str) -> TokenSaverPlugin:
    for plugin in PLUGINS:
        if framework in plugin.frameworks:
            return plugin
    return GENERIC_PLUGIN
