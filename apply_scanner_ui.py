import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update English i18n
replacements_en = [
    (r"scanning_into:\s*'[^']*'", "scanning_into: 'Box ID'"),
    (r"live_scanner:\s*'[^']*'", "live_scanner: 'Scan Ticket'"),
    (r"open_camera:\s*'[^']*'", "open_camera: 'Open Camera'"),
    (r"review_add:\s*'[^']*'", "review_add: 'Ticket Info'"),
    (r"save_to_phone:\s*'[^']*'", "save_to_phone: 'Save'"),
    (r"items_in:\s*'[^']*'", "items_in: 'Box Details: '"),
    (r"print_qr_code:\s*'[^']*'", "print_qr_code: 'Print QR Code'"),
]

# 2. Update Simplified Chinese i18n
replacements_zh_cn = [
    (r"scanning_into:\s*'[^']*'", "scanning_into: '箱号'"),
    (r"live_scanner:\s*'[^']*'", "live_scanner: '扫菲'"),
    (r"open_camera:\s*'[^']*'", "open_camera: '点击扫菲'"),
    (r"review_add:\s*'[^']*'", "review_add: '菲票信息'"),
    (r"save_to_phone:\s*'[^']*'", "save_to_phone: '保存'"),
    (r"items_in:\s*'[^']*'", "items_in: '装箱明细: '"),
    (r"print_qr_code:\s*'[^']*'", "print_qr_code: '打印二维码'"),
]

# 3. Update Traditional Chinese i18n
replacements_zh_tw = [
    (r"scanning_into:\s*'[^']*'", "scanning_into: '箱號'"),
    (r"live_scanner:\s*'[^']*'", "live_scanner: '掃菲'"),
    (r"open_camera:\s*'[^']*'", "open_camera: '點擊掃菲'"),
    (r"review_add:\s*'[^']*'", "review_add: '菲票資訊'"),
    (r"save_to_phone:\s*'[^']*'", "save_to_phone: '儲存'"),
    (r"items_in:\s*'[^']*'", "items_in: '裝箱明細: '"),
    (r"print_qr_code:\s*'[^']*'", "print_qr_code: '列印二維碼'"),
]

en_block_match = re.search(r"'en': \{(.*?)\},(\s*)'zh-CN'", content, re.DOTALL)
zh_cn_block_match = re.search(r"'zh-CN': \{(.*?)\},(\s*)'zh-TW'", content, re.DOTALL)
zh_tw_block_match = re.search(r"'zh-TW': \{(.*?)\}(\s*)\};", content, re.DOTALL)

if en_block_match and zh_cn_block_match and zh_tw_block_match:
    en_block = en_block_match.group(1)
    zh_cn_block = zh_cn_block_match.group(1)
    zh_tw_block = zh_tw_block_match.group(1)
    
    for p, r in replacements_en:
        en_block = re.sub(p, r, en_block)
    for p, r in replacements_zh_cn:
        zh_cn_block = re.sub(p, r, zh_cn_block)
    for p, r in replacements_zh_tw:
        zh_tw_block = re.sub(p, r, zh_tw_block)
        
    content = content[:en_block_match.start(1)] + en_block + content[en_block_match.end(1):]
    
    zh_cn_block_match = re.search(r"'zh-CN': \{(.*?)\},(\s*)'zh-TW'", content, re.DOTALL)
    content = content[:zh_cn_block_match.start(1)] + zh_cn_block + content[zh_cn_block_match.end(1):]
    
    zh_tw_block_match = re.search(r"'zh-TW': \{(.*?)\}(\s*)\};", content, re.DOTALL)
    content = content[:zh_tw_block_match.start(1)] + zh_tw_block + content[zh_tw_block_match.end(1):]

# 4. Remove the hardcoded ' Cut Order:' from 'Currently Scanning Into Cut Order:' in HTML
# Because the translation key `scanning_into` now says "Box ID" entirely.
content = content.replace('data-i18n="scanning_into">Currently Scanning Into Cut Order:</p>', 'data-i18n="scanning_into">Box ID</p>')

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied strict UI terminology replacements for scanning view.")
