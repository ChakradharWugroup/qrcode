import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# The issue: msg_confirm_clear in zh-CN block has no trailing comma
# The injected block ends with: msg_confirm_clear: '...'  (no comma at end)
# followed by: time_today: '...',
# This is missing the comma between them

# Fix: add comma after zh-CN msg_confirm_clear value
# Find all msg_confirm_clear occurrences
positions = []
idx = 0
while True:
    idx = content.find("msg_confirm_clear", idx)
    if idx == -1:
        break
    positions.append(idx)
    idx += 1

# For each one, find the end of its value and ensure there's a comma
for pos in positions:
    end_q = content.find("'", content.find(": '", pos) + 3)
    # Check what's after the closing quote
    after = content[end_q+1:end_q+5]
    # If it's just newline or spaces without comma, add it
    if not after.startswith(',') and not after.startswith("'"):
        content = content[:end_q+1] + ',' + content[end_q+1:]

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed missing commas after msg_confirm_clear!")
