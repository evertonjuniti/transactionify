import json
from unittest.mock import patch
from src.python.transactionify.handlers.provisioning.main import handler


class TestProvisioningHandler:
    """Test cases for the provisioning Lambda handler."""

    @patch('src.python.transactionify.handlers.provisioning.main.register_new_api_key')
    def test_handler_with_provided_user_id(self, mock_register):
        """Test handler with a provided user_id."""
        mock_register.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f6'

        event = {
            'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        }

        response = handler(event, None)

        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['api_key'] == '019a4757-c049-7ea8-a110-2ea110c5a6f6'
        assert body['user_id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        assert 'ttl' not in body  # No TTL for API keys
        assert body['message'] == 'API key successfully created'

        # Verify service was called with correct user_id
        mock_register.assert_called_once_with('019a4757-c049-7ea8-a110-2ea110c5a6f7')

    @patch('src.python.transactionify.handlers.provisioning.main.generate_uuidv7')
    @patch('src.python.transactionify.handlers.provisioning.main.register_new_api_key')
    def test_handler_without_user_id_generates_new(self, mock_register, mock_generate):
        """Test handler generates new user_id when not provided."""
        mock_generate.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        mock_register.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f6'

        event = {}

        response = handler(event, None)

        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['api_key'] == '019a4757-c049-7ea8-a110-2ea110c5a6f6'
        assert body['user_id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        assert 'ttl' not in body  # No TTL for API keys

        # Verify generate_uuidv7 was called once for user_id
        mock_generate.assert_called_once()
        # Verify register_new_api_key was called with generated user_id
        mock_register.assert_called_once_with('019a4757-c049-7ea8-a110-2ea110c5a6f7')

    @patch('src.python.transactionify.handlers.provisioning.main.register_new_api_key')
    def test_handler_invalid_user_id_format(self, mock_register):
        """Test handler rejects invalid user_id format."""
        mock_register.side_effect = ValueError('Invalid user_id format. Must be UUIDv7: invalid-uuid')

        event = {
            'user_id': 'invalid-uuid'
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Invalid user_id format'
        assert 'invalid-uuid' in body['message']

    @patch('src.python.transactionify.handlers.provisioning.main.register_new_api_key')
    def test_handler_uuidv4_rejected(self, mock_register):
        """Test handler rejects UUIDv4 (must be v7)."""
        mock_register.side_effect = ValueError('Invalid user_id format. Must be UUIDv7: 550e8400-e29b-41d4-a716-446655440000')

        event = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000'  # UUIDv4
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Invalid user_id format'

    @patch('src.python.transactionify.handlers.provisioning.main.register_new_api_key')
    def test_handler_dynamodb_error(self, mock_register):
        """Test handler handles DynamoDB errors gracefully."""
        mock_register.side_effect = Exception('DynamoDB error')

        event = {
            'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['error'] == 'Internal server error'
        assert 'DynamoDB error' in body['message']

    @patch('src.python.transactionify.handlers.provisioning.main.generate_uuidv7')
    @patch('src.python.transactionify.handlers.provisioning.main.register_new_api_key')
    def test_handler_empty_user_id_string(self, mock_register, mock_generate):
        """Test handler treats empty string as no user_id."""
        mock_generate.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f7'
        mock_register.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f6'

        event = {
            'user_id': ''
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        # Should generate new user_id
        mock_generate.assert_called_once()
        mock_register.assert_called_once_with('019a4757-c049-7ea8-a110-2ea110c5a6f7')


