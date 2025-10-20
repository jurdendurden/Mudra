"""
Test that keys can be loaded from keys.json
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_keys_json_exists():
    """Test that keys.json exists and is valid"""
    print("Test: keys.json exists and is valid JSON")
    
    keys_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'items', 'keys.json')
    
    assert os.path.exists(keys_file), f"keys.json not found at {keys_file}"
    print("  [PASS] keys.json exists")
    
    with open(keys_file, 'r') as f:
        data = json.load(f)
    
    print("  [PASS] keys.json is valid JSON")
    
    assert 'keys' in data, "keys.json must have a 'keys' array"
    print("  [PASS] keys.json has 'keys' array")
    
    keys = data['keys']
    assert len(keys) > 0, "keys.json must have at least one key"
    print(f"  [PASS] Found {len(keys)} keys")
    
    return keys


def test_key_structure():
    """Test that each key has required fields"""
    print("\nTest: Key structure validation")
    
    keys = test_keys_json_exists()
    
    required_fields = ['template_id', 'name', 'description', 'base_type', 'item_type', 'weight', 'value']
    
    for i, key in enumerate(keys):
        print(f"\n  Checking key {i+1}: {key.get('name', 'UNNAMED')}")
        
        for field in required_fields:
            assert field in key, f"Key {i+1} missing required field: {field}"
            print(f"    [PASS] Has {field}: {key[field]}")
        
        assert key['base_type'] == 'key', f"Key {i+1} must have base_type='key'"
        assert key['item_type'] == 20, f"Key {i+1} must have item_type=20"


def test_key_quality_distribution():
    """Test key quality distribution"""
    print("\n\nTest: Key quality distribution")
    
    keys_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'items', 'keys.json')
    with open(keys_file, 'r') as f:
        data = json.load(f)
    
    keys = data['keys']
    
    quality_counts = {}
    for key in keys:
        quality = key.get('quality_tier', 'unknown')
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    print("  Key quality distribution:")
    for quality, count in sorted(quality_counts.items()):
        print(f"    {quality:12s}: {count} key(s)")
    
    print("  [PASS] Quality distribution calculated")


def test_key_materials():
    """Test key materials"""
    print("\n\nTest: Key materials")
    
    keys_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'items', 'keys.json')
    with open(keys_file, 'r') as f:
        data = json.load(f)
    
    keys = data['keys']
    
    materials = set()
    for key in keys:
        material = key.get('material', 'unknown')
        materials.add(material)
    
    print(f"  Found {len(materials)} different materials:")
    for material in sorted(materials):
        print(f"    - {material}")
    
    print("  [PASS] Materials cataloged")


def display_all_keys():
    """Display all available keys"""
    print("\n\n" + "=" * 60)
    print("AVAILABLE KEYS FOR MAP BUILDER")
    print("=" * 60)
    
    keys_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'items', 'keys.json')
    with open(keys_file, 'r') as f:
        data = json.load(f)
    
    keys = data['keys']
    
    for key in keys:
        print(f"\nKey: {key['name']}")
        print(f"  Template ID: {key['template_id']}")
        print(f"  Description: {key['description']}")
        print(f"  Material: {key.get('material', 'unknown')}")
        print(f"  Quality: {key.get('quality_tier', 'common')}")
        print(f"  Value: {key.get('value', 0)} gold")
        flags = key.get('item_flags', [])
        if flags:
            print(f"  Flags: {', '.join(flags)}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        test_keys_json_exists()
        test_key_structure()
        test_key_quality_distribution()
        test_key_materials()
        display_all_keys()
        
        print("\n*** ALL KEY TESTS PASSED! ***")
        print("\nThe key system is ready for use in the map builder!")
    except AssertionError as e:
        print(f"\n\n[!] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[!] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

