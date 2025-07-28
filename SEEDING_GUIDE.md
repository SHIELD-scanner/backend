# Admin User Seeding Guide

This document explains how to seed an admin user (SysAdmin) in the SHIELD backend database.

## Quick Start

### Option 1: Using Makefile (Recommended)

```bash
# Seed a new admin user
make seed-admin EMAIL=admin@shield.com NAME="System Administrator"

# Update an existing user to admin (if email already exists)
make seed-admin EMAIL=existing@shield.com NAME="Admin User" FORCE=true

# Interactive mode (prompts for email and name)
make seed-admin-interactive
```

### Option 2: Direct Script Usage

```bash
# Using the virtual environment Python
./.venv/bin/python seed_admin.py --email admin@shield.com --name "System Administrator"

# With force update (if user already exists)
./.venv/bin/python seed_admin.py --email existing@shield.com --name "Admin User" --force

# Interactive mode
./.venv/bin/python seed_admin.py
```

## What the Script Does

1. **Creates a new SysAdmin user** with:
   - Email address (must be unique)
   - Full name
   - Role: "SysAdmin"
   - Namespaces: ["*"] (full system access)
   - Status: "active"

2. **Handles existing users**:
   - Without `--force`: Fails if email already exists
   - With `--force`: Updates existing user to SysAdmin role

## SysAdmin Permissions

The seeded SysAdmin user will have:
- **Full system access** (namespaces: ["*"])
- **All permissions** including:
  - `users:*` - Full user management
  - `clusters:*` - All cluster access
  - `namespaces:*` - All namespace access
  - `system:*` - System administration
  - `vulnerabilities:*` - Vulnerability management
  - `sbom:*` - SBOM management
  - `secrets:*` - Secret management

## Examples

### Create First Admin User
```bash
make seed-admin EMAIL=admin@shield.com NAME="System Administrator"
```

### Update Existing User to Admin
```bash
make seed-admin EMAIL=developer@shield.com NAME="John Doe" FORCE=true
```

### Interactive Mode
```bash
make seed-admin-interactive
```

## Prerequisites

1. **MongoDB Connection**: Ensure your MongoDB is running and accessible
2. **Environment Variables**: Set up your `.env` file with MongoDB connection details:
   ```bash
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=shield
   ```
3. **Virtual Environment**: Activate your Python virtual environment

## Troubleshooting

### Common Issues

1. **"User already exists" error**:
   - Use `FORCE=true` to update the existing user
   - Or use a different email address

2. **MongoDB connection error**:
   - Check if MongoDB is running
   - Verify connection string in `.env` file
   - Ensure database permissions

3. **Import errors**:
   - Ensure you're running from the project root directory
   - Check that the virtual environment is activated

### Validation

After seeding, you can verify the user was created by:

1. **Checking the database directly**:
   ```bash
   # Connect to MongoDB and check the users collection
   db.users.find({"role": "SysAdmin"})
   ```

2. **Using the API** (if running):
   ```bash
   curl http://localhost:8000/users/roles
   curl http://localhost:8000/users
   ```

## Security Notes

- **Production Use**: In production, ensure proper authentication/password systems are in place
- **Email Validation**: Use corporate email addresses for admin users
- **Access Control**: Regularly audit SysAdmin users and their access
- **Environment Security**: Protect your `.env` files and MongoDB access credentials
