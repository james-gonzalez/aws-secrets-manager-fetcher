"""Module imports."""

import os
import json
import argparse
import boto3
import botocore


def fetch_secret(secret_name, region_name):
    """
    Fetches the secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name of the secret.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        str: The secret value as a string, or None if the secret is not found.
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_value = response["SecretString"]
        return secret_value
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"ERROR: Secret '{secret_name}' not found.")
        else:
            print(
                f"ERROR: An error occurred while fetching secret '{secret_name}': {e}"
            )
        return None


def list_all_secrets(region_name):
    """
    Lists all secrets available in AWS Secrets Manager for a given region.

    Args:
        region_name (str): The AWS region to list secrets from.

    Returns:
        list: A list of secret names.
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    secrets = []
    paginator = client.get_paginator("list_secrets")
    for page in paginator.paginate():
        secrets.extend(page["SecretList"])

    secret_names = [secret["Name"] for secret in secrets]
    return secret_names


def clear_screen():
    """
    Clears the terminal screen.
    """
    if os.name == "nt":  # For Windows
        os.system("cls")
    else:  # For Unix-based systems
        os.system("clear")


def write_to_file(secret_value, output_file):
    """
    Writes the secret value to a file.

    Args:
        secret_value (str): The secret value to write to the file.
        output_file (str): The path to the output file.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(secret_value)


def main():
    """
    Main function to execute the script. It fetches a secret from AWS Secrets Manager
    and either prints it to the screen or writes it to a file based on the provided arguments.
    """
    parser = argparse.ArgumentParser(
        description="Fetch secret from AWS Secrets Manager"
    )
    parser.add_argument("--output", help="Output file to write the secret value")
    args = parser.parse_args()

    region_name = os.getenv("AWS_DEFAULT_REGION")

    if not region_name:
        region_name = input("Enter the Region Name: ")

    secret_names = list_all_secrets(region_name)
    print("Available Secrets:")
    for idx, name in enumerate(secret_names):
        print(f"{idx + 1}. {name}")

    secret_idx = int(input("Enter the number of the secret you want to fetch: ")) - 1
    secret_name = secret_names[secret_idx]

    secret_value = fetch_secret(secret_name, region_name)

    if secret_value is not None:
        if args.output:
            write_to_file(secret_value, args.output)
            print(f"Secret value fetched and stored in {args.output} successfully.")
        else:
            try:
                secret_dict = json.loads(secret_value)
                pretty_secret = json.dumps(secret_dict, indent=4)
                print("\nFetched Secret Value:")
                print(pretty_secret)
            except json.JSONDecodeError:
                print("\nFetched Secret Value:")
                print(secret_value)

            input("\nPress Enter to clear the screen...")
            clear_screen()
    else:
        print("Exiting program.")

if __name__ == "__main__":
    main()
