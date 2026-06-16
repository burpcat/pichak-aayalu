import pandas as pd
import sys
from datetime import datetime

def parse_splitwise_report(file_path, friend_name, output_file=None):
    """
    Parse Splitwise expenses and generate detailed report for a specific friend.
    
    Args:
        file_path: Path to the CSV or Excel file
        friend_name: Name of the friend (column header)
        output_file: Optional path to save the report (default: prints to console)
    """
    
    # Read the file based on extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("File must be .csv, .xlsx, or .xls")
    
    # Clean up column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # Remove any summary/total rows (usually at the end, look for "Total balance" or similar)
    # Check if last row has "total" or "balance" in description
    if len(df) > 0:
        last_row_desc = str(df.iloc[-1]['Description']).lower()
        if 'total' in last_row_desc or 'balance' in last_row_desc or pd.isna(df.iloc[-1]['Description']):
            print(f"Detected summary row at end: '{df.iloc[-1]['Description']}' - excluding from calculations")
            df = df.iloc[:-1]
    
    # Convert Cost column to numeric, handling any non-numeric values
    if 'Cost' in df.columns:
        df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
    
    # Convert all person columns to numeric
    person_columns = [col for col in df.columns if col not in ['Date', 'Description', 'Category', 'Cost', 'Currency']]
    for col in person_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Verify the friend exists in the columns
    if friend_name not in df.columns:
        print(f"Error: '{friend_name}' not found in columns.")
        print(f"Available names: {[col for col in df.columns if col not in ['Date', 'Description', 'Category', 'Cost', 'Currency']]}")
        return
    
    # Filter rows where the friend is involved (non-zero and not NaN)
    friend_involved = df[friend_name].notna() & (df[friend_name] != 0)
    friend_transactions = df[friend_involved].copy()
    
    if friend_transactions.empty:
        print(f"No transactions found for {friend_name}")
        return
    
    # Sort by date
    friend_transactions = friend_transactions.sort_values('Date')
    
    # Calculate running balance
    friend_transactions['Running Balance'] = friend_transactions[friend_name].cumsum()
    
    # Generate report
    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append(f"SPLITWISE EXPENSE REPORT FOR: {friend_name}")
    report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total Transactions: {len(friend_transactions)}")
    report_lines.append("=" * 100)
    report_lines.append("")
    
    # Summary statistics
    total_owed_by_friend = friend_transactions[friend_transactions[friend_name] > 0][friend_name].sum()
    total_owed_to_friend = abs(friend_transactions[friend_transactions[friend_name] < 0][friend_name].sum())
    final_balance = friend_transactions['Running Balance'].iloc[-1]
    
    # Ensure they're numeric
    total_owed_by_friend = float(total_owed_by_friend) if pd.notna(total_owed_by_friend) else 0.0
    total_owed_to_friend = float(total_owed_to_friend) if pd.notna(total_owed_to_friend) else 0.0
    final_balance = float(final_balance) if pd.notna(final_balance) else 0.0
    
    report_lines.append("SUMMARY")
    report_lines.append("-" * 100)
    report_lines.append(f"Total {friend_name} paid from pocket:  ${total_owed_by_friend:>10.2f}")
    report_lines.append(f"Total others paid for {friend_name}:  ${total_owed_to_friend:>10.2f}")
    report_lines.append(f"Net Balance:                           ${final_balance:>10.2f}")
    if final_balance < 0:  # Negative balance means they OWE
        report_lines.append(f"Status: {friend_name} OWES ${abs(final_balance):.2f}")
    elif final_balance > 0:  # Positive balance means they ARE OWED
        report_lines.append(f"Status: {friend_name} IS OWED ${final_balance:.2f}")
    else:
        report_lines.append(f"Status: ALL SETTLED UP ✓")
    report_lines.append("")
    report_lines.append("")
    
    # Detailed transactions
    report_lines.append("DETAILED TRANSACTIONS")
    report_lines.append("=" * 100)
    report_lines.append("")
    
    for idx, row in friend_transactions.iterrows():
        # Parse date
        try:
            date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        except:
            date_str = str(row['Date'])
        
        # Get transaction details
        description = row['Description']
        category = row.get('Category', 'N/A')
        total_cost = row.get('Cost', 0)
        currency = row.get('Currency', 'USD')
        friend_share = row[friend_name]
        running_balance = row['Running Balance']
        
        # Convert to float safely
        try:
            total_cost = float(total_cost) if pd.notna(total_cost) else 0.0
        except (ValueError, TypeError):
            total_cost = 0.0
        
        try:
            friend_share = float(friend_share) if pd.notna(friend_share) else 0.0
        except (ValueError, TypeError):
            friend_share = 0.0
            
        try:
            running_balance = float(running_balance) if pd.notna(running_balance) else 0.0
        except (ValueError, TypeError):
            running_balance = 0.0
        
        # Determine transaction type and improve clarity for payments
        is_payment = 'payment' in str(category).lower() or 'payment' in str(description).lower()
        is_settlement = 'settlement' in str(description).lower()
        
        if is_payment or is_settlement:
            trans_type = "💰 PAYMENT"
        else:
            trans_type = "🛒 EXPENSE"
        
        # Format the transaction
        report_lines.append(f"{trans_type}")
        report_lines.append(f"Date:           {date_str}")
        report_lines.append(f"Description:    {description}")
        report_lines.append(f"Category:       {category}")
        report_lines.append(f"Total Cost:     {currency} {total_cost:.2f}")
        report_lines.append("")
        
        # Friend's share with clear indication based on transaction type
        if is_payment:
            # For payment transactions
            if friend_share > 0:
                # Positive in payment = they made a payment to settle debt
                report_lines.append(f"  ➤ {friend_name}'s share:  ${friend_share:>8.2f}  [✓ {friend_name} MADE PAYMENT TO SETTLE]")
            elif friend_share < 0:
                # Negative in payment = they received a payment
                report_lines.append(f"  ➤ {friend_name}'s share: -${abs(friend_share):>8.2f}  [✓ {friend_name} RECEIVED PAYMENT]")
            else:
                report_lines.append(f"  ➤ {friend_name}'s share:  $ {friend_share:>8.2f}  [NOT INVOLVED]")
        else:
            # For regular expenses
            if friend_share > 0:
                # Positive = they paid from their pocket (covered for others, so they're owed)
                report_lines.append(f"  ➤ {friend_name}'s share:  ${friend_share:>8.2f}  [{friend_name} PAID FROM POCKET → IS OWED BACK]")
            elif friend_share < 0:
                # Negative = someone else paid for their share (they owe this)
                report_lines.append(f"  ➤ {friend_name}'s share: -${abs(friend_share):>8.2f}  [OTHERS PAID FOR {friend_name} → {friend_name} OWES]")
            else:
                report_lines.append(f"  ➤ {friend_name}'s share:  $ {friend_share:>8.2f}  [NO SHARE]")
        
        # Running balance with status
        balance_line = f"  ➤ Running Balance:        ${running_balance:>8.2f}"
        if running_balance < 0:  # Negative = owes money
            balance_line += f"  [{friend_name} owes ${abs(running_balance):.2f}]"
        elif running_balance > 0:  # Positive = is owed money
            balance_line += f"  [{friend_name} is owed ${running_balance:.2f}]"
        else:
            balance_line += f"  [SETTLED UP ✓]"
        report_lines.append(balance_line)
        
        report_lines.append("")
        report_lines.append("-" * 100)
        report_lines.append("")
    
    # Final summary
    report_lines.append("")
    report_lines.append("=" * 100)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 100)
    
    # Output the report
    full_report = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        print(f"Report saved to: {output_file}")
    else:
        print(full_report)
    
    return friend_transactions


# Example usage
if __name__ == "__main__":
    # Configuration
    FILE_PATH = "spl.csv"  # Update with your file name (.csv, .xlsx, or .xls)
    FRIEND_NAME = "Yash Deshpande"  # Update with the exact column name
    OUTPUT_FILE = "splitwise_report_yash.txt"  # Optional: save to file
    
    # You can also pass as command line arguments
    if len(sys.argv) >= 3:
        FILE_PATH = sys.argv[1]
        FRIEND_NAME = sys.argv[2]
        OUTPUT_FILE = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Generate the report
    print(f"Processing Splitwise data for: {FRIEND_NAME}")
    print(f"Reading from: {FILE_PATH}")
    print()
    
    try:
        parse_splitwise_report(FILE_PATH, FRIEND_NAME, OUTPUT_FILE)
    except FileNotFoundError:
        print(f"Error: File '{FILE_PATH}' not found.")
        print("Please update the FILE_PATH variable with your file path.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()