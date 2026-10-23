
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import uuid

# ---------- APP SETTINGS ----------
st.set_page_config(
    page_title="Student Expense Tracker",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "expenses.csv"

st.title("💰 Student Expense Tracker")
st.write("Manage your daily spending, track expenses, and understand your habits.")

# ---------- LOAD SAVED DATA ----------
def load_expenses():
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
            required = [
                "id", "date", "category",
                "description", "amount"
            ]
            if all(col in df.columns for col in required):
                return df[required]
        except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
            pass

    return pd.DataFrame(columns=[
        "id", "date", "category", "description", "amount"
    ])


def save_expenses(df):
    df.to_csv(DATA_FILE, index=False)


if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

# ---------- SIDEBAR ----------
st.sidebar.header("📌 Navigation")

page = st.sidebar.radio(
    "Choose a page",
    ["Dashboard", "Add Expense", "View Expenses"]
)

# ---------- ADD EXPENSE ----------
if page == "Add Expense":
    st.header("➕ Add a New Expense")

    with st.form("expense_form", clear_on_submit=True):
        expense_date = st.date_input("Expense date", value=date.today())

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Education",
                "Shopping",
                "Accommodation",
                "Entertainment",
                "Other"
            ]
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Lunch at college"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            max_value=1000000.0,
            value=100.0,
            step=10.0
        )

        submitted = st.form_submit_button(
            "Save Expense",
            use_container_width=True
        )

        if submitted:
            if not description.strip():
                st.error("Please enter an expense description.")
            else:
                new_expense = {
                    "id": str(uuid.uuid4()),
                    "date": expense_date.isoformat(),
                    "category": category,
                    "description": description.strip(),
                    "amount": round(amount, 2)
                }

                updated = pd.concat(
                    [
                        st.session_state.expenses,
                        pd.DataFrame([new_expense])
                    ],
                    ignore_index=True
                )

                save_expenses(updated)
                st.session_state.expenses = updated
                st.success("Expense saved successfully! 🎉")

# ---------- PREPARE DATA ----------
df = st.session_state.expenses.copy()

if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["amount", "date"])

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.header("📊 Your Spending Dashboard")

    if df.empty:
        st.info(
            "No expenses yet. Open 'Add Expense' from the sidebar "
            "to record your first expense."
        )
    else:
        total = df["amount"].sum()
        count = len(df)
        average = total / count

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Spending", f"₹{total:,.2f}")
        col2.metric("Number of Expenses", count)
        col3.metric("Average Expense", f"₹{average:,.2f}")

        st.subheader("Spending by Category")

        category_totals = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_totals)

        st.subheader("Daily Spending")

        daily_totals = (
            df.groupby(df["date"].dt.strftime("%Y-%m-%d"))["amount"]
            .sum()
            .sort_index()
        )

        st.line_chart(daily_totals)

        st.subheader("Recent Expenses")
        recent = df.sort_values("date", ascending=False).head(5)
        st.dataframe(
            recent[["date", "category", "description", "amount"]],
            use_container_width=True,
            hide_index=True
        )

# ---------- VIEW EXPENSES ----------
elif page == "View Expenses":
    st.header("🧾 All Your Expenses")

    if df.empty:
        st.info("No expenses to display yet.")
    else:
        categories = ["All"] + sorted(df["category"].dropna().unique().tolist())

        selected_category = st.selectbox(
            "Filter by category",
            categories
        )

        filtered = df.copy()

        if selected_category != "All":
            filtered = filtered[
                filtered["category"] == selected_category
            ]

        st.dataframe(
            filtered.sort_values("date", ascending=False)[
                ["date", "category", "description", "amount"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.write(f"**Filtered total: ₹{filtered['amount'].sum():,.2f}**")

        st.caption(
            "Your records are stored in a local CSV file. "
            "Keep the file private if it contains personal spending details."
        )

st.sidebar.divider()
st.sidebar.caption("Built with Python, Streamlit and Pandas.")
