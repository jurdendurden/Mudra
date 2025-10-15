# Numpad Shortcuts

## Overview
Players can use the numeric keypad (numpad) for quick movement and looking around in the game.

## Numpad Layout and Commands

```
┌───┬───┬───┐
│ 7 │ 8 │ 9 │
│   │ ↑ │ ↑ │
│   │ N │ U │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
│ ← │ 👁 │ → │
│ W │ L │ E │
├───┼───┼───┤
│ 1 │ 2 │ 3 │
│   │ ↓ │ ↓ │
│   │ S │ D │
└───┴───┴───┘
```

### Key Mappings

| Numpad Key | Command | Direction | Description |
|------------|---------|-----------|-------------|
| **8** | `north` | ↑ | Move north |
| **9** | `up` | ↑ | Move up (vertical) |
| **6** | `east` | → | Move east |
| **3** | `down` | ↓ | Move down (vertical) |
| **2** | `south` | ↓ | Move south |
| **4** | `west` | ← | Move west |
| **5** | `look` | 👁 | Look at current room |

## Features

### 1. Quick Movement
- Press numpad keys for instant movement without typing
- No need to type direction commands manually
- Faster gameplay and exploration

### 2. Visual Feedback
- Command input shows the executed command
- Works the same as typing the command manually
- Command appears in output window with `>` prefix

### 3. Smart Input Detection
- Works when command input is focused
- Works when no input is focused (general page navigation)
- Doesn't interfere with other text inputs
- Automatically prevented when typing in other fields

### 4. NumLock Compatibility
- Requires NumLock to be ON
- If keys aren't working, check NumLock status
- Standard keyboard number keys (top row) won't trigger shortcuts

## Usage Examples

### Basic Movement
```
Press Numpad 8  →  Moves north
Press Numpad 6  →  Moves east
Press Numpad 2  →  Moves south
Press Numpad 4  →  Moves west
```

### Vertical Movement
```
Press Numpad 9  →  Moves up (stairs, ladders, etc.)
Press Numpad 3  →  Moves down (stairs, holes, etc.)
```

### Looking Around
```
Press Numpad 5  →  Executes 'look' command
                  Shows room description, exits, items, characters
```

## Technical Implementation

### Files Modified
- `static/js/app.js`

### Key Components

1. **Event Listener**
   - Global `keydown` listener on document
   - Calls `handleNumpadShortcuts()` method

2. **Input Detection**
   - Checks if user is in a different input field
   - Allows shortcuts in command input or when no input focused
   - Prevents interference with forms, chat, etc.

3. **Key Code Mapping**
   ```javascript
   const numpadCommands = {
       'Numpad8': 'north',
       'Numpad9': 'up',
       'Numpad6': 'east',
       'Numpad3': 'down',
       'Numpad2': 'south',
       'Numpad4': 'west',
       'Numpad5': 'look'
   };
   ```

4. **Command Execution**
   - Updates command input field with command
   - Calls `sendCommand()` to execute
   - Command is added to history
   - Server processes command normally

## Benefits

### For Players
- **Faster gameplay**: No typing required for common actions
- **One-handed play**: Can navigate with just the numpad
- **Ergonomic**: Natural hand position for right-handed players
- **Familiar**: Similar to traditional roguelike controls

### For Accessibility
- **Reduced typing**: Helpful for players with mobility issues
- **Alternative input**: Provides keyboard-only navigation
- **Quick access**: Especially useful during combat or timed events

## Keyboard Shortcuts Summary

| Category | Keys | Function |
|----------|------|----------|
| Cardinal Directions | 8, 2, 4, 6 | Move N, S, W, E |
| Vertical Movement | 9, 3 | Move up, down |
| Observation | 5 | Look at room |
| Command History | ↑, ↓ | Navigate history |
| Submit Command | Enter | Send command |

## Troubleshooting

### Shortcuts Not Working?

1. **Check NumLock**
   - Ensure NumLock is turned ON
   - Look for NumLock indicator light on keyboard

2. **Check Input Focus**
   - Shortcuts work in command input or general page
   - Won't work if typing in character creation forms
   - Click on game area or command input

3. **Browser Compatibility**
   - Works in all modern browsers
   - Chrome, Firefox, Edge, Safari all supported
   - Requires JavaScript enabled

4. **Keyboard Layout**
   - Only works with numpad keys, not top row numbers
   - Some laptop keyboards don't have a dedicated numpad
   - Use Fn + NumLock on laptops with embedded numpads

## Future Enhancements

Potential improvements:
- Diagonal movement (7, 9, 1, 3 for NW, NE, SW, SE)
- Additional shortcuts (0 for inventory, +/- for more/less)
- Customizable key bindings
- Visual indicator showing which keys are active
- Tutorial/help overlay showing key mappings

