"""
Point d'entrée de l'application.

Ce fichier est utilisé par PyInstaller (`VTFMaster.spec`).
Il doit rester minimal et stable pour faciliter les builds Windows.
"""

from __future__ import annotations


def main() -> int:
    from vtfmaster_clean import main as app_main

    return int(app_main())


if __name__ == "__main__":
    raise SystemExit(main())
 