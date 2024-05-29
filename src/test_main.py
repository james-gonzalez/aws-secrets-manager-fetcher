"""
Test module for main.py
"""

from unittest.mock import patch
import pytest
from moto import mock_secretsmanager
import boto3
from main import fetch_secret, list_all_secrets, write_to_file, clear_screen, main

# Helper function to create a secret in the mock Secrets Manager
def create_secret(client, name, secret):
    client.create_secret(
        Name=name,
        SecretString=json.dumps(secret) if isinstance(secret, dict) else secret
    )

@mock_secretsmanager
def test_fetch_secret():
    """
    Test fetching a secret from AWS Secrets Manager.
    """
    region_name = "us-west-2"
    secret_name = "test_secret"
    secret_value = {"username": "test_user", "password": "test_pass"}

    client = boto3.client("secretsmanager", region_name=region_name)
    create_secret(client, secret_name, secret_value)

    fetched_secret = fetch_secret(secret_name, region_name)
    assert json.loads(fetched_secret) == secret_value

@mock_secretsmanager
def test_list_all_secrets():
    """
    Test listing all secrets from AWS Secrets Manager.
    """
    region_name = "us-west-2"
    secret_names = ["secret1", "secret2", "secret3"]

    client = boto3.client("secretsmanager", region_name=region_name)
    for name in secret_names:
        create_secret(client, name, {"key": "value"})

    listed_secrets = list_all_secrets(region_name)
    assert set(listed_secrets) == set(secret_names)

def test_write_to_file(tmp_path):
    """
    Test writing a secret to a file.
    """
    secret_value = "test_secret_value"
    output_file = tmp_path / "output.txt"

    write_to_file(secret_value, output_file)
    with open(output_file, "r", encoding="utf-8") as file:
        assert file.read() == secret_value

def test_clear_screen():
    """
    Test clearing the terminal screen.
    """
    # This is a simple test to check if the clear_screen function runs without errors.
    try:
        clear_screen()
    except Exception as e:
        pytest.fail(f"clear_screen raised an exception: {e}")

@patch("builtins.input", side_effect=["us-west-2", "1", "\n"])
@patch("builtins.print")
@patch("main.list_all_secrets", return_value=["test_secret"])
@patch("main.fetch_secret", return_value='{"username": "test_user", "password": "test_pass"}')
@patch("main.clear_screen")
def test_main(mock_clear_screen, mock_fetch_secret, mock_list_all_secrets, mock_print):
    """
    Test the main function.
    """
    main()
    mock_list_all_secrets.assert_called_once_with("us-west-2")
    mock_fetch_secret.assert_called_once_with("test_secret", "us-west-2")
    mock_print.assert_any_call("Available Secrets:")
    mock_print.assert_any_call("Fetched Secret Value:")
    mock_clear_screen.assert_called_once()

if __name__ == "__main__":
    pytest.main()
