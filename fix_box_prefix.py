import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the createNewBox function - it uses cut_order_prefix from i18n
# Change prefix back to "Box" for English, and "箱子" for Chinese

content = content.replace("cut_order_prefix: 'Cut Order'", "cut_order_prefix: 'Box'")
content = content.replace("cut_order_prefix: '裁床单'", "cut_order_prefix: '箱子'")
content = content.replace("cut_order_prefix: '裁床單'", "cut_order_prefix: '箱子'")

# Also fix the regex pattern in createNewBox that matches box names
# It currently tries to match /Box (\d+)/ or /Cut Order (\d+)/
# Update it to use the i18n prefix so it always matches correctly
content = content.replace(
    'const match = b.match(/Box (\\d+)/);',
    'const prefix = i18n[currentLang]["cut_order_prefix"] || "Box"; const match = b.match(new RegExp(prefix.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&") + " (\\\\d+)"));'
)

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")
