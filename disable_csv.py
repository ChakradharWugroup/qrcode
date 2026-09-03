with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

old = 'onclick="exportCSV()" class="w-full bg-gray-800 text-white py-3 rounded-lg font-bold hover:bg-gray-900 transition flex justify-center items-center shadow"'
new = 'disabled class="w-full bg-gray-400 text-gray-200 py-3 rounded-lg font-bold flex justify-center items-center shadow cursor-not-allowed opacity-50"'

if old in content:
    content = content.replace(old, new)
    print("Disabled!")
else:
    print("Not found")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
