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
def get_all_tickets():
    if not api_key:
        st.error("Please enter your Freshdesk API key.")
        return []

    all_tickets = []
    page = 1
    
    while True:
        try:
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
            tickets = response.json()
            
            if not tickets:
                break
                
            all_tickets.extend(tickets)
            page += 1
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching tickets: {e}")
            break
            
    return all_tickets

# Function to close a specific ticket
def close_ticket(ticket_id):
    if not api_key:
        st.error("Please enter your Freshdesk API key.")
        return False

    try:
        # Update ticket status to 'Closed' (status 5 in Freshdesk)
        data = {"status": 5}
        response = requests.put(
            f"{BASE_URL}/tickets/{ticket_id}",
            auth=(api_key, "X"),
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error closing ticket {ticket_id}: {e}")
        return False

# Function to close 3M tickets
def close_3m_tickets():
    target_keywords = ["3M Order Change", "3M Order Confirmation"]
    tickets = get_all_tickets()
    closed_count = 0

    for ticket in tickets:
        subject = ticket.get("subject", "")
        if (any(keyword in subject for keyword in target_keywords) and 
            ticket.get("status") != 5):  # Not closed
            if close_ticket(ticket["id"]):
                closed_count += 1
    return closed_count

# Ticket Cleanup Section
st.subheader("Ticket Cleanup")
if st.button("Close All 3M Tickets"):
    closed_count = close_3m_tickets()
    st.success(f"Closed {closed_count} 3M tickets")

# Display Open 3M Tickets Section
st.subheader("📩 Open 3M Tickets")

if st.button("Refresh Ticket List"):
    st.rerun()

if api_key:
    tickets = get_all_tickets()
    open_3m_tickets = [
        ticket for ticket in tickets
        if (any(keyword in ticket.get("subject", "") 
            for keyword in ["3M Order Change", "3M Order Confirmation"]) and
            ticket.get("status") != 5)  # Not closed
    ]
    
    if open_3m_tickets:
        for ticket in open_3m_tickets:
            st.write(f"📌 Ticket #{ticket['id']}: {ticket.get('subject', 'No subject')}")
    else:
        st.write("No open 3M tickets found.")
else:
    st.warning("Enter Freshdesk API key to view tickets.")
