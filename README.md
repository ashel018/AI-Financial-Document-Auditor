# AI Financial Document Auditor

A Streamlit-based application for intelligent invoice validation and fraud detection.

## Features

### 3 Data Input Methods

1. **Generate Sample Invoice** - Create test invoices with varying difficulty levels
   - Easy: May have missing fields
   - Medium: May have calculation errors
   - Hard: May have fake vendors

2. **Upload JSON File** - Upload real invoice data
   - Supports standard JSON format
   - Sample files included: `sample_invoice.json`, `sample_invoice_fraud.json`

3. **Manual Entry** - Create invoices through an interactive form
   - Field-by-field data entry
   - Multiple line items support
   - Real-time total calculation

### Audit Analysis

The AI auditor performs:
- ✓ Required field validation
- ✓ Mathematical verification
- ✓ Vendor verification
- ✓ Fraud score calculation
- ✓ Risk level assessment

## Quick Start

1. Run the app:
   ```bash
   python -m streamlit run app.py
   ```

2. Open in browser:
   ```
   http://127.0.0.1:8501
   ```

3. Choose a data input method and run the audit

## Sample Invoice Formats

### Valid Invoice (`sample_invoice.json`)
```json
{
  "invoice_id": "INV-2024-001",
  "vendor": "Tech Solutions Ltd",
  "date": "2024-02-15",
  "items": [...],
  "subtotal": 360000,
  "tax": 64800,
  "total": 424800
}
```

### Fraudulent Invoice (`sample_invoice_fraud.json`)
- Contains fake vendor ("Fake Inc")
- Has calculation errors
- Shows suspicious patterns

## Usage Scenarios

### Demo Mode
- Use "Generate Sample" with different difficulties
- Shows how the audit catches various issues
- Perfect for presentations

### Testing Mode
- Upload `sample_invoice.json` to test valid invoice
- Upload `sample_invoice_fraud.json` to test fraud detection
- Demonstrates system accuracy

### Production Mode
- Manually enter invoice details
- Upload real invoices via JSON
- Review detailed audit findings

## Audit Scoring

- **Low Risk** (0-20%): All clear
- **Medium Risk** (20-50%): Minor issues, review recommended
- **High Risk** (50%+): Significant concerns, manual verification required

## Requirements

- Python 3.8+
- streamlit
- json (built-in)
- uuid (built-in)
- random (built-in)

## Installation

```bash
pip install streamlit
```

## File Structure

```
financial_auditor/
├── app.py                          # Main application
├── requirements.txt                # Dependencies
├── sample_invoice.json             # Valid invoice example
├── sample_invoice_fraud.json       # Fraudulent invoice example
└── README.md                       # This file
```

## API Reference

### generate_invoice(difficulty)
Generates test invoices with optional errors based on difficulty level.

**Parameters:**
- `difficulty` (str): 'easy', 'medium', or 'hard'

**Returns:**
- dict: Invoice object

### audit_invoice(invoice)
Performs comprehensive audit on invoice data.

**Parameters:**
- `invoice` (dict): Invoice object with standard fields

**Returns:**
- tuple: (steps, score, decision)
  - steps (list): Audit steps performed
  - score (float): Fraud score 0.0-1.0
  - decision (str): 'Valid Invoice' or 'Fraud Detected'

## Tips for Best Results

1. **For Demos**: Generate samples - they're safe and show all audit features
2. **For Testing**: Use included sample JSON files
3. **For Production**: Manual entry with careful data validation
4. **Field Validation**: Ensure dates are properly formatted
5. **Tax Calculation**: System assumes 18% tax rate

## Troubleshooting

**Blank page appears**
- Refresh the browser (Ctrl+F5)
- Clear browser cache
- Try a different browser

**Upload fails**
- Verify JSON format is valid
- Check file encoding (UTF-8)
- Try sample files first

**Audit not loading**
- Refresh the page
- Restart Streamlit: `python -m streamlit run app.py`

## Future Enhancements

- Machine learning model for fraud detection
- OCR for invoice scanning
- Database integration for invoice history
- API endpoints for integration
- Batch processing mode
- Export audit reports

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, contact support or check the documentation.
