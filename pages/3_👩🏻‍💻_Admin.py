import streamlit as st
from streamlit_app import url, db, admin_collection
from streamlit_cookies_manager import EncryptedCookieManager
from Database import verify_credentials
from datetime import datetime, timedelta

# Initialize the cookie manager
cookies = EncryptedCookieManager(prefix="nutriscanai_", password='NutriScanAICP03')  # Prefix for your app's cookies

# To access the cookie, ensure it is ready
if not cookies.ready():
    st.stop()

# Cache the user verification for quicker access on repeated requests
@st.cache_data(show_spinner=False)
def login_admin(username, password):
    return verify_credentials(url, db, admin_collection, username, password)

def set_cookie(username):
    # Set the expiration to 5 minutes for normal use, 50 seconds for testing
    expiration_time = 600   # 50 seconds for testing, 300 seconds (5 minutes) for real usage
    expires_at = (datetime.now() + timedelta(seconds=expiration_time)).timestamp()  # Store timestamp
    
    cookies['username'] = username
    cookies['login_flag'] = "True"
    cookies['expires_at'] = str(expires_at)  # Save the expiration time as a string
    cookies.save()

def check_cookie_expiration():
    expires_at = cookies.get('expires_at', None)
    if expires_at:
        try:
            if datetime.now().timestamp() > float(expires_at):
                # Cookie expired, clear it
                cookies['username'] = ""
                cookies['login_flag'] = ""
                cookies.save()
                st.session_state['login_flag'] = False
                st.error("Session expired. Please log in again.")
                st.rerun()
        except ValueError:
            st.error("Invalid expiration time format")
# Check if the cookies have expired on page loa

def login():
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        login_flag = login_admin(username, password)
        if login_flag:
            # Store login state in session and cookies
            st.session_state['login_flag'] = True
            st.session_state['username'] = username
            set_cookie(username)
            st.success("Login successful!")
            st.rerun()  # Simulate redirection
        else:
            st.error("Invalid credentials. Please try again.")

def logout():
    # Clear cookies and session state for logout
    cookies['username'] = ""
    cookies['login_flag'] = ""
    cookies['expires_at'] = ""  # Clear the expiration time
    cookies.save()

    # Clear session state as well
    st.session_state['login_flag'] = False
    st.session_state['username'] = ""
    
    st.success("You have been logged out.")
    st.rerun()  # Simulate redirection or page refresh after logout

# Cache the generation of graphs to avoid recomputation
@st.cache_resource(show_spinner=False)
def get_graphs(past_days):
    from Graph import pie_graph, line_graph, stacked_bar_graph
    
    fig1 = line_graph(x_axis='date', y_axis='gender', days=past_days)
    fig2 = pie_graph(variable='gender', top=2, color=['pink'], days=past_days)
    fig3 = pie_graph(variable='state', top=5, days=past_days)
    fig4 = pie_graph(count_types=True, days=past_days)
    fig6 = line_graph(days=past_days, total_users=True)
    fig7 = stacked_bar_graph(x_axis='state', y_axis='gender', days=past_days, top=5)
    
    return [fig1, fig2, fig3, fig4, fig6, fig7]

# Admin Dashboard
def admin_dashboard():
    check_cookie_expiration()
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout"):
            logout()

    st.title(f"Welcome to the Admin Dashboard, {st.session_state['username']}!")

    # Select past days for data
    past_days = st.selectbox(label="Past Days:", options=[1, 3, 7, 15, 30], index=4)

    if past_days > 0:
        figs = get_graphs(past_days)

        st.header("Download Report Of NutriScan:")
        if st.button('Generate Report'):
            from Report_Generator import generate_report
            with st.spinner("Creating Report, Please Wait!"):
                username = st.session_state.get('username', 'Admin')
                generate_report(username, past_days, figs)

                with open('NutriScanAI_Report.docx', 'rb') as file:
                    st.download_button('Download Report', file, 'NutriScanAI_Report.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        # Display graphs in a structured format
        st.write(f'Line Graph for Last {past_days} Days Usage With Respective Gender')
        st.pyplot(figs[0])

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Pie Graph for Male and Female Ratio**")
            st.pyplot(figs[1])
        with col2:
            st.write("**Pie Graph for Top Five States**")
            st.pyplot(figs[2])

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Pie Graph for Type Counts in Last {past_days} Days")
            st.pyplot(figs[3])
        with col2:
            st.empty()
        
        st.write(f'Line Graph for Last {past_days} Days Usage')
        st.pyplot(figs[4])

        st.write(f'Stacked Bar Graph of Gender by State for Last {past_days} Days')
        st.pyplot(figs[5])

# Check for persistent login state in cookies
if 'login_flag' not in st.session_state:
    st.session_state['login_flag'] = cookies.get('login_flag') == "True"
    st.session_state['username'] = cookies.get('username', 'Guest')

# If not logged in, show login page
if not st.session_state['login_flag']:
    login()
else:
    admin_dashboard()
