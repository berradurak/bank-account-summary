import csv
from datetime import datetime
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path("data/transactions.csv")

def load_transactions(path: Path):
    transactions = []
    with path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # parse date
            date = datetime.strptime(row["date"], "%Y-%m-%d").date()

            # parse amount
            amount = float(row["amount"])

            # normalize fields
            tx_type = row.get("type", "").strip().upper()
            category = row.get("category", "").strip() or "Uncategorized"
            desc = row.get("description", "").strip()

            # ensure OUT is negative
            if tx_type == "OUT" and amount > 0:
                amount = -amount

            transactions.append({
                "date": date,
                "amount": amount,
                "type": tx_type,
                "category": category,
                "description": desc
            })
    return transactions

def summarize(transactions):
    total_income = 0.0
    total_expense = 0.0

    # expenses per category
    expense_by_category = defaultdict(float)

    # monthly summary: { "YYYY-MM": {"income": x, "expense": y} }
    monthly = defaultdict(lambda: {"income": 0.0, "expense": 0.0})

    for tx in transactions:
        amount = tx["amount"]
        category = tx["category"]
        month_key = f"{tx['date'].year}-{tx['date'].month:02d}"

        if amount >= 0:
            total_income += amount
            monthly[month_key]["income"] += amount
        else:
            # store expenses as positive totals
            total_expense += -amount
            monthly[month_key]["expense"] += -amount
            expense_by_category[category] += -amount

    net_balance = total_income - total_expense
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "expense_by_category": dict(expense_by_category),
        "monthly": dict(monthly),
    }

def print_summary(summary):
    print("=== OVERALL SUMMARY ===")
    print(f"Total income  : {summary['total_income']:.2f}")
    print(f"Total expense : {summary['total_expense']:.2f}")
    print(f"Net balance   : {summary['net_balance']:.2f}")
    print()

    print("=== EXPENSES BY CATEGORY ===")
    for cat, amount in sorted(summary["expense_by_category"].items(), key=lambda x: -x[1]):
        print(f"- {cat:<15} : {amount:.2f}")
    print()

    print("=== MONTHLY SUMMARY ===")
    # print months in chronological order
    for month in sorted(summary["monthly"].keys()):
        m = summary["monthly"][month]
        income = m["income"]
        expense = m["expense"]
        net = income - expense
        print(f"{month}: Income={income:.2f}  Expense={expense:.2f}  Net={net:.2f}")

def main():
    if not DATA_PATH.exists():
        print(f"CSV file not found: {DATA_PATH}")
        return

    transactions = load_transactions(DATA_PATH)
    if not transactions:
        print("No transactions found.")
        return

    summary = summarize(transactions)
    print_summary(summary)

if __name__ == "__main__":
    main()