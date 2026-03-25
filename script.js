document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".site-header");
    const menuToggle = document.getElementById("menuToggle");
    const siteNav = document.getElementById("siteNav");
    const navLinks = Array.from(document.querySelectorAll(".site-nav a"));
    const sections = Array.from(document.querySelectorAll("main section[id]"));
    const revealItems = Array.from(document.querySelectorAll(".reveal"));
    const contactForm = document.getElementById("contactForm");
    const copyright = document.querySelector(".copyright");

    const closeMenu = () => {
        if (!siteNav || !menuToggle) {
            return;
        }

        siteNav.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");

        const icon = menuToggle.querySelector("i");
        if (icon) {
            icon.classList.remove("fa-times");
            icon.classList.add("fa-bars");
        }
    };

    const openMenu = () => {
        if (!siteNav || !menuToggle) {
            return;
        }

        siteNav.classList.add("is-open");
        menuToggle.setAttribute("aria-expanded", "true");

        const icon = menuToggle.querySelector("i");
        if (icon) {
            icon.classList.remove("fa-bars");
            icon.classList.add("fa-times");
        }
    };

    if (menuToggle && siteNav) {
        menuToggle.addEventListener("click", () => {
            if (siteNav.classList.contains("is-open")) {
                closeMenu();
            } else {
                openMenu();
            }
        });
    }

    navLinks.forEach((link) => {
        link.addEventListener("click", () => {
            closeMenu();
        });
    });

    document.addEventListener("click", (event) => {
        if (!siteNav || !menuToggle || !siteNav.classList.contains("is-open")) {
            return;
        }

        const clickedInsideHeader = header && header.contains(event.target);
        if (!clickedInsideHeader) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    const revealAll = () => {
        revealItems.forEach((item) => item.classList.add("is-visible"));
    };

    if ("IntersectionObserver" in window) {
        const revealObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        revealObserver.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.14,
                rootMargin: "0px 0px -6% 0px",
            }
        );

        revealItems.forEach((item) => revealObserver.observe(item));
    } else {
        revealAll();
    }

    const setActiveLink = (id) => {
        navLinks.forEach((link) => {
            const isActive = link.getAttribute("href") === `#${id}`;
            link.classList.toggle("is-active", isActive);
        });
    };

    if ("IntersectionObserver" in window && sections.length > 0) {
        const sectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setActiveLink(entry.target.id);
                    }
                });
            },
            {
                threshold: 0.3,
                rootMargin: "-42% 0px -42% 0px",
            }
        );

        sections.forEach((section) => sectionObserver.observe(section));
    } else if (sections.length > 0) {
        setActiveLink("home");
    }

    const backToTop = document.createElement("button");
    backToTop.type = "button";
    backToTop.className = "back-to-top";
    backToTop.setAttribute("aria-label", "Back to top");
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTop);

    const updateBackToTop = () => {
        backToTop.classList.toggle("is-visible", window.scrollY > 600);
    };

    window.addEventListener("scroll", updateBackToTop, { passive: true });
    updateBackToTop();

    backToTop.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    });

    const showToast = (title, message) => {
        const existingToast = document.querySelector(".toast");
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement("div");
        toast.className = "toast";
        toast.innerHTML = `
            <strong>${title}</strong>
            <p>${message}</p>
        `;

        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add("is-visible");
        });

        window.setTimeout(() => {
            toast.classList.remove("is-visible");
            window.setTimeout(() => {
                toast.remove();
            }, 220);
        }, 3600);
    };

    if (contactForm) {
        contactForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());
            const messageParts = [
                "New portfolio inquiry",
                `Name: ${data.name || ""}`,
                `Email: ${data.email || ""}`,
                `Project type: ${data.project || ""}`,
                `Details: ${data.message || ""}`,
            ];

            const whatsappMessage = encodeURIComponent(messageParts.join("\n\n"));
            const whatsappUrl = `https://wa.me/918480132050?text=${whatsappMessage}`;

            window.open(whatsappUrl, "_blank", "noopener,noreferrer");
            contactForm.reset();
            closeMenu();
            showToast("WhatsApp ready", "Your project message has been prepared in WhatsApp.");
        });
    }

    if (copyright) {
        copyright.textContent = `\u00A9 ${new Date().getFullYear()} Arpit Kumar Tali. All rights reserved.`;
    }

    setActiveLink("home");
});
