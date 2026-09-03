with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Change quantity input from type="number" to type="text"
old = '<input type="number" id="input-quantity" class="mt-1 w-full border border-gray-300 rounded px-2 py-2 text-sm">'
new = '<input type="text" id="input-quantity" class="mt-1 w-full border border-gray-300 rounded px-2 py-2 text-sm">'

if old in content:
    content = content.replace(old, new)
    print("Fixed!")
else:
    print("Not found - searching...")
    idx = content.find("input-quantity")
    print(repr(content[idx-20:idx+120]))

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
