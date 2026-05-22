"""Configuration management for latexd."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Runtime configuration for the latexd daemon."""

    # Server settings
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False

    # Compiler settings
    pdflatex_path: str = "pdflatex"
    inkscape_path: str = "inkscape"
    compile_timeout: int = 30  # seconds

    # Cache settings
    cache_enabled: bool = True
    cache_dir: Optional[str] = None  # None means use system temp dir
    cache_max_entries: int = 256

    # LaTeX document settings
    latex_packages: list = field(
        default_factory=lambda: ["amsmath", "amssymb", "amsfonts"]
    )
    latex_font_size: str = "12pt"
    latex_document_class: str = "standalone"

    @classmethod
    def from_env(cls) -> "Config":
        """Build a Config instance from environment variables."""
        return cls(
            host=os.environ.get("LATEXD_HOST", "127.0.0.1"),
            port=int(os.environ.get("LATEXD_PORT", "5000")),
            debug=os.environ.get("LATEXD_DEBUG", "").lower() in ("1", "true", "yes"),
            pdflatex_path=os.environ.get("LATEXD_PDFLATEX", "pdflatex"),
            inkscape_path=os.environ.get("LATEXD_INKSCAPE", "inkscape"),
            compile_timeout=int(os.environ.get("LATEXD_TIMEOUT", "30")),
            cache_enabled=os.environ.get("LATEXD_CACHE_ENABLED", "1").lower()
            not in ("0", "false", "no"),
            cache_dir=os.environ.get("LATEXD_CACHE_DIR") or None,
            cache_max_entries=int(os.environ.get("LATEXD_CACHE_MAX", "256")),
            latex_font_size=os.environ.get("LATEXD_FONT_SIZE", "12pt"),
            latex_document_class=os.environ.get(
                "LATEXD_DOCUMENT_CLASS", "standalone"
            ),
        )

    def latex_packages_str(self) -> str:
        """Return \\usepackage lines for all configured packages."""
        return "\n".join(
            f"\\usepackage{{{pkg}}}" for pkg in self.latex_packages
        )
