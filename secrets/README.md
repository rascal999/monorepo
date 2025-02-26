# Encrypted Secrets Management

This directory contains encrypted secrets managed by git-crypt. All files in this directory (except this README and .gitattributes) are automatically encrypted when committed and decrypted when checked out by authorized users.

## Directory Structure

```
secrets/
├── environments/
│   ├── development/
│   ├── staging/
│   └── production/
└── .gitattributes
```

## Setup for New Team Members

1. Ensure git-crypt is installed (automatically included in NixOS configuration)
2. Ensure GPG agent is running properly:
   ```bash
   # Kill existing GPG agent if any
   gpgconf --kill gpg-agent
   # Start a new agent
   gpg-agent --daemon
   ```

3. Generate a GPG key pair if you don't have one:
   ```bash
   # First verify pinentry is working
   pinentry
   # Should respond with "OK Pleased to meet you"
   
   # Then generate the key
   gpg --full-generate-key
   ```
   When prompted:
   - Choose (9) ECC (sign and encrypt)
   - Select Curve 25519
   - Set validity period (e.g., 2y for 2 years)
   - Enter your name and email
   - Set a secure passphrase when prompted by pinentry
   
   Note: You may need to move your mouse or type to generate entropy during key generation.
   If you encounter any pinentry issues, try running `gpg --full-generate-key` in a new terminal session.

3. Export your public key and share it with a repository admin:
   ```bash
   gpg --armor --export your.email@domain.com > pubkey.asc
   ```
4. After an admin has added your key, clone/pull the repository and unlock:
   ```bash
   git-crypt unlock
   ```

## For Administrators

### Adding a New Team Member
```bash
# Import their public key
gpg --import their-pubkey.asc

# Add them to git-crypt
git-crypt add-gpg-user their-key-id
```

### Initial Repository Setup (Already Done)
```bash
# Initialize git-crypt
git-crypt init

# Configure encryption rules (.gitattributes)
* filter=git-crypt diff=git-crypt
.gitattributes !filter !diff
README.md !filter !diff
```

## Best Practices

1. Keep different types of secrets in separate files
2. Use clear, descriptive filenames
3. Include comments in secret files explaining their purpose
4. Regularly rotate sensitive credentials
5. Keep the access list up to date

## Emergency Procedures

If a key is compromised:
1. Immediately rotate all affected secrets
2. Re-initialize git-crypt with a new key
3. Re-add all authorized users
4. Update all affected systems with new secrets

## Verification

To verify encryption is working:
1. Add a test secret
2. Commit the change
3. Check the file contents in the repository (should be encrypted)
4. Another authorized user should be able to decrypt and read the file