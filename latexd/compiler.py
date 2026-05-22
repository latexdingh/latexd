"""Core LaTeX compilation logic: LaTeX source -> DVI/PDF -> SVG/PNG."""

import subprocess
import tempfile
import shutil
import os
from pathlib import Path

LATEX_TEMPLATE = r"""
\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\begin{document}
%s
\end{document}
"""


class CompilationError(Exception):
    """Raised when LaTeX compilation or conversion fails."""
    def __init__(self, message: str, log: str = ""):
        super().__init__(message)
        self.log = log


def _run(cmd: list[str], cwd: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
    )


def compile_latex(snippet: str, output_format: str = "svg", dpi: int = 150) -> bytes:
    """Compile a LaTeX snippet and return the rendered image bytes.

    Args:
        snippet: Raw LaTeX content (e.g. ``$E=mc^2$``).
        output_format: ``'svg'`` or ``'png'``.
        dpi: Resolution for PNG output (ignored for SVG).

    Returns:
        Rendered image as bytes.

    Raises:
        CompilationError: If any step of the pipeline fails.
        ValueError: If *output_format* is unsupported.
    """
    if output_format not in ("svg", "png"):
        raise ValueError(f"Unsupported output format: {output_format!r}")

    tmpdir = tempfile.mkdtemp(prefix="latexd_")
    try:
        tex_path = os.path.join(tmpdir, "input.tex")
        Path(tex_path).write_text(LATEX_TEMPLATE % snippet)

        # Step 1: latex -> dvi
        result = _run(["latex", "-interaction=nonstopmode", "input.tex"], cwd=tmpdir)
        if result.returncode != 0:
            raise CompilationError("LaTeX compilation failed.", result.stdout + result.stderr)

        dvi_path = os.path.join(tmpdir, "input.dvi")

        if output_format == "svg":
            result = _run(["dvisvgm", "--no-fonts", "--exact", "input.dvi", "-o", "output.svg"], cwd=tmpdir)
            if result.returncode != 0:
                raise CompilationError("dvisvgm conversion failed.", result.stderr)
            return Path(os.path.join(tmpdir, "output.svg")).read_bytes()

        # PNG path: dvi -> png via dvipng
        result = _run(
            ["dvipng", "-D", str(dpi), "-T", "tight", "-bg", "Transparent",
             "-o", "output.png", dvi_path],
            cwd=tmpdir,
        )
        if result.returncode != 0:
            raise CompilationError("dvipng conversion failed.", result.stderr)
        return Path(os.path.join(tmpdir, "output.png")).read_bytes()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
