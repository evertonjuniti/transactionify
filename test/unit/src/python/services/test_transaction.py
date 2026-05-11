"""Tests for transaction service."""

import pytest
from unittest.mock import patch
from src.python.transactionify.services.transaction import list_transactions


class TestListTransactions:
    """Test cases for list_transactions function."""

    @patch('src.python.transactionify.services.transaction.query_by_pk')
    @patch('src.python.transactionify.services.transaction.get_by_full_match')
    def test_list_transactions_success(self, mock_get_item, mock_query):
        """Test successful transaction listing."""
        # Mock account lookup
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD'
        }

        # Mock transaction query
        mock_query.return_value = [
            {
                'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                'SK': 'TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a6f9',
                'type': 'payment',
                'value': '100.00',
                'currency': 'USD',
                'timestamp': '2024-02-22T10:00:00Z'
            },
            {
                'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                'SK': 'TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a700',
                'type': 'payment',
                'value': '50.00',
                'currency': 'USD',
                'timestamp': '2024-02-22T11:00:00Z'
            }
        ]

        result = list_transactions(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        assert len(result) == 2
        assert result[0]['id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        assert result[0]['type'] == 'payment'
        assert result[0]['amount']['value'] == '100.00'
        assert result[0]['amount']['currency'] == 'USD'
        assert result[0]['timestamp'] == '2024-02-22T10:00:00Z'

        assert result[1]['id'] == '019a4757-c049-7ea8-a110-2ea110c5a700'
        assert result[1]['amount']['value'] == '50.00'

    @patch('src.python.transactionify.services.transaction.query_by_pk')
    @patch('src.python.transactionify.services.transaction.get_by_full_match')
    def test_list_transactions_empty(self, mock_get_item, mock_query):
        """Test transaction listing with no transactions."""
        # Mock account lookup
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'EUR'
        }

        # Mock empty transaction query
        mock_query.return_value = []

        result = list_transactions(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        assert len(result) == 0
        assert result == []

    @patch('src.python.transactionify.services.transaction.get_by_full_match')
    def test_list_transactions_account_not_found(self, mock_get_item):
        """Test error when account doesn't exist."""
        mock_get_item.return_value = None

        with pytest.raises(ValueError) as exc_info:
            list_transactions(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
            )

        assert 'Account not found' in str(exc_info.value)

    @patch('src.python.transactionify.services.transaction.get_by_full_match')
    def test_list_transactions_validates_user_ownership(self, mock_get_item):
        """Test that listing validates account belongs to user."""
        # Account exists but for different user (returns None when querying with wrong user_id)
        mock_get_item.return_value = None

        with pytest.raises(ValueError):
            list_transactions(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
            )

        # Verify it checked with the correct user_id
        mock_get_item.assert_called_once_with(
            pk='USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            sk='ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

    @patch('src.python.transactionify.services.transaction.query_by_pk')
    @patch('src.python.transactionify.services.transaction.get_by_full_match')
    def test_list_transactions_uses_account_currency(self, mock_get_item, mock_query):
        """Test that transactions use account currency if not specified."""
        # Mock account lookup
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'GBP'
        }

        # Mock transaction without currency field
        mock_query.return_value = [
            {
                'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                'SK': 'TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a6f9',
                'type': 'payment',
                'value': '75.50',
                'timestamp': '2024-02-22T10:00:00Z'
                # No currency field
            }
        ]

        result = list_transactions(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        assert len(result) == 1
        # Should use account currency
        assert result[0]['amount']['currency'] == 'GBP'

    @patch('src.python.transactionify.services.transaction.query_by_pk')
    @patch('src.python.transactionify.services.transaction.get_by_full_match')
    def test_list_transactions_query_parameters(self, mock_get_item, mock_query):
        """Test that query is called with correct parameters."""
        # Mock account lookup
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD'
        }

        mock_query.return_value = []

        list_transactions(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        # Verify query was called with correct PK and SK prefix
        mock_query.assert_called_once_with(
            pk='ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            sk_prefix='TRANSACTION#'
        )
