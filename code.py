import qrcode
for table_number in range(1, 11):  # tables 1 to 10
    url = f"http://10.0.39.17:3000/order.html?table={table_number}"

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"table_{table_number}_qr.png")
    print(f"QR for Table {table_number} saved as table_{table_number}_qr.png")
