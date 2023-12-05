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
            .qr-display-div {
                width: 100%;
            }
            .qr-item {
                width: 50%;
                float: left;
                box-sizing: border-box;
                padding: 5px;
                margin-bottom: 10px;
                page-break-inside: avoid;
            }
            .qr-item img {
                width: 100px;
                height: auto;
            }
            .qr-item span {
                display: block;
                font-size: 24px;
                font-weight: bolder;
                color: black;
                text-align: center;
            }
            .print-button {
                display: none;
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



// function printQR() {
//     let printWindow = window.open('', '_blank');
//     printWindow.document.write('<html lang="en"><head><title>Print QR Codes</title>');
//     printWindow.document.write('<link rel="stylesheet" href="../static/printstyles.css" type="text/css" media="print"></head><body>');
//     printWindow.document.write(document.getElementById('qr-display').innerHTML);
//     printWindow.document.write('</body></html>');
//     // printWindow.document.close();
//
//     printWindow.onload = function() {
//         printWindow.print();
//         printWindow.close();
//     };
// }


