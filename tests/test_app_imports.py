"""
Smoke test to verify app imports without NameError exceptions.

This test ensures that all router files can be imported without undefined
FastAPI primitive names (Depends, HTTPException, Query, Path, Body, status).
"""

import importlib
import pkgutil


def test_app_imports():
    """Test that the main app module imports without NameError."""
    importlib.import_module("api.app")


def test_all_router_modules_importable():
    """Test that all router modules import without undefined names."""
    import api.routers as routers_pkg

    router_modules = []
    for importer, modname, ispkg in pkgutil.iter_modules(routers_pkg.__path__, routers_pkg.__name__ + "."):
        if not ispkg:  # Only import actual modules, not subpackages
            router_modules.append(modname)

    for module_name in router_modules:
        # This will raise ImportError if the module has undefined names
        importlib.import_module(module_name)
