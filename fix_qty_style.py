with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find and fix the Quantity label (blue styled) to match other gray fields
# Use index-based approach since Chinese chars cause print issues

idx = content.find('text-blue-700">Quantity')
if idx == -1:
    print("Not found with blue-700")
else:
    # Find the start of the label tag
    label_start = content.rfind('<label', 0, idx)
    # Find the end of the input tag after the label
    input_end = content.find('>', content.find('<input', label_start)) + 1
    
    old_block = content[label_start:input_end]
    
    # Build replacement: same style as other fields (gray label, normal input, no placeholder)
    # Get the quantity label text (including Chinese chars)
    label_text_start = content.find('>', idx) + 1
    label_text_end = content.find('</label>', label_text_start)
    label_text = content[label_text_start:label_text_end]
    
    new_block = '<label class="block text-[11px] font-bold text-gray-700">' + label_text + '</label>\n                        <input type="number" id="input-quantity" class="mt-1 w-full border border-gray-300 rounded px-2 py-2 text-sm">'
    
    content = content[:label_start] + new_block + content[input_end:]
    print("Fixed!")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
