# Credentials Tester

A modular script for testing various types of credentials. Each credential type is handled by its own module, making it easy to extend and maintain.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
  - [Testing AWS Credentials](#testing-aws-credentials)
  - [Testing OpenRouter Credentials](#testing-openrouter-credentials)
  - [Help for Specific Credential Types](#help-for-specific-credential-types)
- [Extending with New Modules](#extending-with-new-modules)
- [Virtual Environment (Optional)](#virtual-environment-optional)
- [Dependencies](#dependencies)
- [License](#license)

---

## Overview

The Credentials Tester is a command-line tool designed to verify the validity of different types of credentials. It is modular in design, allowing you to add support for new credential types by simply creating a new module.

## Features

- **Modular Design**: Each credential type is implemented as a separate module.
- **Dynamic Loading**: Modules are automatically loaded based on the credential type provided.
- **Specific Help Messages**: Each module provides its own help messages and command-line arguments.
- **Easy to Extend**: Adding support for new credential types is straightforward.

## Prerequisites

- **Python 3.6 or higher**: Ensure that Python is installed on your system.
- **pip**: Python package manager for installing dependencies.

## Installation

1. **Clone the Repository**

   ```bash
   git clone git@gitlab.com:mangopay/appsec/pocs/cred_tester.git
   cd cred_tester
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, install `boto3` manually:

   ```bash
   pip install boto3
   ```

## Directory Structure

```
cred_tester/
├── cred_tester.py       # Main script
├── README.md            # This file
└── modules/
    ├── __init__.py      # Makes 'modules' a Python package
    ├── aws.py           # AWS credentials testing module
    └── openrouter.py    # OpenRouter credentials testing module
```

- **cred_tester.py**: The main entry point of the script.
- **modules/**: Directory containing credential testing modules.
  - **aws.py**: Module for testing AWS credentials.
  - **\_\_init\_\_.py**: Empty file to mark the directory as a Python package.

## Usage

Run the main script followed by the credential type and the required arguments for that type.

```bash
python cred_tester.py <credential_type> [arguments]
```

### Testing AWS Credentials

To test AWS credentials, use the `aws` credential type followed by your AWS Access Key ID and Secret Access Key. An optional session token can be provided.

### Testing OpenRouter Credentials

To test OpenRouter credentials, use the `openrouter` credential type followed by your API key.

**Syntax:**

```bash
python cred_tester.py openrouter <api_key>
```

**Example:**

```bash
python cred_tester.py openrouter sk-or-v1-abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
```

When successful, the script will display a list of available models on your OpenRouter account.

**Syntax:**

```bash
python cred_tester.py aws <access_key> <secret_key> [--session_token <session_token>]
```

**Example:**

```bash
python cred_tester.py aws ABCDEFGHIJKLMNOPQRST abcdefghijklmnopqrstuvwxyz0123456789
```

**With Session Token:**

```bash
python cred_tester.py aws ABCDEFGHIJKLMNOPQRST abcdefghijklmnopqrstuvwxyz0123456789 --session_token EXAMPLE_SESSION_TOKEN
```

### Help for Specific Credential Types

To get help for a specific credential type, use the `-h` or `--help` flag after specifying the credential type.

**Example:**

```bash
python cred_tester.py aws -h
```

**Output:**

```
usage: cred_tester.py aws [-h] [--session_token SESSION_TOKEN] access_key secret_key

AWS Credentials Tester

positional arguments:
  access_key            AWS Access Key ID
  secret_key            AWS Secret Access Key

optional arguments:
  -h, --help            show this help message and exit
  --session_token SESSION_TOKEN
                        AWS Session Token (Optional)
```

## Extending with New Modules

To add support for a new credential type:

1. **Create a New Module File**

   In the `modules/` directory, create a new file named after your credential type, e.g., `gcp.py` for Google Cloud Platform.

2. **Implement Required Functions**

   Your module must implement the following two functions:

   - `add_arguments(parser)`: Define the command-line arguments specific to this credential type.
   - `test_credentials(args)`: Implement the logic to test the credentials.

   **Example `modules/gcp.py`:**

   ```python
   def add_arguments(parser):
       parser.add_argument('service_account_key', type=str, help='GCP Service Account Key File')

   def test_credentials(args):
       # Implement GCP credentials testing logic here
       pass
   ```

3. **Ensure `__init__.py` is Present**

   The `modules/` directory must contain an `__init__.py` file.

4. **Usage**

   You can now use your new module:

   ```bash
   python cred_tester.py gcp <service_account_key>
   ```

## Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies.

1. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**

   - **On macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

   - **On Windows:**

     ```bash
     venv\Scripts\activate
     ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Dependencies

- **Python 3.6 or higher**
- **boto3**: AWS SDK for Python (for AWS credentials)
- **requests**: HTTP library (for OpenRouter and other HTTP-based APIs)

Install all dependencies using:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.

---

**Note:** Replace `yourusername` in the git clone URL with your actual GitHub username if you're hosting the project on GitHub. Ensure that all sensitive information, such as actual AWS credentials, is never committed to version control or shared publicly.
