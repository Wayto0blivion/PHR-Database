// Function to show the selected QR code
function showQR(customerName) {
    const qrImage = document.getElementById("selected-qr");
    // qrImage.src = "{{ qrcode(customer_name, box_size=5) }}";
    //
    // // Display the QR div
    // const qrDisplay = document.getElementById("qr-display");
    // qrDisplay.classList.remove("hidden");

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

}

// Function to print the selected QR code
function printQR() {
    let qrDisplay = document.getElementById("qr-display");
    let qrDisplayContent = qrDisplay.innerHTML;
    let newWindow = window.open();
    newWindow.document.body.innerHTML = qrDisplayContent;
    newWindow.print();
}


