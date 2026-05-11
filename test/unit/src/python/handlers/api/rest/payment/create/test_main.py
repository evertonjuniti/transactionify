"""Tests for create payment Lambda handler."""

import json
from unittest.mock import patch
from src.python.transactionify.handlers.api.rest.payment.create.main import handler


class TestCreatePaymentHandler:
    """Test cases for the create payment Lambda handler."""

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_success(self, mock_create_payment):
        """Test successful payment creation."""
        mock_create_payment.return_value = {
            'id': '019a4757-c049-7ea8-a110-2ea110c5a6f9',
            'type': 'payment',
            'amount': {
                'value': '100.00',
                'currency': 'USD'
            },
            'status': 'pending'
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
            },
            'body': json.dumps({
                'type': 'payment',
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body == {
            'id': '019a4757-c049-7ea8-a110-2ea110c5a6f9',
            'type': 'payment',
            'amount': {
                'value': '100.00',
                'currency': 'USD'
            },
            'status': 'pending'
        }
        mock_create_payment.assert_called_once_with(
            '019a4757-c049-7ea8-a110-2ea110c5a6f7',
            '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            '100.00',
            'USD'
        )

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_success_eur(self, mock_create_payment):
        """Test successful payment creation with EUR."""
        mock_create_payment.return_value = {
            'id': '019a4757-c049-7ea8-a110-2ea110c5a700',
            'type': 'payment',
            'amount': {
                'value': '50.00',
                'currency': 'EUR'
            },
            'status': 'pending'
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
            },
            'body': json.dumps({
                'amount': {
                    'value': '50.00',
                    'currency': 'EUR'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['id'] == '019a4757-c049-7ea8-a110-2ea110c5a700'
        assert body['amount']['currency'] == 'EUR'

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_lowercase_currency(self, mock_create_payment):
        """Test that lowercase currency is converted to uppercase."""
        mock_create_payment.return_value = {
            'id': '019a4757-c049-7ea8-a110-2ea110c5a6f9',
            'type': 'payment',
            'amount': {
                'value': '100.00',
                'currency': 'USD'
            },
            'status': 'pending'
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
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'usd'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 200
        # Should call service with uppercase
        mock_create_payment.assert_called_once_with(
            '019a4757-c049-7ea8-a110-2ea110c5a6f7',
            '019a4757-c049-7ea8-a110-2ea110c5a6f8',
            '100.00',
            'USD'
        )

    def test_handler_missing_amount_value(self):
        """Test error when amount.value is missing."""
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
            },
            'body': json.dumps({
                'amount': {
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'amount.value' in body['message']

    def test_handler_missing_amount_currency(self):
        """Test error when amount.currency is missing."""
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
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'amount.currency' in body['message']

    def test_handler_missing_amount_object(self):
        """Test error when amount object is missing."""
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
            },
            'body': json.dumps({})
        }

        response = handler(event, None)

        assert response['statusCode'] == 400

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
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
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
            'pathParameters': {
                'account_id': '019a4757-c049-7ea8-a110-2ea110c5a6f8'
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 401

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
            'pathParameters': {},
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'account_id' in body['message']

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_account_not_found(self, mock_create_payment):
        """Test error when account doesn't exist."""
        mock_create_payment.side_effect = ValueError('Account not found or does not belong to user')

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
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['message'] == 'Account not found'

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_currency_mismatch(self, mock_create_payment):
        """Test error when payment currency doesn't match account currency."""
        mock_create_payment.side_effect = ValueError('Currency mismatch. Account currency is USD, but payment currency is EUR')

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
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'EUR'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Currency does not match' in body['message']

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_internal_error(self, mock_create_payment):
        """Test error handling for internal errors."""
        mock_create_payment.side_effect = Exception('DynamoDB error')

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
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['message'] == 'An error occurred while creating the payment'

    @patch('src.python.transactionify.handlers.api.rest.payment.create.main.create_payment')
    def test_handler_does_not_expose_internal_errors(self, mock_create_payment):
        """Test that internal error details are not exposed to clients."""
        mock_create_payment.side_effect = Exception('Database connection failed: host=internal-db.company.com')

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
            },
            'body': json.dumps({
                'amount': {
                    'value': '100.00',
                    'currency': 'USD'
                }
            })
        }

        response = handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['message'] == 'An error occurred while creating the payment'
        # Verify internal details are NOT in the response
        assert 'Database connection' not in body['message']
        assert 'internal-db.company.com' not in body['message']
