from src.python.transactionify.tools.validators.uuid import (
    is_valid_uuidv7,
    UUID_V7_PATTERN,
)


class TestIsValidUuidv7:
    """Test cases for is_valid_uuidv7 function."""

    def test_valid_uuidv7(self):
        """Test validation of valid UUIDv7 strings."""
        valid_uuids = [
            '019a4757-c049-7ea8-a110-2ea110c5a6f6',
            '019a4757-c049-7ea8-9110-2ea110c5a6f6',  # variant 9
            '019a4757-c049-7ea8-b110-2ea110c5a6f6',  # variant b
            '019A4757-C049-7EA8-A110-2EA110C5A6F6',  # uppercase
            '019a4757-c049-7ea8-8110-2ea110c5a6f6',  # variant 8
        ]
        
        for uuid in valid_uuids:
            assert is_valid_uuidv7(uuid) is True, f"Failed for {uuid}"

    def test_invalid_uuidv4(self):
        """Test that UUIDv4 is rejected (version 4, not 7)."""
        uuid_v4 = '550e8400-e29b-41d4-a716-446655440000'
        
        assert is_valid_uuidv7(uuid_v4) is False

    def test_invalid_uuidv1(self):
        """Test that UUIDv1 is rejected (version 1, not 7)."""
        uuid_v1 = '6ba7b810-9dad-11d1-80b4-00c04fd430c8'
        
        assert is_valid_uuidv7(uuid_v1) is False

    def test_invalid_format_no_hyphens(self):
        """Test rejection of UUID without hyphens."""
        uuid_no_hyphens = '019a4757c0497ea8a1102ea110c5a6f6'
        
        assert is_valid_uuidv7(uuid_no_hyphens) is False

    def test_invalid_format_wrong_length(self):
        """Test rejection of UUID with wrong length."""
        invalid_uuids = [
            '019a4757-c049-7ea8-a110-2ea110c5a6',  # too short
            '019a4757-c049-7ea8-a110-2ea110c5a6f6f',  # too long
            '019a4757-c049-7ea8-a110',  # way too short
        ]
        
        for uuid in invalid_uuids:
            assert is_valid_uuidv7(uuid) is False, f"Should reject {uuid}"

    def test_invalid_variant(self):
        """Test rejection of UUIDv7 with invalid variant field."""
        # Variant field (17th character) must be 8, 9, a, or b
        invalid_variants = [
            '019a4757-c049-7ea8-0110-2ea110c5a6f6',  # variant 0 (invalid)
            '019a4757-c049-7ea8-1110-2ea110c5a6f6',  # variant 1 (invalid)
            '019a4757-c049-7ea8-c110-2ea110c5a6f6',  # variant c (invalid)
            '019a4757-c049-7ea8-f110-2ea110c5a6f6',  # variant f (invalid)
        ]
        
        for uuid in invalid_variants:
            assert is_valid_uuidv7(uuid) is False, f"Should reject variant in {uuid}"

    def test_empty_string(self):
        """Test rejection of empty string."""
        assert is_valid_uuidv7('') is False

    def test_none_value(self):
        """Test rejection of None value."""
        assert is_valid_uuidv7(None) is False

    def test_invalid_characters(self):
        """Test rejection of UUID with invalid characters."""
        invalid_uuids = [
            '019a4757-c049-7ea8-a110-2ea110c5a6g6',  # 'g' is not hex
            '019a4757-c049-7ea8-a110-2ea110c5a6z6',  # 'z' is not hex
            '019a4757-c049-7ea8-a110-2ea110c5a6!6',  # special char
        ]
        
        for uuid in invalid_uuids:
            assert is_valid_uuidv7(uuid) is False, f"Should reject {uuid}"

    def test_whitespace_not_trimmed(self):
        """Test that whitespace is not automatically trimmed."""
        uuid_with_space = ' 019a4757-c049-7ea8-a110-2ea110c5a6f6'
        
        # Should fail because space is included
        assert is_valid_uuidv7(uuid_with_space) is False

    def test_uuid_pattern_directly(self):
        """Test UUID_V7_PATTERN regex directly."""
        valid_uuid = '019a4757-c049-7ea8-a110-2ea110c5a6f6'
        invalid_uuid = 'not-a-uuid'
        
        assert UUID_V7_PATTERN.match(valid_uuid) is not None
        assert UUID_V7_PATTERN.match(invalid_uuid) is None

    def test_case_insensitive(self):
        """Test that validation is case-insensitive."""
        lowercase = '019a4757-c049-7ea8-a110-2ea110c5a6f6'
        uppercase = '019A4757-C049-7EA8-A110-2EA110C5A6F6'
        mixed = '019a4757-C049-7EA8-a110-2ea110C5A6F6'
        
        assert is_valid_uuidv7(lowercase) is True
        assert is_valid_uuidv7(uppercase) is True
        assert is_valid_uuidv7(mixed) is True

    def test_version_field_must_be_7(self):
        """Test that version field (13th character) must be '7'."""
        # Valid: version 7
        valid = '019a4757-c049-7ea8-a110-2ea110c5a6f6'
        assert is_valid_uuidv7(valid) is True
        
        # Invalid: other versions
        invalid_versions = [
            '019a4757-c049-0ea8-a110-2ea110c5a6f6',  # version 0
            '019a4757-c049-1ea8-a110-2ea110c5a6f6',  # version 1
            '019a4757-c049-4ea8-a110-2ea110c5a6f6',  # version 4
            '019a4757-c049-6ea8-a110-2ea110c5a6f6',  # version 6
        ]
        
        for uuid in invalid_versions:
            assert is_valid_uuidv7(uuid) is False, f"Should reject version in {uuid}"
