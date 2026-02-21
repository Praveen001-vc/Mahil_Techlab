(() => {
  function setFooterYear() {
    const yearEl = document.getElementById("year");
    if (yearEl) {
      yearEl.textContent = String(new Date().getFullYear());
    }
  }

  function initMobileNav() {
    const toggle = document.getElementById("nav-toggle");
    const nav = document.getElementById("site-nav");

    if (!toggle || !nav) {
      return;
    }

    toggle.addEventListener("click", () => {
      const opened = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(opened));
      toggle.textContent = opened ? "Close" : "Menu";
    });
  }

  function initRevealAnimations() {
    const items = Array.from(document.querySelectorAll(".reveal"));
    if (!items.length) {
      return;
    }

    if (!("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }

          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        });
      },
      { threshold: 0.15 }
    );

    items.forEach((el, index) => {
      el.style.setProperty("--delay", `${Math.min(index * 70, 360)}ms`);
      observer.observe(el);
    });
  }

  function initCourseSelectionActions() {
    const enrollmentForm = document.getElementById("enroll-form");
    const courseSelect = document.getElementById("id_course");

    if (!enrollmentForm || !courseSelect) {
      return;
    }

    document.addEventListener("click", (event) => {
      const link = event.target.closest("[data-course-id]");
      if (!link) {
        return;
      }

      event.preventDefault();

      const courseId = link.getAttribute("data-course-id");
      if (!courseId) {
        return;
      }

      courseSelect.value = courseId;
      enrollmentForm.scrollIntoView({ behavior: "smooth", block: "start" });
      courseSelect.focus();
    });
  }

  function initPasswordToggles() {
    const toggles = Array.from(document.querySelectorAll("[data-toggle-password]"));
    if (!toggles.length) {
      return;
    }

    toggles.forEach((toggleBtn) => {
      toggleBtn.addEventListener("click", () => {
        const targetId = toggleBtn.getAttribute("data-target-id");
        if (!targetId) {
          return;
        }

        const input = document.getElementById(targetId);
        if (!input) {
          return;
        }

        const isMasked = input.type === "password";
        input.type = isMasked ? "text" : "password";
        toggleBtn.setAttribute("aria-pressed", String(isMasked));
        toggleBtn.setAttribute("aria-label", isMasked ? "Hide password" : "Show password");
        toggleBtn.classList.toggle("is-visible", isMasked);
      });
    });
  }

  setFooterYear();
  initMobileNav();
  initRevealAnimations();
  initCourseSelectionActions();
  initPasswordToggles();
})();
