with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# The 3rd occurrence (idx 23615) is the zh-CN block that missed injection (it has time_today after it, not msg_phone_full)
# Find it and inject the zh-CN messages after it

zh_cn_msgs = """,
                  msg_phone_full: '\u624b\u673a\u5b58\u50a8\u5df2\u6ee1\uff0c\u65e0\u6cd5\u4fdd\u5b58\u3002',
                  msg_box_empty: '\u7b71\u5b50\u662f\u7a7a\u7684\uff01\u8bf7\u5148\u626b\u63cf\u83f2\u7968\u3002',
                  msg_sync_ok: '\u6210\u529f\u4e0b\u8f7d {count} \u5f20\u83f2\u7968\uff01',
                  msg_sync_err: '\u540c\u6b65\u9519\u8bef\uff1a',
                  msg_server_err: '\u670d\u52a1\u5668\u9519\u8bef\uff1a',
                  msg_network_err: '\u7f51\u7edc\u9519\u8bef\uff1a',
                  msg_camera_err: '\u6444\u50cf\u5934\u9519\u8bef\u3002\u8bf7\u5728\u8bbe\u7f6e\u4e2d\u5141\u8bb8\u6444\u50cf\u5934\u6743\u9650\u3002',
                  msg_scan_qty: '\u8bf7\u626b\u63cf\u4e8c\u7ef4\u7801\u5e76\u8f93\u5165\u6570\u91cf\uff01',
                  msg_duplicate: '\u91cd\u590d\u8b66\u544a\uff1a\u6b64\u4e8c\u7ef4\u7801\u5df2\u5728\u6b64\u7b71\u5b50\u4e2d\uff01',
                  msg_offline: '\u60a8\u5f53\u524d\u5904\u4e8e\u79bb\u7ebf\u72b6\u6001\uff0c\u8bf7\u5148\u8fde\u63a5\u7f51\u7edc\u3002',
                  msg_all_synced: '\u6240\u6709\u6570\u636e\u5df2\u4e0a\u4f20\u5230\u4e91\u7aef\uff01',
                  msg_push_ok: '\u6210\u529f\u4e0a\u4f20 {count} \u5f20\u83f2\u7968\u5230\u4e91\u7aef\uff01',
                  msg_push_err: '\u670d\u52a1\u5668\u9519\u8bef\uff0c\u65e0\u6cd5\u4e0a\u4f20\u5230\u4e91\u7aef\u3002',
                  msg_push_net: '\u7f51\u7edc\u9519\u8bef\uff0c\u8bf7\u786e\u8ba4\u670d\u52a1\u5668\u53ef\u4ee5\u8bbf\u95ee\u3002',
                  msg_db_cleared: '\u672c\u5730\u6570\u636e\u5df2\u4ece\u624b\u673a\u4e2d\u6e05\u9664\u3002',
                  msg_db_empty: '\u6ca1\u6709\u6570\u636e\uff01',
                  msg_confirm_clear: '\u6240\u6709\u6570\u636e\u5df2\u5b89\u5168\u4e0a\u4f20\u3002\u662f\u5426\u6e05\u9664\u624b\u673a\u5185\u5b58\u4ee5\u5f00\u59cb\u65b0\u5de5\u4f5c\uff1f'"""

# Find the 3rd occurrence (zh-CN block that only has time_today after it)
idx1 = content.find("clear_warning", 0)
idx2 = content.find("clear_warning", idx1+1)
idx3 = content.find("clear_warning", idx2+1)

# Find the end of the value at idx3: look for the closing quote and comma
end_of_value = content.find("',", idx3)
if end_of_value != -1:
    # Insert after the closing quote + comma
    insert_at = end_of_value + 2
    content = content[:insert_at] + zh_cn_msgs + content[insert_at:]
    print(f"Injected zh-CN messages at position {insert_at}")
else:
    print("Could not find end of value")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
