from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pkgutil import iter_modules
from typing import Callable, Dict, Iterable, Optional


@dataclass(frozen=True)
class PageDefinition:
    slug: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    render: Callable[..., None] | None = None


_registry: Dict[str, PageDefinition] = {}
_modules_loaded = False


def register(page: PageDefinition) -> None:
    if page.slug in _registry:
        raise ValueError(f"Page with slug '{page.slug}' already registered")
    if page.render is None:
        raise ValueError("Page definition requires a render callable")
    _registry[page.slug] = page


def page(slug: str, *, title: str, description: str | None = None, icon: str | None = None):
    """Decorator used by page modules to register their render function."""

    def decorator(func: Callable[..., None]) -> Callable[..., None]:
        register(
            PageDefinition(
                slug=slug,
                title=title,
                description=description,
                icon=icon,
                render=func,
            )
        )
        return func

    return decorator


def ensure_loaded() -> None:
    global _modules_loaded
    if _modules_loaded:
        return

    package = __name__.rsplit(".", 1)[0]
    package_module = import_module(package)
    package_path = getattr(package_module, "__path__", None)
    if not package_path:
        return

    for module_info in iter_modules(package_path):
        name = module_info.name
        if name.startswith("_") or name == "registry":
            continue
        import_module(f"{package}.{name}")

    _modules_loaded = True


def get(slug: str) -> Optional[PageDefinition]:
    return _registry.get(slug)


def all_pages() -> Iterable[PageDefinition]:
    return _registry.values()
