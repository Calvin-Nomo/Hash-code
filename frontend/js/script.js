function printReceipt() {
  // Get all receipt information from the page
  const orderId = document.getElementById("orderId").textContent;
  const orderDate = document.getElementById("orderDate").textContent;
  const orderType = document.getElementById("orderType").textContent;
  const clientName = document.getElementById("clientName").textContent;
  const clientPhone = document.getElementById("clientPhone").textContent;
  const paymentMethod = document.getElementById("paymentMethod").textContent;
  const paymentStatus = document.getElementById("paymentStatus").textContent;
  const orderStatus = document.getElementById("orderstatus").textContent;
  const tableNumber = document.getElementById("table_number").textContent;

  const fees = document.getElementById("fees1").textContent;
  const total = document.getElementById("totalAmount").textContent;
  const final = document.getElementById("finalAmount").textContent;

  const itemsTable = document.getElementById("orderItemsTbody").innerHTML;

  // Generate QR code
  const qrText = `Order ${orderId} | Amount: ${final} | Client: ${clientName}`;
  const qrURL = `https://chart.googleapis.com/chart?cht=qr&chs=150x150&chl=${encodeURIComponent(qrText)}`;

  // Open print window
  const w = window.open("", "", "width=500,height=700");

  w.document.write(`
    <html>
    <head>
      <title>Receipt ${orderId}</title>
      <style>
        body {
          font-family: Arial;
          padding: 5px;
          line-height: 1.4;
          font-size: 14px;
        }
        .header {
          text-align: center;
          margin-bottom: 5px;
        }
        .header h2 {
          margin: 0;
          font-size: 18px;
        }
        .info {
          font-size: 13px;
          margin-bottom: 5px;
        }
        hr {
          border: none;
          border-top: 1px dashed #aaa;
          margin: 8px 0;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 5px;
          font-size: 13px;
        }
        table th {
          border-bottom: 1px solid #ccc;
          padding-bottom: 4px;
        }
        table td {
          padding: 3px 0;
        }
        .totals p {
          font-size: 14px;
          margin: 4px 0;
        }
        .qr-box {
          text-align: center;
          margin-top: 10px;
        }
        .qr-box img {
          margin-top: 5px;
          width: 130px;
        }
        .center {
          text-align: center;
        }
      </style>
    </head>

    <body>

      <div class="header">
        <h2>SMART MENU</h2>
        <p>Receipt • Order System</p>
      </div>

      <div class="info">
        <strong>Order ID:</strong> ${orderId}<br>
        <strong>Date:</strong> ${orderDate}<br>
        <strong>Type:</strong> ${orderType}<br>
        <strong>Table:</strong> ${tableNumber}<br>
      </div>

      <hr>

      <div class="info">
        <strong>Client:</strong> ${clientName}<br>
        <strong>Phone:</strong> ${clientPhone}<br>
      </div>

      <hr>

      <div class="info">
        <strong>Payment:</strong> ${paymentMethod}<br>
        <strong>Status:</strong> ${paymentStatus}<br>
      </div>

      <hr>

      <h3 class="center">Items</h3>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Item</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          ${itemsTable}
        </tbody>
      </table>

      <hr>

      <div class="totals">
        <p><strong>Transaction Fee:</strong> ${fees}</p>
        <p><strong>Total:</strong> ${total}</p>
        <p><strong>Final Amount:</strong> ${final}</p>
      </div>

      <div class="qr-box">
        <p>Scan to verify order</p>
        <img src="${qrURL}" alt="QR Code"/>
      </div>

      <hr>

      <p class="center">Thank you for your order!</p>

      <script>
        window.print();
        window.close();
      <\/script>

    </body>
    </html>
  `);

  w.document.close();
}
