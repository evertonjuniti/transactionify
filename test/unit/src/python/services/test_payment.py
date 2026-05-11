"""Tests for payment service."""

import pytest
from unittest.mock import patch
from src.python.transactionify.services.payment import create_payment


class TestCreatePayment:
    """Test cases for create_payment function."""

    @patch('src.python.transactionify.services.payment.generate_uuidv7')
    @patch('src.python.transactionify.services.payment.get_ttl_2_weeks')
    @patch('src.python.transactionify.services.payment.put_item')
    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_success_usd(self, mock_get_item, mock_put_item, mock_get_ttl, mock_generate_uuid):
        """Test successful payment creation with USD."""
        # Mock account lookup
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD'
        }
        mock_generate_uuid.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        mock_get_ttl.return_value = 1234567890

        result = create_payment(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
            amount_value='100.00',
            amount_currency='USD'
        )

        assert result == {
            'id': '019a4757-c049-7ea8-a110-2ea110c5a6f9',
            'type': 'payment',
            'amount': {
                'value': '100.00',
                'currency': 'USD'
            },
            'status': 'pending'
        }

        # Verify account was checked
        mock_get_item.assert_called_once_with(
            pk='USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            sk='ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

        # Verify transaction was created with timestamp
        call_args = mock_put_item.call_args
        assert call_args[1]['pk'] == 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8'
        assert call_args[1]['sk'] == 'TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a6f9'
        attributes = call_args[1]['attributes']
        assert attributes['type'] == 'payment'
        assert attributes['value'] == '100.00'
        assert attributes['currency'] == 'USD'
        assert attributes['status'] == 'pending'
        assert attributes['ttl'] == 1234567890
        assert 'timestamp' in attributes
        assert attributes['timestamp'].endswith('Z')  # ISO 8601 format

    @patch('src.python.transactionify.services.payment.generate_uuidv7')
    @patch('src.python.transactionify.services.payment.get_ttl_2_weeks')
    @patch('src.python.transactionify.services.payment.put_item')
    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_success_eur(self, mock_get_item, mock_put_item, mock_get_ttl, mock_generate_uuid):
        """Test successful payment creation with EUR."""
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'EUR'
        }
        mock_generate_uuid.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        mock_get_ttl.return_value = 1234567890

        result = create_payment(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
            amount_value='50.00',
            amount_currency='EUR'
        )

        assert result['id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        assert result['amount']['currency'] == 'EUR'
        assert result['amount']['value'] == '50.00'

    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_account_not_found(self, mock_get_item):
        """Test error when account doesn't exist."""
        mock_get_item.return_value = None

        with pytest.raises(ValueError) as exc_info:
            create_payment(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
                amount_value='100.00',
                amount_currency='USD'
            )

        assert 'Account not found' in str(exc_info.value)

    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_currency_mismatch(self, mock_get_item):
        """Test error when payment currency doesn't match account currency."""
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD'
        }

        with pytest.raises(ValueError) as exc_info:
            create_payment(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
                amount_value='100.00',
                amount_currency='EUR'
            )

        assert 'Currency mismatch' in str(exc_info.value)
        assert 'USD' in str(exc_info.value)
        assert 'EUR' in str(exc_info.value)

    @patch('src.python.transactionify.services.payment.generate_uuidv7')
    @patch('src.python.transactionify.services.payment.get_ttl_2_weeks')
    @patch('src.python.transactionify.services.payment.put_item')
    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_with_decimal_amount(self, mock_get_item, mock_put_item, mock_get_ttl, mock_generate_uuid):
        """Test payment creation with decimal amounts."""
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'GBP'
        }
        mock_generate_uuid.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        mock_get_ttl.return_value = 1234567890

        result = create_payment(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
            amount_value='123.45',
            amount_currency='GBP'
        )

        assert result['id'] == '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        assert result['amount']['value'] == '123.45'
        assert result['amount']['currency'] == 'GBP'

    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_validates_user_ownership(self, mock_get_item):
        """Test that payment validates account belongs to user."""
        # Account exists but for different user (returns None when querying with wrong user_id)
        mock_get_item.return_value = None

        with pytest.raises(ValueError):
            create_payment(
                user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
                account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
                amount_value='100.00',
                amount_currency='USD'
            )

        # Verify it checked with the correct user_id
        mock_get_item.assert_called_once_with(
            pk='USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            sk='ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8'
        )

    @patch('src.python.transactionify.services.payment.generate_uuidv7')
    @patch('src.python.transactionify.services.payment.get_ttl_2_weeks')
    @patch('src.python.transactionify.services.payment.put_item')
    @patch('src.python.transactionify.services.payment.get_by_full_match')
    def test_create_payment_generates_unique_transaction_id(self, mock_get_item, mock_put_item, mock_get_ttl, mock_generate_uuid):
        """Test that each payment generates a unique transaction ID."""
        mock_get_item.return_value = {
            'PK': 'USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7',
            'SK': 'ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8',
            'currency': 'USD'
        }
        mock_generate_uuid.return_value = '019a4757-c049-7ea8-a110-2ea110c5a6f9'
        mock_get_ttl.return_value = 1234567890

        create_payment(
            user_id='019a4757-c049-7ea8-a110-2ea110c5a6f7',
            account_id='019a4757-c049-7ea8-a110-2ea110c5a6f8',
            amount_value='100.00',
            amount_currency='USD'
        )

        # Verify UUID generation was called
        mock_generate_uuid.assert_called_once()
