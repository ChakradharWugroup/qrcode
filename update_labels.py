import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace UI labels
replacements = [
    (r'>Company Name<', '>Customer<'),
    (r'>Company<', '>Customer<'),
    (r'>Bed No[^<]*<', '>Cut No.<'),
    (r'>Bed<', '>Cut No.<'),
    (r'>Quantity<', '>Qty<'),
    (r'col_box:\s*\'Box\'', 'col_box: \'Cut Order\''),
    (r'start_new_box:\s*\'Start New Box\'', 'start_new_box: \'Start New Cut Order\''),
    (r'your_boxes:\s*\'Your Boxes\'', 'your_boxes: \'Cut Orders\''),
    (r'back_to_boxes:\s*\'Back to Boxes\'', 'back_to_boxes: \'Back to Cut Orders\''),
    (r'no_boxes:\s*\'No boxes yet\.\'', 'no_boxes: \'No cut orders yet.\''),
    (r'no_items_box:\s*\'No items in this box yet\.\'', 'no_items_box: \'No items in this cut order yet.\''),
    (r'total_scans:\s*\'Total Factory Scans: \'', 'total_scans: \'Total Cut Qty: \''),
    (r'const newBoxName = `Box \$\{nextSeq\} - \$\{today\}`;', 'const newBoxName = `Cut Order ${nextSeq} - ${today}`;'),
    (r'alert\("Box is empty!', 'alert("Cut Order is empty!'),
    (r'csvContent \+= "Box Name,', 'csvContent += "Cut Order Name,'),
    (r'let qrText = `Box:', 'let qrText = `Cut Order:'),
    (r'>Currently Scanning Into:<', '>Currently Scanning Into Cut Order:<')
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated offline_app.html successfully.")
