import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update English i18n
replacements_en = [
    (r"start_new_box:\s*'[^']*'", "start_new_box: '+New Box'"),
    (r"your_boxes:\s*'[^']*'", "your_boxes: 'Box List'"),
    (r"sync_qiaofei:\s*'[^']*'", "sync_qiaofei: 'Download Tickets'"),
    (r"database_options:\s*'[^']*'", "database_options: 'Tickets Manage'"),
    (r"total_scans:\s*'[^']*'", "total_scans: 'Total Tickets: '"),
    (r"push_cloud:\s*'[^']*'", "push_cloud: 'Upload to Cloud'"),
    (r"clear_data:\s*'[^']*'", "clear_data: 'Clear Local Tickets'"),
    (r"global_history:\s*'[^']*'", "global_history: 'Local Added Tickets'"),
    (r"tickets_ready:\s*'[^']*'", "tickets_ready: 'Tickets Downloaded'"),
]

# 2. Update Simplified Chinese i18n
replacements_zh_cn = [
    (r"start_new_box:\s*'撘€憪蝞勗\?'|start_new_box:\s*'[^']*'", "start_new_box: '+新箱子'"),
    (r"your_boxes:\s*'\?函\?蝞勗\?'|your_boxes:\s*'[^']*'", "your_boxes: '箱子列表'"),
    (r"sync_qiaofei:\s*'同步 ERP 数据'|sync_qiaofei:\s*'[^']*'", "sync_qiaofei: '下载菲票'"),
    (r"database_options:\s*'\?唳摨€★'|database_options:\s*'[^']*'", "database_options: '菲票管理'"),
    (r"total_scans:\s*'撌亙\?\?餅\?\?: '|total_scans:\s*'[^']*'", "total_scans: '菲票数: '"),
    (r"push_cloud:\s*'\?券€鈭垢\?唳摨\?'|push_cloud:\s*'[^']*'", "push_cloud: '上传云端'"),
    (r"clear_data:\s*'皜\?€\?\?\?'|clear_data:\s*'[^']*'", "clear_data: '清除本地菲票'"),
    (r"global_history:\s*'\?典\?\?急\?\?'|global_history:\s*'[^']*'", "global_history: '本地新增菲票'"),
    (r"tickets_ready:\s*'张菲票已就绪'|tickets_ready:\s*'[^']*'", "tickets_ready: '菲票已下载'"),
]

# 3. Update Traditional Chinese i18n
replacements_zh_tw = [
    (r"start_new_box:\s*'\?\?\?啁拳摮\?'|start_new_box:\s*'[^']*'", "start_new_box: '+新箱子'"),
    (r"your_boxes:\s*'\?函\?蝞勗\?'|your_boxes:\s*'[^']*'", "your_boxes: '箱子列表'"),
    (r"sync_qiaofei:\s*'同步 ERP 數據'|sync_qiaofei:\s*'[^']*'", "sync_qiaofei: '下載菲票'"),
    (r"database_options:\s*'鞈\?摨恍\?\?'|database_options:\s*'[^']*'", "database_options: '菲票管理'"),
    (r"total_scans:\s*'撌亙\?蝮賣\?\?\?: '|total_scans:\s*'[^']*'", "total_scans: '菲票數: '"),
    (r"push_cloud:\s*'\?券€\?脩垢鞈\?摨\?'|push_cloud:\s*'[^']*'", "push_cloud: '上傳雲端'"),
    (r"clear_data:\s*'皜\?€\?\?\?\?'|clear_data:\s*'[^']*'", "clear_data: '清除本地菲票'"),
    (r"global_history:\s*'\?典\?\?\?甇瑕'|global_history:\s*'[^']*'", "global_history: '本地新增菲票'"),
    (r"tickets_ready:\s*'張菲票已就緒'|tickets_ready:\s*'[^']*'", "tickets_ready: '菲票已下載'"),
]

# Because the file contains all 3 dicts sequentially, it's safer to isolate blocks
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
    
    # re-find because indices changed
    zh_cn_block_match = re.search(r"'zh-CN': \{(.*?)\},(\s*)'zh-TW'", content, re.DOTALL)
    content = content[:zh_cn_block_match.start(1)] + zh_cn_block + content[zh_cn_block_match.end(1):]
    
    zh_tw_block_match = re.search(r"'zh-TW': \{(.*?)\}(\s*)\};", content, re.DOTALL)
    content = content[:zh_tw_block_match.start(1)] + zh_tw_block + content[zh_tw_block_match.end(1):]

# 4. Javascript fixes
# Fix "Syncing..." to "Downloading..."
content = content.replace("> Syncing...<", "> Downloading...<")
content = content.replace("Syncing...`;", "${i18n[currentLang]['downloading'] || 'Downloading...'}`;")
content = content.replace("Syncing...<", "${i18n[currentLang]['downloading'] || 'Downloading...'}<")

# Add downloading translation to the injected blocks
content = content.replace("time_today: 'Today',", "downloading: 'Downloading...',\n                  time_today: 'Today',")
content = content.replace("time_today: '今天',", "downloading: '下载中...',\n                  time_today: '今天',")
content = content.replace("time_today: '今天',", "downloading: '下載中...',\n                  time_today: '今天',") # zh-TW has 今天 too based on script above

# Fix Alert message for Clear All Data
old_alert_code = """alert(`STOP! You have ${unsyncedCount} pending items that have not been pushed to the cloud database.\\n\\nPlease connect to the internet and click "<span data-i18n="push_cloud">Push to Cloud Database</span>" before clearing your data!`);"""
new_alert_code = """alert(i18n[currentLang]['clear_warning'] ? i18n[currentLang]['clear_warning'].replace('{count}', unsyncedCount) : `ERROR! ${unsyncedCount} pending tickets have not been uploaded.`);"""
content = content.replace(old_alert_code, new_alert_code)

# Add clear_warning translation
content = content.replace("time_today: 'Today',", "clear_warning: 'ERROR! {count} pending tickets have not been uploaded.',\n                  time_today: 'Today',")
content = content.replace("time_today: '今天',", "clear_warning: '錯誤！{count} 張菲票尚未上傳',\n                  time_today: '今天',")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied strict UI terminology replacements.")
