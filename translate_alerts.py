with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# ─── Step 1: Add all message translations into each i18n dictionary ───

# English additions to insert after 'clear_warning'
en_msgs = """
                  msg_phone_full: 'Phone memory full. Cannot save.',
                  msg_box_empty: 'Box is empty! Please scan items first.',
                  msg_sync_ok: 'Successfully downloaded {count} tickets!',
                  msg_sync_err: 'Sync Error: ',
                  msg_server_err: 'Server Error: ',
                  msg_network_err: 'Network error: ',
                  msg_camera_err: 'Camera error. Please allow camera permissions in Settings.',
                  msg_scan_qty: 'Please scan a QR code and enter a quantity!',
                  msg_duplicate: 'DUPLICATE: This QR code is already in this box!',
                  msg_offline: 'You are offline. Please connect to the internet first.',
                  msg_all_synced: 'All items are already uploaded to the cloud!',
                  msg_push_ok: 'Successfully uploaded {count} tickets to the cloud!',
                  msg_push_err: 'Server error. Could not upload to cloud.',
                  msg_push_net: 'Network error. Make sure the server is reachable.',
                  msg_db_cleared: 'Local data cleared from phone.',
                  msg_db_empty: 'No data found!',
                  msg_confirm_clear: 'All data has been safely uploaded. Clear phone memory to start fresh?',
"""

zh_cn_msgs = """
                  msg_phone_full: '手机存储已满，无法保存。',
                  msg_box_empty: '箱子是空的！请先扫描菲票。',
                  msg_sync_ok: '成功下载 {count} 张菲票！',
                  msg_sync_err: '同步错误：',
                  msg_server_err: '服务器错误：',
                  msg_network_err: '网络错误：',
                  msg_camera_err: '摄像头错误。请在设置中允许摄像头权限。',
                  msg_scan_qty: '请扫描二维码并输入数量！',
                  msg_duplicate: '重复警告：此二维码已在此箱子中！',
                  msg_offline: '您当前处于离线状态，请先连接网络。',
                  msg_all_synced: '所有数据已上传到云端！',
                  msg_push_ok: '成功上传 {count} 张菲票到云端！',
                  msg_push_err: '服务器错误，无法上传到云端。',
                  msg_push_net: '网络错误，请确认服务器可以访问。',
                  msg_db_cleared: '本地数据已从手机中清除。',
                  msg_db_empty: '没有数据！',
                  msg_confirm_clear: '所有数据已安全上传。是否清除手机内存以开始新的工作？',
"""

zh_tw_msgs = """
                  msg_phone_full: '手機儲存已滿，無法儲存。',
                  msg_box_empty: '箱子是空的！請先掃描菲票。',
                  msg_sync_ok: '成功下載 {count} 張菲票！',
                  msg_sync_err: '同步錯誤：',
                  msg_server_err: '伺服器錯誤：',
                  msg_network_err: '網路錯誤：',
                  msg_camera_err: '相機錯誤。請在設定中允許相機權限。',
                  msg_scan_qty: '請掃描二維碼並輸入數量！',
                  msg_duplicate: '重複警告：此二維碼已在此箱子中！',
                  msg_offline: '您目前處於離線狀態，請先連線網路。',
                  msg_all_synced: '所有資料已上傳至雲端！',
                  msg_push_ok: '成功上傳 {count} 張菲票至雲端！',
                  msg_push_err: '伺服器錯誤，無法上傳至雲端。',
                  msg_push_net: '網路錯誤，請確認伺服器可以存取。',
                  msg_db_cleared: '本地資料已從手機清除。',
                  msg_db_empty: '沒有資料！',
                  msg_confirm_clear: '所有資料已安全上傳。是否清除手機記憶體以開始新工作？',
"""

# Helper function to inject messages into each i18n block
def inject_after(text, marker, injection):
    idx = text.find(marker)
    if idx == -1:
        return text, False
    insert_at = idx + len(marker)
    return text[:insert_at] + injection + text[insert_at:], True

# Inject into en block (find unique marker)
content, ok = inject_after(content, "clear_warning: 'ERROR! {count} pending tickets have not been uploaded.',", en_msgs)
print("EN injected:", ok)

# Inject into zh-CN block
content, ok = inject_after(content, "clear_warning: '错误！{count} 张菲票尚未上传',", zh_cn_msgs)
print("ZH-CN injected:", ok)

# Inject into zh-TW block
content, ok = inject_after(content, "clear_warning: '錯誤！{count} 張菲票尚未上傳',", zh_tw_msgs)
print("ZH-TW injected:", ok)

# ─── Step 2: Replace all hardcoded alert() calls with i18n versions ───
def t(key, replace_map=None):
    """Generate i18n alert call"""
    s = f"i18n[currentLang]['{key}']"
    if replace_map:
        for placeholder, val in replace_map.items():
            s = f"{s}.replace('{placeholder}', {val})"
    return s

replacements = [
    (
        'alert("Phone memory full. Cannot save.")',
        f'alert({t("msg_phone_full")})'
    ),
    (
        'alert("Cut Order is empty! Please scan items first.")',
        f'alert({t("msg_box_empty")})'
    ),
    (
        'alert(`Successfully synced ${data.total_tickets} tickets from Qiaofei!`)',
        f'alert({t("msg_sync_ok")}.replace("{{count}}", data.total_tickets))'
    ),
    (
        'alert("Error: " + data.error)',
        f'alert({t("msg_sync_err")} + data.error)'
    ),
    (
        'alert("Server Error " + response.status + ": " + errText)',
        f'alert({t("msg_server_err")} + response.status + ": " + errText)'
    ),
    (
        'alert("Network error: " + err.message)',
        f'alert({t("msg_network_err")} + err.message)'
    ),
    (
        'alert("Camera error. Please allow camera permissions.")',
        f'alert({t("msg_camera_err")})'
    ),
    (
        'alert("Please scan a QR and enter a quantity!")',
        f'alert({t("msg_scan_qty")})'
    ),
    (
        'alert("DUPLICATE WARNING: This QR code is already in this box!")',
        f'alert({t("msg_duplicate")})'
    ),
    (
        'alert("You are currently offline. Please connect to the internet first.")',
        f'alert({t("msg_offline")})'
    ),
    (
        'alert("All items are already pushed to the cloud!")',
        f'alert({t("msg_all_synced")})'
    ),
    (
        'alert(`Successfully pushed ${unsynced.length} items to the cloud!`)',
        f'alert({t("msg_push_ok")}.replace("{{count}}", unsynced.length))'
    ),
    (
        'alert("Server error. Could not push to cloud.\\n\\nDetails: " + errText)',
        f'alert({t("msg_push_err")} + "\\n" + errText)'
    ),
    (
        'alert("Network error. Make sure the server is reachable.")',
        f'alert({t("msg_push_net")})'
    ),
    (
        'alert("Database cleared from phone.")',
        f'alert({t("msg_db_cleared")})'
    ),
    (
        'alert("Database is empty!")',
        f'alert({t("msg_db_empty")})'
    ),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND: {old[:60]}...")

# Also fix the confirm() dialog in clearDatabase
old_confirm = 'confirm("All data has been safely pushed to the cloud. Are you sure you want to clear the phone\'s memory to start fresh?")'
new_confirm = f'confirm({t("msg_confirm_clear")})'
if old_confirm in content:
    content = content.replace(old_confirm, new_confirm)
    print("Replaced confirm dialog!")
else:
    print("Confirm dialog NOT FOUND - checking...")
    idx = content.find('confirm(')
    if idx != -1:
        print(repr(content[idx:idx+150]))

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
print("\nDone!")
