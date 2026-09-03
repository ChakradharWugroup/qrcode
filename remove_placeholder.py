with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Remove placeholder from TID input field
content = content.replace('placeholder="Scan above or type here..."', '')
content = content.replace("placeholder='Scan above or type here...'", '')

# Also remove from i18n-placeholder attribute if used
content = content.replace('data-i18n-placeholder="scan_placeholder"', '')

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done!")
