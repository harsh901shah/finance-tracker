#!/usr/bin/env python3
"""
Test script for dynamic transaction template system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.template_service import TemplateService
from services.database_service import DatabaseService

def test_template_system():
    """Test the template system"""
    print("🧪 Testing Dynamic Transaction Template System\n")
    
    # Initialize database
    print("1️⃣ Initializing database...")
    try:
        DatabaseService.initialize_database()
        print("   ✅ Database initialized\n")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}\n")
        return False
    
    # Initialize templates table
    print("2️⃣ Creating templates table...")
    try:
        TemplateService.initialize_templates_table()
        print("   ✅ Templates table created\n")
    except Exception as e:
        print(f"   ❌ Templates table creation failed: {e}\n")
        return False
    
    # Test user
    test_user_id = "test_user_123"
    
    # Seed default templates
    print("3️⃣ Seeding default templates...")
    try:
        TemplateService.seed_default_templates(test_user_id)
        print("   ✅ Default templates seeded\n")
    except Exception as e:
        print(f"   ❌ Seeding failed: {e}\n")
        return False
    
    # Get templates
    print("4️⃣ Retrieving templates...")
    try:
        templates = TemplateService.get_user_templates(test_user_id)
        print(f"   ✅ Found {len(templates)} templates\n")
        
        # Show first 5 templates
        print("   📋 Sample templates:")
        for template in templates[:5]:
            print(f"      {template['icon']} {template['template_name']} - {template['transaction_type']}")
        print()
    except Exception as e:
        print(f"   ❌ Retrieval failed: {e}\n")
        return False
    
    # Create custom template
    print("5️⃣ Creating custom template...")
    try:
        custom_template = {
            'template_name': 'Crypto Trading',
            'icon': '₿',
            'transaction_type': 'Investment',
            'category': 'Cryptocurrency',
            'default_amount': 1000.0,
            'default_payment_method': 'Bank Transfer',
            'fields_schema': {
                'coin_name': {
                    'type': 'select',
                    'label': 'Coin Name',
                    'required': True,
                    'options': ['Bitcoin', 'Ethereum', 'Dogecoin']
                },
                'exchange': {
                    'type': 'text',
                    'label': 'Exchange',
                    'required': True
                },
                'wallet_address': {
                    'type': 'text',
                    'label': 'Wallet Address',
                    'required': False
                }
            },
            'sort_order': 100
        }
        
        template_id = TemplateService.create_template(test_user_id, custom_template)
        if template_id:
            print(f"   ✅ Custom template created (ID: {template_id})\n")
        else:
            print("   ⚠️  Template already exists or creation failed\n")
    except Exception as e:
        print(f"   ❌ Custom template creation failed: {e}\n")
        return False
    
    # Test transaction with custom fields
    print("6️⃣ Testing transaction with custom fields...")
    try:
        from datetime import date
        
        transaction = {
            'date': date.today().strftime('%Y-%m-%d'),
            'amount': 5000.0,
            'type': 'Investment',
            'description': 'Crypto Trading - Bitcoin purchase',
            'category': 'Cryptocurrency',
            'payment_method': 'Bank Transfer',
            # Custom fields
            'coin_name': 'Bitcoin',
            'exchange': 'Coinbase',
            'wallet_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        }
        
        transaction_id = DatabaseService.add_transaction(transaction, test_user_id)
        print(f"   ✅ Transaction created (ID: {transaction_id})\n")
        
        # Retrieve and verify
        transactions = DatabaseService.get_transactions(test_user_id)
        if transactions:
            latest = transactions[0]
            print(f"   📊 Transaction details:")
            print(f"      Amount: ${latest['amount']}")
            print(f"      Category: {latest['category']}")
            if latest.get('additional_data'):
                import json
                custom_data = json.loads(latest['additional_data'])
                print(f"      Custom fields: {custom_data}")
        print()
    except Exception as e:
        print(f"   ❌ Transaction test failed: {e}\n")
        return False
    
    print("✅ All tests passed!\n")
    print("🎉 Dynamic template system is working correctly!")
    print("\n📝 Next steps:")
    print("   1. Run the app: python3 -m streamlit run finance_tracker.py")
    print("   2. Navigate to 'Add Transaction' page")
    print("   3. Click 'Create Default Templates' button")
    print("   4. Start adding transactions with custom templates!")
    
    return True

if __name__ == "__main__":
    success = test_template_system()
    sys.exit(0 if success else 1)
