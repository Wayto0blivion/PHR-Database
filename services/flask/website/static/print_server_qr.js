// Function to show the selected QR code
function showQR(customerName) {
    const qrImage = document.getElementById("selected-qr");

    const url = `/generate_qr/${customerName}`;

    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const objectURL = URL.createObjectURL(blob);
            qrImage.src = objectURL;

            const qrDisplay = document.getElementById("qr-display");
            qrDisplay.classList.remove("hidden");
        })
        .catch(error => {
            console.error("There was an error fetching the QR code:", error)
        });

    document.getElementById('selected_customer').innerHTML = customerName;
}


function printQR() {
    let qrDisplay = document.getElementById("qr-display");
    let qrDisplayContent = qrDisplay.innerHTML;
    let newWindow = window.open();
    newWindow.document.write('<html lang=""><head><title>Print QR Codes</title>');

    // Embedding the CSS directly
    newWindow.document.write('<style>');
    newWindow.document.write(`
        @media print {
  body {
    font-family: 'Arial', sans-serif; /* Professional font-family */
  }

  .qr-display-div {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 10px; /* More space between rows */
  }

  .qr-item {
    display: flex;
    flex-direction: column;
    align-items: center; /* Center align the items vertically */
    justify-content: center;
    padding: 5px; /* Add padding around the QR code */
    max-width: 400px;
  }

  .qr-item img {
    width: 100px; /* Fixed width for images */
    height: auto; /* Maintain aspect ratio */
  }

  .qr-item span {
    font-size: 12px; /* Adjust font size as needed */
    font-weight: normal; /* Avoid overly bold fonts */
    text-align: center; /* Center the text below the QR code */
    margin-top: 5px; /* Space between the QR code and the text */
  }

  .login-button, #print-button {
    display: none;
  }

  .container {
  page-break-after: avoid; /* Avoid breaking the page after the container */
    break-inside: avoid; /* Avoid breaking inside the container */
  }
  }
    `);
    newWindow.document.write('</style>');
    newWindow.document.write('</head><body>');
    newWindow.document.write(qrDisplayContent);
    newWindow.document.write('</body></html>');
    newWindow.document.close(); // necessary for IE >= 10
    newWindow.focus(); // necessary for IE >= 10*/

    newWindow.print();
    newWindow.close();
}