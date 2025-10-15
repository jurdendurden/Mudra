import re
from app import db
from app.models.character import Character
from app.models.room import Room
from app.models.item import Item
from app.models.chat_message import ChatMessage

class CommandProcessor:
    """Process and execute game commands"""
    
    def __init__(self):
        self.commands = {
            'look': self.cmd_look,
            'l': self.cmd_look,
            'examine': self.cmd_examine,
            'ex': self.cmd_examine,
            'inventory': self.cmd_inventory,
            'i': self.cmd_inventory,
            'get': self.cmd_get,
            'take': self.cmd_get,
            'drop': self.cmd_drop,
            'equip': self.cmd_equip,
            'unequip': self.cmd_unequip,
            'north': self.cmd_move,
            'n': self.cmd_move,
            'south': self.cmd_move,
            's': self.cmd_move,
            'east': self.cmd_move,
            'e': self.cmd_move,
            'west': self.cmd_move,
            'w': self.cmd_move,
            'up': self.cmd_move,
            'u': self.cmd_move,
            'down': self.cmd_move,
            'd': self.cmd_move,
            'go': self.cmd_go,
            'say': self.cmd_say,
            'emote': self.cmd_emote,
            'chat': self.cmd_chat,
            'censor': self.cmd_censor,
            'who': self.cmd_who,
            'help': self.cmd_help,
            'quit': self.cmd_quit,
            'save': self.cmd_save
        }
    
    def process_command(self, character, command_text):
        """Process a command and return the result"""
        # Parse command
        parts = command_text.split()
        if not parts:
            return {'error': 'Empty command'}
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Find command handler
        if command in self.commands:
            try:
                # For directional commands, pass the direction as the first argument
                if command in ['north', 'n', 'south', 's', 'east', 'e', 'west', 'w', 'up', 'u', 'down', 'd']:
                    print(f"[PROCESS_COMMAND] Processing directional command: {command}")
                    result = self.commands[command](character, command, args)
                    print(f"[PROCESS_COMMAND] Got result with keys: {result.keys() if result else 'None'}")
                    print(f"[PROCESS_COMMAND] Result action: {result.get('action', 'NOT SET') if result else 'NO RESULT'}")
                    return result
                else:
                    return self.commands[command](character, args)
            except Exception as e:
                print(f"[PROCESS_COMMAND ERROR] {str(e)}")
                import traceback
                traceback.print_exc()
                return {'error': f'Command error: {str(e)}'}
        else:
            return {'error': f'Unknown command: {command}. Type "help" for available commands.'}
    
    def _format_room_description(self, room, character, include_items_and_chars=True):
        """Format a room description with exits, items, and characters
        
        Args:
            room: The room to describe
            character: The character viewing the room
            include_items_and_chars: Whether to include items and characters in the description
        
        Returns:
            str: Formatted room description
        """
        # Build base description
        description = f"<b><u>{room.name}</u></b>\n{room.description}"
        
        # Add exits
        exits = room.get_available_exits()
        if exits:
            description += f"\n\n<b>Obvious exits: [</b> {', '.join(exits)} <b>]</b>"
        
        if include_items_and_chars:
            # Add characters in room
            other_chars = [char for char in room.get_characters_in_room() if char.id != character.id]
            if other_chars:
                char_names = [char.name for char in other_chars]
                description += f"\n\n<b>Also here:</b> {', '.join(char_names)}"
            
            # Add items in room
            room_items = room.get_items_in_room()
            if room_items:
                item_names = [item.name for item in room_items]
                description += f"\n\n<b>Items:</b> {', '.join(item_names)}"
        
        return description
    
    def cmd_look(self, character, args):
        """Look at room or object"""
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        room = character.current_room
        
        if not args:
            # Look at room - use helper method
            return {
                'message': self._format_room_description(room, character, include_items_and_chars=True),
                'room_description': True
            }
        else:
            # Look at specific object
            target = ' '.join(args)
            return self._look_at_object(character, target)
    
    def cmd_examine(self, character, args):
        """Examine an object in detail"""
        if not args:
            return {'error': 'Examine what?'}
        
        target = ' '.join(args)
        return self._examine_object(character, target)
    
    def cmd_inventory(self, character, args):
        """Show character inventory"""
        items = character.inventory.all()
        
        if not items:
            return {'message': 'You are carrying nothing.'}
        
        message = "<b>You are carrying:</b>\n"
        for item in items:
            equipped = " (equipped)" if item.equipped_character_id == character.id else ""
            message += f"  {item.name}{equipped}\n"
        
        return {'message': message}
    
    def cmd_get(self, character, args):
        """Get/take an item from the room"""
        if not args:
            return {'error': 'Get what?'}
        
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        target = ' '.join(args)
        room = character.current_room
        
        # Find item in room
        item = None
        for room_item in room.get_items_in_room():
            if target.lower() in room_item.name.lower():
                item = room_item
                break
        
        if not item:
            return {'error': f'You don\'t see "{target}" here.'}
        
        # Move item to character
        item.owner_character_id = character.id
        item.room_id = None
        
        db.session.commit()
        
        return {
            'message': f'You pick up {item.name}.',
            'affects_room': True,
            'action': 'get_item',
            'room_message': f'{character.name} picks up {item.name}.'
        }
    
    def cmd_drop(self, character, args):
        """Drop an item in the room"""
        if not args:
            return {'error': 'Drop what?'}
        
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        target = ' '.join(args)
        
        # Find item in inventory
        item = None
        for inv_item in character.inventory:
            if target.lower() in inv_item.name.lower():
                item = inv_item
                break
        
        if not item:
            return {'error': f'You don\'t have "{target}".'}
        
        # Unequip if equipped
        if item.equipped_character_id == character.id:
            item.equipped_character_id = None
        
        # Move item to room
        item.owner_character_id = None
        item.room_id = character.current_room.id
        
        db.session.commit()
        
        return {
            'message': f'You drop {item.name}.',
            'affects_room': True,
            'action': 'drop_item',
            'room_message': f'{character.name} drops {item.name}.'
        }
    
    def cmd_equip(self, character, args):
        """Equip an item"""
        if not args:
            return {'error': 'Equip what?'}
        
        target = ' '.join(args)
        
        # Find item in inventory
        item = None
        for inv_item in character.inventory:
            if target.lower() in inv_item.name.lower():
                item = inv_item
                break
        
        if not item:
            return {'error': f'You don\'t have "{target}".'}
        
        if not item.is_equipment():
            return {'error': f'{item.name} is not equipment.'}
        
        # Equip item
        item.equipped_character_id = character.id
        
        db.session.commit()
        
        return {'message': f'You equip {item.name}.'}
    
    def cmd_unequip(self, character, args):
        """Unequip an item"""
        if not args:
            return {'error': 'Unequip what?'}
        
        target = ' '.join(args)
        
        # Find equipped item
        item = None
        for inv_item in character.inventory:
            if (target.lower() in inv_item.name.lower() and 
                inv_item.equipped_character_id == character.id):
                item = inv_item
                break
        
        if not item:
            return {'error': f'You don\'t have "{target}" equipped.'}
        
        # Unequip item
        item.equipped_character_id = None
        
        db.session.commit()
        
        return {'message': f'You unequip {item.name}.'}
    
    def cmd_move(self, character, direction_cmd, extra_args):
        """Move in a direction (called by directional commands)"""
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        # Map short commands to full directions
        direction_map = {
            'north': 'north', 'n': 'north',
            'south': 'south', 's': 'south',
            'east': 'east', 'e': 'east',
            'west': 'west', 'w': 'west',
            'up': 'up', 'u': 'up',
            'down': 'down', 'd': 'down'
        }
        
        direction = direction_map.get(direction_cmd.lower())
        if not direction:
            return {'error': 'Invalid direction'}
        
        room = character.current_room
        
        target_room_id = room.get_exit_room(direction)
        if not target_room_id:
            return {'error': f'You can\'t go {direction} from here.'}
        
        target_room = Room.query.filter_by(room_id=target_room_id).first()
        if not target_room:
            return {'error': 'Target room not found.'}
        
        # Move character
        old_coords = (character.x_coord, character.y_coord, character.z_coord)
        character.current_room_id = target_room.id
        character.x_coord = target_room.x_coord
        character.y_coord = target_room.y_coord
        character.z_coord = target_room.z_coord
        
        print(f"[MOVE DEBUG] {character.name} moving from {old_coords} to ({target_room.x_coord}, {target_room.y_coord}, {target_room.z_coord})")
        print(f"[MOVE DEBUG] Character coords before commit: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
        
        db.session.commit()
        
        print(f"[MOVE DEBUG] Character coords after commit: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
        
        # Verify the update persisted
        db.session.refresh(character)
        print(f"[MOVE DEBUG] Character coords after refresh: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
        
        # Get formatted room description (same as look command)
        room_description = self._format_room_description(target_room, character, include_items_and_chars=True)
        
        result = {
            'message': room_description,
            'affects_room': True,
            'action': 'move',
            'room_message': f'{character.name} goes {direction}.'
        }
        
        print(f"[CMD_MOVE] Returning result with action: {result.get('action')}")
        print(f"[CMD_MOVE] Full result: {result}")
        
        return result
    
    def cmd_go(self, character, args):
        """Go in a direction"""
        if not args:
            return {'error': 'Go where?'}
        
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        direction = args[0].lower()
        room = character.current_room
        
        target_room_id = room.get_exit_room(direction)
        if not target_room_id:
            return {'error': f'You can\'t go {direction} from here.'}
        
        target_room = Room.query.filter_by(room_id=target_room_id).first()
        if not target_room:
            return {'error': 'Target room not found.'}
        
        # Move character
        character.current_room_id = target_room.id
        character.x_coord = target_room.x_coord
        character.y_coord = target_room.y_coord
        character.z_coord = target_room.z_coord
        
        db.session.commit()
        
        # Get formatted room description (same as look command)
        room_description = self._format_room_description(target_room, character, include_items_and_chars=True)
        
        return {
            'message': room_description,
            'affects_room': True,
            'action': 'move',
            'room_message': f'{character.name} goes {direction}.'
        }
    
    def cmd_say(self, character, args):
        """Say something"""
        if not args:
            return {'error': 'Say what?'}
        
        message = ' '.join(args)
        
        return {
            'message': f'You say, "{message}"',
            'affects_room': True,
            'action': 'say',
            'room_message': f'{character.name} says, "{message}"'
        }
    
    def cmd_emote(self, character, args):
        """Perform an emote"""
        if not args:
            return {'error': 'Emote what?'}
        
        emote = ' '.join(args)
        
        return {
            'message': f'{character.name} {emote}',
            'affects_room': True,
            'action': 'emote',
            'room_message': f'{character.name} {emote}'
        }
    
    def cmd_chat(self, character, args):
        """Send a chat message to all players"""
        if not args:
            return {'error': 'Chat what?'}
        
        message = ' '.join(args)
        
        # Create chat message record
        chat_message = ChatMessage(
            character_id=character.id,
            character_name=character.name,
            message=message
        )
        
        # Save to chat database
        chat_message.save()
        
        # Format message with timestamp
        timestamp = chat_message.timestamp.strftime('%H:%M:%S')
        formatted_message = f'[chat] {timestamp} {character.name}: {message}'
        
        return {
            'affects_room': True,
            'action': 'chat',
            'room_message': formatted_message,
            'chat_message': chat_message.to_dict()
        }
    
    def cmd_censor(self, character, args):
        """Toggle chat censorship on/off"""
        # Get the player associated with this character
        player = character.player

        # Toggle the censor setting
        player.censor_enabled = not player.censor_enabled

        db.session.commit()

        status = "on" if player.censor_enabled else "off"
        return {'message': f'Chat censoring turned {status}.'}
    
    def cmd_who(self, character, args):
        """Show who is online"""
        # TODO: Implement online player list
        return {'message': 'Online players: (feature not implemented yet)'}
    
    def cmd_help(self, character, args):
        """Show help"""
        help_text = """
<b>Available Commands:</b>
<u>Movement:</u>
  north/n, south/s, east/e, west/w, up/u, down/d
  (You can also use: go <direction>)
  <b>Tip:</b> Use numpad keys for quick movement!
  (8=N, 2=S, 4=W, 6=E, 9=Up, 3=Down, 5=Look)
<u>Interaction:</u>
  look/l, examine/ex <object>, get/take <item>, drop <item>
<u>Equipment:</u>
  equip <item>, unequip <item>, inventory/i
<u>Social:</u>
  say <message>, emote <action>, chat <message>, censor, who
<u>System:</u>
  help, save, quit
        """
        return {'message': help_text}
    
    def cmd_quit(self, character, args):
        """Quit the game"""
        return {'message': 'Goodbye!', 'quit': True}
    
    def cmd_save(self, character, args):
        """Save character"""
        db.session.commit()
        return {'message': 'Character saved.'}
    
    def _look_at_object(self, character, target):
        """Look at a specific object"""
        # Check inventory first
        for item in character.inventory:
            if target.lower() in item.name.lower():
                return {'message': f'<b>{item.name}</b>\n{item.description or "No description available."}'}
        
        # Check room items
        if character.current_room:
            for item in character.current_room.get_items_in_room():
                if target.lower() in item.name.lower():
                    return {'message': f'<b>{item.name}</b>\n{item.description or "No description available."}'}
        
        # Check other characters
        if character.current_room:
            for char in character.current_room.get_characters_in_room():
                if char.id != character.id and target.lower() in char.name.lower():
                    return {'message': f'<b>{char.name}</b>\n{char.description or "No description available."}'}
        
        return {'error': f'You don\'t see "{target}" here.'}
    
    def _examine_object(self, character, target):
        """Examine an object in detail"""
        # For now, same as look
        return self._look_at_object(character, target)
