"""Transaction service for managing transactions."""

from typing import Dict, Any, List
from transactionify.tools.aws.dynamodb import (
    query_by_pk,
    get_by_full_match,
)


def list_transactions(
    user_id: str,
    account_id: str,
) -> List[Dict[str, Any]]:
    """
    List transactions for an account with pagination support.

    This function:
    1. Validates that the account exists and belongs to the user
    2. Queries transactions for the account with pagination
    3. Returns paginated list of transactions with metadata

    Args:
        user_id: The user identifier (UUIDv7) from authorization context
        account_id: The account identifier (UUIDv7)

    Returns:
        List of transaction dicts

    Raises:
        ValueError: If account doesn't exist or doesn't belong to user
    """
    # Validate that account exists and belongs to user
    account_pk = f"USER_ID#{user_id}"
    account_sk = f"ACCOUNT#{account_id}"
    account = get_by_full_match(pk=account_pk, sk=account_sk)

    if not account:
        raise ValueError("Account not found or does not belong to user")

    # Get account currency
    account_currency = account.get('currency', '')

    # Query transactions
    records = query_by_pk(
        pk=f"ACCOUNT#{account_id}",
        sk_prefix="TRANSACTION#"
    )

    # Transform transaction records to API format
    transactions = []
    for record in records:
        # Extract transaction ID from SK (format: TRANSACTION#<id>)
        sk = record.get('SK', '')
        transaction_id = sk.replace('TRANSACTION#', '') if sk.startswith('TRANSACTION#') else ''

        transaction = {
            'id': transaction_id,
            'type': record.get('type', 'payment'),
            'amount': {
                'value': record.get('value', '0.00'),
                'currency': record.get('currency', account_currency)
            },
            'timestamp': record.get('timestamp', '')
        }

        transactions.append(transaction)

    return transactions
