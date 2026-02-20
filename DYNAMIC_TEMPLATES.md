# Dynamic Transaction Template System

## 🎯 Overview

The Dynamic Transaction Template System allows users to create **unlimited custom transaction types** with their own fields, categories, and validation rules. This is a **market-differentiating feature** that no other finance tracker offers.

## ✨ Key Features

### 1. **Unlimited Custom Categories**
- Create 1, 10, 30, 100+ transaction types
- No hardcoded limits
- Fully user-controlled

### 2. **Custom Fields Per Transaction**
- Add any fields you need: text, numbers, dropdowns, dates
- Track data points that matter to YOU
- Required/optional field validation

### 3. **Zero Code Changes**
- All customization happens in the UI
- No database schema changes needed
- JSON-based flexible storage

### 4. **Real-World Use Cases**

#### Crypto Investor
```
Template: "Crypto Trading"
Fields:
  - Coin Name (dropdown): Bitcoin, Ethereum, Dogecoin
  - Exchange (text): Coinbase, Binance, etc.
  - Wallet Address (text): Your wallet
  - Transaction Hash (text): Blockchain reference
```

#### Pet Owner (3 Dogs)
```
Template: "Pet - Max"
Fields:
  - Vet Name (text)
  - Service Type (dropdown): Grooming, Vet Visit, Food
  - Next Appointment (date)
  - Weight (number)
```

#### Real Estate Investor
```
Template: "Property - 123 Main St"
Fields:
  - Tenant Name (text)
  - Lease End Date (date)
  - Maintenance Type (dropdown)
  - Property Manager (text)
```

#### Freelancer
```
Template: "Client - Acme Corp"
Fields:
  - Project Name (text)
  - Invoice Number (text)
  - Payment Terms (dropdown): Net 30, Net 60
  - Hours Worked (number)
```

## 🏗️ Architecture

### Database Schema

#### `transaction_templates` Table
```sql
CREATE TABLE transaction_templates (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    template_name TEXT NOT NULL,
    icon TEXT DEFAULT '💰',
    transaction_type TEXT NOT NULL,
    category TEXT NOT NULL,
    default_amount REAL DEFAULT 0.0,
    default_payment_method TEXT DEFAULT 'Bank Transfer',
    fields_schema TEXT,  -- JSON: {"field_name": {"type": "text", "required": true}}
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, template_name)
)
```

#### `transactions` Table (Enhanced)
```sql
-- Existing columns remain unchanged
-- New column added:
custom_fields TEXT  -- JSON: {"coin_name": "Bitcoin", "exchange": "Coinbase"}
```

### JSON Schema Pattern

**Template Definition:**
```json
{
  "template_name": "Crypto Trading",
  "icon": "₿",
  "transaction_type": "Investment",
  "category": "Cryptocurrency",
  "default_amount": 1000.0,
  "fields_schema": {
    "coin_name": {
      "type": "select",
      "label": "Coin Name",
      "required": true,
      "options": ["Bitcoin", "Ethereum", "Dogecoin"]
    },
    "exchange": {
      "type": "text",
      "label": "Exchange",
      "required": true
    },
    "wallet_address": {
      "type": "text",
      "label": "Wallet Address",
      "required": false
    }
  }
}
```

**Transaction with Custom Fields:**
```json
{
  "date": "2026-02-17",
  "amount": 5000.0,
  "type": "Investment",
  "category": "Cryptocurrency",
  "description": "Crypto Trading - Bitcoin purchase",
  "payment_method": "Bank Transfer",
  "custom_fields": {
    "coin_name": "Bitcoin",
    "exchange": "Coinbase",
    "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
  }
}
```

## 📁 File Structure

```
finance-tracker/
├── services/
│   └── template_service.py          # Template CRUD operations
├── components/
│   └── dynamic_form_builder.py      # Renders forms from templates
├── pages/
│   ├── add_transaction_page_v2.py   # New dynamic add transaction page
│   └── template_manager_page.py     # Template management UI
└── test_templates.py                # Test suite
```

## 🚀 Usage

### For Users

#### 1. Create Templates
1. Navigate to **"Manage Templates"** in sidebar
2. Click **"Create New"** tab
3. Fill in template details:
   - Name: "Crypto Trading"
   - Icon: ₿
   - Type: Investment
   - Category: Cryptocurrency
4. Add custom fields (optional)
5. Click **"Create Template"**

#### 2. Use Templates
1. Navigate to **"Add Transaction"**
2. Click on your custom template button
3. Fill in the form (including custom fields)
4. Click **"Add"**

#### 3. Manage Templates
- **Activate/Deactivate**: Hide templates without deleting
- **Delete**: Remove templates permanently
- **Edit**: Update template details (coming soon)

### For Developers

#### Create Template Programmatically
```python
from services.template_service import TemplateService

template_data = {
    'template_name': 'Crypto Trading',
    'icon': '₿',
    'transaction_type': 'Investment',
    'category': 'Cryptocurrency',
    'default_amount': 1000.0,
    'fields_schema': {
        'coin_name': {
            'type': 'select',
            'options': ['Bitcoin', 'Ethereum'],
            'required': True
        }
    }
}

template_id = TemplateService.create_template(user_id, template_data)
```

#### Add Transaction with Custom Fields
```python
from services.database_service import DatabaseService

transaction = {
    'date': '2026-02-17',
    'amount': 5000.0,
    'type': 'Investment',
    'category': 'Cryptocurrency',
    'description': 'Bitcoin purchase',
    'payment_method': 'Bank Transfer',
    # Custom fields - automatically stored in additional_data
    'coin_name': 'Bitcoin',
    'exchange': 'Coinbase'
}

transaction_id = DatabaseService.add_transaction(transaction, user_id)
```

## 🧪 Testing

Run the test suite:
```bash
python3 test_templates.py
```

Expected output:
```
✅ All tests passed!
🎉 Dynamic template system is working correctly!
```

## 🎨 Supported Field Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Single-line text input | Name, Address |
| `number` | Numeric input | Amount, Quantity |
| `select` | Dropdown menu | Coin Name, Category |
| `date` | Date picker | Due Date, Appointment |

## 🔒 Security

- **User Isolation**: Templates are user-specific
- **SQL Injection Protection**: Parameterized queries
- **JSON Validation**: Schema validation on save
- **XSS Protection**: Input sanitization

## 📊 Performance

- **Fast Queries**: Indexed by user_id
- **Efficient Storage**: JSON compression
- **Lazy Loading**: Templates loaded on-demand
- **Caching**: Template cache per user session

## 🚧 Future Enhancements

1. **Template Sharing**: Share templates with other users
2. **Template Marketplace**: Browse community templates
3. **Advanced Validation**: Regex patterns, min/max values
4. **Conditional Fields**: Show fields based on other field values
5. **Template Import/Export**: Backup and restore templates
6. **Template Analytics**: Track which templates are used most

## 🎯 Competitive Advantage

### What Other Apps Offer
- ❌ Fixed 10-15 categories
- ❌ Can only rename categories
- ❌ No custom fields
- ❌ One-size-fits-all approach

### What We Offer
- ✅ Unlimited categories
- ✅ Custom fields per category
- ✅ Full customization
- ✅ Adapts to user's life

## 📈 Marketing Angle

> "The only finance tracker that adapts to YOUR life. Track crypto wallets, rental properties, pet expenses, client invoices - anything. Create unlimited custom categories with the exact fields YOU need."

## 🐛 Known Issues

None currently. System is production-ready.

## 📞 Support

For issues or questions:
- GitHub Issues: [finance-tracker/issues](https://github.com/harsh901shah/finance-tracker/issues)
- Email: support@financetracker.com

## 📝 Changelog

### v2.0.0 (2026-02-17)
- ✨ Initial release of dynamic template system
- ✨ 26 default templates seeded
- ✨ Custom field support (text, number, select, date)
- ✨ Template manager UI
- ✨ Dynamic form builder
- ✨ Full test coverage

---

**Built with ❤️ for power users who demand flexibility**
