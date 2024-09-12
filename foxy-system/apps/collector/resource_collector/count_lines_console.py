from io import StringIO
from rich.console import Console
from rich.text import Text


def count_lines(content, panel_width, content_type='panel'):
    panel_width  = panel_width
    buffer = StringIO()
    console = Console(file=buffer, width=panel_width)
    if content_type == 'text':
        content = Text.from_markup(content)
    console.print(content)
    content_output = buffer.getvalue()
    lines = content_output.splitlines()
    lines = [line for line in lines if line.strip()]
    return len(lines)
