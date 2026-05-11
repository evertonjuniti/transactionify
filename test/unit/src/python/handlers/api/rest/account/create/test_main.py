"""Tests for create account Lambda handler."""

import json
from unittest.mock import patch
from src.python.transactionify.handlers.api.rest.account.create.main import handler


class TestCreateAccountHandler:
    """Test cases for the create account Lambda handler."""

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_success_usd(self, mock_create_account):
        """Test successful account creation with USD."""
        mock_create_account.return_value = {
            'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD',
            'balance': {
                'value': '0.00',
                'currency': 'USD'
            }
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'USD'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body == {
            'id': '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'balance': {
                'value': '0.00',
                'currency': 'USD'
            }
        }
        mock_create_account.assert_called_once_with('019a4757-c049-7ea8-a110-2ea110c5a6f7', 'USD')

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_success_eur(self, mock_create_account):
        """Test successful account creation with EUR."""
        mock_create_account.return_value = {
            'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'EUR',
            'balance': {
                'value': '0.00',
                'currency': 'EUR'
            }
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'EUR'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f8'
        assert body['balance']['currency'] == 'EUR'
        mock_create_account.assert_called_once_with('019a4757-c049-7ea8-a110-2ea110c5a6f7', 'EUR')

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_success_gbp(self, mock_create_account):
        """Test successful account creation with GBP."""
        mock_create_account.return_value = {
            'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'GBP',
            'balance': {
                'value': '0.00',
                'currency': 'GBP'
            }
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'GBP'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f8'
        assert body['balance']['currency'] == 'GBP'

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_lowercase_currency(self, mock_create_account):
        """Test that lowercase currency is converted to uppercase."""
        mock_create_account.return_value = {
            'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD',
            'balance': {
                'value': '0.00',
                'currency': 'USD'
            }
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'usd'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        # Should call service with uppercase
        mock_create_account.assert_called_once_with('019a4757-c049-7ea8-a110-2ea110c5a6f7', 'USD')

    def test_handler_missing_currency(self):
        """Test error when currency is missing."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({})
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'currency' in body['message']

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_invalid_currency(self, mock_create_account):
        """Test error when currency is invalid."""
        mock_create_account.side_effect = ValueError('Invalid currency. Must be one of: USD, EUR, GBP')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'JPY'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        # Check for safe error message (not exposing internal error)
        assert body['message'] == 'Invalid currency. Allowed values: USD, EUR, GBP'

    def test_handler_invalid_json(self):
        """Test error when request body is invalid JSON."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': 'invalid json'
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'JSON' in body['message']

    def test_handler_missing_user_id(self):
        """Test error when user_id is missing from authorizer context."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {}
                }
            },
            'body': json.dumps({'currency': 'USD'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'Unauthorized' in body['message']

    def test_handler_missing_authorizer_context(self):
        """Test error when authorizer context is missing."""
        event = {
            'requestContext': {},
            'body': json.dumps({'currency': 'USD'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 401

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_dynamodb_error(self, mock_create_account):
        """Test error handling for DynamoDB errors."""
        mock_create_account.side_effect = Exception('DynamoDB error')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'USD'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        # Check for safe error message (not exposing internal error)
        assert body['message'] == 'An error occurred while creating the account'

    def test_handler_empty_body(self):
        """Test error when body is empty."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': ''
        }

        response = handler(event, None)

        assert response['statusCode'] == 400

    def test_handler_missing_body(self):
        """Test error when body key is missing from event."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 400

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_does_not_expose_internal_errors(self, mock_create_account):
        """Test that internal error details are not exposed to clients."""
        # Simulate an internal error with sensitive information
        mock_create_account.side_effect = Exception('Database connection failed: host=internal-db.company.com port=5432')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'USD'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])

        # Verify we return a safe generic message
        assert body['message'] == 'An error occurred while creating the account'

        # Verify internal details are NOT in the response
        assert 'Database connection' not in body['message']
        assert 'internal-db.company.com' not in body['message']
        assert '5432' not in body['message']

    @patch('src.python.transactionify.handlers.api.rest.account.create.main.create_account')
    def test_handler_generic_validation_error(self, mock_create_account):
        """Test that non-currency validation errors return generic message."""
        # Simulate a validation error that doesn't mention currency
        mock_create_account.side_effect = ValueError('User ID validation failed')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'body': json.dumps({'currency': 'USD'})
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])

        # Should return generic validation error message
        assert body['message'] == 'Invalid request data'

        # Should not expose internal validation details
        assert 'User ID validation failed' not in body['message']
