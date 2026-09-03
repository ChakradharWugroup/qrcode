with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Remove the extra '+' in the dictionaries
for i, line in enumerate(lines):
    if "start_new_box: '+New Box'" in line:
        lines[i] = line.replace("+New Box", "New Box")
    elif "start_new_box: '+新箱子'" in line:
        lines[i] = line.replace("+新箱子", "新箱子")

# We want to move the "createNewBox" button to right after "sync-summary" closes
button_start = -1
button_end = -1
sync_controls_start = -1
sync_summary_end = -1

for i, line in enumerate(lines):
    if '<button onclick="createNewBox()"' in line:
        button_start = i
    if button_start != -1 and button_end == -1 and '</button>' in line:
        button_end = i
    if '<div class="flex space-x-2 w-full">' in line:
        sync_controls_start = i
    if '<div id="sync-summary"' in line:
        # Find when sync-summary ends
        # It's an open div, contains another div, then closes. It's about 10 lines
        pass

# Since parsing HTML with lines is messy, let's use string split on the exact blocks
content = "".join(lines)

button_html = """        <button onclick="createNewBox()" class="w-full bg-blue-600 text-white py-4 rounded-lg font-bold text-xl hover:bg-blue-700 transition shadow-lg flex justify-center items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            <span data-i18n="start_new_box">Start New Box</span>
        </button>"""

if button_html in content:
    print("Found button HTML exactly.")
else:
    # try softer match
    import re
    m = re.search(r'<button onclick="createNewBox\(\)".*?</button>', content, re.DOTALL)
    if m:
        button_html = m.group(0)
        print("Found button HTML softly.")

# Find the sync controls + summary block
# The easiest way is to remove the button HTML from its original place, and insert it right before the "Your Boxes" section

content = content.replace(button_html, "")

insert_target = """        <div class="bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-lg font-bold mb-2 text-gray-800 border-b pb-2" data-i18n="your_boxes">Your Boxes</h2>"""

if insert_target in content:
    content = content.replace(insert_target, button_html + "\n\n" + insert_target)
    print("Successfully moved button before 'Your Boxes'!")
else:
    # Try soft match
    import re
    m = re.search(r'<div class="bg-white p-6 rounded-lg shadow-md">\s*<h2[^>]*data-i18n="your_boxes"', content)
    if m:
        content = content[:m.start()] + button_html + "\n\n        " + content[m.start():]
        print("Successfully moved button using soft match!")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

