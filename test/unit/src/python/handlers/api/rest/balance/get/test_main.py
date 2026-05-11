"""Tests for get balance Lambda handler."""

import json
from unittest.mock import patch
from src.python.transactionify.handlers.api.rest.balance.get.main import handler


class TestGetBalanceHandler:
    """Test cases for the get balance Lambda handler."""

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_success(self, mock_get_balance):
        """Test successful balance retrieval."""
        mock_get_balance.return_value = {
            'balance': {
                'value': '100.00',
                'currency': 'USD'
            },
            'date': '2024-02-23T12:00:00Z'
        }

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
        assert body == {
            'balance': {
                'value': '100.00',
                'currency': 'USD'
            },
            'date': '2024-02-23T12:00:00Z'
        }
        mock_get_balance.assert_called_once_with(
            '019a4757-c049-7ea8-a110-2ea110c5a6f7',
            '019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_success_eur(self, mock_get_balance):
        """Test successful balance retrieval with EUR."""
        mock_get_balance.return_value = {
            'balance': {
                'value': '50.75',
                'currency': 'EUR'
            },
            'date': '2024-02-23T12:00:00Z'
        }

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
        assert body['balance']['currency'] == 'EUR'
        assert body['balance']['value'] == '50.75'

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_zero_balance(self, mock_get_balance):
        """Test successful balance retrieval with zero balance."""
        mock_get_balance.return_value = {
            'balance': {
                'value': '0.00',
                'currency': 'GBP'
            },
            'date': '2024-02-23T12:00:00Z'
        }

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
        assert body['balance']['value'] == '0.00'

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

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_account_not_found(self, mock_get_balance):
        """Test error when account doesn't exist."""
        mock_get_balance.side_effect = ValueError('Account not found or does not belong to user')

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

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_balance_not_found(self, mock_get_balance):
        """Test error when balance record doesn't exist."""
        mock_get_balance.side_effect = ValueError('Balance record not found for account')

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
        assert body['message'] == 'Balance not found'

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_internal_error(self, mock_get_balance):
        """Test error handling for internal errors."""
        mock_get_balance.side_effect = Exception('DynamoDB error')

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
        assert body['message'] == 'An error occurred while retrieving the balance'

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_does_not_expose_internal_errors(self, mock_get_balance):
        """Test that internal error details are not exposed to clients."""
        mock_get_balance.side_effect = Exception('Database connection failed: host=internal-db.company.com')

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
        assert body['message'] == 'An error occurred while retrieving the balance'
        # Verify internal details are NOT in the response
        assert 'Database connection' not in body['message']
        assert 'internal-db.company.com' not in body['message']

    @patch('src.python.transactionify.handlers.api.rest.balance.get.main.get_balance')
    def test_handler_date_field_included(self, mock_get_balance):
        """Test that date field is included in response."""
        mock_get_balance.return_value = {
            'balance': {
                'value': '100.00',
                'currency': 'USD'
            },
            'date': '2024-02-23T12:00:00.123456Z'
        }

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
        assert 'date' in body
        assert body['date'] == '2024-02-23T12:00:00.123456Z'
