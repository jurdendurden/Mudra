// Main game client JavaScript
class GameClient {
    constructor() {
        this.socket = null;
        this.characterId = null;
        this.characterName = null;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.isConnected = false;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.outputWindow = document.getElementById('output-window');
        this.commandInput = document.getElementById('command-input');
        this.chatOutput = document.getElementById('chat-output');
        this.inventoryList = document.getElementById('inventory-list');
        this.minimap = document.getElementById('minimap');
    }
    
    setupEventListeners() {
        // Command input
        if (this.commandInput) {
            this.commandInput.addEventListener('keydown', (e) => this.handleCommandInput(e));
        }
        
        // Inventory items
        if (this.inventoryList) {
            this.inventoryList.addEventListener('click', (e) => this.handleInventoryClick(e));
        }
    }
    
    connect() {
        if (this.isConnected) return;
        
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.addOutput('Connected to game server', 'system');
            
            // Join game with character
            if (this.characterId) {
                this.socket.emit('join_game', { character_id: this.characterId });
            }
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.addOutput('Disconnected from game server', 'error');
        });
        
        this.socket.on('connected', (data) => {
            this.addOutput(data.message, 'system');
        });
        
        this.socket.on('error', (data) => {
            this.addOutput(`Error: ${data.message}`, 'error');
        });
        
        this.socket.on('game_joined', (data) => {
            this.characterId = data.character_id;
            this.characterName = data.character_name;
            this.addOutput(`Joined game as ${data.character_name}`, 'system');
            
            // Request initial room info
            this.socket.emit('request_room_info');
            
            // Load recent chat messages
            this.loadRecentChatMessages();
        });
        
        this.socket.on('command_result', (data) => {
            this.handleCommandResult(data);
        });
        
        this.socket.on('room_info', (data) => {
            this.updateRoomInfo(data);
        });
        
        this.socket.on('room_update', (data) => {
            this.addOutput(`${data.character_name} ${data.message}`, 'room');
        });
        
        this.socket.on('chat_message', (data) => {
            this.addChatMessage(data);
        });
    }
    
    handleCommandInput(e) {
        if (e.key === 'Enter') {
            const command = this.commandInput.value.trim();
            if (command) {
                this.sendCommand(command);
                this.commandInput.value = '';
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateHistory(-1);
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.navigateHistory(1);
        }
    }
    
    
    handleInventoryClick(e) {
        const item = e.target.closest('.inventory-item');
        if (item) {
            const itemId = item.dataset.itemId;
            const itemName = item.textContent.trim();
            
            // Simple context menu for now
            const action = prompt(`What do you want to do with ${itemName}?\n1. Examine\n2. Equip\n3. Unequip\n4. Drop\n\nEnter number:`);
            
            switch (action) {
                case '1':
                    this.sendCommand(`examine ${itemName}`);
                    break;
                case '2':
                    this.sendCommand(`equip ${itemName}`);
                    break;
                case '3':
                    this.sendCommand(`unequip ${itemName}`);
                    break;
                case '4':
                    this.sendCommand(`drop ${itemName}`);
                    break;
            }
        }
    }
    
    sendCommand(command) {
        if (!this.isConnected) {
            this.addOutput('Not connected to game server', 'error');
            return;
        }
        
        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;
        
        // Send to server
        this.socket.emit('game_command', { command: command });
        
        // Show command in output
        this.addOutput(`> ${command}`, 'command');
    }
    
    sendChatMessage(message) {
        if (!this.isConnected) {
            this.addOutput('Not connected to game server', 'error');
            return;
        }
        
        // Send as chat command
        this.sendCommand(`chat ${message}`);
    }
    
    handleCommandResult(data) {
        if (data.result && data.result.error) {
            this.addOutput(data.result.error, 'error');
        } else if (data.result && data.result.message) {
            this.addOutput(data.result.message, 'game');
        }
        
        // Handle special results
        if (data.result && data.result.new_room) {
            this.updateRoomInfo({ room: data.result.new_room });
        }
        
        
        if (data.result && data.result.quit) {
            // Handle quit command
            setTimeout(() => {
                window.location.href = '/auth/logout';
            }, 2000);
        }
    }
    
    updateRoomInfo(data) {
        if (data.room) {
            // Update room name in header
            const roomElement = document.getElementById('current-room');
            if (roomElement) {
                roomElement.textContent = data.room.name;
            }
            
            // Update room description
            this.addOutput(`<b>${data.room.name}</b>`, 'room');
            this.addOutput(data.room.description, 'room');
            
            if (data.room.exits && data.room.exits.length > 0) {
                this.addOutput(`<b>Exits:</b> ${data.room.exits.join(', ')}`, 'room');
            }
        }
        
        if (data.characters && data.characters.length > 0) {
            const charNames = data.characters.map(char => char.name).join(', ');
            this.addOutput(`<b>Also here:</b> ${charNames}`, 'room');
        }
        
        if (data.items && data.items.length > 0) {
            const itemNames = data.items.map(item => item.name).join(', ');
            this.addOutput(`<b>Items:</b> ${itemNames}`, 'room');
        }
    }
    
    addChatMessage(data) {
        if (!this.chatOutput) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        
        // Use timestamp from server if available, otherwise use current time
        const timestamp = data.formatted_timestamp || new Date().toLocaleTimeString();
        
        // Filter message if player has censorship enabled
        let message = data.message;
        if (data.player_censor_enabled) {
            message = this.filterMessage(message);
        }
        
        messageDiv.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="character">${data.character_name}:</span>
            <span class="message">${message}</span>
        `;
        
        this.chatOutput.appendChild(messageDiv);
        this.chatOutput.scrollTop = this.chatOutput.scrollHeight;
    }
    
    filterMessage(message) {
        // Filter profanity from chat messages
        if (!message) return message;
        
        // Common English curse words and slurs
        const filteredWords = [
            'damn', 'hell', 'crap', 'shit', 'fuck', 'bitch', 'ass', 'asshole',
            'bastard', 'piss', 'pissed', 'cunt', 'cock', 'dick', 'pussy',
            'whore', 'slut', 'fag', 'faggot', 'nigger', 'nigga', 'kike',
            'chink', 'spic', 'wetback', 'retard', 'retarded', 'gay',
            'f*ck', 'f**k', 'f***', 'sh*t', 's**t', 'a$$', 'b*tch', 'b**ch',
            'd*mn', 'h*ll', 'cr*p', 'p*ss', 'c*nt', 'c*ck', 'd*ck', 'p*ssy',
            'wh*re', 'sl*t', 'f*g', 'f*ggot', 'n*gger', 'n*gga', 'k*ke',
            'ch*nk', 'sp*c', 'ret*rd', 'g*y', 'wtf', 'omg', 'stfu', 'gtfo'
        ];
        
        let filteredMessage = message;
        
        filteredWords.forEach(word => {
            const regex = new RegExp('\\b' + word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'gi');
            const asterisks = '*'.repeat(word.length);
            filteredMessage = filteredMessage.replace(regex, asterisks);
        });
        
        return filteredMessage;
    }
    
    addOutput(text, type = 'game') {
        if (!this.outputWindow) return;
        
        const outputDiv = document.createElement('div');
        outputDiv.className = `output-${type}`;
        
        // Parse HTML and apply formatting
        outputDiv.innerHTML = this.formatText(text);
        
        this.outputWindow.appendChild(outputDiv);
        this.outputWindow.scrollTop = this.outputWindow.scrollHeight;
    }
    
    formatText(text) {
        // Basic HTML formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
    
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;
        
        this.historyIndex += direction;
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.commandHistory.length) {
            this.historyIndex = this.commandHistory.length;
            this.commandInput.value = '';
            return;
        }
        
        this.commandInput.value = this.commandHistory[this.historyIndex];
    }
    
    updateCharacterStats(stats) {
        // Update character stats in header
        Object.keys(stats).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = stats[key];
            }
        });
    }
    
    updateInventory(inventory) {
        if (!this.inventoryList) return;
        
        this.inventoryList.innerHTML = '';
        
        inventory.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = `inventory-item ${item.is_equipped ? 'equipped' : ''}`;
            itemDiv.dataset.itemId = item.id;
            itemDiv.innerHTML = `
                ${item.name}
                ${item.is_equipped ? '<small class="text-success">(equipped)</small>' : ''}
            `;
            this.inventoryList.appendChild(itemDiv);
        });
    }
    
    async loadRecentChatMessages() {
        try {
            const response = await fetch('/game/api/chat/recent?limit=20');
            const data = await response.json();
            
            if (data.success && data.messages) {
                // Clear existing chat messages
                if (this.chatOutput) {
                    this.chatOutput.innerHTML = '';
                }
                
                // Add recent messages
                data.messages.forEach(msg => {
                    this.addChatMessage(msg);
                });
            }
        } catch (error) {
            console.error('Failed to load recent chat messages:', error);
        }
    }
}

// Initialize game client when DOM is loaded
function initializeGameClient() {
    window.gameClient = new GameClient();
    window.gameClient.connect();
}

// Export for use in templates
window.GameClient = GameClient;
