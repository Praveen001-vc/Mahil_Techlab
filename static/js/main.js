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

  function initHomeSlider() {
    const slider = document.querySelector("[data-home-slider]");
    if (!slider) {
      return;
    }

    const track = slider.querySelector(".home-slider-track");
    if (!track) {
      return;
    }

    const realSlides = Array.from(track.querySelectorAll(".home-slide"));
    const dots = Array.from(slider.querySelectorAll("[data-slide-dot]"));
    const progressBar = slider.querySelector("[data-slide-progress]");
    const prevBtn = slider.querySelector("[data-slide-prev]");
    const nextBtn = slider.querySelector("[data-slide-next]");

    if (!realSlides.length) {
      return;
    }

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const realCount = realSlides.length;
    const transitionMs = prefersReducedMotion ? 0 : 850;
    const autoIntervalMs = 6200;
    const swipeThresholdPx = 48;
    const swipeVerticalLimitPx = 90;
    let currentIndex = 0;
    let autoTimer = null;
    let touchActive = false;
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    track.style.transitionDuration = `${transitionMs}ms`;

    if (realCount <= 1) {
      if (prevBtn) {
        prevBtn.style.display = "none";
      }
      if (nextBtn) {
        nextBtn.style.display = "none";
      }
      dots.forEach((dot, dotIndex) => {
        dot.classList.toggle("is-active", dotIndex === 0);
      });
      if (progressBar) {
        progressBar.style.display = "none";
      }
      return;
    }

    const firstClone = realSlides[0].cloneNode(true);
    const lastClone = realSlides[realCount - 1].cloneNode(true);
    firstClone.setAttribute("aria-hidden", "true");
    lastClone.setAttribute("aria-hidden", "true");
    firstClone.classList.add("is-clone");
    lastClone.classList.add("is-clone");
    track.appendChild(firstClone);
    track.insertBefore(lastClone, track.firstElementChild);

    const slides = Array.from(track.querySelectorAll(".home-slide"));
    currentIndex = 1;

    function getRealIndex(slideIndex) {
      if (slideIndex === 0) {
        return realCount - 1;
      }
      if (slideIndex === realCount + 1) {
        return 0;
      }
      return slideIndex - 1;
    }

    function setActiveSlide(index, animate = true) {
      const safeIndex = Math.max(0, Math.min(index, realCount + 1));
      currentIndex = safeIndex;
      track.style.transitionDuration = animate ? `${transitionMs}ms` : "0ms";
      track.style.transform = `translate3d(-${currentIndex * 100}%, 0, 0)`;

      const realIndex = getRealIndex(currentIndex);
      slides.forEach((slide, slideIndex) => {
        slide.classList.toggle("is-active", slideIndex === currentIndex);
      });
      dots.forEach((dot, dotIndex) => {
        dot.classList.toggle("is-active", dotIndex === realIndex);
      });

      if (transitionMs === 0) {
        normalizeLoop();
      }
    }

    function goNext() {
      setActiveSlide(currentIndex + 1);
    }

    function resetProgress(play) {
      if (!progressBar) {
        return;
      }

      progressBar.style.transition = "none";
      progressBar.style.transform = "scaleX(0)";
      if (!play || prefersReducedMotion) {
        return;
      }

      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          progressBar.style.transition = `transform ${autoIntervalMs}ms linear`;
          progressBar.style.transform = "scaleX(1)";
        });
      });
    }

    function stopAuto() {
      if (autoTimer) {
        window.clearTimeout(autoTimer);
        autoTimer = null;
      }
      resetProgress(false);
    }

    function restartAuto() {
      stopAuto();
      if (prefersReducedMotion) {
        return;
      }
      resetProgress(true);
      autoTimer = window.setTimeout(() => {
        goNext();
        restartAuto();
      }, autoIntervalMs);
    }

    function normalizeLoop() {
      if (currentIndex === 0) {
        setActiveSlide(realCount, false);
      } else if (currentIndex === realCount + 1) {
        setActiveSlide(1, false);
      }
    }

    function handleTouchStart(event) {
      if (!event.touches || event.touches.length !== 1) {
        return;
      }

      const touch = event.touches[0];
      touchActive = true;
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
      touchEndX = touch.clientX;
      touchEndY = touch.clientY;
      stopAuto();
    }

    function handleTouchMove(event) {
      if (!touchActive || !event.touches || event.touches.length !== 1) {
        return;
      }

      const touch = event.touches[0];
      touchEndX = touch.clientX;
      touchEndY = touch.clientY;

      const deltaX = touchEndX - touchStartX;
      const deltaY = touchEndY - touchStartY;
      if (Math.abs(deltaX) > 10 && Math.abs(deltaX) > Math.abs(deltaY)) {
        event.preventDefault();
      }
    }

    function handleTouchEnd() {
      if (!touchActive) {
        return;
      }

      touchActive = false;
      const deltaX = touchEndX - touchStartX;
      const deltaY = touchEndY - touchStartY;

      if (Math.abs(deltaY) > swipeVerticalLimitPx) {
        restartAuto();
        return;
      }

      if (Math.abs(deltaX) >= swipeThresholdPx) {
        if (deltaX > 0) {
          setActiveSlide(currentIndex - 1);
        } else {
          setActiveSlide(currentIndex + 1);
        }
      }

      restartAuto();
    }

    function handleTouchCancel() {
      touchActive = false;
      restartAuto();
    }

    track.addEventListener("transitionend", normalizeLoop);

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        setActiveSlide(currentIndex - 1);
        restartAuto();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        goNext();
        restartAuto();
      });
    }

    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        const index = Number(dot.getAttribute("data-slide-dot"));
        if (Number.isNaN(index)) {
          return;
        }
        setActiveSlide(index + 1);
        restartAuto();
      });
    });

    slider.addEventListener("mouseenter", stopAuto);
    slider.addEventListener("mouseleave", restartAuto);
    slider.addEventListener("focusin", stopAuto);
    slider.addEventListener("focusout", () => {
      if (!slider.contains(document.activeElement)) {
        restartAuto();
      }
    });
    slider.addEventListener("touchstart", handleTouchStart, { passive: true });
    slider.addEventListener("touchmove", handleTouchMove, { passive: false });
    slider.addEventListener("touchend", handleTouchEnd);
    slider.addEventListener("touchcancel", handleTouchCancel);

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stopAuto();
      } else {
        restartAuto();
      }
    });

    setActiveSlide(currentIndex, false);
    window.requestAnimationFrame(() => {
      track.style.transitionDuration = `${transitionMs}ms`;
    });
    restartAuto();
  }

  function initSmoothAnchorScroll() {
    const anchorLinks = Array.from(document.querySelectorAll('a[href^="#"]'));
    if (!anchorLinks.length) {
      return;
    }

    anchorLinks.forEach((link) => {
      link.addEventListener("click", (event) => {
        const href = link.getAttribute("href");
        if (!href || href === "#") {
          return;
        }

        const target = document.querySelector(href);
        if (!target) {
          return;
        }

        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  function initFlashMessages() {
    const flashMessages = Array.from(document.querySelectorAll("[data-flash-message]"));
    if (!flashMessages.length) {
      return;
    }

    flashMessages.forEach((message, index) => {
      const removeDelayMs = 4000 + index * 150;
      const hideDelayMs = Math.max(2600, removeDelayMs - 380);

      window.setTimeout(() => {
        message.classList.add("is-hiding");
      }, hideDelayMs);

      window.setTimeout(() => {
        message.remove();
      }, removeDelayMs);
    });
  }

  setFooterYear();
  initMobileNav();
  initRevealAnimations();
  initCourseSelectionActions();
  initPasswordToggles();
  initHomeSlider();
  initSmoothAnchorScroll();
  initFlashMessages();
})();
