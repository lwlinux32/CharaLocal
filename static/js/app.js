/**
 * Local Character AI - Frontend Application
 * Pure Vanilla JavaScript (No React, No TypeScript, No Build Step)
 */

(function () {
  "use strict";

  // Application State
  const state = {
    characters: [],
    selectedCharacter: null,
    conversations: [],
    selectedConversation: null,
    messages: [],
    settings: {},
    isStreaming: false,
    abortController: null,
    activeTag: "all",
    searchQuery: ""
  };

  // DOM Elements
  const DOM = {
    sidebar: document.getElementById("sidebar"),
    mobileMenuToggle: document.getElementById("mobile-menu-toggle"),
    characterList: document.getElementById("character-list"),
    characterSearchInput: document.getElementById("character-search-input"),
    tagPillsContainer: document.getElementById("tag-pills-container"),
    btnOpenCreateChar: document.getElementById("btn-open-create-char"),
    btnImportCharModal: document.getElementById("btn-import-char-modal"),
    btnOpenSettings: document.getElementById("btn-open-settings"),
    btnHeaderLocalGuide: document.getElementById("btn-header-local-guide"),

    // Chat Header
    chatHeaderAvatar: document.getElementById("chat-header-avatar"),
    chatHeaderName: document.getElementById("chat-header-name"),
    chatHeaderTagline: document.getElementById("chat-header-tagline"),
    btnViewScenario: document.getElementById("btn-view-scenario"),
    btnToggleConvMenu: document.getElementById("btn-toggle-conv-menu"),
    currentConvTitle: document.getElementById("current-conv-title"),
    convDropdownMenu: document.getElementById("conv-dropdown-menu"),
    convDropdownList: document.getElementById("conv-dropdown-list"),
    btnNewChat: document.getElementById("btn-new-chat"),
    btnManageMemories: document.getElementById("btn-manage-memories"),
    btnEditCurrentChar: document.getElementById("btn-edit-current-char"),
    btnExportChar: document.getElementById("btn-export-char"),

    // Chat Area
    messagesContainer: document.getElementById("messages-container"),
    chatInput: document.getElementById("chat-input"),
    btnSendMessage: document.getElementById("btn-send-message"),
    btnStopStream: document.getElementById("btn-stop-stream"),

    // Settings Modal
    modalSettings: document.getElementById("modal-settings"),
    settingBaseUrl: document.getElementById("setting-base-url"),
    settingApiKey: document.getElementById("setting-api-key"),
    settingApiKeyStatus: document.getElementById("setting-api-key-status"),
    btnToggleKeyVisibility: document.getElementById("btn-toggle-key-visibility"),
    settingModel: document.getElementById("setting-model"),
    btnFetchModels: document.getElementById("btn-fetch-models"),
    detectedModelsContainer: document.getElementById("detected-models-container"),
    detectedModelsList: document.getElementById("detected-models-list"),
    btnOpenLocalGuide: document.getElementById("btn-open-local-guide"),
    modalLocalGuide: document.getElementById("modal-local-guide"),
    guideTabs: document.getElementById("guide-tabs"),
    settingTemperature: document.getElementById("setting-temperature"),
    tempValDisplay: document.getElementById("temp-val-display"),
    settingMaxTokens: document.getElementById("setting-max-tokens"),
    settingContextLimit: document.getElementById("setting-context-limit"),
    contextValDisplay: document.getElementById("context-val-display"),
    settingStreaming: document.getElementById("setting-streaming"),
    btnTestConnection: document.getElementById("btn-test-connection"),
    testConnectionResult: document.getElementById("test-connection-result"),
    btnSaveSettings: document.getElementById("btn-save-settings"),

    // Character Form Modal
    modalCharForm: document.getElementById("modal-character-form"),
    charModalTitle: document.getElementById("char-modal-title"),
    charFormId: document.getElementById("char-form-id"),
    charFormName: document.getElementById("char-form-name"),
    charFormAvatar: document.getElementById("char-form-avatar"),
    charFormShortDesc: document.getElementById("char-form-short-desc"),
    charFormDescription: document.getElementById("char-form-description"),
    charFormPersonality: document.getElementById("char-form-personality"),
    charFormScenario: document.getElementById("char-form-scenario"),
    charFormGreeting: document.getElementById("char-form-greeting"),
    charFormSystemPrompt: document.getElementById("char-form-system-prompt"),
    charFormExampleDialogue: document.getElementById("char-form-example-dialogue"),
    charFormTags: document.getElementById("char-form-tags"),
    charFormCreator: document.getElementById("char-form-creator"),
    btnDeleteCharFromForm: document.getElementById("btn-delete-char-from-form"),
    btnSaveCharacter: document.getElementById("btn-save-character"),

    // Scenario Modal
    modalCharScenario: document.getElementById("modal-char-scenario"),
    scenarioModalTitle: document.getElementById("scenario-modal-title"),
    scenarioModalBody: document.getElementById("scenario-modal-body"),

    // Memories Modal
    modalMemories: document.getElementById("modal-memories"),
    newMemoryContent: document.getElementById("new-memory-content"),
    newMemoryImportance: document.getElementById("new-memory-importance"),
    btnAddMemory: document.getElementById("btn-add-memory"),
    memoriesList: document.getElementById("memories-list"),
    memoriesCount: document.getElementById("memories-count"),

    // Import Modal
    modalImport: document.getElementById("modal-import"),
    importFileInput: document.getElementById("import-file-input"),
    importJsonPaste: document.getElementById("import-json-paste"),
    btnSubmitImport: document.getElementById("btn-submit-import"),

    // Toast Container
    toastContainer: document.getElementById("toast-container")
  };

  // --------------------------------------------------------------------------
  // Utility: Formatting and Markdown-Lite
  // --------------------------------------------------------------------------
  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatMessageText(text) {
    if (!text) return "";
    let safe = escapeHtml(text);

    // Asterisks for actions / narration: *action*
    safe = safe.replace(/\*([^*]+)\*/g, '<em class="action-text">*$1*</em>');

    // Bold text: **bold**
    safe = safe.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Line breaks
    safe = safe.replace(/\n/g, "<br>");

    return safe;
  }

  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    DOM.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 250);
    }, 3200);
  }

  function openModal(modalEl) {
    if (modalEl) modalEl.classList.add("show");
  }

  function closeModal(modalEl) {
    if (modalEl) modalEl.classList.remove("show");
  }

  // --------------------------------------------------------------------------
  // API Calls
  // --------------------------------------------------------------------------
  async function fetchSettings() {
    try {
      const res = await fetch("/api/settings");
      if (res.ok) {
        state.settings = await res.json();
        populateSettingsUI();
      }
    } catch (err) {
      console.error("Failed to load settings:", err);
    }
  }

  async function fetchCharacters() {
    try {
      let url = "/api/characters";
      const params = new URLSearchParams();
      if (state.searchQuery) params.append("search", state.searchQuery);
      if (state.activeTag && state.activeTag !== "all") params.append("tag", state.activeTag);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url);
      if (res.ok) {
        state.characters = await res.json();
        renderCharacterList();

        // If no character currently selected and we have characters, select the first one
        if (!state.selectedCharacter && state.characters.length > 0) {
          selectCharacter(state.characters[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch characters:", err);
    }
  }

  async function selectCharacter(charId) {
    try {
      const res = await fetch(`/api/characters/${charId}`);
      if (!res.ok) return;
      state.selectedCharacter = await res.json();
      renderActiveCharacterHeader();
      renderCharacterList(); // to update active card highlight

      // Load conversations for this character
      await fetchConversationsForCharacter(charId);

      // Close mobile sidebar if open
      if (window.innerWidth <= 768) {
        DOM.sidebar.classList.remove("open");
      }
    } catch (err) {
      console.error("Failed to select character:", err);
    }
  }

  async function fetchConversationsForCharacter(charId) {
    try {
      const res = await fetch(`/api/characters/${charId}/conversations`);
      if (res.ok) {
        state.conversations = await res.json();
        renderConversationDropdown();

        if (state.conversations.length > 0) {
          // Select most recent conversation
          await selectConversation(state.conversations[0].id);
        } else {
          // Create new conversation
          await createNewConversationForCurrentChar();
        }
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }

  async function selectConversation(convId) {
    try {
      const res = await fetch(`/api/conversations/${convId}`);
      if (!res.ok) return;
      const data = await res.json();
      state.selectedConversation = data.conversation;
      state.messages = data.messages || [];

      DOM.currentConvTitle.textContent = state.selectedConversation.title || "Chat";
      renderConversationDropdown();
      renderMessages();
      scrollToBottom();
    } catch (err) {
      console.error("Failed to select conversation:", err);
    }
  }

  async function createNewConversationForCurrentChar() {
    if (!state.selectedCharacter) return;
    try {
      const res = await fetch(`/api/characters/${state.selectedCharacter.id}/conversations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: `Chat with ${state.selectedCharacter.name}` })
      });
      if (res.ok) {
        const newConv = await res.json();
        showToast("New conversation started", "success");
        await fetchConversationsForCharacter(state.selectedCharacter.id);
        await selectConversation(newConv.id);
      }
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Rendering
  // --------------------------------------------------------------------------
  function renderCharacterList() {
    DOM.characterList.innerHTML = "";

    if (state.characters.length === 0) {
      DOM.characterList.innerHTML = `
        <div style="text-align: center; color: var(--text-subtle); padding: 32px 16px; font-size: 0.85rem;">
          No characters match your search.
        </div>
      `;
      return;
    }

    state.characters.forEach((char) => {
      const card = document.createElement("div");
      card.className = `character-card ${state.selectedCharacter && state.selectedCharacter.id === char.id ? "active" : ""}`;
      card.dataset.id = char.id;

      const tags = char.tags ? char.tags.split(",").slice(0, 2) : [];
      const tagsHtml = tags.map(t => `<span class="card-tag">${escapeHtml(t.trim())}</span>`).join("");

      card.innerHTML = `
        <img class="card-avatar" src="${escapeHtml(char.avatar)}" alt="${escapeHtml(char.name)}" onerror="this.src='https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80'">
        <div class="card-info">
          <div class="card-header">
            <span class="card-name">${escapeHtml(char.name)}</span>
          </div>
          <div class="card-desc">${escapeHtml(char.short_description || char.personality || "")}</div>
          <div class="card-tags">${tagsHtml}</div>
        </div>
      `;

      card.addEventListener("click", () => selectCharacter(char.id));
      DOM.characterList.appendChild(card);
    });
  }

  function renderActiveCharacterHeader() {
    const char = state.selectedCharacter;
    if (!char) return;

    DOM.chatHeaderAvatar.src = char.avatar || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80";
    DOM.chatHeaderAvatar.onerror = () => {
      DOM.chatHeaderAvatar.src = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80";
    };
    DOM.chatHeaderName.textContent = char.name;
    DOM.chatHeaderTagline.textContent = char.short_description || "Ready to chat.";
    DOM.chatInput.placeholder = `Message ${char.name}... (Actions in *asterisks*)`;
  }

  function renderConversationDropdown() {
    DOM.convDropdownList.innerHTML = "";

    if (!state.conversations || state.conversations.length === 0) {
      DOM.convDropdownList.innerHTML = `<div style="padding: 10px; font-size: 0.8rem; color: var(--text-subtle);">No conversations yet</div>`;
      return;
    }

    state.conversations.forEach((conv) => {
      const item = document.createElement("div");
      const isSelected = state.selectedConversation && state.selectedConversation.id === conv.id;
      item.className = `dropdown-item ${isSelected ? "active" : ""}`;

      item.innerHTML = `
        <span class="dropdown-item-title" title="${escapeHtml(conv.title)}">${escapeHtml(conv.title)}</span>
        <div class="dropdown-item-actions">
          <button class="msg-action-btn btn-rename-conv" title="Rename" data-id="${conv.id}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          </button>
          <button class="msg-action-btn btn-delete-conv" title="Delete" data-id="${conv.id}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
        </div>
      `;

      item.querySelector(".dropdown-item-title").addEventListener("click", () => {
        selectConversation(conv.id);
        DOM.convDropdownMenu.classList.remove("show");
      });

      item.querySelector(".btn-rename-conv").addEventListener("click", (e) => {
        e.stopPropagation();
        renameConversationPrompt(conv);
      });

      item.querySelector(".btn-delete-conv").addEventListener("click", (e) => {
        e.stopPropagation();
        deleteConversationConfirm(conv);
      });

      DOM.convDropdownList.appendChild(item);
    });
  }

  function renderMessages() {
    DOM.messagesContainer.innerHTML = "";

    if (!state.selectedCharacter) return;

    // Greeting / Intro Card at top of conversation
    const introCard = document.createElement("div");
    introCard.className = "empty-chat-state";
    introCard.innerHTML = `
      <img class="empty-chat-avatar" src="${escapeHtml(state.selectedCharacter.avatar)}" alt="${escapeHtml(state.selectedCharacter.name)}">
      <h2 class="empty-chat-title">${escapeHtml(state.selectedCharacter.name)}</h2>
      <p class="empty-chat-desc">${escapeHtml(state.selectedCharacter.description || state.selectedCharacter.short_description || "")}</p>
      ${state.selectedCharacter.scenario ? `<div class="scenario-badge"><strong>Scenario:</strong> ${escapeHtml(state.selectedCharacter.scenario)}</div>` : ""}
    `;
    DOM.messagesContainer.appendChild(introCard);

    // Messages list
    state.messages.forEach((msg) => {
      appendMessageToDOM(msg, false);
    });
  }

  function appendMessageToDOM(msg, isLast = false) {
    const isUser = msg.role === "user";
    const char = state.selectedCharacter;

    const row = document.createElement("div");
    row.className = `message-row ${msg.role}`;
    row.id = `msg-${msg.id}`;

    let avatarHtml = "";
    if (isUser) {
      avatarHtml = `<div class="user-avatar-placeholder">U</div>`;
    } else {
      const avatarSrc = (char && char.avatar) || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80";
      avatarHtml = `<img class="message-avatar" src="${escapeHtml(avatarSrc)}" alt="${escapeHtml(char ? char.name : 'Character')}">`;
    }

    const authorName = isUser ? "You" : (char ? char.name : "Character");
    const formattedContent = formatMessageText(msg.content);

    row.innerHTML = `
      ${avatarHtml}
      <div class="message-bubble-wrap">
        <span class="message-author">${escapeHtml(authorName)}</span>
        <div class="message-bubble" id="bubble-content-${msg.id}">${formattedContent}</div>
        <div class="message-actions">
          <button class="msg-action-btn btn-copy-msg" data-content="${encodeURIComponent(msg.content)}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Copy
          </button>
          ${!isUser ? `
          <button class="msg-action-btn btn-regenerate-msg" data-id="${msg.id}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6"/><path d="M22 11.5A10 10 0 0 0 3.2 7.2M2 12.5a10 10 0 0 0 18.8 4.2"/></svg>
            Regenerate
          </button>` : ""}
          <button class="msg-action-btn btn-delete-msg" data-id="${msg.id}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>
          </button>
        </div>
      </div>
    `;

    // Copy event listener
    row.querySelector(".btn-copy-msg").addEventListener("click", () => {
      navigator.clipboard.writeText(msg.content);
      showToast("Message copied to clipboard", "info");
    });

    // Delete event listener
    row.querySelector(".btn-delete-msg").addEventListener("click", async () => {
      if (confirm("Delete this message?")) {
        await deleteMessageFromDB(msg.id);
        row.remove();
        state.messages = state.messages.filter(m => m.id !== msg.id);
      }
    });

    // Regenerate event listener
    const regenBtn = row.querySelector(".btn-regenerate-msg");
    if (regenBtn) {
      regenBtn.addEventListener("click", () => {
        handleRegenerateResponse();
      });
    }

    DOM.messagesContainer.appendChild(row);
  }

  function scrollToBottom() {
    DOM.messagesContainer.scrollTop = DOM.messagesContainer.scrollHeight;
  }

  // --------------------------------------------------------------------------
  // Message Sending & Streaming Response
  // --------------------------------------------------------------------------
  async function sendMessage() {
    const text = DOM.chatInput.value.trim();
    if (!text || state.isStreaming || !state.selectedConversation) return;

    DOM.chatInput.value = "";
    DOM.chatInput.style.height = "auto";

    // 1. Optimistically append user message to UI
    const tempUserMsg = {
      id: "temp-" + Date.now(),
      conversation_id: state.selectedConversation.id,
      role: "user",
      content: text,
      created_at: new Date().toISOString()
    };
    state.messages.push(tempUserMsg);
    appendMessageToDOM(tempUserMsg);
    scrollToBottom();

    // 2. Prepare streaming assistant bubble
    const tempAssistantId = "stream-" + Date.now();
    const char = state.selectedCharacter;
    const streamRow = document.createElement("div");
    streamRow.className = "message-row assistant";
    streamRow.id = `msg-${tempAssistantId}`;

    const avatarSrc = (char && char.avatar) || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80";
    streamRow.innerHTML = `
      <img class="message-avatar" src="${escapeHtml(avatarSrc)}" alt="${escapeHtml(char.name)}">
      <div class="message-bubble-wrap">
        <span class="message-author">${escapeHtml(char.name)}</span>
        <div class="message-bubble" id="bubble-content-${tempAssistantId}">
          <span class="stream-text"></span><span class="typing-cursor"></span>
        </div>
      </div>
    `;
    DOM.messagesContainer.appendChild(streamRow);
    scrollToBottom();

    const streamTextEl = streamRow.querySelector(".stream-text");
    const cursorEl = streamRow.querySelector(".typing-cursor");

    // UI Streaming state
    setStreamingState(true);
    state.abortController = new AbortController();

    let fullAccumulated = "";

    try {
      const response = await fetch(`/api/conversations/${state.selectedConversation.id}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text, role: "user" }),
        signal: state.abortController.signal
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep last incomplete line

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line) continue;

          if (line.startsWith("event: token")) {
            const nextLine = lines[++i];
            if (nextLine && nextLine.startsWith("data: ")) {
              try {
                const tokenData = JSON.parse(nextLine.slice(6));
                fullAccumulated += tokenData.token;
                streamTextEl.innerHTML = formatMessageText(fullAccumulated);
                scrollToBottom();
              } catch (e) {}
            }
          } else if (line.startsWith("event: done")) {
            const nextLine = lines[++i];
            if (nextLine && nextLine.startsWith("data: ")) {
              try {
                const finalMsg = JSON.parse(nextLine.slice(6));
                state.messages.push(finalMsg);
              } catch (e) {}
            }
          }
        }
      }
    } catch (err) {
      if (err.name === "AbortError") {
        fullAccumulated += "\n*(Generation stopped by user)*";
      } else {
        fullAccumulated += `\n*(Generation error: ${err.message})*`;
      }
      streamTextEl.innerHTML = formatMessageText(fullAccumulated);
    } finally {
      if (cursorEl) cursorEl.remove();
      setStreamingState(false);
      state.abortController = null;
      // Re-fetch conversation messages to sync database IDs and timestamps
      if (state.selectedConversation) {
        const syncRes = await fetch(`/api/conversations/${state.selectedConversation.id}`);
        if (syncRes.ok) {
          const syncData = await syncRes.json();
          state.messages = syncData.messages || [];
          renderMessages();
          scrollToBottom();
        }
      }
    }
  }

  async function handleRegenerateResponse() {
    if (state.isStreaming || !state.selectedConversation) return;

    // Remove last message row from DOM if assistant
    const lastMsg = state.messages[state.messages.length - 1];
    if (lastMsg && lastMsg.role === "assistant") {
      const el = document.getElementById(`msg-${lastMsg.id}`);
      if (el) el.remove();
      state.messages.pop();
    }

    const tempAssistantId = "regen-" + Date.now();
    const char = state.selectedCharacter;
    const streamRow = document.createElement("div");
    streamRow.className = "message-row assistant";
    streamRow.id = `msg-${tempAssistantId}`;

    const avatarSrc = (char && char.avatar) || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80";
    streamRow.innerHTML = `
      <img class="message-avatar" src="${escapeHtml(avatarSrc)}" alt="${escapeHtml(char.name)}">
      <div class="message-bubble-wrap">
        <span class="message-author">${escapeHtml(char.name)}</span>
        <div class="message-bubble" id="bubble-content-${tempAssistantId}">
          <span class="stream-text"></span><span class="typing-cursor"></span>
        </div>
      </div>
    `;
    DOM.messagesContainer.appendChild(streamRow);
    scrollToBottom();

    const streamTextEl = streamRow.querySelector(".stream-text");
    const cursorEl = streamRow.querySelector(".typing-cursor");

    setStreamingState(true);
    state.abortController = new AbortController();

    let fullAccumulated = "";

    try {
      const response = await fetch(`/api/conversations/${state.selectedConversation.id}/regenerate`, {
        method: "POST",
        signal: state.abortController.signal
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line) continue;

          if (line.startsWith("event: token")) {
            const nextLine = lines[++i];
            if (nextLine && nextLine.startsWith("data: ")) {
              try {
                const tokenData = JSON.parse(nextLine.slice(6));
                fullAccumulated += tokenData.token;
                streamTextEl.innerHTML = formatMessageText(fullAccumulated);
                scrollToBottom();
              } catch (e) {}
            }
          } else if (line.startsWith("event: done")) {
            const nextLine = lines[++i];
            if (nextLine && nextLine.startsWith("data: ")) {
              try {
                const finalMsg = JSON.parse(nextLine.slice(6));
                state.messages.push(finalMsg);
              } catch (e) {}
            }
          }
        }
      }
    } catch (err) {
      if (err.name === "AbortError") {
        fullAccumulated += "\n*(Regeneration cancelled)*";
      } else {
        fullAccumulated += `\n*(Regeneration error: ${err.message})*`;
      }
      streamTextEl.innerHTML = formatMessageText(fullAccumulated);
    } finally {
      if (cursorEl) cursorEl.remove();
      setStreamingState(false);
      state.abortController = null;

      if (state.selectedConversation) {
        const syncRes = await fetch(`/api/conversations/${state.selectedConversation.id}`);
        if (syncRes.ok) {
          const syncData = await syncRes.json();
          state.messages = syncData.messages || [];
          renderMessages();
          scrollToBottom();
        }
      }
    }
  }

  function stopStreaming() {
    if (state.abortController) {
      state.abortController.abort();
    }
  }

  function setStreamingState(isStreaming) {
    state.isStreaming = isStreaming;
    if (isStreaming) {
      DOM.btnSendMessage.style.display = "none";
      DOM.btnStopStream.style.display = "flex";
    } else {
      DOM.btnSendMessage.style.display = "flex";
      DOM.btnStopStream.style.display = "none";
    }
  }

  async function deleteMessageFromDB(msgId) {
    if (!state.selectedConversation) return;
    try {
      await fetch(`/api/conversations/${state.selectedConversation.id}/messages/${msgId}`, {
        method: "DELETE"
      });
      showToast("Message deleted", "info");
    } catch (err) {
      console.error("Failed to delete message:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Conversation Management (Rename, Delete)
  // --------------------------------------------------------------------------
  async function renameConversationPrompt(conv) {
    const newTitle = prompt("Enter new title for this conversation:", conv.title);
    if (!newTitle || newTitle.trim() === "" || newTitle === conv.title) return;

    try {
      const res = await fetch(`/api/conversations/${conv.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle.trim() })
      });
      if (res.ok) {
        showToast("Conversation renamed", "success");
        if (state.selectedConversation && state.selectedConversation.id === conv.id) {
          state.selectedConversation.title = newTitle.trim();
          DOM.currentConvTitle.textContent = newTitle.trim();
        }
        await fetchConversationsForCharacter(state.selectedCharacter.id);
      }
    } catch (err) {
      console.error("Failed to rename conversation:", err);
    }
  }

  async function deleteConversationConfirm(conv) {
    if (!confirm(`Delete conversation "${conv.title}"?`)) return;

    try {
      const res = await fetch(`/api/conversations/${conv.id}`, { method: "DELETE" });
      if (res.ok) {
        showToast("Conversation deleted", "info");
        await fetchConversationsForCharacter(state.selectedCharacter.id);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Character Creation / Editing
  // --------------------------------------------------------------------------
  function openCharacterForm(char = null) {
    if (char) {
      // Edit mode
      DOM.charModalTitle.textContent = `Edit Character: ${char.name}`;
      DOM.charFormId.value = char.id;
      DOM.charFormName.value = char.name || "";
      DOM.charFormAvatar.value = char.avatar || "";
      DOM.charFormShortDesc.value = char.short_description || "";
      DOM.charFormDescription.value = char.description || "";
      DOM.charFormPersonality.value = char.personality || "";
      DOM.charFormScenario.value = char.scenario || "";
      DOM.charFormGreeting.value = char.greeting || "";
      DOM.charFormSystemPrompt.value = char.system_prompt || "";
      DOM.charFormExampleDialogue.value = char.example_dialogue || "";
      DOM.charFormTags.value = char.tags || "";
      DOM.charFormCreator.value = char.creator || "You";
      DOM.btnDeleteCharFromForm.style.display = "block";
    } else {
      // Create mode
      DOM.charModalTitle.textContent = "Create New Character";
      DOM.charFormId.value = "";
      DOM.charFormName.value = "";
      DOM.charFormAvatar.value = "";
      DOM.charFormShortDesc.value = "";
      DOM.charFormDescription.value = "";
      DOM.charFormPersonality.value = "";
      DOM.charFormScenario.value = "";
      DOM.charFormGreeting.value = "Hello! It's good to meet you.";
      DOM.charFormSystemPrompt.value = "";
      DOM.charFormExampleDialogue.value = "";
      DOM.charFormTags.value = "Custom";
      DOM.charFormCreator.value = "You";
      DOM.btnDeleteCharFromForm.style.display = "none";
    }
    openModal(DOM.modalCharForm);
  }

  async function saveCharacterFromForm() {
    const name = DOM.charFormName.value.trim();
    if (!name) {
      showToast("Character name is required", "error");
      DOM.charFormName.focus();
      return;
    }

    const payload = {
      name: name,
      avatar: DOM.charFormAvatar.value.trim() || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80",
      short_description: DOM.charFormShortDesc.value.trim(),
      description: DOM.charFormDescription.value.trim(),
      personality: DOM.charFormPersonality.value.trim(),
      scenario: DOM.charFormScenario.value.trim(),
      greeting: DOM.charFormGreeting.value.trim() || "Hello!",
      system_prompt: DOM.charFormSystemPrompt.value.trim(),
      example_dialogue: DOM.charFormExampleDialogue.value.trim(),
      tags: DOM.charFormTags.value.trim(),
      creator: DOM.charFormCreator.value.trim() || "You"
    };

    const charId = DOM.charFormId.value;

    try {
      if (charId) {
        // Update existing character
        const res = await fetch(`/api/characters/${charId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const updated = await res.json();
          showToast(`Updated character "${updated.name}"`, "success");
          closeModal(DOM.modalCharForm);
          await fetchCharacters();
          await selectCharacter(charId);
        }
      } else {
        // Create new character
        const res = await fetch("/api/characters", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const created = await res.json();
          showToast(`Created character "${created.name}"`, "success");
          closeModal(DOM.modalCharForm);
          await fetchCharacters();
          await selectCharacter(created.id);
        }
      }
    } catch (err) {
      console.error("Failed to save character:", err);
      showToast("Error saving character", "error");
    }
  }

  async function deleteCurrentCharacter() {
    const char = state.selectedCharacter;
    if (!char) return;

    if (!confirm(`Are you sure you want to permanently delete "${char.name}" and all their chats and memories?`)) {
      return;
    }

    try {
      const res = await fetch(`/api/characters/${char.id}`, { method: "DELETE" });
      if (res.ok) {
        showToast(`Deleted character "${char.name}"`, "info");
        closeModal(DOM.modalCharForm);
        state.selectedCharacter = null;
        await fetchCharacters();
      }
    } catch (err) {
      console.error("Failed to delete character:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Scenario & Lore Dossier Viewer
  // --------------------------------------------------------------------------
  function openScenarioViewer() {
    const char = state.selectedCharacter;
    if (!char) return;

    DOM.scenarioModalTitle.textContent = `${char.name} — Lore & Scenario Dossier`;
    DOM.scenarioModalBody.innerHTML = `
      <div style="display: flex; gap: 16px; align-items: center; margin-bottom: 16px;">
        <img src="${escapeHtml(char.avatar)}" alt="${escapeHtml(char.name)}" style="width: 64px; height: 64px; border-radius: var(--radius-full); object-fit: cover; border: 2px solid var(--primary);">
        <div>
          <h4 style="font-size: 1.1rem; font-weight: 700;">${escapeHtml(char.name)}</h4>
          <p style="font-size: 0.825rem; color: var(--text-muted);">${escapeHtml(char.short_description || "")}</p>
          <div style="margin-top: 4px; display: flex; gap: 4px;">
            ${(char.tags ? char.tags.split(",") : []).map(t => `<span class="card-tag">${escapeHtml(t.trim())}</span>`).join("")}
          </div>
        </div>
      </div>

      ${char.scenario ? `
      <div style="margin-bottom: 14px;">
        <h5 style="font-size: 0.85rem; font-weight: 600; color: #c4b5fd; text-transform: uppercase; margin-bottom: 4px;">Current Scenario</h5>
        <div style="background-color: var(--bg-card); padding: 12px; border-radius: var(--radius-md); font-size: 0.875rem; border: 1px solid var(--border-subtle); line-height: 1.5;">
          ${escapeHtml(char.scenario)}
        </div>
      </div>` : ""}

      ${char.personality ? `
      <div style="margin-bottom: 14px;">
        <h5 style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Personality & Mindset</h5>
        <div style="background-color: var(--bg-card); padding: 12px; border-radius: var(--radius-md); font-size: 0.875rem; border: 1px solid var(--border-subtle); line-height: 1.5;">
          ${escapeHtml(char.personality)}
        </div>
      </div>` : ""}

      ${char.description ? `
      <div style="margin-bottom: 14px;">
        <h5 style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Background & Lore</h5>
        <div style="background-color: var(--bg-card); padding: 12px; border-radius: var(--radius-md); font-size: 0.875rem; border: 1px solid var(--border-subtle); line-height: 1.5;">
          ${escapeHtml(char.description)}
        </div>
      </div>` : ""}
    `;

    openModal(DOM.modalCharScenario);
  }

  // --------------------------------------------------------------------------
  // Long-Term Memories Manager
  // --------------------------------------------------------------------------
  async function openMemoriesManager() {
    if (!state.selectedCharacter) return;
    await loadMemoriesList();
    openModal(DOM.modalMemories);
  }

  async function loadMemoriesList() {
    const char = state.selectedCharacter;
    if (!char) return;

    try {
      const res = await fetch(`/api/characters/${char.id}/memories`);
      if (res.ok) {
        const memories = await res.json();
        DOM.memoriesCount.textContent = memories.length;
        DOM.memoriesList.innerHTML = "";

        if (memories.length === 0) {
          DOM.memoriesList.innerHTML = `
            <div style="padding: 16px; text-align: center; color: var(--text-subtle); font-size: 0.825rem;">
              No memories recorded yet. Add facts above to establish shared character memory!
            </div>
          `;
          return;
        }

        memories.forEach((mem) => {
          const item = document.createElement("div");
          item.style.cssText = "display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border-subtle); font-size: 0.85rem;";

          const stars = "★".repeat(mem.importance) + "☆".repeat(5 - mem.importance);

          item.innerHTML = `
            <div style="flex: 1; margin-right: 12px;">
              <div>${escapeHtml(mem.content)}</div>
              <div style="font-size: 0.725rem; color: #fbbf24; margin-top: 2px;">Importance: ${stars}</div>
            </div>
            <button class="msg-action-btn btn-delete-mem" data-id="${mem.id}" style="color: var(--danger);">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/></svg>
            </button>
          `;

          item.querySelector(".btn-delete-mem").addEventListener("click", async () => {
            await fetch(`/api/memories/${mem.id}`, { method: "DELETE" });
            showToast("Memory deleted", "info");
            await loadMemoriesList();
          });

          DOM.memoriesList.appendChild(item);
        });
      }
    } catch (err) {
      console.error("Failed to load memories:", err);
    }
  }

  async function addNewMemory() {
    const char = state.selectedCharacter;
    const content = DOM.newMemoryContent.value.trim();
    const importance = parseInt(DOM.newMemoryImportance.value, 10) || 1;

    if (!char || !content) {
      showToast("Please enter memory content", "error");
      DOM.newMemoryContent.focus();
      return;
    }

    try {
      const res = await fetch(`/api/characters/${char.id}/memories`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: content,
          importance: importance,
          conversation_id: state.selectedConversation ? state.selectedConversation.id : null
        })
      });

      if (res.ok) {
        showToast("Memory added to character", "success");
        DOM.newMemoryContent.value = "";
        await loadMemoriesList();
      }
    } catch (err) {
      console.error("Failed to add memory:", err);
    }
  }

  // --------------------------------------------------------------------------
  // Settings & Presets
  // --------------------------------------------------------------------------
  function populateSettingsUI() {
    const s = state.settings;
    DOM.settingBaseUrl.value = s.base_url || "https://api.openai.com/v1";
    DOM.settingModel.value = s.model || "gpt-4o-mini";
    DOM.settingTemperature.value = s.temperature || 0.85;
    DOM.tempValDisplay.textContent = DOM.settingTemperature.value;
    DOM.settingMaxTokens.value = s.max_tokens || 1024;
    DOM.settingContextLimit.value = s.context_limit || 20;
    DOM.contextValDisplay.textContent = DOM.settingContextLimit.value;
    DOM.settingStreaming.checked = s.streaming !== false;

    if (s.has_api_key) {
      DOM.settingApiKeyStatus.textContent = `Configured: ${s.masked_api_key} (Type new key to update or leave blank to keep)`;
    } else {
      DOM.settingApiKeyStatus.textContent = "No API key configured (Required for OpenAI / Gemini; optional for local Ollama/LM Studio)";
    }
  }

  function applyPreset(presetKey) {
    const presets = {
      openai: {
        base_url: "https://api.openai.com/v1",
        model: "gpt-4o-mini",
        hint: "Requires OpenAI API key (sk-...)"
      },
      gemini: {
        base_url: "https://generativelanguage.googleapis.com/v1beta/openai/",
        model: "gemini-3.8-flash",
        hint: "Requires Google AI Gemini API key"
      },
      ollama: {
        base_url: "http://localhost:11434/v1",
        model: "llama3",
        hint: "Local inference - No API key needed"
      },
      lmstudio: {
        base_url: "http://localhost:1234/v1",
        model: "local-model",
        hint: "Local inference - No API key needed"
      },
      groq: {
        base_url: "https://api.groq.com/openai/v1",
        model: "llama-3.3-70b-versatile",
        hint: "Ultra-fast inference - Requires Groq key (gsk_...)"
      },
      openrouter: {
        base_url: "https://openrouter.ai/api/v1",
        model: "anthropic/claude-3.5-sonnet",
        hint: "Requires OpenRouter key (sk-or-...)"
      }
    };

    const p = presets[presetKey];
    if (p) {
      DOM.settingBaseUrl.value = p.base_url;
      DOM.settingModel.value = p.model;
      showToast(`Applied preset: ${presetKey.toUpperCase()} (${p.hint})`, "info");
    }
  }

  async function saveSettings() {
    const payload = {
      base_url: DOM.settingBaseUrl.value.trim(),
      model: DOM.settingModel.value.trim(),
      temperature: parseFloat(DOM.settingTemperature.value),
      max_tokens: parseInt(DOM.settingMaxTokens.value, 10),
      context_limit: parseInt(DOM.settingContextLimit.value, 10),
      streaming: DOM.settingStreaming.checked
    };

    const keyVal = DOM.settingApiKey.value.trim();
    if (keyVal) {
      payload.api_key = keyVal;
    }

    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        state.settings = data.settings;
        showToast("Settings saved successfully", "success");
        closeModal(DOM.modalSettings);
        DOM.settingApiKey.value = "";
      }
    } catch (err) {
      console.error("Failed to save settings:", err);
      showToast("Error saving settings", "error");
    }
  }

  function renderDetectedModels(models) {
    if (!models || models.length === 0) {
      DOM.detectedModelsContainer.style.display = "none";
      return;
    }
    DOM.detectedModelsContainer.style.display = "block";
    DOM.detectedModelsList.innerHTML = "";
    models.forEach((m) => {
      const badge = document.createElement("button");
      badge.type = "button";
      badge.className = "badge-model";
      badge.textContent = m;
      badge.title = `Click to select model: ${m}`;
      badge.addEventListener("click", () => {
        DOM.settingModel.value = m;
        showToast(`Selected model: ${m}`, "success");
      });
      DOM.detectedModelsList.appendChild(badge);
    });
  }

  async function fetchInstalledModels() {
    const baseUrl = DOM.settingBaseUrl.value.trim();
    if (!baseUrl) {
      showToast("Please enter an API Base URL first", "error");
      DOM.settingBaseUrl.focus();
      return;
    }

    DOM.btnFetchModels.textContent = "Fetching...";
    DOM.btnFetchModels.disabled = true;

    try {
      const res = await fetch(`/api/settings/local-models?base_url=${encodeURIComponent(baseUrl)}`);
      const data = await res.json();
      const models = data.models || [];

      if (models.length > 0) {
        showToast(`Found ${models.length} model(s) on endpoint!`, "success");
        renderDetectedModels(models);
        // If current model is empty, set to first one
        if (!DOM.settingModel.value) {
          DOM.settingModel.value = models[0];
        }
      } else {
        showToast("No models found on endpoint. Check if server is running.", "info");
        DOM.detectedModelsContainer.style.display = "none";
      }
    } catch (err) {
      showToast(`Failed to fetch models: ${err.message}`, "error");
    } finally {
      DOM.btnFetchModels.textContent = "🔍 Fetch Installed Models";
      DOM.btnFetchModels.disabled = false;
    }
  }

  async function testConnection() {
    const resultBox = DOM.testConnectionResult;
    resultBox.style.display = "block";
    resultBox.style.backgroundColor = "rgba(59, 130, 246, 0.15)";
    resultBox.style.color = "var(--text-main)";
    resultBox.textContent = "Testing connection to endpoint...";

    const payload = {
      base_url: DOM.settingBaseUrl.value.trim(),
      api_key: DOM.settingApiKey.value.trim(),
      model: DOM.settingModel.value.trim()
    };

    try {
      const res = await fetch("/api/settings/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        resultBox.style.backgroundColor = "rgba(16, 185, 129, 0.2)";
        resultBox.style.color = "#34d399";
        resultBox.textContent = `✓ ${data.message}`;
        if (data.models && data.models.length > 0) {
          renderDetectedModels(data.models);
        }
      } else {
        resultBox.style.backgroundColor = "rgba(239, 68, 68, 0.2)";
        resultBox.style.color = "#f87171";
        resultBox.textContent = `✗ ${data.message}`;
        if (data.models && data.models.length > 0) {
          renderDetectedModels(data.models);
        }
      }
    } catch (err) {
      resultBox.style.backgroundColor = "rgba(239, 68, 68, 0.2)";
      resultBox.style.color = "#f87171";
      resultBox.textContent = `✗ Connection failed: ${err.message}`;
    }
  }

  // --------------------------------------------------------------------------
  // Export & Import
  // --------------------------------------------------------------------------
  function exportCurrentCharacter() {
    const char = state.selectedCharacter;
    if (!char) return;
    window.location.href = `/api/characters/${char.id}/export`;
    showToast(`Exporting ${char.name}...`, "info");
  }

  async function handleImportSubmit() {
    let jsonStr = DOM.importJsonPaste.value.trim();
    const file = DOM.importFileInput.files[0];

    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        await processImportJson(e.target.result);
      };
      reader.readAsText(file);
    } else if (jsonStr) {
      await processImportJson(jsonStr);
    } else {
      showToast("Please choose a file or paste JSON", "error");
    }
  }

  async function processImportJson(rawStr) {
    try {
      const parsed = JSON.parse(rawStr);

      if (parsed.conversation) {
        // Conversation import
        const res = await fetch("/api/conversations/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(parsed)
        });
        if (res.ok) {
          const imported = await res.json();
          showToast("Conversation imported successfully", "success");
          closeModal(DOM.modalImport);
          await selectConversation(imported.id);
        } else {
          const err = await res.json();
          showToast(`Import error: ${err.detail || "Invalid conversation"}`, "error");
        }
      } else {
        // Character import
        const res = await fetch("/api/characters/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(parsed)
        });
        if (res.ok) {
          const importedChar = await res.json();
          showToast(`Character "${importedChar.name}" imported!`, "success");
          closeModal(DOM.modalImport);
          DOM.importJsonPaste.value = "";
          DOM.importFileInput.value = "";
          await fetchCharacters();
          await selectCharacter(importedChar.id);
        } else {
          const err = await res.json();
          showToast(`Import error: ${err.detail || "Invalid format"}`, "error");
        }
      }
    } catch (err) {
      showToast(`Invalid JSON file: ${err.message}`, "error");
    }
  }

  // --------------------------------------------------------------------------
  // Event Listeners Initialization
  // --------------------------------------------------------------------------
  function initEventListeners() {
    // Mobile menu toggle
    DOM.mobileMenuToggle.addEventListener("click", () => {
      DOM.sidebar.classList.toggle("open");
    });

    // Close sidebar on click outside on mobile
    document.addEventListener("click", (e) => {
      if (window.innerWidth <= 768) {
        if (!DOM.sidebar.contains(e.target) && !DOM.mobileMenuToggle.contains(e.target)) {
          DOM.sidebar.classList.remove("open");
        }
      }
    });

    // Search input
    let searchDebounce = null;
    DOM.characterSearchInput.addEventListener("input", (e) => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        state.searchQuery = e.target.value.trim();
        fetchCharacters();
      }, 250);
    });

    // Tag pills filtering
    DOM.tagPillsContainer.addEventListener("click", (e) => {
      const pill = e.target.closest(".tag-pill");
      if (!pill) return;
      DOM.tagPillsContainer.querySelectorAll(".tag-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      state.activeTag = pill.dataset.tag;
      fetchCharacters();
    });

    // Open modals
    DOM.btnOpenCreateChar.addEventListener("click", () => openCharacterForm(null));
    DOM.btnEditCurrentChar.addEventListener("click", () => openCharacterForm(state.selectedCharacter));
    DOM.btnExportChar.addEventListener("click", exportCurrentCharacter);
    DOM.btnViewScenario.addEventListener("click", openScenarioViewer);
    DOM.btnManageMemories.addEventListener("click", openMemoriesManager);
    DOM.btnOpenSettings.addEventListener("click", () => {
      fetchSettings();
      DOM.testConnectionResult.style.display = "none";
      openModal(DOM.modalSettings);
    });
    DOM.btnImportCharModal.addEventListener("click", () => openModal(DOM.modalImport));

    // Close modals
    document.querySelectorAll(".btn-close-modal").forEach((btn) => {
      btn.addEventListener("click", () => {
        const modalId = btn.dataset.modal;
        if (modalId) closeModal(document.getElementById(modalId));
      });
    });

    // Close modal when clicking on overlay background
    document.querySelectorAll(".modal-overlay").forEach((overlay) => {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeModal(overlay);
      });
    });

    // Conversation dropdown toggle
    DOM.btnToggleConvMenu.addEventListener("click", (e) => {
      e.stopPropagation();
      DOM.convDropdownMenu.classList.toggle("show");
    });

    document.addEventListener("click", () => {
      DOM.convDropdownMenu.classList.remove("show");
    });

    // New chat button
    DOM.btnNewChat.addEventListener("click", () => {
      DOM.convDropdownMenu.classList.remove("show");
      createNewConversationForCurrentChar();
    });

    // Chat textarea auto-expansion & Send on Enter
    DOM.chatInput.addEventListener("input", () => {
      DOM.chatInput.style.height = "auto";
      DOM.chatInput.style.height = Math.min(DOM.chatInput.scrollHeight, 160) + "px";
    });

    DOM.chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    DOM.btnSendMessage.addEventListener("click", sendMessage);
    DOM.btnStopStream.addEventListener("click", stopStreaming);

    // Character Form Actions
    DOM.btnSaveCharacter.addEventListener("click", saveCharacterFromForm);
    DOM.btnDeleteCharFromForm.addEventListener("click", deleteCurrentCharacter);

    // Memories Form Actions
    DOM.btnAddMemory.addEventListener("click", addNewMemory);

    // Settings actions
    DOM.settingTemperature.addEventListener("input", (e) => {
      DOM.tempValDisplay.textContent = e.target.value;
    });

    DOM.settingContextLimit.addEventListener("input", (e) => {
      DOM.contextValDisplay.textContent = e.target.value;
    });

    DOM.btnToggleKeyVisibility.addEventListener("click", () => {
      const isPwd = DOM.settingApiKey.type === "password";
      DOM.settingApiKey.type = isPwd ? "text" : "password";
    });

    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
    });

    DOM.btnSaveSettings.addEventListener("click", saveSettings);
    DOM.btnTestConnection.addEventListener("click", testConnection);

    if (DOM.btnFetchModels) {
      DOM.btnFetchModels.addEventListener("click", fetchInstalledModels);
    }

    if (DOM.btnOpenLocalGuide) {
      DOM.btnOpenLocalGuide.addEventListener("click", () => openModal(DOM.modalLocalGuide));
    }

    if (DOM.btnHeaderLocalGuide) {
      DOM.btnHeaderLocalGuide.addEventListener("click", () => openModal(DOM.modalLocalGuide));
    }

    if (DOM.guideTabs) {
      DOM.guideTabs.addEventListener("click", (e) => {
        const tabBtn = e.target.closest(".guide-tab");
        if (!tabBtn) return;
        const targetId = tabBtn.dataset.tab;
        DOM.guideTabs.querySelectorAll(".guide-tab").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".guide-panel").forEach(p => p.classList.remove("active"));
        tabBtn.classList.add("active");
        const panel = document.getElementById(targetId);
        if (panel) panel.classList.add("active");
      });
    }

    // Import action
    DOM.btnSubmitImport.addEventListener("click", handleImportSubmit);
  }

  // --------------------------------------------------------------------------
  // Application Bootstrap
  // --------------------------------------------------------------------------
  async function initApp() {
    initEventListeners();
    await fetchSettings();
    await fetchCharacters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
  } else {
    initApp();
  }
})();
