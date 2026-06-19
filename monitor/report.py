from datetime import datetime

def create_html_report(data):

    filename = (
        f"report_{datetime.now():%Y%m%d_%H%M%S}.html"
    )

    html = f"""
    <html>
    <head>
        <title>System Report</title>
    </head>
    <body>
        <h1>Windows System Monitor Report</h1>
        <pre>{data}</pre>
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename
