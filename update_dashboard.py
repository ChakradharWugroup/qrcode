with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("Create New Box / Collection", "Create New Cut Order")
content = content.replace("Your Collections", "Your Cut Orders")
content = content.replace("Box 1, Box 2, Summer Batch...", "Cut Order 1, Cut Order 2...")
content = content.replace("No collections yet.", "No cut orders yet.")

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
