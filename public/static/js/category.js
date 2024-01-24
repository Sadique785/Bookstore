// document.addEventListener("DOMContentLoaded", function () {
//     console.log("gggg")
//     const categorySelect = document.getElementById('categoryselect');
//     const subcategorySelect = document.getElementById('subcategorySelect');

//     categorySelect.addEventListener('change', function () {
//         const categorySlug = this.value;
//         console.log(categorySlug,"slug");

//         fetch(`/get_subcategories/${categorySlug}/`)
//             .then(response => response.text())
//             console.log(response.data,"response")
//             .then(data => {
//                 subcategorySelect.innerHTML = data;
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//             });
//     });
// });

// document.addEventListener('DOMContentLoaded', function() {
    // Counter to track the number of file input fields
    // let fileInputCount = 1;

    // Function to create a new file input field
//     function createFileInput() {
//         fileInputCount++;
//         const fileInputContainer = document.createElement('div');
//         fileInputContainer.classList.add('file-input-container');

//         const newFileInput = document.createElement('input');
//         newFileInput.type = 'file';
//         newFileInput.name = `images_${fileInputCount}`;
//         newFileInput.accept = 'image/*';
//         newFileInput.classList.add('image-input');

//         fileInputContainer.appendChild(newFileInput);
//         document.getElementById('productForm').insertBefore(fileInputContainer, document.getElementById('addMorePhotos'));
//     }

//     // Event listener for the "Add more photos" button
//     document.getElementById('addMorePhotos').addEventListener('click', function() {
//         createFileInput();
//     });
// });

