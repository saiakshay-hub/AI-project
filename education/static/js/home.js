document.addEventListener("DOMContentLoaded", function () {
    const words = ["Ai Tutor"];  // Add more words if you want
    let i = 0;
    let j = 0;
    let isDeleting = false;
    const speed = 100;
    const wordSpan = document.querySelector(".dynamic-heading .word");

    function typeEffect() {
        const currentWord = words[i];

        if (isDeleting) {
            if (j > 0) {
                wordSpan.textContent = currentWord.substring(0, j--);
            } else {
                wordSpan.textContent = "";   // make sure it's cleared
                isDeleting = false;
                i = (i + 1) % words.length;
                setTimeout(typeEffect, 500);
                return;
            }
        } else {
            wordSpan.textContent = currentWord.substring(0, j++);
            if (j > currentWord.length) {
                isDeleting = true;
                setTimeout(typeEffect, 1000);
                return;
            }
        }
        setTimeout(typeEffect, speed);
    }

    typeEffect();
});
