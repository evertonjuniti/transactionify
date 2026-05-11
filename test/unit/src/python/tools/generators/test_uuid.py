"""Tests for UUID generation utilities."""

from unittest.mock import MagicMock
from src.python.transactionify.tools.generators.uuid import generate_uuidv7


class TestGenerateUuidv7:
    """Test cases for generate_uuidv7 function."""

    def test_generate_uuidv7_with_uuid_utils(self):
        """Test UUID generation with uuid_utils library."""
        # Mock the import
        import sys
        mock_uuid_lib = MagicMock()
        mock_uuid_lib.uuid7.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f6'
        sys.modules['uuid_utils'] = mock_uuid_lib

        # Reload to pick up the mock
        import importlib
        from src.python.transactionify.tools.generators import uuid as uuid_module
        importlib.reload(uuid_module)

        result = uuid_module.generate_uuidv7()

        # Cleanup
        del sys.modules['uuid_utils']
        importlib.reload(uuid_module)

        assert isinstance(result, str)
        assert result == '019a4757-c049-7ea8-a110-2ea110c5a6f6'

    def test_generate_uuidv7_fallback(self):
        """Test UUID generation fallback when uuid_utils not available."""
        result = generate_uuidv7()

        # Verify it's a valid UUID format
        assert isinstance(result, str)
        assert len(result) == 36
        parts = result.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

        # Verify version is 7
        assert parts[2][0] == '7'

    def test_generate_uuidv7_produces_unique_values(self):
        """Test that generate_uuidv7 produces unique values."""
        uuids = [generate_uuidv7() for _ in range(10)]

        # All should be unique
        assert len(set(uuids)) == 10

    def test_generate_uuidv7_valid_format(self):
        """Test that generated UUIDs match the expected format."""
        for _ in range(5):
            uuid = generate_uuidv7()
            # Our fallback implementation should produce valid v7 format
            # (though not cryptographically proper v7 without the library)
            assert '-' in uuid
            assert len(uuid) == 36
