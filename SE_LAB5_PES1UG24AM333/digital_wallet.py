
"""Demonstrate basic digital wallet operations and security checks."""

import hashlib
import hmac
import os
import secrets
import tempfile
from datetime import datetime

  = os.environ.get("GATEWAY_SECRET")
WALLET_PIN = os.environ.get("WALLET_PIN")
PIN_SALT = b"digital-wallet-demo-salt-v1"
PBKDF2_ITERATIONS = 600_000

wallet = {"balance": 0.0, "daily_limit": 1000}
transactions = []


def hash_pin(pin):
    """Return a salted PBKDF2 hash of a wallet PIN."""
    return hashlib.pbkdf2_hmac(
        "sha256", pin.encode(), PIN_SALT, PBKDF2_ITERATIONS
    )


def add_money(amount, source="UPI", log=None):
    """Credit money to the wallet and optionally record it in a log."""
    if amount <= 0:
        return False

    if log is None:
        log = []

    wallet["balance"] += amount
    transactions.append({
        "type": "credit",
        "amount": amount,
        "party": source,
        "time": datetime.now().isoformat(),
    })
    log.append(amount)
    return True


def set_daily_limit(new_limit):
    """Set the maximum permitted payment amount."""
    if new_limit < 0:
        raise ValueError("Daily limit cannot be negative")
    wallet["daily_limit"] = new_limit


def pay_merchant(merchant, amount, pin):
    """Debit a payment after checking the PIN and wallet limits."""
    if WALLET_PIN is None or not hmac.compare_digest(
        hash_pin(pin), hash_pin(WALLET_PIN)
    ):
        print("Wrong PIN for payment to", merchant)
        return False

    if amount <= 0:
        print("Payment amount must be positive")
        return False

    if (
        amount > wallet["balance"]
        or amount > wallet["daily_limit"]
    ):
        print("Payment to", merchant, "declined")
        return False

    wallet["balance"] -= amount
    transactions.append({
        "type": "debit",
        "amount": amount,
        "party": merchant,
        "time": datetime.now().isoformat(),
    })
    return True


def mini_statement(count=3):
    """Print the most recent wallet transactions."""
    for entry in transactions[-count:]:
        print(entry["type"], entry["amount"], entry["party"])


def cashback_for(amount, _merchant_type):
    """Calculate cashback at a rate of two percent."""
    return round(amount * 0.02, 2)


def check_gateway(secret):
    """Check a supplied gateway secret against the configured secret."""
    return (
        GATEWAY_SECRET is not None
        and hmac.compare_digest(secret, GATEWAY_SECRET)
    )


def receipt_path():
    """Create a temporary receipt file securely and return its path."""
    with tempfile.NamedTemporaryFile(
        suffix=".pdf", delete=False
    ) as receipt:
        return receipt.name


def main():
    """Run the wallet demonstration."""
    otp = secrets.randbelow(900_000) + 100_000
    print("OTP generated:", otp)

    add_money(2000)
    add_money(500, "Card")
    add_money(-10)
    set_daily_limit(1500)

    pay_merchant("Coffee Corner", 180, "4321")
    pay_merchant("Book Store", 5000, "4321")
    pay_merchant("Grocery Mart", 350, "0000")
    pay_merchant("Pharmacy", 420, "4321")

    mini_statement()
    print("Cashback on 420:", cashback_for(420, "health"))
    print("Gateway check:", check_gateway("wrong"))
    print("Final balance: Rs.", wallet["balance"])

    credit_amounts = [
        item["amount"]
        for item in transactions
        if item["type"] == "credit"
    ]
    print("Total credited:", sum(credit_amounts))


if __name__ == "__main__":
    main()
