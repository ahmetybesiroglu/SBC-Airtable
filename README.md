Sure, here's an updated README for your public GitHub repository:

---

# SBC Options Valuation

## Overview

This project automates the valuation of stock-based compensation options using the Black-Scholes model. The process involves fetching historical stock prices to calculate volatilities, obtaining risk-free rates from treasury yields, and computing the option values based on user-provided inputs. The calculated values are stored in Airtable for easy access and management.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Setup](#setup)
  - [Virtual Environment](#virtual-environment)
  - [Dependencies](#dependencies)
  - [Environment Variables](#environment-variables)
- [Airtable Structure](#airtable-structure)
  - [Tranches Table](#tranches-table)
  - [Valuations Table](#valuations-table)
  - [Volatilities Table](#volatilities-table)
  - [Treasury Yields Table](#treasury-yields-table)
- [Running the Script](#running-the-script)
- [Additional Information](#additional-information)

## How It Works

1. **User Input**: Users input data into the Tranches table in Airtable.
2. **Valuation Association**: Users associate each valuation with a tranche, which automatically populates grant date, vest date, and expiry date.
3. **Configure Valuation Date**: After associating a tranche, users need to input the `valuation_date` manually.
4. **Volatility Calculation**: The script fetches historical stock prices for public companies and calculates volatilities.
5. **Risk-Free Rate**: The script fetches treasury yields and extrapolates them to match the expected term.
6. **Black-Scholes Model**: The script calculates the option values using the Black-Scholes formula.
7. **Data Storage**: The calculated volatilities, risk-free rates, and option values are stored back in Airtable.
8. **Recalculation Mechanism**: The script iterates over all the valuation rows that exist with all the necessary inputs and an empty `option_valuation` column. If one wants to recalculate an option, simply delete the `option_valuation` value for that entry, and the script will recompute it.

## Setup

### Virtual Environment

1. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```

### Dependencies

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables. You need to replace the placeholders with your actual Airtable API key and base/table IDs.

```ini
AIRTABLE_API_KEY=your_airtable_api_key
BASE_ID=your_base_id
TRANCHES_TABLE_ID=your_tranches_table_id
VALUATIONS_TABLE_ID=your_valuations_table_id
VOLATILITIES_TABLE_ID=your_volatilities_table_id
TREASURY_YIELDS_TABLE_ID=your_treasury_yields_table_id
```

## Airtable Structure

### Tranches Table

The Tranches table contains the following fields:

- **Tranche ID**: Auto Number
- **Grant Date**: Date (ISO 8601 formatted date)
- **Vesting Date**: Date (ISO 8601 formatted date)
- **Expiry Date**: Date (ISO 8601 formatted date)

### Valuations Table

The Valuations table contains the following fields:

- **Valuation ID**: Auto Number
- **Public Comps**: Text (Comma-separated list of public company tickers)
- **Valuation Date**: Date (ISO 8601 formatted date)
- **Stock Price**: Currency (Positive number)
- **Strike Price**: Currency (Positive number)
- **Volatility Frequency**: Single select (Daily, Weekly, Monthly)
- **Option Value**: Currency (Calculated value)
- **Expected Term**: Formula (Computed value based on Vesting Date and Expiry Date)
- **Tranche ID**: Link to another record (Array of record IDs from the Tranches table)
- **Vesting Date**: Lookup (Array of dates from linked Tranches records)
- **Expiry Date**: Lookup (Array of dates from linked Tranches records)
- **Grant Date**: Lookup (Array of dates from linked Tranches records)
- **Average Volatility**: Rollup (AVERAGE(values) from Volatilities)
- **Risk-free Rate**: Lookup (Array of yields from Treasury Yields)

### Volatilities Table

The Volatilities table contains the following fields:

- **Volatility ID**: Auto Number
- **Valuation ID**: Link to another record (Array of record IDs from the Valuations table)
- **Ticker**: Text
- **Date From**: Date (ISO 8601 formatted date)
- **Date To**: Date (ISO 8601 formatted date)
- **Volatility**: Percent

### Treasury Yields Table

The Treasury Yields table contains the following fields:

- **Yield ID**: Auto Number
- **Valuation ID**: Link to another record (Array of record IDs from the Valuations table)
- **Yield**: Percent

## Running the Script

After setting up your environment and ensuring your Airtable structure matches the described format, you can run the script using:

```bash
python run.py
```

## Additional Information

The script is designed to iterate over all valuation rows with necessary inputs and an empty `option_valuation` column. This allows for the recalculation of any option valuation by simply deleting the existing `option_valuation` value. The script will then detect the empty column and recalculate the option value based on the provided inputs. This feature ensures that the valuation data remains up-to-date and accurate. To make the process more user-friendly, start by filling out the Tranches table with grant dates, vest dates, and expiry dates. Then, associate each valuation with a tranche, and most of the necessary inputs will be populated automatically. After associating a tranche, make sure to manually input the `valuation_date`.

## Repository Link

For more information and to access the repository, visit: [SBC Options Valuation on GitHub](https://github.com/ahmetybesiroglu/SBC-Airtable)

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License.

## Contact

For further questions, please contact [ahmetybesiroglu@gmail.com](mailto:ahmetybesiroglu@gmail.com).