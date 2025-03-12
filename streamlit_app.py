import streamlit as st
import requests

# Streamlit App Title
st.title("Product HelpDesk Ticket Cleanup")

# Configuration Section
#st.subheader("Freshdesk Configuration")
api_key = "ZMYPc0EUJg1tBuvOn1Fx"  # API key hardcoded here for now (please avoid hardcoding in production)

# Subdomain configuration (since we know it's rseaproduct)
subdomain = "rseaproduct"
BASE_URL = f"https://{subdomain}.freshdesk.com/api/v2"

# Set headers for the API requests
headers = {"Content-Type": "application/json"}

# Function to get all tickets from Freshdesk
def get_tickets(page=1):
    if not api_key:
        st.error("Please enter your Freshdesk API key.")
        return []

    try:
        # Fetching tickets with pagination (100 per page)
        params = {
            'per_page': 100,
            'page': page
        }
        response = requests.get(
            f"{BASE_URL}/tickets",
            auth=(api_key, "X"),
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tickets: {e}")
        return []

# Function to delete a specific ticket
def delete_ticket(ticket_id):
    if not api_key:
        st.error("Please enter your Freshdesk API key.")
        return False

    try:
        # Deleting the ticket by ticket ID
        response = requests.delete(f"{BASE_URL}/tickets/{ticket_id}", auth=(api_key, "X"), headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting ticket {ticket_id}: {e}")
        return False

# Manual Deletion Section: Delete 3M-related tickets
def delete_3m_tickets():
    target_keywords = ["3M Order Change", "3M Order Confirmation"]
    tickets = get_tickets()
    deleted_count = 0

    for ticket in tickets:
        subject = ticket.get("subject", "")
        if any(keyword in subject for keyword in target_keywords):
            if delete_ticket(ticket["id"]):
                deleted_count += 1
    return deleted_count

# Ticket Cleanup Section: Delete 3M Tickets
st.subheader("Ticket Cleanup")
if st.button("Delete 3M Tickets"):
    deleted_count = delete_3m_tickets()
    st.success(f"Deleted {deleted_count} tickets with 3M subjects")

# Display All Tickets Section: View All Open Tickets
st.subheader("📩 All Open 3M Tickets")

# Add pagination controls
col1, col2 = st.columns([4, 1])
with col2:
    page = st.number_input("Page", min_value=1, max_value=10, value=1, step=1)

if st.button("Refresh Ticket List"):
    st.rerun()

if api_key:
    tickets = get_tickets(page)
    if tickets:
        st.write(f"Showing page {page} (up to 100 tickets per page)")
        for ticket in tickets:
            st.write(f"📌 Ticket #{ticket['id']}: {ticket.get('subject', 'No subject')}")
    else:
        st.write("No tickets found.")
else:
    st.warning("Enter Freshdesk API key to view tickets.")
