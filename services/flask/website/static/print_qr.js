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
  const qrDisplay = document.getElementById("qr-display");
  const content = qrDisplay.outerHTML; // keeps wrapper & classes

  const win = window.open("", "_blank");
  win.document.open();

  win.document.write(`
    <html lang="en">
      <head>
        <title>Print QR Codes</title>
        <meta charset="utf-8" />
        <style>
          * { box-sizing: border-box; }
          html, body { margin: 0; padding: 0; }

          @media print {
            @page { size: auto; margin: 0; }

            body {
              margin: 0;
              padding: 0;
              -webkit-print-color-adjust: exact;
              print-color-adjust: exact;
            }

            /* Full printable viewport */
            .page {
              width: 100vw;
              height: 100vh;
              display: flex;
              align-items: flex-start;
              justify-content: flex-start;
              padding: 3vmin 3vmin 12vmin 3vmin;
              overflow: hidden;
            }

            /*
              For 4x6 labels:
                - portrait: vmin = width (4")
                - landscape: vmin = height (4")
            */
            .sheet {
              width: 74vmin;
              height: 74vmin;
              padding: 1vmin;
              display: grid;
              grid-template-columns: 1fr 1fr;
              grid-template-rows: 1fr 1fr;
              column-gap: 1vmin;
              row-gap: 5vmin;
              align-items: start;
              justify-items: start;
            }

            /* ignore bootstrap col/row behavior) */
            #qr-display.qr-display-div {
              width: 100%;
              height: 100%;
              display: contents; /* let children become grid items of .sheet */
            }

            /* Each QR tile */
            #qr-display .qr-item {
              width: 100%;
              height: 100%;
              display: flex !important;
              flex-direction: column;
              align-items: center;
              justify-content: flex-start;
              padding: 0 0 1.2vmin 0 !important;  /* override inline padding and add more room on the bottom */
              margin: 0 !important;
              break-inside: avoid;
              page-break-inside: avoid;
              text-align: center;
            }

            /* QR size based on vmin so it scales with orientation */
            #qr-display .qr-item img {
              width: clamp(1.05in, 25vmin, 1.35in) !important;
              height: auto !important;
              display: block;
              margin: 0 0 0.8vmin 0 !important;
            }

            #qr-display .qr-item span {
              font-weight: 800 !important;
              line-height: 1.05 !important;
              padding-top: 0.3vmin !important;
              color: #000 !important;

              /* allow wrapping */
              white-space: normal !important;
              overflow: hidden;
              text-overflow: ellipsis;
              
              /* break long words if needed */
              overflow-wrap: anywhere;
              word-break: break-word;
              
              /* clamp to 2 lines so it won't push content off the label */
              display: -webkit-box;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 2;
              
              /* keeps it centered and sized */
              text-align: left;
              max-width: 100%;
              
              /* keeps scaling */
              font-size: clamp(12pt, 3.5vmin, 17pt) !important;
              }
          }
        </style>
      </head>
      <body>
        <div class="page">
          <div class="sheet">
            ${content}
          </div>
        </div>
      </body>
    </html>
  `);

  win.document.close();

  // Wait for images to load (prevents clipping from reflow)
  const imgs = win.document.images;
  let loaded = 0;

  if (imgs.length === 0) {
    win.focus(); win.print(); win.close();
    return;
  }

  for (const img of imgs) {
    if (img.complete) loaded++;
    else img.onload = img.onerror = () => {
      loaded++;
      if (loaded === imgs.length) {
        win.focus(); win.print(); win.close();
      }
    };
  }

  if (loaded === imgs.length) {
    win.focus(); win.print(); win.close();
  }
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