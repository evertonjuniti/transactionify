"""Tests for balance service."""

import pytest
from unittest.mock import patch
from src.python.transactionify.services.balance import get_balance


class TestGetBalance:
    """Test cases for get_balance function."""

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_success_usd(self, mock_get_item):
        """Test successful balance retrieval with USD."""
        # Mock account lookup
        def side_effect(pk, sk):
            if sk.startswith('ACCOUNT#'):
                return {
                    'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
                    'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'currency': 'USD'
                }
            elif sk == 'BALANCE':
                return {
                    'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'SK': 'BALANCE',
                    'value': '100.00'
                }
            return None

        mock_get_item.side_effect = side_effect

        result = get_balance(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        assert result['balance']['value'] == '100.00'
        assert result['balance']['currency'] == 'USD'
        assert 'date' in result
        # Verify date is ISO 8601 format
        assert result['date'].endswith('Z')
        assert 'T' in result['date']

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_success_eur(self, mock_get_item):
        """Test successful balance retrieval with EUR."""
        def side_effect(pk, sk):
            if sk.startswith('ACCOUNT#'):
                return {
                    'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
                    'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'currency': 'EUR'
                }
            elif sk == 'BALANCE':
                return {
                    'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'SK': 'BALANCE',
                    'value': '50.75'
                }
            return None

        mock_get_item.side_effect = side_effect

        result = get_balance(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        assert result['balance']['value'] == '50.75'
        assert result['balance']['currency'] == 'EUR'

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_zero_balance(self, mock_get_item):
        """Test balance retrieval with zero balance."""
        def side_effect(pk, sk):
            if sk.startswith('ACCOUNT#'):
                return {
                    'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
                    'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'currency': 'GBP'
                }
            elif sk == 'BALANCE':
                return {
                    'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'SK': 'BALANCE',
                    'value': '0.00'
                }
            return None

        mock_get_item.side_effect = side_effect

        result = get_balance(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        assert result['balance']['value'] == '0.00'
        assert result['balance']['currency'] == 'GBP'

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_account_not_found(self, mock_get_item):
        """Test error when account doesn't exist."""
        mock_get_item.return_value = None

        with pytest.raises(ValueError) as exc_info:
            get_balance(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
            )

        assert 'Account not found' in str(exc_info.value)

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_validates_user_ownership(self, mock_get_item):
        """Test that balance validates account belongs to user."""
        # Account exists but for different user (returns None when querying with wrong user_id)
        mock_get_item.return_value = None

        with pytest.raises(ValueError):
            get_balance(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
            )

        # Verify it checked with the correct user_id
        assert mock_get_item.call_count >= 1
        first_call = mock_get_item.call_args_list[0]
        assert first_call[1]['pk'] == 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7'
        assert first_call[1]['sk'] == 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8'

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_record_not_found(self, mock_get_item):
        """Test error when balance record doesn't exist."""
        def side_effect(pk, sk):
            if sk.startswith('ACCOUNT#'):
                # Account exists
                return {
                    'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
                    'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'currency': 'USD'
                }
            elif sk == 'BALANCE':
                # Balance record doesn't exist
                return None
            return None

        mock_get_item.side_effect = side_effect

        with pytest.raises(ValueError) as exc_info:
            get_balance(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
            )

        assert 'Balance record not found' in str(exc_info.value)

    @patch('src.python.transactionify.services.balance.get_by_full_match')
    def test_get_balance_date_format(self, mock_get_item):
        """Test that date is in correct ISO 8601 format."""
        def side_effect(pk, sk):
            if sk.startswith('ACCOUNT#'):
                return {
                    'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
                    'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'currency': 'USD'
                }
            elif sk == 'BALANCE':
                return {
                    'PK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
                    'SK': 'BALANCE',
                    'value': '100.00'
                }
            return None

        mock_get_item.side_effect = side_effect

        result = get_balance(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        # Verify date format: YYYY-MM-DDTHH:MM:SS.ffffffZ
        date = result['date']
        assert date.endswith('Z')
        assert 'T' in date
        parts = date.split('T')
        assert len(parts) == 2
        date_part = parts[0]
        time_part = parts[1].rstrip('Z')
        # Verify date has dashes
        assert '-' in date_part
        # Verify time has colons
        assert ':' in time_part
