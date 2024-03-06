



function generate_pdf() {
    const { jsPDF } = window.jspdf;
    let doc = new jsPDF();
    let pdfjs = document.getElementById('content');

    doc.html(pdfjs, {
        callback: function(doc) {
            doc.save("invoice.pdf");
        },
        x: 12,
        y: 12,
        width: 170, // target width in the PDF document
        windowWidth: 650 // window width in CSS pixels
    });

    // Redirect to the previous page
    // window.location.href = document.referrer;
}

// Automatically trigger the download on page load
// document.addEventListener('DOMContentLoaded', function () {
//     generate_pdf();
// });