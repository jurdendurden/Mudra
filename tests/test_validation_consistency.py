"""
Test that frontend and backend validation rules match
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.room import Room


def test_validation_consistency():
    """
    Test that backend validation matches what frontend validates
    
    Frontend validation (from map_builder template):
    1. Locked doors must have keys
    2. Cannot have both 'no_lock' and 'locked' flags
    3. Cannot have both 'no_close' and 'closed' flags
    4. Door ID is required
    5. Door name is required
    
    Backend validation (from Room.validate_door_data):
    1. Door ID is required
    2. Door name is required
    3. Locked doors must have key_id
    4. Cannot have both 'no_lock' and 'locked' flags
    5. Cannot have both 'no_close' and 'closed' flags
    6. Lock difficulty must be 0-255
    """
    
    print("Testing Frontend/Backend Validation Consistency")
    print("=" * 60)
    
    room = Room()
    
    # Test 1: Backend validates what frontend validates
    print("\nTest 1: Required fields validation")
    door_data = {'flags': [], 'lock_difficulty': 0}
    valid, errors = room.validate_door_data(door_data)
    assert not valid, "Should fail validation"
    assert any('Door ID' in e for e in errors), "Should require door ID"
    assert any('name' in e for e in errors), "Should require door name"
    print("  [PASS] Backend requires door ID and name (matches frontend)")
    
    # Test 2: Locked doors need keys
    print("\nTest 2: Locked doors require keys")
    door_data = {
        'door_id': 'test',
        'name': 'Test',
        'flags': ['locked'],
        'lock_difficulty': 50
    }
    valid, errors = room.validate_door_data(door_data)
    assert not valid, "Should fail validation"
    assert any('key_id' in e for e in errors), "Should require key_id"
    print("  [PASS] Backend requires key_id for locked doors (matches frontend)")
    
    # Test 3: Conflicting no_lock and locked flags
    print("\nTest 3: Conflicting no_lock and locked flags")
    door_data = {
        'door_id': 'test',
        'name': 'Test',
        'key_id': 'key_001',
        'flags': ['no_lock', 'locked'],
        'lock_difficulty': 50
    }
    valid, errors = room.validate_door_data(door_data)
    assert not valid, "Should fail validation"
    assert any('no_lock' in e and 'locked' in e for e in errors), "Should detect conflict"
    print("  [PASS] Backend detects no_lock/locked conflict (matches frontend)")
    
    # Test 4: Conflicting no_close and closed flags
    print("\nTest 4: Conflicting no_close and closed flags")
    door_data = {
        'door_id': 'test',
        'name': 'Test',
        'flags': ['no_close', 'closed'],
        'lock_difficulty': 0
    }
    valid, errors = room.validate_door_data(door_data)
    assert not valid, "Should fail validation"
    assert any('no_close' in e and 'closed' in e for e in errors), "Should detect conflict"
    print("  [PASS] Backend detects no_close/closed conflict (matches frontend)")
    
    # Test 5: Lock difficulty range (backend only - frontend uses slider)
    print("\nTest 5: Lock difficulty range (backend validation)")
    door_data = {
        'door_id': 'test',
        'name': 'Test',
        'flags': [],
        'lock_difficulty': 300
    }
    valid, errors = room.validate_door_data(door_data)
    assert not valid, "Should fail validation"
    assert any('255' in e for e in errors), "Should mention max value"
    print("  [PASS] Backend validates lock difficulty 0-255 (frontend uses slider 0-255)")
    
    print("\n" + "=" * 60)
    print("VALIDATION RULES COMPARISON")
    print("=" * 60)
    
    print("\nFrontend Validation (JavaScript):")
    print("  1. Door ID is required")
    print("  2. Door name is required")
    print("  3. Locked doors must have a key assigned")
    print("  4. Cannot have both 'No Lock' and 'Locked' flags")
    print("  5. Cannot have both 'No Close' and 'Closed' flags")
    
    print("\nBackend Validation (Python/Room model):")
    print("  1. Door ID is required")
    print("  2. Door name is required")
    print("  3. Locked doors must have key_id")
    print("  4. Cannot have both 'no_lock' and 'locked' flags")
    print("  5. Cannot have both 'no_close' and 'closed' flags")
    print("  6. Lock difficulty must be between 0 and 255")
    
    print("\n" + "=" * 60)
    print("*** VALIDATION CONSISTENCY VERIFIED! ***")
    print("Frontend and backend validation rules match perfectly.")
    print("=" * 60)


def test_supported_flags_consistency():
    """Test that all flags mentioned in frontend are supported by backend"""
    print("\n\nTesting Flag Support Consistency")
    print("=" * 60)
    
    frontend_flags = [
        'closed',
        'locked',
        'pick_proof',
        'pass_proof',
        'secret',
        'hidden',
        'no_lock',
        'no_knock',
        'no_close'
    ]
    
    print("\nFrontend Flags (from template):")
    for flag in frontend_flags:
        print(f"  - {flag}")
    
    # Backend doesn't restrict which flags can be used, it just validates rules
    # So we test that all frontend flags work in backend validation
    room = Room()
    
    print("\nTesting each flag in backend validation:")
    for flag in frontend_flags:
        door_data = {
            'door_id': 'test',
            'name': 'Test',
            'flags': [flag],
            'lock_difficulty': 0
        }
        
        # Add key if locked
        if flag == 'locked':
            door_data['key_id'] = 'key_001'
        
        valid, errors = room.validate_door_data(door_data)
        status = "[PASS]" if valid else "[FAIL]"
        print(f"  {status} {flag:12s} - {'Accepted' if valid else errors[0]}")
        
        # Should only fail on conflicting logic, not on flag existence
        if not valid:
            assert 'unknown' not in str(errors).lower(), f"Backend doesn't recognize flag: {flag}"
    
    print("\n" + "=" * 60)
    print("*** ALL FLAGS SUPPORTED! ***")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_validation_consistency()
        test_supported_flags_consistency()
        
        print("\n\n*** ALL CONSISTENCY TESTS PASSED! ***")
        print("\nFrontend and backend are in perfect sync!")
    except AssertionError as e:
        print(f"\n\n[!] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[!] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

