import streamlit as st
import pandas as pd

# The main title of the application
st.title("Loan Amortization Table Generator")
st.write("Enter your loan details to see the full amortization schedule.")

# --- User Input Section ---
st.header("Loan Details")

# Input for the total loan amount
loan_amount = st.number_input(
    "Total Loan Amount",
    min_value=1000,
    max_value=1000000,
    value=150000,
    step=1000,
    help="The total amount of the loan."
)

# Input for the annual interest rate
annual_rate = st.number_input(
    "Annual Interest Rate (%)",
    min_value=0.1,
    max_value=20.0,
    value=5.0,
    step=0.1,
    help="The annual interest rate in percent."
)

# Dropdown for the loan term in months
# A range of common loan terms is provided in months
loan_terms_months = list(range(12, 361, 12)) # 1 to 30 years in 12-month increments
loan_term_months = st.selectbox(
    "Loan Term (in months)",
    options=loan_terms_months,
    index=14,  # Defaults to 180 months (15 years)
    help="The total number of months for the loan term."
)

# --- Calculation Section ---
if st.button("Generate Amortization Table"):
    if loan_amount and annual_rate and loan_term_months:
        # Convert annual rate to monthly rate
        monthly_rate = (annual_rate / 100) / 12

        # Calculate the monthly payment using the amortization formula
        # M = P * [r(1+r)^n] / [(1+r)^n - 1]
        try:
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**-loan_term_months)
        except ZeroDivisionError:
            st.error("The monthly interest rate cannot be zero. Please enter a valid interest rate.")
            st.stop()
        
        # --- Create the Amortization Table ---
        st.header("Amortization Schedule")
        
        # Initialize a list to hold the data for the DataFrame
        schedule = []
        
        # Start with the initial loan balance
        remaining_balance = loan_amount
        
        # Loop through each month to calculate the schedule
        for month in range(1, loan_term_months + 1):
            # Calculate interest for the current month
            interest_paid = remaining_balance * monthly_rate
            
            # Calculate principal paid for the current month
            principal_paid = monthly_payment - interest_paid
            
            # Update the remaining balance
            remaining_balance -= principal_paid
            
            # Handle potential floating point inaccuracies for the last payment
            if month == loan_term_months and remaining_balance < 0:
                principal_paid += remaining_balance
                remaining_balance = 0
            
            # Append the month's data to the schedule list with the new column names
            schedule.append({
                "Months": month,
                "Opening Balance": f"${remaining_balance + principal_paid:,.2f}",
                "Interest": f"${interest_paid:,.2f}",
                "Monthly Installment": f"${monthly_payment:,.2f}",
                "Principal Payment": f"${principal_paid:,.2f}",
                "Closing Balance": f"${remaining_balance:,.2f}",
            })

        # Create a pandas DataFrame from the schedule data
        df = pd.DataFrame(schedule)
        
        # Display the DataFrame in Streamlit
        st.dataframe(df)

        # Show a summary of the loan
        st.header("Summary")
        st.write(f"**Monthly Payment:** ${monthly_payment:,.2f}")
        st.write(f"**Total Principal Paid:** ${loan_amount:,.2f}")
        total_interest = (monthly_payment * loan_term_months) - loan_amount
        st.write(f"**Total Interest Paid:** ${total_interest:,.2f}")
        st.write(f"**Total Cost of Loan:** ${loan_amount + total_interest:,.2f}")

    else:
        st.warning("Please fill in all the loan details to generate the table.")
