"""mkg_docx - generation de documents Word a la charte MKG Consulting (V6).

Deux usages principaux :
- API Python directe via :class:`MKGDocument`.
- Spec declarative JSON via :func:`build_from_spec` / :func:`build_from_spec_file`.

Plus un mode de remise a la charte d'un .docx existant (:mod:`mkg_docx.reformat`).
"""
from __future__ import annotations

from .builder import MKGDocument
from .spec import build_from_spec, build_from_spec_file

__all__ = ["MKGDocument", "build_from_spec", "build_from_spec_file"]
