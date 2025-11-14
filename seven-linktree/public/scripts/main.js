document.addEventListener("DOMContentLoaded", () => {
  const card = document.querySelector("[data-card]");
  if (card) {
    setTimeout(() => {
      card.classList.add("is-visible");
    }, 80);
  }
});
