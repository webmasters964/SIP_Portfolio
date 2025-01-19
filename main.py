import plotly.express as px
import streamlit as st
import pandas as pd


# Page Configuration
st.set_page_config(page_title="SIP Portfolio App - skiptrade.in", page_icon="🎯",layout="wide")
st.title("SIP Calculator with Step-up Feature")

# -------------------------------------
# Function: Sidebar Inputs
# -------------------------------------
def create_sidebar():
    """
    Creates the sidebar inputs, dynamically allows selection of a target value,
    and returns the values for the selected portfolio.
    """
    # Sidebar Header
    st.sidebar.header("Portfolio Inputs")

    # Portfolio Selection
    portfolio = st.sidebar.selectbox(
        "Select Portfolio",
        ["Portfolio 1: Short-Term (15 Years)", "Portfolio 2: Long-Term (20 Years)"],
        key="portfolio_selection",
    )

    # Set default values based on the selected portfolio
    if portfolio == "Portfolio 1: Short-Term (15 Years)":
        default_sip_amount = 25000
        default_num_months = 180
        default_return_rate = 12.5
        default_target_value = 2.5e7  # ₹2.5 Crore
    else:
        default_sip_amount = 25000
        default_num_months = 240
        default_return_rate = 12.5
        default_target_value = 5e7  # ₹5 Crore

    # SIP Details
    st.sidebar.subheader("SIP Details")
    sip_amount = st.sidebar.number_input(
        "Monthly SIP Amount (₹)", value=default_sip_amount, min_value=1, key="sip_amount"
    )
    num_months = st.sidebar.number_input(
        "Number of Months", value=default_num_months, min_value=1, key="num_months"
    )
    annual_return_rate = st.sidebar.number_input(
        "Expected Annual Return Rate (%)",
        value=default_return_rate,
        key="annual_return_rate",
    ) / 100
    step_up_percentage = st.sidebar.number_input(
        "Step-Up Percentage (%)", value=10, min_value=0, key="step_up_percentage"
    ) / 100

    # Target Value Selection
    st.sidebar.subheader("Target Value Selection")
    target_value_options = [
        1e6, 1.5e6, 2e6, 2.5e6, 3e6, 4e6, 5e6, 1e7, 1.5e7, 2e7, 2.5e7, 3e7, 4e7, 5e7
    ]  # ₹10 Lakh to ₹5 Crore

    # Ensure default target value is included in options
    if default_target_value not in target_value_options:
        target_value_options.append(default_target_value)
        target_value_options.sort()

    # Set default index for the selectbox
    default_index = target_value_options.index(default_target_value)

    target_value = st.sidebar.selectbox(
        "Select Your Target Value (₹)", 
        options=target_value_options, 
        index=default_index,
        format_func=lambda x: f"₹{x:,.0f}", 
        key="target_value"
    )

    return portfolio, sip_amount, num_months, annual_return_rate, step_up_percentage, target_value


# -------------------------------------
# Function: Fund Allocation
# -------------------------------------
def get_funds_for_portfolio(portfolio):
    """
    Returns the fund allocation based on the selected portfolio.
    """
    if portfolio == "Portfolio 1: Short-Term (15 Years)":
        return [
            {
                "Fund Name": "Bandhan Nifty Alpha 50 Index Fund - Direct Plan",
                "Category": "Index Fund",
                "Allocation (%)": 30,
                "Rationale": "High-alpha stocks for incremental growth.",
            },
            {
                "Fund Name": "HDFC Balanced Advantage Fund - Direct Plan",
                "Category": "Hybrid Fund",
                "Allocation (%)": 20,
                "Rationale": "Stability and growth with balanced equity-debt exposure.",
            },            
            {
                "Fund Name": "Invesco India Flexi Cap Fund Direct Growth",
                "Category": "Multicap Fund",
                "Allocation (%)": 20,
                "Rationale": "Flexibility to invest across market caps for long-term growth.",
            },           
            {
                "Fund Name": "UTI Nifty 200 Quality 30 Index Fund - Growth",
                "Category": "Large-Cap & Mid-Cap Index Fund",
                "Allocation (%)": 20,
                "Rationale": "Exposure to high-quality large- and mid-cap stocks for steady returns.",
            },         
            {
                "Fund Name": "Tata Digital India Fund Direct Growth",
                "Category": "Sector - Technology",
                "Allocation (%)": 10,
                "Rationale": "Targeted exposure to a high-growth technology sector.",
            },
        ]
    else:
        return [
            {
                "Fund Name": "Mirae Asset Nifty Smallcap 250 Momentum Quality 100 ETF",
                "Category": "Small-Cap Index Fund",
                "Allocation (%)": 25,
                "Rationale": "High-growth potential in small-cap stocks.",
            },            
            {
                "Fund Name": "Kotak Nifty Midcap 150 Momentum 50 Index Fund",
                "Category": "Midcap Index Fund",
                "Allocation (%)": 20,
                "Rationale": "Targeted exposure to mid-cap momentum stocks for higher returns.",
            },
            {
                "Fund Name": "Axis Growth Opportunities Fund Direct Growth",
                "Category": "Large & Mid-Cap",
                "Allocation (%)": 15,
                "Rationale": "Balanced allocation to large and mid-cap stocks.",
            },
            {
                "Fund Name": "SBI Energy Opportunities Fund Direct Growth",
                "Category": "Thematic Fund",
                "Allocation (%)": 15,
                "Rationale": "Exposure to the growing energy sector for potential high returns.",
            },
            {
                "Fund Name": "Invesco India Smallcap Fund - Direct Plan - Growth",
                "Category": "Small-Cap Fund",
                "Allocation (%)": 15,
                "Rationale": "Focused exposure to high-growth small-cap stocks.",
            },
            {
                "Fund Name": "UTI Nifty 500 Value 50 Index Fund - Direct Plan Growth",
                "Category": "Value Index Fund",
                "Allocation (%)": 10,
                "Rationale": "Targeted exposure to a high-growth Value sector.",
            }
        ]

# -------------------------------------
# Function: Calculate Future Value (Without Step-up)
# -------------------------------------
def fv_without_stepup(sip_amount, monthly_return_rate, num_months):
    total_fv = 0
    total_invested = 0
    summary = []

    for month in range(1, num_months + 1):
        total_fv += sip_amount * (1 + monthly_return_rate) ** (num_months - month + 1)
        total_invested += sip_amount

        if month % 12 == 0 or month == num_months:
            summary.append(
                {
                    "Year": f"FY{2025 + (month - 1) // 12}",
                    'NonSIPAmount': sip_amount,
                    "NonInvestedAmount": total_invested,
                    "NonFutureValue": total_fv,
                }
            )

    return total_fv, total_invested, summary
    


# -------------------------------------
# Function: Calculate Future Value (With Step-up)
# -------------------------------------
def fv_with_stepup(sip_amount, monthly_return_rate, num_months, step_up_percentage):
    total_fv = 0
    total_invested = 0
    current_sip = sip_amount
    summary = []

    for month in range(1, num_months + 1):
        if month % 12 == 1 and month > 1:
            current_sip *= (1 + step_up_percentage)

        total_fv += current_sip * (1 + monthly_return_rate) ** (num_months - month + 1)
        total_invested += current_sip

        if month % 12 == 0 or month == num_months:
            summary.append(
                {
                    "Year": f"FY{2025 + (month - 1) // 12}",
                    'StepupSIPAmount': current_sip,
                    "StepupInvestedAmount": total_invested,
                    "StepupFutureValue": total_fv,
                }
            )

    return total_fv, total_invested, summary

# -------------------------------------
# Function: Process Funds
# -------------------------------------
def process_funds(funds, sip_amount):
    """
    Processes the fund allocations, calculates SIP per installment,
    and returns a DataFrame.
    """
    frequency_multiplier = {"Monthly": 1, "15-days": 2, "Weekly": 4}
    investment_data = []

    for i, fund in enumerate(funds):
        allocation_amount = sip_amount * (fund["Allocation (%)"] / 100)
        selected_frequency = st.selectbox(
            f"Frequency for {fund['Fund Name']}",
            ["Monthly", "15-days", "Weekly"],
            key=f"frequency_{i}",
        )
        sip_per_installment = allocation_amount / frequency_multiplier[selected_frequency]
        investment_data.append({
            "Fund Name": fund["Fund Name"],
            "Category": fund["Category"],
            "Allocation (%)": fund["Allocation (%)"],
            "Allocation Amount (₹)": allocation_amount,
            "SIP Amount per Installment (₹)": sip_per_installment,
            "Investment Frequency": selected_frequency,
            "Rationale": fund["Rationale"]
        })

    investment_df = pd.DataFrame(investment_data)
    return investment_df


# -------------------------------------
# Main Application Logic
# -------------------------------------
# Retrieve user inputs and target value from the sidebar
portfolio, sip_amount, num_months, annual_return_rate, step_up_percentage, target_value = create_sidebar()


# Get fund allocations
funds = get_funds_for_portfolio(portfolio)

# Process fund allocations and display
st.subheader(f"{portfolio}: Fund Allocation and Frequency")
investment_df = process_funds(funds, sip_amount)
st.write("### Final Investment Plan")
st.header(f"Portfolio Details - {portfolio}")
st.dataframe(investment_df.style.format({
    "Allocation Amount (₹)": "₹{:.2f}",
    "SIP Amount per Installment (₹)": "₹{:.2f}"
}))

# Monthly return rate
monthly_return_rate = (1 + annual_return_rate) ** (1 / 12) - 1
monthly_return_rate = round(monthly_return_rate, 4)
st.write(f"Monthly Return Rate: {monthly_return_rate * 100:.2f}%")

# Calculate future values
fv_without, invested_without, summary_without = fv_without_stepup(
    sip_amount, monthly_return_rate, num_months
)
fv_with, invested_with, summary_with = fv_with_stepup(
    sip_amount, monthly_return_rate, num_months, step_up_percentage
)

# Display results in a two-column layout with headers and spacing
st.markdown("---")
st.header("SIP Results Summary")
# Display Portfolio Details
st.header(f"Portfolio Details: {portfolio}")
col1, col2,col3,col4 = st.columns(4, gap="large")

with col1:
    st.markdown("### Non-Step-Up Plan")
    st.metric("💰 Total Amount Invested", f"₹{invested_without:,.2f}")
    st.metric("📈 Future Value", f"₹{fv_without:,.2f}")
with col2:
    st.markdown("### Step-Up Plan")
    st.metric("💰 Total Amount Invested", f"₹{invested_with:,.2f}")
    st.metric("📈 Future Value", f"₹{fv_with:,.2f}")

with col3:
    st.markdown("### Summary of Investment")
    st.metric(label="💸 SIP Amount (Monthly)", value=f"₹{sip_amount:,.2f}")
    st.metric(label="📆 Investment Period", value=f"{num_months} months")

with col4:
    st.markdown("### Target Value")
    st.metric(label="🎯 Target Value", value=f"₹{target_value:,.0f}")
    st.metric(label="📊 CAGR", value=f"{annual_return_rate * 100:.2f}%")


# Target Achievement Logic
st.header("🎯 Target Achievement")
if fv_with >= target_value:
    st.success(f"🎉 Congratulations! You can achieve your target of ₹{target_value:,.0f} with this plan.")
else:
    st.warning(f"⚠️ You may not reach your target of ₹{target_value:,.0f}. Consider increasing your SIP amount or step-up rate.")

# Combine summaries into one table
summary_df_without_stepup = pd.DataFrame(summary_without)
summary_df_with_stepup = pd.DataFrame(summary_with)


# Ensure 'Year' column exists in both DataFrames
if 'Year' not in summary_df_without_stepup.columns:
    st.error("Year column is missing in summary_df_without_stepup")
if 'Year' not in summary_df_with_stepup.columns:
    st.error("Year column is missing in summary_df_with_stepup")

# Merge the summaries
combined_summary = pd.merge(
    summary_df_without_stepup, 
    summary_df_with_stepup, 
    on='Year',
    how='outer'  # Use 'outer' to include all years
)

# Check the combined summary
st.write("Combined Summary:")
st.write(combined_summary)

# Now create the plot
fig_combined = px.line(
    combined_summary, 
    x='Year', 
    y=[       
        'NonInvestedAmount', 
        'StepupInvestedAmount', 
        'NonFutureValue', 
        'StepupFutureValue'  # Corrected key
    ],
    labels={'value': 'Amount (₹)', 'variable': 'Metric'},
    title="Invested Amount and Future Value Comparison",
    template="plotly_white"
)

# Display the plot
st.plotly_chart(fig_combined, use_container_width=True)