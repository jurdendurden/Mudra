from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.character import Character
from app.models.item import Item, ItemTemplate
from app.models.room import Room

api_bp = Blueprint('api', __name__)

@api_bp.route('/character/<int:character_id>/inventory')
@login_required
def get_inventory(character_id):
    """Get character inventory"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    inventory = []
    for item in character.inventory:
        item_data = {
            'id': item.id,
            'name': item.get_display_name(),
            'description': item.description,
            'condition': item.condition,
            'weight': item.get_effective_weight(),
            'is_equipped': item.equipped_character_id == character.id,
            'is_equipment': item.is_equipment(),
            'is_weapon': item.is_weapon(),
            'is_armor': item.is_armor(),
            'is_consumable': item.is_consumable(),
            'is_container': item.is_container(),
        }
        
        # Add weapon stats if applicable
        if item.is_weapon():
            min_dmg, max_dmg = item.get_effective_damage()
            item_data['damage'] = f"{min_dmg}-{max_dmg}" if min_dmg else "N/A"
            item_data['attack_speed'] = item.get_attack_speed()
        
        # Add armor stats if applicable
        if item.is_armor():
            item_data['armor_class'] = item.get_armor_class()
        
        inventory.append(item_data)
    
    return jsonify({'inventory': inventory})

@api_bp.route('/character/<int:character_id>/equipment')
@login_required
def get_equipment(character_id):
    """Get character equipped items"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    # Define equipment slots
    slots = [
        'head', 'face', 'neck', 'shoulders', 'chest', 'back',
        'arms', 'wrists', 'hands', 'waist', 'legs', 'feet',
        'finger_left', 'finger_right', 'ears', 'main_hand', 
        'off_hand', 'two_handed', 'ranged'
    ]
    
    equipment = {}
    for slot in slots:
        equipment[slot] = None
    
    # Get equipped items
    for item in character.equipped_items:
        slot = item.equipped_slot
        if slot and slot in equipment:
            item_data = {
                'id': item.id,
                'name': item.get_display_name(),
                'description': item.description,
                'condition': item.condition,
                'weight': item.get_effective_weight(),
                'slot': slot,
                'is_weapon': item.is_weapon(),
                'is_armor': item.is_armor(),
            }
            
            # Add weapon stats if applicable
            if item.is_weapon():
                min_dmg, max_dmg = item.get_effective_damage()
                item_data['damage'] = f"{min_dmg}-{max_dmg}" if min_dmg else "N/A"
                item_data['attack_speed'] = item.get_attack_speed()
            
            # Add armor stats if applicable
            if item.is_armor():
                item_data['armor_class'] = item.get_armor_class()
            
            equipment[slot] = item_data
    
    return jsonify({'equipment': equipment})

@api_bp.route('/character/<int:character_id>/equip/<int:item_id>', methods=['POST'])
@login_required
def equip_item(character_id, item_id):
    """Equip an item"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    item = Item.query.filter_by(
        id=item_id, 
        owner_character_id=character.id
    ).first_or_404()
    
    if not item.is_equipment():
        return jsonify({'error': 'Item is not equipment'}), 400
    
    # Unequip any item in the same slot (simplified for now)
    # TODO: Implement proper equipment slots
    
    item.equipped_character_id = character.id
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Equipped {item.name}'})

@api_bp.route('/character/<int:character_id>/unequip/<int:item_id>', methods=['POST'])
@login_required
def unequip_item(character_id, item_id):
    """Unequip an item"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    item = Item.query.filter_by(
        id=item_id, 
        equipped_character_id=character.id
    ).first_or_404()
    
    item.equipped_character_id = None
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Unequipped {item.name}'})

@api_bp.route('/room/<int:room_id>')
@login_required
def get_room(room_id):
    """Get room information"""
    room = Room.query.get_or_404(room_id)
    
    # Get characters in room
    characters = []
    for char in room.get_characters_in_room():
        if char.id != current_user.id:  # Don't include self
            characters.append({
                'id': char.id,
                'name': char.name,
                'description': char.description
            })
    
    # Get items in room
    items = []
    for item in room.get_items_in_room():
        items.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'condition': item.condition
        })
    
    return jsonify({
        'room': {
            'id': room.id,
            'name': room.name,
            'description': room.description,
            'exits': room.get_available_exits(),
            'lighting': room.lighting,
            'is_safe': room.is_safe
        },
        'characters': characters,
        'items': items
    })

@api_bp.route('/character/<int:character_id>/move', methods=['POST'])
@login_required
def move_character(character_id, direction):
    """Move character to another room"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    if not character.current_room:
        return jsonify({'error': 'Character not in a room'}), 400
    
    target_room_id = character.current_room.get_exit_room(direction)
    if not target_room_id:
        return jsonify({'error': f'No exit to the {direction}'}), 400
    
    target_room = Room.query.filter_by(room_id=target_room_id).first()
    if not target_room:
        return jsonify({'error': 'Target room not found'}), 400
    
    # Move character
    character.current_room_id = target_room.id
    character.x_coord = target_room.x_coord
    character.y_coord = target_room.y_coord
    character.z_coord = target_room.z_coord
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_room_id': target_room.id,
        'message': f'Moved {direction} to {target_room.name}'
    })
