import streamlit as st
import pandas as pd
from sklearn.linear_model import LogisticRegression

# ------------------------
# Load data and train model
# ------------------------
data = pd.read_csv("kirana_churn_data1.csv")

X = data.drop("churn_risk", axis=1)
y = data["churn_risk"]

model = LogisticRegression()
model.fit(X, y)

# ------------------------
# Streamlit Dashboard
# ------------------------
st.title("🛒 Kirana Churn Dashboard")
st.write("This dashboard shows which kirana shops may churn and what action to take.")

# Show dataset
st.subheader("Kirana Data (Sample)")
st.dataframe(data)

# ------------------------
# Input for new kirana
# ------------------------
st.subheader("Check New Kirana")

login = st.number_input("Login count (7 days)", 0)
orders = st.number_input("Order count (7 days)", 0)
avg_value = st.number_input("Average order value", 0)
days_last = st.number_input("Days since last order", 0)
tickets = st.number_input("Support tickets (7 days)", 0)
failures = st.number_input("Order failures (7 days)", 0)
drop = st.number_input("Order drop percent", 0)

if st.button("Check Churn Risk"):
    # Create DataFrame for new kirana
    new_data = pd.DataFrame([{
        "login_count_7d": login,
        "order_count_7d": orders,
        "avg_order_value": avg_value,
        "days_since_last_order": days_last,
        "support_tickets_7d": tickets,
        "order_failures_7d": failures,
        "order_drop_percent": drop
    }])

    # Predict churn
    prediction = model.predict(new_data)[0]

    # ------------------------
    # Smarter churn reason logic
    # ------------------------
    reasons = []
    if days_last > 7:
        reasons.append("Inactivity")
    if tickets >= 3:
        reasons.append("Frustration")
    if drop > 50:
        reasons.append("Sudden Drop")
    if failures >= 2:
        reasons.append("Technical Issue")

    priority = ["Inactivity", "Frustration", "Sudden Drop", "Technical Issue", "Onboarding", "Low-value"]
    churn_reason = next((r for r in priority if r in reasons), "Healthy")

    actions = {
        "Inactivity": "Send reminder + sales rep call",
        "Frustration": "Escalate support",
        "Sudden Drop": "Urgent intervention",
        "Technical Issue": "Fix app / retry order",
        "Healthy": "No action needed"
    }
    recommended_action = actions[churn_reason]

    # Display result
    if prediction == 1:
        st.error("⚠️ High Churn Risk")
        st.write(f"Reason: {churn_reason}")
        st.write(f"Action: {recommended_action}")
    else:
        st.success("✅ Low Churn Risk")
        st.write(f"Reason: {churn_reason}")
        st.write(f"Action: {recommended_action}")

# ------------------------
# Display multiple kiranas with color
# ------------------------
st.subheader("All Kiranas Churn Risk")

# Apply logic to dataset for display
def determine_reason(row):
    reasons = []
    if row['days_since_last_order'] > 7:
        reasons.append("Inactivity")
    if row['support_tickets_7d'] >= 3:
        reasons.append("Frustration")
    if row['order_drop_percent'] > 50:
        reasons.append("Sudden Drop")
    if row['order_failures_7d'] >= 2:
        reasons.append("Technical Issue")
    priority = ["Inactivity", "Frustration", "Sudden Drop", "Technical Issue", "Onboarding", "Low-value"]
    return next((r for r in priority if r in reasons), "Healthy")

def map_action(reason):
    actions = {
        "Inactivity": "Send reminder + sales rep call",
        "Frustration": "Escalate support",
        "Sudden Drop": "Urgent intervention",
        "Technical Issue": "Fix app / retry order",
        "Healthy": "No action needed"
    }
    return actions[reason]

# Add reason and action columns
data['churn_reason'] = data.apply(determine_reason, axis=1)
data['recommended_action'] = data['churn_reason'].apply(map_action)
data['risk_text'] = data['churn_risk'].apply(lambda x: "High" if x==1 else "Low")

# Color formatting
def highlight_risk(row):
    if row['churn_risk'] == 1:
        # red background + white text for high risk
        return ['background-color: #ff4d4d; color: white']*len(row)
    else:
        # green background + black text for low risk
        return ['background-color: #b3ffb3; color: black']*len(row)


st.dataframe(data.style.apply(highlight_risk, axis=1))
