with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("parts.push(`Bed: ${bed}`);", "parts.push(`Cut No.: ${bed}`);")
content = content.replace("parts.push(`Company: ${company}`);", "parts.push(`Customer: ${company}`);")
# Also check if it's in the print string
content = content.replace("Company: ${company}", "Customer: ${company}")
content = content.replace("Bed: ${bed}", "Cut No.: ${bed}")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
