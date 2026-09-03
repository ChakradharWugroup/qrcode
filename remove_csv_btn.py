import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Remove the entire export CSV button block
pattern = r'\s*<button disabled[^>]*>[\s\S]*?Export All Data[^<]*\(CSV\)[\s\S]*?</button>'
new_content = re.sub(pattern, '', content)

if new_content != content:
    print("Removed CSV button!")
else:
    print("Not found by regex, trying string search...")
    idx = content.find('exportCSV')
    print(repr(content[idx-50:idx+300]))

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(new_content)
