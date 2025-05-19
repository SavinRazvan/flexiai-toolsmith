/**
 * @file chat.js
 * @description
 * Handles the chat UI for FlexiAI Toolsmith: connecting via SSE to stream assistant
 * responses, rendering messages, and sending user input via AJAX.
 */

document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  // ─── Feature toggles & state ─────────────────────────────────────────────
  const ENABLE_HTML      = true;   // if true, allow raw HTML in assistant messages
  const DEBUG            = true;   // set to true to see debug‐level logs
  let reconnectTimeout   = null;   // for debounced reconnects

  // ─── Logging helpers ─────────────────────────────────────────────────────
  function logInfo(...args)  { if (DEBUG) console.info(...args); }
  function logDebug(...args) { if (DEBUG) console.debug(...args); }

  // ─── SSE cleanup & reconnect helpers ─────────────────────────────────────
  function cleanupSSE() {
    if (src) {
      src.close();
      src = null;
    }
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
  }

  function scheduleReconnect() {
    if (reconnectTimeout) return;
    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null;
      connectSSE();
    }, 3000);
  }

  // ─── Helper: Decode HTML entities (e.g. &quot;) back to real chars ─────
  function decodeEntities(str) {
    const txt = document.createElement("textarea");
    txt.innerHTML = str;
    return txt.value;
  }

  // ─── Purify Configuration ───────────────────────────────────────────────
  const purifyConfig = {
    ADD_TAGS: [
      "iframe","form","fieldset","legend",
      "div","p","label","input","textarea","button"
    ],
    ADD_ATTR: [
      "allow","allowfullscreen","frameborder","scrolling","src","class",
      "width","height","action","method","id","name","type","placeholder","required","value"
    ]
  };

  // ─── Shared IDs & Names ─────────────────────────────────────────────────
  const USER_ID        = window.USER_ID        || "unknown_user";
  const USER_NAME      = window.USER_NAME      || "User";
  const ASSISTANT_NAME = window.ASSISTANT_NAME || "Assistant";
  console.info(
    `[Chat.js] Startup: USER_ID=${USER_ID}, USER_NAME=${USER_NAME}, ASSISTANT_NAME=${ASSISTANT_NAME}`
  );

  // ─── Container & Elements ────────────────────────────────────────────────
  const isFullPage = !!document.getElementById("chat-box");
  const container  = isFullPage
    ? document.getElementById("chat-box")
    : document.getElementById("chat-widget");
  const conv     = container.querySelector("#conversation");
  const form     = container.querySelector("#chat-form");
  const input    = container.querySelector("#user-input");
  const sendBtn  = form.querySelector("button[type='submit']");
  const openBtn  = document.getElementById("open-chat-btn");
  const closeBtn = container.querySelector("#close-chat-btn");
  const header   = container.querySelector("#chat-header");
  console.debug("[Chat.js] Elements:", { conv, form, input, sendBtn, openBtn, closeBtn, header });

  // ─── Widget toggle & drag support ───────────────────────────────────────
  if (!isFullPage && openBtn && closeBtn && container && header) {
    openBtn.addEventListener("click", () => {
      container.classList.remove("hidden");
      openBtn.style.display = "none";
    });
    closeBtn.addEventListener("click", () => {
      container.classList.add("hidden");
      openBtn.style.display = "";
    });
    header.addEventListener("mousedown", e => {
      if (e.target === closeBtn) return;
      const rect = container.getBoundingClientRect();
      const dx = e.clientX - rect.left, dy = e.clientY - rect.top;
      function onMouseMove(ev) {
        container.style.left = (ev.clientX - dx) + "px";
        container.style.top  = (ev.clientY - dy) + "px";
      }
      function onMouseUp() {
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      }
      document.addEventListener("mousemove", onMouseMove, { passive: true });
      document.addEventListener("mouseup", onMouseUp, { passive: true });
    });
  }

  // ─── Message Rendering ──────────────────────────────────────────────────
  function appendMessage(who, md) {
    logInfo("[Chat.js] appendMessage:", who, `${md.length} chars`);
    const el = document.createElement("div");
    el.className = `message ${who === USER_NAME ? "user" : "assistant"}`;

    if (who === USER_NAME) {
      const span = document.createElement("span");
      span.textContent = md;
      span.setAttribute("data-md", md);
      el.appendChild(span);
      conv.appendChild(el);
      conv.scrollTop = conv.scrollHeight;
      return span;
    }

    let html;
    const trimmed = md.trim();
    if (
      ENABLE_HTML &&
      /^<pure_html>[\s\S]*<\/pure_html>$/.test(trimmed)
    ) {
      html = trimmed.replace(/^<pure_html>/, "").replace(/<\/pure_html>$/, "");
    } else if (
      ENABLE_HTML &&
      /^\s*<\s*(form|div|fieldset|label|input|textarea|button)/i.test(trimmed)
    ) {
      html = trimmed;
    } else {
      html = marked.parse(md);
    }
    el.innerHTML = DOMPurify.sanitize(html, purifyConfig);

    const first = el.firstElementChild || el;
    first.setAttribute("data-md", md);

    conv.appendChild(el);
    conv.scrollTop = conv.scrollHeight;
    return first;
  }

  function updateMessage(elem, chunk) {
    logDebug("[Chat.js] updateMessage: +", `${chunk.length} chars`);
    const prev = elem.getAttribute("data-md") || "";
    const combined = prev + chunk;
    elem.setAttribute("data-md", combined);

    let html;
    const trimmed = combined.trim();
    if (
      ENABLE_HTML &&
      /^<pure_html>[\s\S]*<\/pure_html>$/.test(trimmed)
    ) {
      html = trimmed.replace(/^<pure_html>/, "").replace(/<\/pure_html>$/, "");
    } else if (
      ENABLE_HTML &&
      /^\s*<\s*(form|div|fieldset|label|input|textarea|button)/i.test(trimmed)
    ) {
      html = trimmed;
    } else {
      html = marked.parse(combined);
    }
    elem.innerHTML = DOMPurify.sanitize(html, purifyConfig);

    // — Auto-scroll disabled during streaming chunks to reduce rendering lag —
    // conv.scrollTop = conv.scrollHeight;
  }

  // ─── Streaming State & SSE ──────────────────────────────────────────────
  let src = null;

  window.addEventListener("beforeunload", cleanupSSE);
  window.addEventListener("pagehide",     cleanupSSE);

  function handleMessageDelta(evt) {
    const msgId  = evt.message_id;
    const chunks = Array.isArray(evt.content) ? evt.content : [evt.content];
    logDebug("[Chat.js] handleMessageDelta:", msgId, "chunks=", chunks.length);

    let span = conv.querySelector(`[data-message-id="${msgId}"]`);

    for (let chunk of chunks) {
      logDebug("[Chat.js] chunk:", chunk.slice(0, 30));

      if (!span) {
        const t = chunk.trimStart();
        const htmlMode = ENABLE_HTML && (
          t.startsWith("<pure_html>") ||
          /^\s*<\s*(form|div|fieldset|label|input|textarea|button)/i.test(t)
        );

        span = appendMessage(ASSISTANT_NAME, htmlMode ? "" : chunk);
        span.dataset.messageId = msgId;
        span.dataset.htmlMode  = htmlMode;

        if (htmlMode && t.startsWith("<pure_html>")) {
          const inner = chunk.replace(/^<pure_html>/, "").replace(/<\/pure_html>$/, "");
          span.innerHTML = DOMPurify.sanitize(inner, purifyConfig);
        }

        continue;
      }

      const htmlMode = span.dataset.htmlMode === "true";
      if (htmlMode) {
        span.innerHTML += DOMPurify.sanitize(
          chunk.replace(/<\/pure_html>/i, ""),
          purifyConfig
        );
      } else {
        updateMessage(span, chunk);
      }
    }
  }

  function handleMessageCompleted(evt) {
    const msgId = evt.message_id || (evt.data && evt.data.id);
    logInfo("[Chat.js] handleMessageCompleted:", msgId);
    if (!msgId) return;

    const el = conv.querySelector(`[data-message-id="${msgId}"]`);
    if (!el) return;

    const fullMd = el.getAttribute("data-md").trim();
    const isHTML = ENABLE_HTML && /^\s*<\s*(form|div|input|textarea|button|fieldset|label|p)/i.test(fullMd);

    el.innerHTML = isHTML
      ? DOMPurify.sanitize(decodeEntities(fullMd), purifyConfig)
      : DOMPurify.sanitize(marked.parse(fullMd), purifyConfig);

    delete el.dataset.messageId;
    delete el.dataset.htmlMode;

    // — Single scroll after message has fully arrived —
    conv.scrollTop = conv.scrollHeight;

    sendBtn.removeAttribute("disabled");
  }

  function handleRunComplete() {
    logInfo("[Chat.js] run complete – clearing state");
    sendBtn.removeAttribute("disabled");
  }

  // ─── SSE Connection & Reconnect ─────────────────────────────────────────
  let hasSentReady = false;

  async function sendReady() {
    if (hasSentReady) return;
    hasSentReady = true;
    logInfo("[Chat.js] sendReady()");
    try {
      const res = await fetch("/chat/ready", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      logInfo("[Chat.js] /ready OK");
    } catch (err) {
      console.error("[Chat.js] sendReady failed", err);
    }
  }

  function connectSSE() {
    cleanupSSE();

    console.info("[Chat.js] connecting SSE to /chat/assistant_stream_message");
    src = new EventSource("/chat/assistant_stream_message");

    src.onopen = () => {
      console.info("[Chat.js] SSE open");
      hasSentReady = false;
      sendReady();
    };

    src.onerror = err => {
      console.warn("[Chat.js] SSE error", err);
      cleanupSSE();
      scheduleReconnect();
    };

    src.addEventListener("message_delta",       e => handleMessageDelta(JSON.parse(e.data)));
    src.addEventListener("message_completed",   e => handleMessageCompleted(JSON.parse(e.data)));
    src.addEventListener("thread.run.completed", e => handleRunComplete());
    src.addEventListener("done",                e => handleRunComplete());
  }

  connectSSE();

  // ─── Send User Message ──────────────────────────────────────────────────
  async function sendUserMessage(text) {
    console.info("[Chat.js] sendUserMessage:", text);
    sendBtn.setAttribute("disabled", "");
    try {
      const res = await fetch("/chat/user_send_message", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ message: text })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      console.info("[Chat.js] user message sent");
    } catch (err) {
      console.error("[Chat.js] sendUserMessage failed", err);
      sendBtn.removeAttribute("disabled");
    }
  }

  // ─── Chat Form Submit ────────────────────────────────────────────────────
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    appendMessage(USER_NAME, text);
    input.value = "";
    await sendUserMessage(text);
  });

  // ─── Handle In-chat Forms (e.g. user-info) ──────────────────────────────
  conv.addEventListener("submit", async e => {
    if (e.target.id !== "user-info-form") return;
    e.preventDefault();

    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      const res = await fetch("/submit_user_info", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { message } = await res.json();

      e.target.closest(".message.assistant")?.remove();
      appendMessage(ASSISTANT_NAME, message);
    } catch (err) {
      console.error("[Chat.js] form submission failed", err);
      appendMessage(ASSISTANT_NAME, "Submission failed. Please try again.");
    }
  });

});
