// --- 1. Hamburger Menu Logic ---
    const hamburger = document.getElementById("hamburger");
    const navLinks = document.getElementById("nav-links");

    if (hamburger && navLinks) {
        hamburger.onclick = function() {
            // Toggle 'active' class for mobile menu
            navLinks.classList.toggle("active");
            console.log("Hamburger Menu toggled!"); 
        };
    }