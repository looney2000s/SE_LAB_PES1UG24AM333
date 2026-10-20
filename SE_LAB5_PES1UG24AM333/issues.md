| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Hard-coded gateway secret | Security | 6 | Gateway secret is hard-coded in the source code, which may expose sensitive credentials. | Read the gateway secret from an environment variable instead of storing it directly in the source code. |
| Hard-coded wallet PIN | Security | 7 | Wallet PIN is hard-coded in the source code. | Read the wallet PIN from an environment variable. |
| Weak SHA-1 hashing | Security | 14 | SHA-1 is not suitable for securely storing PIN hashes. | Replace SHA-1 with PBKDF2-HMAC-SHA256 using a salt and an appropriate iteration count. |
| Insecure temporary file creation | Security | 60 | `tempfile.mktemp()` can introduce a race condition when creating temporary files. | Use `tempfile.NamedTemporaryFile()` to create the temporary file securely. |
| Insecure OTP generation | Security | 64 | `random.randint()` uses a pseudo-random generator unsuitable for security-sensitive OTPs. | Use the `secrets` module to generate a cryptographically secure OTP. |
| Mutable default argument | Bug | 17 | `log=[]` creates a shared list that can retain values between function calls. | Change the default to `None` and initialize a new list inside the function. |
| Missing module docstring | Code quality | 1 | The Python module does not have a docstring describing its purpose. | Add a module-level docstring. |
| Missing function docstrings | Code quality | 13, 17, 27, 32, 45, 50, 54, 58, 63 | Functions lack docstrings explaining their purposes. | Add descriptive docstrings to the functions. |
| Non-standard function and variable names | Code quality | 9, 13, 17, 27, 32, 45, 50, 54, 58, 78 | Several names do not follow Pylint's recommended naming conventions. | Rename functions and variables using snake_case and constants using UPPER_CASE where appropriate. |
| Global statement | Code quality | 28 | `setDailyLimit()` modifies a global variable using the `global` statement. | Store the daily limit in the wallet data structure to avoid modifying a separate global variable. |
| Unused function argument | Code quality | 50 | `merchantType` is accepted by `cashbackFor()` but is not used. | Rename it to `_merchant_type` to indicate that it is intentionally unused, or remove it if the function interface permits. |
| Flake8 inline comment spacing | Style | 76 | The inline comment does not have the required spacing before `#`. | Add at least two spaces before the inline comment. |
| Flake8 operator spacing | Style | 78 | The list comprehension assignment lacks whitespace around `=`. | Add spaces around the assignment operator. |
| Flake8 comma spacing | Style | 79 | The `sum()` call lacks a space after the comma in the surrounding expression. | Add the required whitespace after the comma. |
| Flake8 blank lines | 80 | Style | The file does not have the required blank lines after the function definition. | Add the appropriate blank lines and place the program entry point under an `if __name__ == "__main__":` guard. |