(() => {
  const menuToggle = document.querySelector(".menu-toggle");
  const submenuToggle = document.querySelector(".submenu-toggle");
  for (const toggle of [menuToggle, submenuToggle]) {
    if (!toggle) continue;
    toggle.hidden = false;
    toggle.addEventListener("click", () => {
      toggle.setAttribute("aria-expanded", String(toggle.getAttribute("aria-expanded") !== "true"));
    });
  }
  const actionItem = submenuToggle?.closest(".has-children");
  actionItem?.addEventListener("pointerenter", () => {
    if (window.matchMedia("(min-width: 801px)").matches) {
      submenuToggle.setAttribute("aria-expanded", "true");
    }
  });
  actionItem?.addEventListener("pointerleave", () => {
    if (window.matchMedia("(min-width: 801px)").matches && !actionItem.contains(document.activeElement)) {
      submenuToggle.setAttribute("aria-expanded", "false");
    }
  });
  actionItem?.addEventListener("focusout", () => {
    queueMicrotask(() => {
      if (!actionItem.contains(document.activeElement) && !actionItem.matches(":hover")) {
        submenuToggle.setAttribute("aria-expanded", "false");
      }
    });
  });
  document.querySelector(".site-navigation").addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const inSubmenu = event.target.closest(".has-children");
    const toggle = inSubmenu && submenuToggle.getAttribute("aria-expanded") === "true" ? submenuToggle : menuToggle;
    if (toggle?.getAttribute("aria-expanded") === "true") {
      toggle.setAttribute("aria-expanded", "false");
      toggle.focus();
    }
  });

  for (const track of document.querySelectorAll(".prose p")) {
    const slides = [...track.children];
    if (slides.length < 4 || !slides.every((slide) => slide.matches(".markdown-image"))) continue;
    if ([...track.childNodes].some((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim())) continue;
    const gallery = document.createElement("div");
    gallery.className = "gallery";
    gallery.setAttribute("role", "region");
    gallery.setAttribute("aria-label", "Galerie de photos");
    track.before(gallery);
    gallery.append(track);
    track.classList.add("gallery-track");
    track.setAttribute("tabindex", "0");
    track.setAttribute("aria-label", "Photos — faites défiler horizontalement");
    const controls = document.createElement("div");
    controls.className = "gallery-controls";
    const previous = document.createElement("button");
    previous.type = "button";
    previous.textContent = "‹";
    previous.setAttribute("aria-label", "Photo précédente");
    const next = document.createElement("button");
    next.type = "button";
    next.textContent = "›";
    next.setAttribute("aria-label", "Photo suivante");
    const count = document.createElement("span");
    count.className = "gallery-count";
    count.setAttribute("aria-live", "polite");
    controls.append(previous, count, next);
    gallery.append(controls);
    let current = 0;
    const update = () => {
      current = Math.round(track.scrollLeft / track.clientWidth);
      previous.disabled = current === 0;
      next.disabled = current === slides.length - 1;
      count.textContent = `${current + 1} / ${slides.length}`;
    };
    const move = (direction) => {
      const index = Math.max(0, Math.min(slides.length - 1, current + direction));
      track.scrollTo({ left: index * track.clientWidth, behavior: "instant" });
      update();
    };
    previous.addEventListener("click", () => move(-1));
    next.addEventListener("click", () => move(1));
    track.addEventListener("scroll", update, { passive: true });
    track.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        move(event.key === "ArrowLeft" ? -1 : 1);
      }
    });
    new ResizeObserver(() => {
      track.scrollTo({ left: current * track.clientWidth, behavior: "instant" });
      update();
    }).observe(track);
    update();
  }

  const dialog = document.querySelector(".lightbox");
  if (!dialog || typeof dialog.showModal !== "function") return;
  const enlarged = document.createElement("img");
  const caption = dialog.querySelector("figcaption");
  const original = dialog.querySelector(".lightbox-original");
  const close = dialog.querySelector(".lightbox-close");
  let opener;
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[data-lightbox]");
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const image = link.querySelector("img");
    if (!image) return;
    event.preventDefault();
    opener = link;
    enlarged.src = link.href;
    enlarged.alt = image.alt;
    dialog.querySelector("figure").prepend(enlarged);
    caption.textContent = image.title || image.alt;
    original.href = link.href;
    dialog.showModal();
    close.focus();
  });
  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) {
      dialog.close();
    }
  });
  dialog.addEventListener("close", () => {
    enlarged.removeAttribute("src");
    opener?.focus();
  });
})();
