import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import os 

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personal Finance Management System",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f7f7f7;
        border: 1px solid #ddd;
    }

    .section-title {
        font-size: 25px;
        font-weight: bold;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA FILE
# ============================================================

DATA_FILE = "finance_data.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(DATA_FILE)

        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])

        return df

    return pd.DataFrame(
        columns=[
            "Date",
            "Type",
            "Category",
            "Description",
            "Amount"
        ]
    )


# ============================================================
# SAVE DATA
# ============================================================

def save_data(df):

    df.to_csv(DATA_FILE, index=False)


# ============================================================
# INITIALIZE
# ============================================================

if "transactions" not in st.session_state:

    st.session_state.transactions = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💰 Finance Manager")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Transaction",
        "Transactions",
        "Financial Forecast",
        "Reports"
    ]
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">💰 Personal Finance Management System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Track your income, expenses, savings and future financial position.</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    df = st.session_state.transactions

    if df.empty:

        st.info("No transactions available. Add your first transaction.")

    else:

        income = df[df["Type"] == "Income"]["Amount"].sum()

        expenses = df[df["Type"] == "Expense"]["Amount"].sum()

        savings = income - expenses

        savings_rate = (savings / income * 100) if income > 0 else 0

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Income",
            f"₹{income:,.2f}"
        )

        col2.metric(
            "Total Expenses",
            f"₹{expenses:,.2f}"
        )

        col3.metric(
            "Current Savings",
            f"₹{savings:,.2f}"
        )

        col4.metric(
            "Savings Rate",
            f"{savings_rate:.1f}%"
        )

        st.divider()

        # ----------------------------------------------------
        # EXPENSE BY CATEGORY
        # ----------------------------------------------------

        st.subheader("📊 Expense Breakdown")

        expense_df = df[df["Type"] == "Expense"]

        if not expense_df.empty:

            category_data = (
                expense_df
                .groupby("Category")["Amount"]
                .sum()
                .sort_values(ascending=False)
            )

            col1, col2 = st.columns(2)

            with col1:

                st.bar_chart(category_data)

            with col2:

                st.dataframe(
                    category_data.reset_index(),
                    use_container_width=True,
                    hide_index=True
                )

        # ----------------------------------------------------
        # MONTHLY ANALYSIS
        # ----------------------------------------------------

        st.subheader("📈 Monthly Financial Analysis")

        monthly_df = df.copy()

        monthly_df["Month"] = (
            monthly_df["Date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_income = (
            monthly_df[
                monthly_df["Type"] == "Income"
            ]
            .groupby("Month")["Amount"]
            .sum()
        )

        monthly_expense = (
            monthly_df[
                monthly_df["Type"] == "Expense"
            ]
            .groupby("Month")["Amount"]
            .sum()
        )

        monthly = pd.DataFrame({
            "Income": monthly_income,
            "Expenses": monthly_expense
        }).fillna(0)

        monthly["Savings"] = (
            monthly["Income"] -
            monthly["Expenses"]
        )

        st.line_chart(monthly)

        # ----------------------------------------------------
        # RECENT TRANSACTIONS
        # ----------------------------------------------------

        st.subheader("🧾 Recent Transactions")

        st.dataframe(
            df.sort_values(
                "Date",
                ascending=False
            ).head(10),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ADD TRANSACTION
# ============================================================

elif page == "Add Transaction":

    st.subheader("➕ Add New Transaction")

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense"]
    )

    transaction_date = st.date_input(
        "Date",
        date.today()
    )

    if transaction_type == "Income":

        categories = [
            "Salary",
            "Freelance",
            "Business",
            "Investment",
            "Gift",
            "Other"
        ]

    else:

        categories = [
            "Food",
            "Transport",
            "Rent",
            "Education",
            "Shopping",
            "Entertainment",
            "Bills",
            "Healthcare",
            "Travel",
            "Other"
        ]

    category = st.selectbox(
        "Category",
        categories
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Monthly salary / Grocery shopping"
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=100.0
    )

    if st.button(
        "💾 Save Transaction",
        use_container_width=True
    ):

        if amount <= 0:

            st.error("Please enter an amount greater than ₹0.")

        else:

            new_transaction = pd.DataFrame({
                "Date": [pd.Timestamp(transaction_date)],
                "Type": [transaction_type],
                "Category": [category],
                "Description": [description],
                "Amount": [amount]
            })

            st.session_state.transactions = pd.concat(
                [
                    st.session_state.transactions,
                    new_transaction
                ],
                ignore_index=True
            )

            save_data(
                st.session_state.transactions
            )

            st.success(
                "Transaction added successfully!"
            )


# ============================================================
# TRANSACTIONS
# ============================================================

elif page == "Transactions":

    st.subheader("🧾 Transaction History")

    df = st.session_state.transactions

    if df.empty:

        st.info("No transactions available.")

    else:

        # FILTERS

        col1, col2, col3 = st.columns(3)

        with col1:

            selected_type = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense"]
            )

        with col2:

            categories = ["All"] + sorted(
                df["Category"].dropna().unique().tolist()
            )

            selected_category = st.selectbox(
                "Category",
                categories
            )

        with col3:

            search = st.text_input(
                "Search Description"
            )

        filtered_df = df.copy()

        if selected_type != "All":

            filtered_df = filtered_df[
                filtered_df["Type"] == selected_type
            ]

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["Category"] == selected_category
            ]

        if search:

            filtered_df = filtered_df[
                filtered_df["Description"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            filtered_df.sort_values(
                "Date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        # DOWNLOAD

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            "⬇️ Download Transactions CSV",
            csv,
            "transactions.csv",
            "text/csv"
        )


# ============================================================
# FINANCIAL FORECAST
# ============================================================

elif page == "Financial Forecast":

    st.subheader("🔮 Financial Forecasting")

    df = st.session_state.transactions

    if df.empty:

        st.warning(
            "Add some income and expense transactions first."
        )

    else:

        expense_df = df[
            df["Type"] == "Expense"
        ].copy()

        income_df = df[
            df["Type"] == "Income"
        ].copy()

        if expense_df.empty:

            st.warning(
                "Not enough expense data for forecasting."
            )

        else:

            # ------------------------------------------------
            # MONTHLY DATA
            # ------------------------------------------------

            expense_df["Month"] = (
                expense_df["Date"]
                .dt.to_period("M")
                .astype(str)
            )

            income_df["Month"] = (
                income_df["Date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_expenses = (
                expense_df
                .groupby("Month")["Amount"]
                .sum()
            )

            monthly_income = (
                income_df
                .groupby("Month")["Amount"]
                .sum()
            )

            avg_expense = (
                monthly_expenses.mean()
            )

            avg_income = (
                monthly_income.mean()
            )

            current_savings = (
                income_df["Amount"].sum()
                -
                expense_df["Amount"].sum()
            )

            # ------------------------------------------------
            # FORECAST INPUT
            # ------------------------------------------------

            months = st.slider(
                "Forecast period (months)",
                1,
                12,
                6
            )

            # ------------------------------------------------
            # FORECAST
            # ------------------------------------------------

            forecast_income = avg_income * months

            forecast_expenses = avg_expense * months

            forecast_savings = (
                current_savings
                +
                forecast_income
                -
                forecast_expenses
            )

            # ------------------------------------------------
            # RESULTS
            # ------------------------------------------------

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Average Monthly Income",
                f"₹{avg_income:,.2f}"
            )

            col2.metric(
                "Average Monthly Expenses",
                f"₹{avg_expense:,.2f}"
            )

            col3.metric(
                "Expected Savings",
                f"₹{forecast_savings:,.2f}"
            )

            st.divider()

            # ------------------------------------------------
            # FORECAST TABLE
            # ------------------------------------------------

            forecast_data = []

            balance = current_savings

            for i in range(1, months + 1):

                balance = (
                    balance
                    +
                    avg_income
                    -
                    avg_expense
                )

                forecast_data.append({
                    "Month": f"Month {i}",
                    "Expected Income": avg_income,
                    "Expected Expenses": avg_expense,
                    "Expected Savings": balance
                })

            forecast_df = pd.DataFrame(
                forecast_data
            )

            st.subheader(
                "📈 Future Financial Forecast"
            )

            st.dataframe(
                forecast_df,
                use_container_width=True,
                hide_index=True
            )

            # ------------------------------------------------
            # FORECAST GRAPH
            # ------------------------------------------------

            chart_df = forecast_df.set_index(
                "Month"
            )

            st.line_chart(
                chart_df[
                    [
                        "Expected Income",
                        "Expected Expenses",
                        "Expected Savings"
                    ]
                ]
            )

            # ------------------------------------------------
            # FINANCIAL ADVICE
            # ------------------------------------------------

            st.subheader(
                "💡 Financial Insights"
            )

            if avg_income > avg_expense:

                st.success(
                    "Your average income is higher than your "
                    "average expenses. You have positive "
                    "cash flow."
                )

            else:

                st.error(
                    "Your average expenses are higher than "
                    "your average income. Consider reducing "
                    "non-essential expenses."
                )

            if avg_income > 0:

                saving_percentage = (
                    (avg_income - avg_expense)
                    / avg_income
                    * 100
                )

                if saving_percentage >= 20:

                    st.success(
                        f"Your projected savings rate is "
                        f"{saving_percentage:.1f}%. Good financial discipline."
                    )

                elif saving_percentage >= 10:

                    st.warning(
                        f"Your projected savings rate is "
                        f"{saving_percentage:.1f}%. There is room for improvement."
                    )

                else:

                    st.warning(
                        f"Your projected savings rate is "
                        f"{saving_percentage:.1f}%. Try reducing unnecessary expenses."
                    )


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":

    st.subheader("📊 Financial Reports")

    df = st.session_state.transactions

    if df.empty:

        st.info(
            "No data available to generate reports."
        )

    else:

        # ----------------------------------------------------
        # INCOME REPORT
        # ----------------------------------------------------

        income_df = df[
            df["Type"] == "Income"
        ]

        expense_df = df[
            df["Type"] == "Expense"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "💰 Income by Category"
            )

            if not income_df.empty:

                income_category = (
                    income_df
                    .groupby("Category")["Amount"]
                    .sum()
                )

                st.bar_chart(
                    income_category
                )

        with col2:

            st.subheader(
                "💸 Expenses by Category"
            )

            if not expense_df.empty:

                expense_category = (
                    expense_df
                    .groupby("Category")["Amount"]
                    .sum()
                )

                st.bar_chart(
                    expense_category
                )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        st.subheader(
            "📋 Financial Summary"
        )

        total_income = income_df["Amount"].sum()

        total_expense = expense_df["Amount"].sum()

        net_savings = (
            total_income -
            total_expense
        )

        report = pd.DataFrame({
            "Financial Metric": [
                "Total Income",
                "Total Expenses",
                "Net Savings"
            ],
            "Amount (₹)": [
                total_income,
                total_expense,
                net_savings
            ]
        })

        st.table(report)

        # ----------------------------------------------------
        # DOWNLOAD COMPLETE DATA
        # ----------------------------------------------------

        csv = df.to_csv(index=False)

        st.download_button(
            "⬇️ Download Complete Financial Report",
            csv,
            "financial_report.csv",
            "text/csv"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Personal Finance Management & Financial Forecasting System | "
    "Built with Python + Streamlit"
)