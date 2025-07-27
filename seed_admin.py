#!/usr/bin/env python3
"""
Seed script to create a SysAdmin user in the SHIELD backend.

Usage:
    python seed_admin.py --email admin@example.com --name "Admin User"
    python seed_admin.py --email admin@example.com --name "Admin User" --force
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the app directory
load_dotenv(dotenv_path=Path(__file__).parent / "app" / ".env")

# Add the project root to Python path to allow absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.userClient import UserClient
from app.models.user import User


def seed_admin_user(email: str, fullname: str, force: bool = False) -> bool:
    """
    Seed a SysAdmin user in the database.
    
    Args:
        email: Admin user email
        fullname: Admin user full name
        force: If True, update existing user. If False, fail if user exists.
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize the user client
        client = UserClient()
        
        # Check if user already exists
        existing_user = client.get_by_email(email)
        
        if existing_user:
            if not force:
                print(f"❌ User with email '{email}' already exists!")
                print(f"   Current user: {existing_user.fullname} (Role: {existing_user.role})")
                print("   Use --force to update the existing user to SysAdmin.")
                return False
            else:
                print(f"🔄 Updating existing user '{email}' to SysAdmin...")
                # Update existing user to SysAdmin
                updated_user = client.update(existing_user.id, {
                    "fullname": fullname,
                    "role": "SysAdmin",
                    "namespaces": ["*"],  # Full system access
                    "status": "active"
                })
                
                if updated_user:
                    print(f"✅ Successfully updated user to SysAdmin!")
                    print(f"   ID: {updated_user.id}")
                    print(f"   Email: {updated_user.email}")
                    print(f"   Name: {updated_user.fullname}")
                    print(f"   Role: {updated_user.role}")
                    print(f"   Namespaces: {updated_user.namespaces}")
                    return True
                else:
                    print(f"❌ Failed to update user!")
                    return False
        else:
            print(f"🚀 Creating new SysAdmin user...")
            
            # Create new admin user
            user_data = {
                "email": email,
                "fullname": fullname,
                "role": "SysAdmin",
                "namespaces": ["*"]  # Full system access for SysAdmin
            }
            
            new_user = client.create(user_data)
            
            print(f"✅ Successfully created SysAdmin user!")
            print(f"   ID: {new_user.id}")
            print(f"   Email: {new_user.email}")
            print(f"   Name: {new_user.fullname}")
            print(f"   Role: {new_user.role}")
            print(f"   Namespaces: {new_user.namespaces}")
            print(f"   Status: {new_user.status}")
            print(f"   Created: {new_user.createdAt}")
            return True
            
    except Exception as e:
        print(f"❌ Error seeding admin user: {str(e)}")
        return False


def main():
    """Main function to handle command line arguments and seed admin user."""
    parser = argparse.ArgumentParser(
        description="Seed a SysAdmin user in the SHIELD backend database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new admin user
  python seed_admin.py --email admin@shield.com --name "System Administrator"
  
  # Update existing user to admin (if email already exists)
  python seed_admin.py --email existing@shield.com --name "Admin User" --force
  
  # Interactive mode
  python seed_admin.py
        """
    )
    
    parser.add_argument(
        "--email",
        type=str,
        help="Email address for the admin user"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        help="Full name for the admin user"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Update existing user if email already exists"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, run in interactive mode
    if not args.email or not args.name:
        print("🛡️  SHIELD Backend - Admin User Seeder")
        print("=====================================\n")
        
        if not args.email:
            email = input("Enter admin email address: ").strip()
        else:
            email = args.email
            
        if not args.name:
            name = input("Enter admin full name: ").strip()
        else:
            name = args.name
        
        if not email or not name:
            print("❌ Email and name are required!")
            sys.exit(1)
    else:
        email = args.email
        name = args.name
    
    # Validate email format (basic check)
    if "@" not in email or "." not in email:
        print("❌ Please provide a valid email address!")
        sys.exit(1)
    
    if len(name.strip()) < 2:
        print("❌ Name must be at least 2 characters long!")
        sys.exit(1)
    
    print(f"\n📝 Creating SysAdmin user:")
    print(f"   Email: {email}")
    print(f"   Name: {name}")
    print(f"   Force update: {args.force}")
    print()
    
    # Seed the admin user
    success = seed_admin_user(email, name, args.force)
    
    if success:
        print(f"\n🎉 Admin user seeding completed successfully!")
        print(f"\n📋 Next steps:")
        print(f"   1. The user can now log in with email: {email}")
        print(f"   2. Set up authentication/password system if not already configured")
        print(f"   3. The user has full system access with role 'SysAdmin'")
        sys.exit(0)
    else:
        print(f"\n💥 Admin user seeding failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
