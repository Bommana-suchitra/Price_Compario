
/* =====================================
   Image Preview (NO FILE NAME)
===================================== */

function previewImage(input) {
    const file = input.files[0];
    if (!file) return;

    const previewImg = document.getElementById("previewImg");
    if (!previewImg) return;

    // Show uploaded image preview
    previewImg.src = URL.createObjectURL(file);
    previewImg.style.display = "block";
}

/* =====================================
   Prevent Double Submit
===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("submit", () => {
            const btn = form.querySelector("button[type='submit']");
            if (btn) {
                btn.disabled = true;
                btn.innerText = "Processing...";
                btn.style.opacity = "0.7";
                btn.style.cursor = "not-allowed";
            }
        });
    });
});
