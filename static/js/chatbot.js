/**
 * JavaScript for Chatbot functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    
    // Add initial bot message
    addBotMessage("Hello! I'm your AI health assistant. How can I help you today? I can answer questions about general health, nutrition, exercise, and wellness. Please note that I'm not a substitute for professional medical advice.");
    
    // Event listener for send button
    sendButton.addEventListener('click', sendMessage);
    
    // Event listener for Enter key press
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Function to send message
    function sendMessage() {
        const message = messageInput.value.trim();
        
        if (message === '') {
            return;
        }
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input field
        messageInput.value = '';
        
        // Show thinking indicator
        addThinkingIndicator();
        
        // Send message to server
        fetch('/ask_chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove thinking indicator
            removeThinkingIndicator();
            
            // Add bot response to chat
            addBotMessage(data.response);
        })
        .catch(error => {
            // Remove thinking indicator
            removeThinkingIndicator();
            
            // Add error message
            addBotMessage("I'm sorry, I'm having trouble connecting to my knowledge base. Please try again later.");
            console.error('Error:', error);
        });
    }
    
    // Function to add user message to chat
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', 'user-message');
        messageElement.textContent = message;
        
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom of chat
        scrollToBottom();
    }
    
    // Function to add bot message to chat
    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', 'bot-message');
        
        // Convert URLs to clickable links
        message = message.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        // Parse markdown-style formatting
        message = message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(?:\r\n|\r|\n)/g, '<br>');
        
        messageElement.innerHTML = message;
        
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom of chat
        scrollToBottom();
    }
    
    // Function to add thinking indicator
    function addThinkingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('chat-message', 'bot-message', 'thinking-indicator');
        indicator.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        
        chatContainer.appendChild(indicator);
        
        // Scroll to bottom of chat
        scrollToBottom();
    }
    
    // Function to remove thinking indicator
    function removeThinkingIndicator() {
        const indicator = document.querySelector('.thinking-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Function to scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Function to save chat history
    function saveChatHistory() {
        const messages = Array.from(chatContainer.children).map(msg => {
            return {
                type: msg.classList.contains('user-message') ? 'user' : 'bot',
                content: msg.textContent
            };
        });
        
        localStorage.setItem('chatHistory', JSON.stringify(messages));
    }
    
    // Add common health queries for quick access
    const quickQueries = [
        "How can I improve my sleep?",
        "What are good exercises for back pain?",
        "How to reduce stress?",
        "Nutrition tips for energy",
        "Signs of dehydration"
    ];
    
    const suggestionsContainer = document.getElementById('quick-suggestions');
    if (suggestionsContainer) {
        quickQueries.forEach(query => {
            const button = document.createElement('button');
            button.classList.add('btn', 'btn-sm', 'btn-outline-info', 'me-2', 'mb-2');
            button.textContent = query;
            
            button.addEventListener('click', function() {
                messageInput.value = query;
                sendMessage();
            });
            
            suggestionsContainer.appendChild(button);
        });
    }
});
