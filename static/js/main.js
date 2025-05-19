// FILE: static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
  const openBtn    = document.getElementById('open-chat-btn');
  const chatWidget = document.getElementById('chat-widget');
  if (openBtn && chatWidget) {
    openBtn.addEventListener('click', () => {
      chatWidget.classList.remove('hidden');
      openBtn.style.display = 'none';
    });
  }
});
