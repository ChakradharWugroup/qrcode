with open("templates/offline_app.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("Print QR Code", "Print Bundle Ticket")
content = content.replace("print_qr_code: 'Print QR Code'", "print_qr_code: 'Print Bundle Ticket'")

with open("templates/offline_app.html", "w", encoding="utf-8") as f:
    f.write(content)
