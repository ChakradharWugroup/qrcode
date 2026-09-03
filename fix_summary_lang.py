with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

# The problem: sync-summary-text is set dynamically with innerText and doesn't have a data-i18n tag,
# so when the language changes, the setLanguage function has no way to re-translate it.
# Fix: After the data-i18n loop in setLanguage, add code to re-translate the sync summary text.

old_code = """            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[lang][key]) {
                    el.innerHTML = i18n[lang][key];
                }
            });"""

new_code = """            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[lang][key]) {
                    el.innerHTML = i18n[lang][key];
                }
            });
            
            // Re-translate dynamically-set text (sync summary)
            const summaryEl = document.getElementById('sync-summary-text');
            if (summaryEl) {
                const currentText = summaryEl.innerText;
                const numMatch = currentText.match(/\\d+/);
                if (numMatch) {
                    summaryEl.innerText = numMatch[0] + ' ' + (i18n[lang]['tickets_ready'] || 'Tickets Downloaded');
                }
            }"""

content = content.replace(old_code, new_code)

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")
