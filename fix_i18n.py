import re

with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update <select> options for time range
content = content.replace('<option value="today">Today</option>', '<option value="today" data-i18n="time_today">Today</option>')
content = content.replace('<option value="yesterday">Yesterday</option>', '<option value="yesterday" data-i18n="time_yesterday">Yesterday</option>')
content = content.replace('<option value="week">This Week</option>', '<option value="week" data-i18n="time_week">This Week</option>')
content = content.replace('<option value="month" selected>This Month</option>', '<option value="month" selected data-i18n="time_month">This Month</option>')
content = content.replace('<option value="3months">Last 3 Months</option>', '<option value="3months" data-i18n="time_3months">Last 3 Months</option>')

# 2. Update Time Range label
content = content.replace('>Time Range</div>', ' data-i18n="time_range">Time Range</div>')

# 3. Update View Data link
content = content.replace('>View Data</span>', ' data-i18n="view_data">View Data</span>')

# 4. Wrap "Open Camera" in a span for i18n
content = re.sub(
    r'(<button id="start-scan-btn"[^>]*>[\s\S]*?</svg>)\s*Open Camera\s*(</button>)',
    r'\1\n                <span data-i18n="open_camera">Open Camera</span>\n            \2',
    content
)

# 5. Fix Javascript hardcodings
content = content.replace(
    'document.getElementById(\'sync-summary-text\').innerText = `${keys.length} Master Tickets Ready`;',
    'document.getElementById(\'sync-summary-text\').innerText = `${keys.length} ${i18n[currentLang]["tickets_ready"]}`;'
)
content = content.replace(
    '0 tickets loaded',
    '<span data-i18n="zero_tickets">0 tickets loaded</span>'
)
content = content.replace(
    '<button onclick="resumeBox(\'${box}\')" class="bg-blue-100 text-blue-700 px-4 py-2 rounded text-sm font-bold border border-blue-300 hover:bg-blue-200">\n                        Open\n                    </button>',
    '<button onclick="resumeBox(\'${box}\')" class="bg-blue-100 text-blue-700 px-4 py-2 rounded text-sm font-bold border border-blue-300 hover:bg-blue-200">\n                        ${i18n[currentLang]["open_btn"]}\n                    </button>'
)
content = content.replace(
    'const newBoxName = `Cut Order ${nextSeq} - ${today}`;',
    'const newBoxName = `${i18n[currentLang]["cut_order_prefix"]} ${nextSeq} - ${today}`;'
)

# 6. Inject the missing translations into the i18n dictionary for English
en_insert = """
                  time_today: 'Today',
                  time_yesterday: 'Yesterday',
                  time_week: 'This Week',
                  time_month: 'This Month',
                  time_3months: 'Last 3 Months',
                  time_range: 'Time Range',
                  view_data: 'View Data',
                  tickets_ready: 'Master Tickets Ready',
                  zero_tickets: '0 tickets loaded',
                  cut_order_prefix: 'Cut Order',
"""
content = content.replace("title: '100% Offline QR App',", "title: '100% Offline QR App'," + en_insert)

# Inject for zh-CN
zh_cn_insert = """
                  time_today: '今天',
                  time_yesterday: '昨天',
                  time_week: '本周',
                  time_month: '本月',
                  time_3months: '最近3个月',
                  time_range: '时间范围',
                  view_data: '查看数据',
                  tickets_ready: '张菲票已就绪',
                  zero_tickets: '0 张菲票',
                  cut_order_prefix: '裁床单',
"""
content = content.replace("title: '100% 离线扫码应用',", "title: '100% 离线扫码应用'," + zh_cn_insert)

# Inject for zh-TW
zh_tw_insert = """
                  time_today: '今天',
                  time_yesterday: '昨天',
                  time_week: '本週',
                  time_month: '本月',
                  time_3months: '最近3個月',
                  time_range: '時間範圍',
                  view_data: '查看數據',
                  tickets_ready: '張菲票已就緒',
                  zero_tickets: '0 張菲票',
                  cut_order_prefix: '裁床單',
"""
content = content.replace("title: '100% 離線掃碼應用',", "title: '100% 離線掃碼應用'," + zh_tw_insert)

# 7. Fix the "sync_qiaofei" translation bug in Chinese
content = re.sub(r"(?<=zh-CN': \{).*?sync_qiaofei:\s*'[^']*'", lambda m: m.group(0).replace(m.group(0).split('sync_qiaofei:')[1], " '同步 ERP 数据'"), content, flags=re.DOTALL)
content = re.sub(r"(?<=zh-TW': \{).*?sync_qiaofei:\s*'[^']*'", lambda m: m.group(0).replace(m.group(0).split('sync_qiaofei:')[1], " '同步 ERP 數據'"), content, flags=re.DOTALL)


with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated i18n completely!")
