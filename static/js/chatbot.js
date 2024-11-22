import { GoogleGenerativeAI } from "@google/generative-ai";

const sendMessage = document.querySelector(".chat-input span");
const chatInput = document.querySelector(".chat-input textarea");
const chatbox = document.querySelector(".chatbox");
const chatbotToggler = document.querySelector(".chatbot-toggler");

let userMessage;

// Gemini API key
const API_KEY = "AIzaSyCOmWvgJJpt891TQI7tUZQiVsiKJma0H1Y";
const genAI = new GoogleGenerativeAI("AIzaSyCOmWvgJJpt891TQI7tUZQiVsiKJma0H1Y");

const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const chat = model.startChat({
  history: [],
  generationConfig: {
    maxOutputTokens: 25,
  },
});

const createChatLi = (message, className) => {
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);
  let chatContent = className == "incoming" ? <span class="material-symbols-outlined">smart_toy</span><p>${message}</p> : <p>${message}</p>;
  chatLi.innerHTML = chatContent;
  return chatLi;
};

const generateResponse = (chatLi) => {

  chat.sendMessage(userMessage).then((response) => {
    const msg = response.response.candidates[0].content.parts[0].text;
    chatLi.innerHTML = <span class="material-symbols-outlined">smart_toy</span><p>${msg}</p>;
  });
};

const handleChat = () => {
  userMessage = chatInput.value;
  if (!userMessage) return;

  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatInput.value = "";
  setTimeout(() => {
    const chatLi = createChatLi("THINKING...", "incoming");
    chatbox.appendChild(chatLi);
    generateResponse(chatLi);
  }, 1000);
};

sendMessage.addEventListener("click", handleChat);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);