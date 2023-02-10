from __future__ import annotations
from typing import Type, TypeVar, Callable, Optional, Union
import typing as t
import os
from flask import Flask, g, Blueprint
from shared.dependencies import Dependencies as Deps

T = TypeVar("T")


class DependencyBlueprint(Blueprint):
    def __init__(self,
                 name: str, import_name: str, static_folder: t.Optional[t.Union[str, os.PathLike]] = None,
                 static_url_path: t.Optional[str] = None, template_folder: t.Optional[str] = None,
                 url_prefix: t.Optional[str] = None, subdomain: t.Optional[str] = None,
                 url_defaults: t.Optional[dict] = None,
                 root_path: t.Optional[str] = None, cli_group: t.Optional[str] = ...):
        super().__init__(name, import_name, static_folder, static_url_path,
                         template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group)
        self._dependency_setup = None

    def register_dependencies(self, reg: Callable[[Deps], Optional[Deps]]) -> DependencyBlueprint:
        self._dependency_setup = reg
        return self

    def apply_dependencies(self, deps: Deps) -> Deps:
        if self._dependency_setup is None:
            return deps

        self._dependency_setup(deps)
        return deps


class Dependencies:
    def __init__(self, app: Flask):
        app.before_first_request(self.before_request)
        app.before_request(self.before_request)
        self._deps = Deps()
        self._app = app

    def before_request(self):
        g.dependencies = self._deps

    def register_with(self, reg: Callable[[Deps], Optional[Deps]]) -> Dependencies:
        reg(self._deps)
        return self

    def register_blueprint(self, blueprint: Union[Blueprint, DependencyBlueprint], **options: t.Any) -> None:
        if isinstance(blueprint, DependencyBlueprint):
            blueprint.apply_dependencies(self._deps)
        self._app.register_blueprint(blueprint, **options)


def get_dependency(t: Type[T]) -> T:
    return g.dependencies.get(t)
