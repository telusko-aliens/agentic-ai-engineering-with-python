// the page talks to the FastAPI endpoints in api.py (same server, so no full URL needed)

const userInput = document.getElementById('user-input');
const switchUserBtn = document.getElementById('switch-user-btn');
const newConversationBtn = document.getElementById('new-conversation-btn');
const conversationSelect = document.getElementById('conversation-select');
const messagesBox = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const preferencesList = document.getElementById('preferences-list');
const groceryList = document.getElementById('grocery-list');
const refreshBtn = document.getElementById('refresh-btn');

let userId = userInput.value.trim().toLowerCase();
// a conversation is a LangGraph thread, so its id is sent as thread_id: riya-conversation-1, riya-conversation-2, ...
let conversationId = '';
let conversations = []; // previous conversations of this user, from the server, newest first

function newConversationId() {
  // one more than the highest number used so far
  const numbers = conversations.map((c) => Number(c.thread_id.split('-conversation-')[1]) || 0);
  return `${userId}-conversation-${Math.max(0, ...numbers) + 1}`;
}


// ---------- show messages ----------

function addMessage(type, text) {
  const div = document.createElement('div');
  div.className = `message ${type}`;
  div.textContent = text;
  messagesBox.appendChild(div);
  messagesBox.scrollTop = messagesBox.scrollHeight;
  return div;
}


// ---------- the list of previous conversations ----------

async function loadConversations() {
  const response = await fetch(`/users/${userId}/conversations`);
  const data = await response.json();
  conversations = data.conversations;
  fillConversationSelect();
}

function fillConversationSelect() {
  conversationSelect.innerHTML = '';

  // a new conversation is not in the list until its first message is sent
  if (!conversations.some((c) => c.thread_id === conversationId)) {
    conversationSelect.appendChild(new Option('New conversation', conversationId));
  }
  for (const conversation of conversations) {
    conversationSelect.appendChild(new Option(conversation.title, conversation.thread_id));
  }
  conversationSelect.value = conversationId;
}


// ---------- short-term memory: load the saved chat of this conversation ----------

async function loadConversation() {
  fillConversationSelect();
  messagesBox.innerHTML = '';

  const response = await fetch(`/conversations/${conversationId}/messages`);
  const data = await response.json();

  if (data.messages.length === 0) {
    addMessage('ai thinking', 'New conversation. Tell me about your diet or ask for a meal idea!');
  }
  for (const message of data.messages) {
    addMessage(message.type, message.content);
  }
}


// ---------- long-term memory: preferences and grocery list of this user ----------

function fillList(listElement, items, emptyText) {
  listElement.innerHTML = '';
  if (items.length === 0) {
    const li = document.createElement('li');
    li.className = 'empty';
    li.textContent = emptyText;
    listElement.appendChild(li);
  }
  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = item;
    listElement.appendChild(li);
  }
}

async function loadMemory() {
  const preferencesResponse = await fetch(`/users/${userId}/preferences`);
  const preferencesData = await preferencesResponse.json();
  fillList(preferencesList, preferencesData.preferences, 'nothing saved yet');

  const groceryResponse = await fetch(`/users/${userId}/grocery`);
  const groceryData = await groceryResponse.json();
  fillList(groceryList, groceryData.grocery_list, 'empty');
}


// ---------- send a message and stream the reply word by word ----------

async function sendMessage(text) {
  addMessage('human', text);
  const replyDiv = addMessage('ai thinking', 'The kitchen team is working...');
  sendBtn.disabled = true;

  const response = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, thread_id: conversationId, message: text }),
  });

  // read the streamed answer piece by piece and add it to the reply bubble
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let reply = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    reply += decoder.decode(value, { stream: true });
    replyDiv.className = 'message ai';
    replyDiv.textContent = reply;
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  sendBtn.disabled = false;
  // the first message adds this conversation to the list
  await loadConversations();
  // the agent may have saved a preference or changed the grocery list
  await loadMemory();
}


// ---------- buttons ----------

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  messageInput.value = '';
  await sendMessage(text);
});

newConversationBtn.addEventListener('click', async () => {
  // a new conversation forgets the chat, but long-term memory stays
  conversationId = newConversationId();
  await loadConversation();
});

conversationSelect.addEventListener('change', async () => {
  // go back to a previous conversation: its saved chat is loaded from Postgres
  conversationId = conversationSelect.value;
  await loadConversation();
});

async function startUser() {
  // open the newest conversation of this user, or a new one if there is none yet
  await loadConversations();
  conversationId = conversations.length > 0 ? conversations[0].thread_id : newConversationId();
  await loadConversation();
  await loadMemory();
}

switchUserBtn.addEventListener('click', async () => {
  // a different user has their own conversations, preferences and grocery list (isolation)
  userId = userInput.value.trim().toLowerCase() || 'guest';
  await startUser();
});

refreshBtn.addEventListener('click', loadMemory);


// ---------- start ----------

startUser();
