"""Tests for list transactions Lambda handler."""

import json
from unittest.mock import patch
from src.python.transactionify.handlers.api.rest.transaction.list.main import handler


class TestListTransactionsHandler:
    """Test cases for the list transactions Lambda handler."""

    @patch('src.python.transactionify.handlers.api.rest.transaction.list.main.list_transactions')
    def test_handler_success(self, mock_list_transactions):
        """Test successful transaction listing."""
        mock_list_transactions.return_value = [
            {
                'id': '019a4757-c049-7ea8-a110-2ea110c5a6f9',
                'type': 'payment',
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                },
                'timestamp': '2024-02-22T10:00:00Z'
            },
            {
                'id': '019a4757-c049-7ea8-a110-2ea110c5a700',
                'type': 'payment',
                'amount': {
                    'value': '50.00',
                    'currency': 'USD'
                },
                'timestamp': '2024-02-22T11:00:00Z'
            }
        ]

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body) == 2
        assert body[0]['id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        assert body[0]['type'] == 'payment'
        assert body[0]['amount']['value'] == '100.00'
        assert body[0]['timestamp'] == '2024-02-22T10:00:00Z'
        mock_list_transactions.assert_called_once_with(
            '019a4757-c049-7ea8-a110-2ea110c5a6f7',
            '019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

    @patch('src.python.transactionify.handlers.api.rest.transaction.list.main.list_transactions')
    def test_handler_empty_list(self, mock_list_transactions):
        """Test successful listing with no transactions."""
        mock_list_transactions.return_value = []

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body) == 0
        assert body == []

    def test_handler_missing_user_id(self):
        """Test error when user_id is missing from authorizer context."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {}
                }
            },
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert body['message'] == 'Unauthorized'

    def test_handler_missing_account_id(self):
        """Test error when account_id is missing from path parameters."""
        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'pathParameters': {}
        }

        response = handler(event, None)

        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['message'] == 'Account not found'

    @patch('src.python.transactionify.handlers.api.rest.transaction.list.main.list_transactions')
    def test_handler_account_not_found(self, mock_list_transactions):
        """Test error when account doesn't exist."""
        mock_list_transactions.side_effect = ValueError('Account not found or does not belong to user')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['message'] == 'Account not found'

    @patch('src.python.transactionify.handlers.api.rest.transaction.list.main.list_transactions')
    def test_handler_internal_error(self, mock_list_transactions):
        """Test error handling for internal errors."""
        mock_list_transactions.side_effect = Exception('DynamoDB error')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['message'] == 'An error occurred while retrieving transactions'

    @patch('src.python.transactionify.handlers.api.rest.transaction.list.main.list_transactions')
    def test_handler_does_not_expose_internal_errors(self, mock_list_transactions):
        """Test that internal error details are not exposed to clients."""
        mock_list_transactions.side_effect = Exception('Database connection failed: host=internal-db.company.com')

        event = {
            'requestContext': {
                'authorizer': {
                    'lambda': {
                        'user_id': '019a4757-c049-7ea8-a110-2ea110c5a6f7'
                    }
                }
            },
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            }
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['message'] == 'An error occurred while retrieving transactions'
        # Verify internal details are NOT in the response
        assert 'Database connection' not in body['message']
        assert 'internal-db.company.com' not in body['message']
