# Personal Finance Tracker

A Streamlit-based personal finance tracking application that helps you manage your expenses, income, and budget.

## Features

- **Dashboard**: View your financial summary with key metrics and visualizations
- **Net Worth Summary**: Track your assets, liabilities, and overall net worth
- **Transaction Management**: Add, view, and filter your financial transactions
- **Document Upload**: Import transactions from bank statements, credit card statements, and brokerage accounts
- **Budget Planning**: Set monthly budgets by category and track your spending against them
- **Data Import/Export**: Import transactions from CSV files and export your data

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd finance-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run finance_tracker.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

## Data Security

This application stores all your financial data locally on your machine. No data is sent to external servers.

- Database file: `finance_tracker.db` (not included in the repository)
- Configuration: Create a `config.yaml` file for your settings (see `config.example.yaml`)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.