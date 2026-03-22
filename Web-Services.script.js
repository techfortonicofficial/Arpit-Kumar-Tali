const pageBody = document.body;
const revealItems = document.querySelectorAll(".reveal");
const menuToggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelectorAll(".site-nav a");
const progressBar = document.querySelector(".progress-bar");
const tiltTargets = document.querySelectorAll("[data-tilt]");
const spotlightCards = document.querySelectorAll(".spotlight-card");
const currentYearNodes = document.querySelectorAll(".js-year");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
      threshold: 0.16,
      rootMargin: "0px 0px -8% 0px"
    }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    const isOpen = pageBody.classList.toggle("nav-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
  });
}

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    pageBody.classList.remove("nav-open");
    menuToggle?.setAttribute("aria-expanded", "false");
    menuToggle?.setAttribute("aria-label", "Open menu");
  });
});

const activePage = pageBody.dataset.page;
if (activePage) {
  navLinks.forEach((link) => {
    if (link.dataset.nav === activePage) {
      link.classList.add("is-active");
    }
  });
}

const updateProgressBar = () => {
  if (!progressBar) {
    return;
  }

  const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollableHeight > 0 ? window.scrollY / scrollableHeight : 0;
  progressBar.style.transform = `scaleX(${Math.min(Math.max(progress, 0), 1)})`;
};

updateProgressBar();
window.addEventListener("scroll", updateProgressBar, { passive: true });

if (!prefersReducedMotion) {
  tiltTargets.forEach((target) => {
    const panel = target.querySelector(".hero-window");
    if (!panel) {
      return;
    }

    target.addEventListener("mousemove", (event) => {
      const rect = target.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = (event.clientY - rect.top) / rect.height;
      const tiltY = (x - 0.5) * 10;
      const tiltX = (0.5 - y) * 10;

      panel.style.setProperty("--tilt-x", `${tiltX}deg`);
      panel.style.setProperty("--tilt-y", `${tiltY}deg`);
    });

    target.addEventListener("mouseleave", () => {
      panel.style.setProperty("--tilt-x", "0deg");
      panel.style.setProperty("--tilt-y", "0deg");
    });
  });

  spotlightCards.forEach((card) => {
    card.addEventListener("mousemove", (event) => {
      const rect = card.getBoundingClientRect();
      const mouseX = `${((event.clientX - rect.left) / rect.width) * 100}%`;
      const mouseY = `${((event.clientY - rect.top) / rect.height) * 100}%`;
      card.style.setProperty("--mouse-x", mouseX);
      card.style.setProperty("--mouse-y", mouseY);
    });
  });
}

currentYearNodes.forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
