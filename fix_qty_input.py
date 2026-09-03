with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add inputmode="numeric" and pattern to force number keypad on mobile
old = '<input type="text" id="input-quantity" class="mt-1 w-full border border-gray-300 rounded px-2 py-2 text-sm">'
new = '<input type="text" inputmode="numeric" pattern="[0-9]*" id="input-quantity" class="mt-1 w-full border border-gray-300 rounded px-2 py-2 text-sm">'

if old in content:
    content = content.replace(old, new)
    print("Fixed!")
else:
    print("Not found")
    idx = content.find("input-quantity")
    print(repr(content[idx-10:idx+150]))

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
