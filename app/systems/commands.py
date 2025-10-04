import re
from app import db
from app.models.character import Character
from app.models.room import Room
from app.models.item import Item

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
                return self.commands[command](character, args)
            except Exception as e:
                return {'error': f'Command error: {str(e)}'}
        else:
            return {'error': f'Unknown command: {command}. Type "help" for available commands.'}
    
    def cmd_look(self, character, args):
        """Look at room or object"""
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        room = character.current_room
        
        if not args:
            # Look at room
            result = {
                'message': f"<b>{room.name}</b>\n{room.description}",
                'room_description': True
            }
            
            # Add exits
            exits = room.get_available_exits()
            if exits:
                result['message'] += f"\n\n<b>Exits:</b> {', '.join(exits)}"
            
            # Add characters in room
            other_chars = [char for char in room.get_characters_in_room() if char.id != character.id]
            if other_chars:
                char_names = [char.name for char in other_chars]
                result['message'] += f"\n\n<b>Also here:</b> {', '.join(char_names)}"
            
            # Add items in room
            room_items = room.get_items_in_room()
            if room_items:
                item_names = [item.name for item in room_items]
                result['message'] += f"\n\n<b>Items:</b> {', '.join(item_names)}"
            
            return result
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
    
    def cmd_move(self, character, args):
        """Move in a direction"""
        if not character.current_room:
            return {'error': 'You are not in a room'}
        
        # Get direction from command name
        direction_map = {
            'north': 'north', 'n': 'north',
            'south': 'south', 's': 'south',
            'east': 'east', 'e': 'east',
            'west': 'west', 'w': 'west',
            'up': 'up', 'u': 'up',
            'down': 'down', 'd': 'down'
        }
        
        # This is a simplified version - we'll get the actual command from the caller
        return {'error': 'Use the go command with a direction'}
    
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
        
        return {
            'message': f'You go {direction} to {target_room.name}.',
            'affects_room': True,
            'action': 'move',
            'room_message': f'{character.name} goes {direction}.',
            'new_room': {
                'id': target_room.id,
                'name': target_room.name,
                'description': target_room.description
            }
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
    
    def cmd_who(self, character, args):
        """Show who is online"""
        # TODO: Implement online player list
        return {'message': 'Online players: (feature not implemented yet)'}
    
    def cmd_help(self, character, args):
        """Show help"""
        help_text = """
<b>Available Commands:</b>
<u>Movement:</u>
  north/n, south/s, east/e, west/w, up/u, down/d, go <direction>
<u>Interaction:</u>
  look/l, examine/ex <object>, get/take <item>, drop <item>
<u>Equipment:</u>
  equip <item>, unequip <item>, inventory/i
<u>Social:</u>
  say <message>, emote <action>, who
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
