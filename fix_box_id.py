import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# Use regex to replace the entire createNewBox function body up to newBoxName assignment
old_pattern = r'function createNewBox\(\) \{[\s\S]*?const newBoxName = `\$\{i18n\[currentLang\]\["cut_order_prefix"\]\} \$\{nextSeq\} - \$\{today\}`;'

new_code = '''function createNewBox() {
            // Generate unique box ID: YYYYMMDD-HH:MM:SS-XXXX
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const mins = String(now.getMinutes()).padStart(2, '0');
            const secs = String(now.getSeconds()).padStart(2, '0');
            const rand = Math.floor(1000 + Math.random() * 9000);
            const newBoxName = `${year}${month}${day}-${hours}:${mins}:${secs}-${rand}`;'''

match = re.search(old_pattern, content)
if match:
    content = content[:match.start()] + new_code + content[match.end():]
    print("Replaced via regex!")
else:
    print("Regex not matched, trying line-based approach...")
    # Find start and end of the old block manually
    start = content.find("function createNewBox()")
    # Find the newBoxName line
    nb_line = content.find("const newBoxName = `", start)
    # Find end of that line
    nb_end = content.find("`;\n", nb_line) + 3
    
    old_block = content[start:nb_end]
    print("Block to replace:", repr(old_block[:200]))
    
    content = content[:start] + new_code + content[nb_end:]
    print("Replaced via line approach!")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
