import streamlit as st
import requests
from datetime import datetime, timedelta

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
            
            if not tickets:  # No more tickets
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

# Function to close recent 3M tickets
def close_recent_3m_tickets():
    target_keywords = ["3M Order Change", "3M Order Confirmation"]
    one_week_ago = datetime.now() - timedelta(days=7)
    tickets = get_all_tickets()
    closed_count = 0

    for ticket in tickets:
        subject = ticket.get("subject", "")
        created_at = datetime.fromisoformat(ticket.get("created_at", "").replace("Z", "+00:00"))
        
        if (any(keyword in subject for keyword in target_keywords) and 
            created_at > one_week_ago and 
            ticket.get("status") != 5):  # Not already closed
            
            if close_ticket(ticket["id"]):
                closed_count += 1
    return closed_count

# Ticket Cleanup Section
st.subheader("Ticket Cleanup")
if st.button("Close Recent 3M Tickets"):
    closed_count = close_recent_3m_tickets()
    st.success(f"Closed {closed_count} 3M tickets from the last week")

# Display Recent 3M Tickets Section
st.subheader("📩 Recent 3M Tickets (Last 7 Days)")

if st.button("Refresh Ticket List"):
    st.rerun()

if api_key:
    one_week_ago = datetime.now() - timedelta(days=7)
    tickets = get_all_tickets()
    recent_3m_tickets = [
        ticket for ticket in tickets
        if (any(keyword in ticket.get("subject", "") 
            for keyword in ["3M Order Change", "3M Order Confirmation"]) and
            datetime.fromisoformat(ticket.get("created_at", "").replace("Z", "+00:00")) > one_week_ago)
    ]
    
    if recent_3m_tickets:
        for ticket in recent_3m_tickets:
            status = "🟢 Open" if ticket.get("status") != 5 else "🔴 Closed"
            st.write(f"📌 Ticket #{ticket['id']}: {ticket.get('subject', 'No subject')} - {status}")
    else:
        st.write("No recent 3M tickets found.")
else:
    st.warning("Enter Freshdesk API key to view tickets.")
