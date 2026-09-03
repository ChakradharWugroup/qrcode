import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

broken_line = r"btn\.innerHTML = '<span class=\"i18n\" data-en=\"Syncing\.\.\.\" data-zh=\"[^\"]+\">\$\{i18n\[currentLang\]\['downloading'\] \|\| 'Downloading\.\.\.'\}</span>';"
fixed_line = "btn.innerHTML = `<span class=\"i18n\" data-en=\"Downloading...\" data-zh=\"下载中...\">${i18n[currentLang]['downloading'] || 'Downloading...'}</span>`;"

content = re.sub(broken_line, fixed_line, content)

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
