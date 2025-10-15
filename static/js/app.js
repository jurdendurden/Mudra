// Main game client JavaScript
class GameClient {
    constructor() {
        this.socket = null;
        this.characterId = null;
        this.characterName = null;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.isConnected = false;
        this.minimapUpdateInterval = null;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.outputWindow = document.getElementById('output-window');
        this.commandInput = document.getElementById('command-input');
        this.chatOutput = document.getElementById('chat-output');
        this.inventoryList = document.getElementById('inventory-list');
        this.minimap = document.getElementById('minimap');
        this.minimapCtx = this.minimap ? this.minimap.getContext('2d') : null;
        this.playerPosition = { x: 0, y: 0, z: 0 };
        this.nearbyRooms = [];
        
        // Debug minimap initialization
        if (this.minimap) {
            console.log('Minimap canvas found:', this.minimap);
            console.log('Canvas dimensions:', this.minimap.width, 'x', this.minimap.height);
            console.log('Canvas context:', this.minimapCtx);
        } else {
            console.error('Minimap canvas not found!');
        }
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
        
        // Numpad shortcuts for movement and look
        document.addEventListener('keydown', (e) => this.handleNumpadShortcuts(e));
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
            
            // Clear minimap update interval on disconnect
            if (this.minimapUpdateInterval) {
                clearInterval(this.minimapUpdateInterval);
                this.minimapUpdateInterval = null;
            }
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
            
            // Load and render minimap
            this.loadMinimap();
            
            // Set up periodic minimap updates every 5 seconds
            if (this.minimapUpdateInterval) {
                clearInterval(this.minimapUpdateInterval);
            }
            this.minimapUpdateInterval = setInterval(() => {
                console.log('Periodic minimap update triggered');
                this.loadMinimap();
            }, 5000);
            console.log('Minimap auto-update started (every 5 seconds)');
        });
        
        this.socket.on('command_result', (data) => {
            console.log('Command result received:', data);
            console.log('Result action:', data.result ? data.result.action : 'no result');
            
            this.handleCommandResult(data);
            
            // Reload minimap and coordinates after movement commands
            if (data.result && data.result.action === 'move') {
                console.log('✅ Movement detected! Updating minimap and coordinates...');
                // Immediate update, then reload minimap from server
                this.loadMinimap();
            } else {
                console.log('❌ Not a movement command (action:', data.result ? data.result.action : 'none', ')');
            }
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
                // Highlight the command text instead of clearing it
                this.commandInput.select();
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
    
    handleNumpadShortcuts(e) {
        // Don't trigger if user is typing in a text input (except our command input)
        const activeElement = document.activeElement;
        if (activeElement && 
            activeElement.tagName !== 'BODY' && 
            activeElement.id !== 'command-input' &&
            (activeElement.tagName === 'INPUT' || 
             activeElement.tagName === 'TEXTAREA' || 
             activeElement.contentEditable === 'true')) {
            return;
        }
        
        // Map numpad keys to commands
        const numpadCommands = {
            'Numpad8': 'north',    // 8 = North
            'Numpad9': 'up',       // 9 = Up
            'Numpad6': 'east',     // 6 = East
            'Numpad3': 'down',     // 3 = Down
            'Numpad2': 'south',    // 2 = South
            'Numpad4': 'west',     // 4 = West
            'Numpad5': 'look'      // 5 = Look
        };
        
        // Check if a numpad key was pressed
        if (numpadCommands[e.code]) {
            e.preventDefault();
            const command = numpadCommands[e.code];
            
            // Update command input to show what command is being executed
            if (this.commandInput) {
                this.commandInput.value = command;
            }
            
            // Send the command
            this.sendCommand(command);
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
        
        // For movement commands, update the room name in header
        if (data.result && data.result.action === 'move') {
            // Extract room name from the message (it's the first bold text)
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = data.result.message;
            const boldElement = tempDiv.querySelector('b');
            if (boldElement) {
                const roomElement = document.getElementById('current-room');
                if (roomElement) {
                    roomElement.textContent = boldElement.textContent;
                }
            }
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
                this.addOutput(`<b>Exits: </b> ${data.room.exits.join(', ')}`, 'room');
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
        // Select the text for easy editing/replacing
        this.commandInput.select();
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
    
    async loadMinimap() {
        if (!this.characterId) {
            console.log('Minimap: No character ID');
            return;
        }
        if (!this.minimapCtx) {
            console.log('Minimap: No canvas context');
            return;
        }
        
        try {
            // Add cache-busting parameter to ensure fresh data
            const apiUrl = `/game/api/minimap/${this.characterId}?t=${Date.now()}`;
            console.log(`Loading minimap from: ${apiUrl}`);
            const response = await fetch(apiUrl, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
            const data = await response.json();
            
            console.log('Minimap API response:', data);
            
            if (data.success) {
                console.log(`Minimap loaded: ${data.rooms.length} rooms, player at (${data.player_position.x}, ${data.player_position.y}, ${data.player_position.z})`);
                
                // Check if position actually changed
                if (this.playerPosition.x !== data.player_position.x || 
                    this.playerPosition.y !== data.player_position.y || 
                    this.playerPosition.z !== data.player_position.z) {
                    console.log(`Player position changed from (${this.playerPosition.x}, ${this.playerPosition.y}, ${this.playerPosition.z}) to (${data.player_position.x}, ${data.player_position.y}, ${data.player_position.z})`);
                }
                
                this.nearbyRooms = data.rooms;
                this.playerPosition = data.player_position;
                this.renderMinimap();
                this.updateCoordinatesDisplay();
            } else {
                console.error('Minimap API returned error:', data);
            }
        } catch (error) {
            console.error('Failed to load minimap:', error);
        }
    }
    
    renderMinimap() {
        if (!this.minimapCtx || !this.minimap) {
            console.log('Minimap render skipped: no context or canvas');
            return;
        }
        
        console.log(`Rendering minimap: ${this.nearbyRooms.length} rooms at player position (${this.playerPosition.x}, ${this.playerPosition.y}, ${this.playerPosition.z})`);
        
        const ctx = this.minimapCtx;
        const canvas = this.minimap;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Fill background
        ctx.fillStyle = '#1a252f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Calculate scale and offset
        const cellSize = 18; // Scaled down from 40px to 18px
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        console.log(`Minimap center: (${centerX}, ${centerY}), cellSize: ${cellSize}`);
        
        // Draw connection lines first (so they appear behind rooms)
        this.nearbyRooms.forEach(room => {
            if (room.exits) {
                Object.entries(room.exits).forEach(([direction, targetRoomId]) => {
                    // Skip up/down exits - they'll be shown with arrows
                    if (direction === 'up' || direction === 'down') return;
                    
                    const targetRoom = this.nearbyRooms.find(r => r.room_id === targetRoomId);
                    if (targetRoom) {
                        this.drawMinimapConnection(ctx, room, targetRoom, centerX, centerY, cellSize);
                    }
                });
            }
        });
        
        // Draw room nodes
        let playerRoomFound = false;
        this.nearbyRooms.forEach(room => {
            const isPlayerRoom = (room.x === this.playerPosition.x && 
                                  room.y === this.playerPosition.y && 
                                  room.z === this.playerPosition.z);
            if (isPlayerRoom) {
                playerRoomFound = true;
                console.log(`🟢 Drawing player room at (${room.x}, ${room.y}, ${room.z}): ${room.name}`);
            }
            this.drawMinimapRoom(ctx, room, centerX, centerY, cellSize, isPlayerRoom);
        });
        
        if (!playerRoomFound) {
            console.warn(`⚠️ Player position (${this.playerPosition.x}, ${this.playerPosition.y}, ${this.playerPosition.z}) not found in nearby rooms!`);
        }
        
        console.log('✅ Minimap rendering complete');
    }
    
    drawMinimapConnection(ctx, room1, room2, centerX, centerY, cellSize) {
        // Calculate positions relative to player
        const x1 = centerX + (room1.x - this.playerPosition.x) * cellSize;
        const y1 = centerY - (room1.y - this.playerPosition.y) * cellSize;
        const x2 = centerX + (room2.x - this.playerPosition.x) * cellSize;
        const y2 = centerY - (room2.y - this.playerPosition.y) * cellSize;
        
        // Calculate angle and distance
        const angle = Math.atan2(y2 - y1, x2 - x1);
        const fullLength = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        
        // Offset from center of rooms (7px for smaller rooms)
        const lineOffset = 7;
        const length = Math.max(fullLength - (lineOffset * 2), 1);
        
        // Calculate start point
        const startX = x1 + Math.cos(angle) * lineOffset;
        const startY = y1 + Math.sin(angle) * lineOffset;
        
        // Draw line
        ctx.save();
        ctx.strokeStyle = '#95a5a6';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(startX + Math.cos(angle) * length, startY + Math.sin(angle) * length);
        ctx.stroke();
        ctx.restore();
    }
    
    drawMinimapRoom(ctx, room, centerX, centerY, cellSize, isPlayerRoom) {
        // Calculate position relative to player
        const x = centerX + (room.x - this.playerPosition.x) * cellSize - (cellSize / 2);
        const y = centerY - (room.y - this.playerPosition.y) * cellSize - (cellSize / 2);
        
        // Draw room rectangle
        ctx.fillStyle = '#3498db';
        ctx.strokeStyle = '#2980b9';
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, cellSize, cellSize);
        ctx.strokeRect(x, y, cellSize, cellSize);
        
        // Draw up arrow if room has up exit
        if (room.exits && room.exits.up) {
            ctx.fillStyle = '#22e6e6';
            ctx.beginPath();
            ctx.moveTo(x + cellSize - 2, y + 2);
            ctx.lineTo(x + cellSize - 4, y + 5);
            ctx.lineTo(x + cellSize - 6, y + 2);
            ctx.closePath();
            ctx.fill();
        }
        
        // Draw down arrow if room has down exit
        if (room.exits && room.exits.down) {
            ctx.fillStyle = '#22e6e6';
            ctx.beginPath();
            ctx.moveTo(x + 2, y + 5);
            ctx.lineTo(x + 4, y + 2);
            ctx.lineTo(x + 6, y + 5);
            ctx.closePath();
            ctx.fill();
        }
        
        // Draw player indicator (green dot)
        if (isPlayerRoom) {
            const dotRadius = 3;
            ctx.fillStyle = '#00ff00';
            ctx.beginPath();
            ctx.arc(x + cellSize / 2, y + cellSize / 2, dotRadius, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    updateCoordinatesDisplay() {
        // Update character coordinates display in left panel
        const xCoordElement = document.getElementById('char-x-coord');
        const yCoordElement = document.getElementById('char-y-coord');
        const zCoordElement = document.getElementById('char-z-coord');
        
        console.log('Updating coordinate display elements:', {
            xElement: xCoordElement ? 'found' : 'NOT FOUND',
            yElement: yCoordElement ? 'found' : 'NOT FOUND',
            zElement: zCoordElement ? 'found' : 'NOT FOUND',
            newPosition: `(${this.playerPosition.x}, ${this.playerPosition.y}, ${this.playerPosition.z})`
        });
        
        if (xCoordElement) {
            const oldValue = xCoordElement.textContent;
            xCoordElement.textContent = this.playerPosition.x;
            console.log(`  X coord updated: ${oldValue} -> ${this.playerPosition.x}`);
        } else {
            console.error('  ❌ X coord element not found!');
        }
        if (yCoordElement) {
            const oldValue = yCoordElement.textContent;
            yCoordElement.textContent = this.playerPosition.y;
            console.log(`  Y coord updated: ${oldValue} -> ${this.playerPosition.y}`);
        } else {
            console.error('  ❌ Y coord element not found!');
        }
        if (zCoordElement) {
            const oldValue = zCoordElement.textContent;
            zCoordElement.textContent = this.playerPosition.z;
            console.log(`  Z coord updated: ${oldValue} -> ${this.playerPosition.z}`);
        } else {
            console.error('  ❌ Z coord element not found!');
        }
        
        // Also update coordinates in character modal if it exists
        const modalXElement = document.getElementById('modal-char-x-coord');
        const modalYElement = document.getElementById('modal-char-y-coord');
        const modalZElement = document.getElementById('modal-char-z-coord');
        
        if (modalXElement) modalXElement.textContent = this.playerPosition.x;
        if (modalYElement) modalYElement.textContent = this.playerPosition.y;
        if (modalZElement) modalZElement.textContent = this.playerPosition.z;
        
        console.log(`✅ Coordinate display update complete`);
    }
}

// Initialize game client when DOM is loaded
function initializeGameClient(charId, charName) {
    window.gameClient = new GameClient();
    // Set character ID and name from template
    if (charId) {
        window.gameClient.characterId = charId;
        window.gameClient.characterName = charName;
        console.log('GameClient initialized with character:', charId, charName);
    }
    window.gameClient.connect();
}

// Export for use in templates
window.GameClient = GameClient;
