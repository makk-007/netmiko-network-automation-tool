from datetime import datetime
from pathlib import Path
from .utils import parse_output


def generate_report(
    results: dict,
    commands: list[str],
    output_dir: str = "outputs",
) -> str:
    """Generate a self-contained HTML report from command results.

    Args:
        results: Dictionary mapping device name to raw output string,
                 as returned by run_commands().
        commands: List of commands that were run.
        output_dir: Directory where the report file is saved.

    Returns:
        Path to the generated HTML report file.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    device_sections = ""

    for device, raw in results.items():
        command_blocks = raw.split("\n\n")
        tables_html = ""

        for block in command_blocks:
            lines = block.strip().splitlines()
            if not lines:
                continue

            command = lines[0].replace("### ", "")
            output = "\n".join(lines[1:])
            parsed = parse_output(command, output)

            if parsed and len(parsed) > 0:
                headers = list(parsed[0].keys())
                header_row = "".join(f"<th>{h}</th>" for h in headers)
                data_rows = ""
                for row in parsed:
                    cells = "".join(f"<td>{row[h]}</td>" for h in headers)
                    data_rows += f"<tr>{cells}</tr>\n"

                tables_html += f"""
                <div class="command-block">
                    <h3 class="command-title">{command}</h3>
                    <table>
                        <thead><tr>{header_row}</tr></thead>
                        <tbody>{data_rows}</tbody>
                    </table>
                </div>
                """
            else:
                escaped = output.replace("<", "&lt;").replace(">", "&gt;")
                tables_html += f"""
                <div class="command-block">
                    <h3 class="command-title">{command}</h3>
                    <pre>{escaped}</pre>
                </div>
                """

        device_sections += f"""
        <div class="device-card">
            <h2 class="device-title">{device}</h2>
            {tables_html}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Automation Report -- {timestamp}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 2rem;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid #334155;
            padding-bottom: 1rem;
        }}
        header h1 {{
            font-size: 1.5rem;
            color: #38bdf8;
            margin-bottom: 0.25rem;
        }}
        header p {{
            font-size: 0.875rem;
            color: #94a3b8;
        }}
        .device-card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .device-title {{
            font-size: 1.125rem;
            color: #38bdf8;
            margin-bottom: 1rem;
        }}
        .command-block {{
            margin-bottom: 1.25rem;
        }}
        .command-title {{
            font-size: 0.8rem;
            font-family: monospace;
            color: #a78bfa;
            margin-bottom: 0.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        th {{
            background: #0f172a;
            color: #94a3b8;
            text-align: left;
            padding: 0.5rem 0.75rem;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        td {{
            padding: 0.5rem 0.75rem;
            border-top: 1px solid #334155;
            font-family: monospace;
            font-size: 0.8rem;
            color: #cbd5e1;
        }}
        tr:hover td {{ background: #334155; }}
        pre {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 4px;
            padding: 0.75rem;
            font-size: 0.8rem;
            font-family: monospace;
            color: #cbd5e1;
            white-space: pre-wrap;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Network Automation Report</h1>
        <p>Generated: {timestamp} &nbsp;|&nbsp; Commands: {', '.join(commands)}</p>
    </header>
    {device_sections}
</body>
</html>"""

    filename = f"{timestamp}-report.html"
    file_path = output_path / filename
    file_path.write_text(html)
    print(f"[+] Report saved to {file_path}")
    return str(file_path)
