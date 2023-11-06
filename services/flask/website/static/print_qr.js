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
/*
function printQR() {
    let qrDisplay = document.getElementById("qr-display");
    let qrDisplayContent = qrDisplay.innerHTML;
    let newWindow = window.open();
    newWindow.document.body.innerHTML = qrDisplayContent;
    newWindow.print();
}*/


function printQR() {
    let printWindow = window.open('', '_blank');
    printWindow.document.write('<html lang="en"><head><title>Print QR Codes</title>');
    printWindow.document.write('<link rel="stylesheet" href="../static/printstyles.css" type="text/css" media="print"></head><body>');
    printWindow.document.write(document.getElementById('qr-display').innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();

    printWindow.onload = function() {
        printWindow.print();
        // printWindow.close();
    };
}


