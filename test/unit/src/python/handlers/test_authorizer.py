from unittest.mock import patch
from src.python.transactionify.handlers.authorizer.main import (
    handler,
    extract_api_key,
)


class TestAuthorizerHandler:
    """Test cases for the Lambda authorizer handler."""

    def test_handler_no_authorization_header(self):
        """Test handler denies access when no Authorization header is provided."""
        event = {
            'headers': {},
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }
        
        response = handler(event, None)
        
        assert response['isAuthorized'] is False

    def test_handler_invalid_uuidv7_format(self):
        """Test handler denies access when API key is not a valid UUIDv7."""
        event = {
            'headers': {
                'Authorization': 'APIKey invalid-uuid'
            },
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }

        response = handler(event, None)

        assert response['isAuthorized'] is False

    def test_handler_valid_uuidv4_rejected(self):
        """Test handler denies access when API key is UUIDv4 (not v7)."""
        event = {
            'headers': {
                'Authorization': 'APIKey 550e8400-e29b-41d4-a716-446655440000'  # UUIDv4
            },
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }

        response = handler(event, None)

        assert response['isAuthorized'] is False

    @patch('src.python.transactionify.handlers.authorizer.main.get_api_key')
    def test_handler_valid_api_key(self, mock_get_api_key):
        """Test handler allows access with valid UUIDv7 API key."""
        mock_get_api_key.return_value = {
            'PK': 'API_KEY#019a4757-c049-7ea8-a110-2ea110c5a6f6',
            'SK': '',
            'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        }

        event = {
            'headers': {
                'Authorization': 'APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6'
            },
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }

        response = handler(event, None)

        assert response['isAuthorized'] is True
        assert 'context' in response
        assert response['context']['user_id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f7'

    @patch('src.python.transactionify.handlers.authorizer.main.get_api_key')
    def test_handler_api_key_not_found_in_db(self, mock_get_api_key):
        """Test handler denies access when API key not found in DynamoDB."""
        mock_get_api_key.return_value = {}  # Empty dict = not found

        event = {
            'headers': {
                'Authorization': 'APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6'
            },
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }

        response = handler(event, None)

        assert response['isAuthorized'] is False

    @patch('src.python.transactionify.handlers.authorizer.main.get_api_key')
    def test_handler_exception_during_validation(self, mock_get_api_key):
        """Test handler denies access when an exception occurs during validation."""
        mock_get_api_key.side_effect = Exception('DynamoDB error')

        event = {
            'headers': {
                'Authorization': 'APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6'
            },
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }

        response = handler(event, None)

        assert response['isAuthorized'] is False

    def test_handler_case_insensitive_apikey_schema(self):
        """Test handler accepts case-insensitive APIKey schema."""
        event = {
            'headers': {
                'authorization': 'apikey 019a4757-c049-7ea8-a110-2ea110c5a6f6'  # lowercase
            },
            'routeArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/prod/GET/test'
        }

        # Should extract the key (validation will fail in DB lookup, but extraction works)
        api_key = extract_api_key(event)
        assert api_key == '019a4757-c049-7ea8-a110-2ea110c5a6f6'


class TestExtractApiKey:
    """Test cases for extract_api_key function."""

    def test_extract_api_key_with_apikey_schema(self):
        """Test extracting API key with APIKey schema."""
        event = {
            'headers': {
                'Authorization': 'APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6'
            }
        }

        api_key = extract_api_key(event)

        assert api_key == '019a4757-c049-7ea8-a110-2ea110c5a6f6'

    def test_extract_api_key_case_insensitive_schema(self):
        """Test APIKey schema is case-insensitive."""
        test_cases = [
            'APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6',
            'apikey 019a4757-c049-7ea8-a110-2ea110c5a6f6',
            'ApiKey 019a4757-c049-7ea8-a110-2ea110c5a6f6',
            'APIKEY 019a4757-c049-7ea8-a110-2ea110c5a6f6',
        ]

        for auth_value in test_cases:
            event = {'headers': {'Authorization': auth_value}}
            api_key = extract_api_key(event)
            assert api_key == '019a4757-c049-7ea8-a110-2ea110c5a6f6', f"Failed for: {auth_value}"

    def test_extract_api_key_no_headers(self):
        """Test extracting API key when no headers present."""
        event = {'headers': {}}

        api_key = extract_api_key(event)

        assert api_key == ''

    def test_extract_api_key_case_insensitive_header_name(self):
        """Test extracting API key with case-insensitive header name."""
        event = {
            'headers': {
                'authorization': 'APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6'
            }
        }

        api_key = extract_api_key(event)

        assert api_key == '019a4757-c049-7ea8-a110-2ea110c5a6f6'

    def test_extract_api_key_strips_whitespace(self):
        """Test extracting API key strips leading/trailing whitespace."""
        event = {
            'headers': {
                'Authorization': '  APIKey   019a4757-c049-7ea8-a110-2ea110c5a6f6  '
            }
        }

        api_key = extract_api_key(event)

        assert api_key == '019a4757-c049-7ea8-a110-2ea110c5a6f6'

    def test_extract_api_key_bearer_not_supported(self):
        """Test that Bearer prefix is NOT supported (only APIKey)."""
        event = {
            'headers': {
                'Authorization': 'Bearer 019a4757-c049-7ea8-a110-2ea110c5a6f6'
            }
        }

        api_key = extract_api_key(event)

        # Should return empty string as Bearer is not supported
        assert api_key == ''

    def test_extract_api_key_no_schema(self):
        """Test that API key without schema is rejected."""
        event = {
            'headers': {
                'Authorization': '019a4757-c049-7ea8-a110-2ea110c5a6f6'
            }
        }

        api_key = extract_api_key(event)

        assert api_key == ''

    def test_extract_api_key_missing_value(self):
        """Test that schema without value is rejected."""
        event = {
            'headers': {
                'Authorization': 'APIKey'
            }
        }

        api_key = extract_api_key(event)

        assert api_key == ''

    def test_extract_api_key_empty_authorization_header(self):
        """Test empty Authorization header returns empty string."""
        event = {
            'headers': {
                'Authorization': ''
            }
        }

        api_key = extract_api_key(event)

        assert api_key == ''
