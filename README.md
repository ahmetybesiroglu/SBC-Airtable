# SBC Options Valuation

## Overview

This project automates the valuation of stock-based compensation (SBC) options using the Black-Scholes model. The script interacts with Airtable for data management, fetching historical stock prices for volatility calculations, and treasury yields for determining risk-free rates. The entire process—from data input to valuation calculation—is streamlined within Airtable. The calculated values are stored back in Airtable for easy management and future reference.

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
  - [Public Comp Set Table](#public-comp-set-table)
  - [Treasury Yields Table](#treasury-yields-table)
- [Running the Script](#running-the-script)
- [Additional Information](#additional-information)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## How It Works

1. **User Input**: Users input data into the Tranches table in Airtable.
2. **Valuation Association**: Users associate each valuation with a tranche, which automatically populates grant date, vest date, and expiry date.
3. **Configure Valuation Date**: After associating a tranche, users need to input the `valuation_date` manually.
4. **Volatility Calculation**: The script fetches historical stock prices for public companies and calculates volatilities based on the selected frequency (daily, weekly, or monthly).
5. **Risk-Free Rate**: The script fetches treasury yields and extrapolates them to match the expected term using predefined yield curves.
6. **Black-Scholes Model**: The script calculates the option values using the Black-Scholes formula.
7. **Data Storage**: The calculated volatilities, risk-free rates, and option values are stored back in Airtable.
8. **Recalculation Mechanism**: The script iterates over all valuation rows with empty `option_value` fields and calculates the value. If a recalculation is needed, delete the `option_value` for that entry, and the script will recompute it.

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

Create a `.env` file in the root directory of your project and add the following environment variables. Replace the placeholders with your actual Airtable API key and table IDs.

```ini
AIRTABLE_API_KEY=your_airtable_api_key
BASE_ID=your_base_id
TRANCHES_TABLE_ID=your_tranches_table_id
OPTION_VALUATIONS_TABLE_ID=your_valuations_table_id
VOLATILITY_DATA_TABLE_ID=your_volatility_data_table_id
PUBLIC_COMP_SET_TABLE_ID=your_public_comp_set_table_id
```

## Airtable Structure

### Tranches Table

The Tranches table contains the following fields:

- **Tranche ID**: Auto Number
- **Grant Date**: Date (ISO 8601 format)
- **Vesting Date**: Date (ISO 8601 format)
- **Expiry Date**: Date (ISO 8601 format)

### Valuations Table

The Valuations table contains the following fields:

- **Valuation ID**: Auto Number
- **Public Comp Set**: Link to another record (Array of record IDs from the Public Comp Set table)
- **Valuation Date**: Date (ISO 8601 format)
- **Stock Price**: Currency (Positive number)
- **Strike Price**: Currency (Positive number)
- **Volatility Frequency**: Single select (Daily, Weekly, Monthly)
- **Option Value**: Currency (Calculated value)
- **Expected Term**: Formula (Computed based on Vesting Date and Expiry Date)
- **Tranche ID**: Link to another record (Array of record IDs from the Tranches table)
- **Vesting Date**: Lookup (Array of dates from linked Tranches records)
- **Expiry Date**: Lookup (Array of dates from linked Tranches records)
- **Grant Date**: Lookup (Array of dates from linked Tranches records)
- **Average Volatility**: Rollup (AVERAGE(values) from Volatilities)
- **Risk-Free Rate**: Lookup (Array of yields from Treasury Yields)

### Volatilities Table

The Volatilities table contains the following fields:

- **Volatility ID**: Auto Number
- **Valuation ID**: Link to another record (Array of record IDs from the Valuations table)
- **Ticker**: Text
- **Volatility**: Percent

### Public Comp Set Table

The Public Comp Set table contains the following fields:

- **Comp ID**: Auto Number
- **Ticker**: Text

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

The script iterates over all valuation rows with necessary inputs and an empty `option_value` column. This allows for the recalculation of any option valuation by simply deleting the existing `option_value` value. The script will then detect the empty column and recalculate the option value based on the provided inputs. This feature ensures that the valuation data remains up-to-date and accurate.

To make the process more user-friendly, start by filling out the Tranches table with grant dates, vest dates, and expiry dates. Then, associate each valuation with a tranche, and most of the necessary inputs will be populated automatically. After associating a tranche, make sure to manually input the `valuation_date`.

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
