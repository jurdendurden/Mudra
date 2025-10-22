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
    
    # Get bag slots information
    bag_slots = character.bag_slots if character.bag_slots else {}
    bag_slots_data = {}
    total_slots = 20  # Base inventory slots
    
    # Process equipped bags in quick slots
    for slot_num in range(5):
        slot_key = str(slot_num)
        if slot_key in bag_slots and bag_slots[slot_key]:
            bag_item = Item.query.get(bag_slots[slot_key])
            if bag_item and bag_item.template:
                bag_slots_data[slot_num] = {
                    'id': bag_item.id,
                    'name': bag_item.name,
                    'slots': bag_item.template.container_capacity,
                    'icon_path': bag_item.template.icon_path if bag_item.template.icon_path else None,
                    'quality_tier': bag_item.template.quality_tier
                }
                total_slots += bag_item.template.container_capacity
            else:
                bag_slots_data[slot_num] = None
        else:
            bag_slots_data[slot_num] = None
    
    inventory = []
    for item in character.inventory:
        # Skip equipped items - they appear in equipment slots, not inventory
        if item.equipped_character_id == character.id:
            continue
            
        item_data = {
            'id': item.id,
            'name': item.get_display_name(),
            'description': item.description,
            'condition': item.condition,
            'weight': item.get_effective_weight(),
            'is_equipped': False,  # Already filtered out equipped items
            'is_equipment': item.is_equipment(),
            'is_weapon': item.is_weapon(),
            'is_armor': item.is_armor(),
            'is_consumable': item.is_consumable(),
            'is_container': item.is_container(),
            'icon_path': item.template.icon_path if item.template and item.template.icon_path else None,
            'quality_tier': item.template.quality_tier if item.template else 'common',
        }
        
        # Add container info if applicable
        if item.is_container() and item.template:
            item_data['container_slots'] = item.template.container_capacity
        
        # Add weapon stats if applicable
        if item.is_weapon():
            min_dmg, max_dmg = item.get_effective_damage()
            item_data['damage'] = f"{min_dmg}-{max_dmg}" if min_dmg else "N/A"
            item_data['attack_speed'] = item.get_attack_speed()
        
        # Add armor stats if applicable
        if item.is_armor():
            item_data['armor_class'] = item.get_armor_class()
        
        inventory.append(item_data)
    
    return jsonify({
        'inventory': inventory,
        'bag_slots': bag_slots_data,
        'total_slots': total_slots,
        'used_slots': len(inventory)
    })

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
                'icon_path': item.template.icon_path if item.template and item.template.icon_path else None,
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
    
    # Get the target slot from request body if provided
    data = request.get_json() or {}
    target_slot = data.get('slot')
    
    # If no slot provided, try to determine from item template
    if not target_slot and item.template and item.template.armor_slot:
        target_slot = item.template.armor_slot
    
    # Unequip any item currently in the same slot
    if target_slot:
        existing_item = Item.query.filter_by(
            equipped_character_id=character.id,
            equipped_slot=target_slot
        ).first()
        if existing_item:
            existing_item.equipped_character_id = None
            existing_item.equipped_slot = None
    
    # Equip the new item
    item.equipped_character_id = character.id
    item.equipped_slot = target_slot
    
    # Recalculate character stats with new equipment
    character.calculate_derived_stats()
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Equipped {item.name}',
        'item_name': item.name,
        'slot': target_slot
    })

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
    item.equipped_slot = None
    
    # Recalculate character stats without this equipment
    character.calculate_derived_stats()
    
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

@api_bp.route('/character/<int:character_id>/bag-slot/<int:slot_num>', methods=['POST'])
@login_required
def equip_bag_to_slot(character_id, slot_num):
    """Equip a bag to a quick bag slot"""
    character = Character.query.filter_by(
        id=character_id,
        player_id=current_user.id
    ).first_or_404()
    
    if slot_num < 0 or slot_num > 4:
        return jsonify({'error': 'Invalid bag slot number (0-4)'}), 400
    
    data = request.get_json()
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({'error': 'No item_id provided'}), 400
    
    # Get the item
    item = Item.query.filter_by(
        id=item_id,
        owner_character_id=character.id
    ).first_or_404()
    
    # Check if item is a container
    if not item.is_container():
        return jsonify({'error': 'Item is not a container'}), 400
    
    # Initialize bag_slots if needed
    if not character.bag_slots:
        character.bag_slots = {}
    
    # Check if there's already a bag in this slot
    slot_key = str(slot_num)
    if slot_key in character.bag_slots and character.bag_slots[slot_key]:
        old_bag_id = character.bag_slots[slot_key]
        # Don't allow if trying to equip the same bag
        if old_bag_id == item_id:
            return jsonify({'error': 'Bag is already equipped in this slot'}), 400
        
        return jsonify({'error': 'Slot already occupied. Unequip first.'}), 400
    
    # Equip the bag
    character.bag_slots[slot_key] = item_id
    
    # Mark modified for SQLAlchemy
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(character, 'bag_slots')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Equipped {item.name} to bag slot {slot_num}',
        'slot': slot_num,
        'item_id': item_id
    })

@api_bp.route('/character/<int:character_id>/bag-slot/<int:slot_num>', methods=['DELETE'])
@login_required
def unequip_bag_from_slot(character_id, slot_num):
    """Unequip a bag from a quick bag slot"""
    character = Character.query.filter_by(
        id=character_id,
        player_id=current_user.id
    ).first_or_404()
    
    if slot_num < 0 or slot_num > 4:
        return jsonify({'error': 'Invalid bag slot number (0-4)'}), 400
    
    if not character.bag_slots:
        return jsonify({'error': 'No bags equipped'}), 400
    
    slot_key = str(slot_num)
    if slot_key not in character.bag_slots or not character.bag_slots[slot_key]:
        return jsonify({'error': 'No bag in this slot'}), 400
    
    # Get the bag name before removing
    bag_id = character.bag_slots[slot_key]
    bag = Item.query.get(bag_id)
    bag_name = bag.name if bag else "Unknown"
    
    # Remove the bag from the slot
    character.bag_slots[slot_key] = None
    
    # Mark modified for SQLAlchemy
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(character, 'bag_slots')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Unequipped {bag_name} from bag slot {slot_num}',
        'slot': slot_num
    })
