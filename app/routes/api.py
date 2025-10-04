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
        inventory.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'condition': item.condition,
            'weight': item.template.weight if item.template else 0,
            'is_equipped': item.equipped_character_id == character.id
        })
    
    return jsonify({'inventory': inventory})

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
