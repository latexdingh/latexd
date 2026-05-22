# latexd

A lightweight daemon that exposes a local REST API for compiling LaTeX snippets to SVG or PNG — useful for note-taking integrations.

---

## Installation

```bash
pip install latexd
```

> **Requirements:** A working LaTeX distribution (e.g. [TeX Live](https://tug.org/texlive/) or [MiKTeX](https://miktex.org/)) must be installed on your system.

---

## Usage

Start the daemon:

```bash
latexd start
```

The server runs on `http://localhost:5731` by default.

### Compile a LaTeX snippet

```bash
curl -X POST http://localhost:5731/compile \
  -H "Content-Type: application/json" \
  -d '{"latex": "E = mc^2", "format": "svg"}'
```

**Response:**

```json
{
  "format": "svg",
  "data": "<svg xmlns=...>...</svg>"
}
```

### Supported formats

| Format | Description         |
|--------|---------------------|
| `svg`  | Scalable vector graphic |
| `png`  | Raster image (300 dpi) |

### Stop the daemon

```bash
latexd stop
```

---

## Configuration

| Option     | Default       | Description              |
|------------|---------------|--------------------------|
| `--port`   | `5731`        | Port to listen on        |
| `--host`   | `127.0.0.1`   | Host address             |
| `--dpi`    | `300`         | DPI for PNG output       |

---

## License

MIT © latexd contributors