function clickEvent() {
    let myDiv = document.getElementById("qr-div");
    let myDivContent = myDiv.innerHTML;
    let newWindow = window.open();
    newWindow.document.body.innerHTML = myDivContent;
    newWindow.print();
    console.log("text");
}