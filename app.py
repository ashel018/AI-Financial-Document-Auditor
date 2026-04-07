import streamlit as st
import random
import uuid
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
from io import BytesIO
import hashlib
import string

# -------------------------------
# AUTHENTICATION & USER MANAGEMENT
# -------------------------------

# Sample user database (in production, use real database)
USERS_DB = {
    "admin": {"password": "admin123", "email": "admin@auditor.com", "name": "Admin User"},
    "user1": {"password": "user123", "email": "user@auditor.com", "name": "Audit User"},
    "manager": {"password": "manager123", "email": "manager@auditor.com", "name": "Manager"}
}

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def verify_credentials(username, password):
    """Verify username and password"""
    if username in USERS_DB:
        if USERS_DB[username]["password"] == password:
            return True
    return False

def init_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "otp_sent" not in st.session_state:
        st.session_state.otp_sent = False
    if "otp_code" not in st.session_state:
        st.session_state.otp_code = None
    if "invoice" not in st.session_state:
        st.session_state.invoice = None
    if "audit_results" not in st.session_state:
        st.session_state.audit_results = None

def login_page():
    """Display login page with 2-step verification"""
    st.set_page_config(page_title="AI Financial Auditor - Login", layout="centered")
    
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 50px auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://static.streamlit.io/examples/dice.jpg", width=100)
    
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Financial Auditor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Intelligent Invoice Validation System</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step 1: Username and Password
    if not st.session_state.otp_sent:
        st.subheader("Step 1: Login Credentials")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Login", use_container_width=True, key="login_btn"):
                if username and password:
                    if verify_credentials(username, password):
                        st.session_state.username = username
                        otp = generate_otp()
                        st.session_state.otp_code = otp
                        st.session_state.otp_sent = True
                        st.success("Credentials verified! Check the next step.")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.markdown("### Demo Credentials")
        st.write("**Username:** admin | **Password:** admin123")
        st.write("**Username:** user1 | **Password:** user123")
        st.write("**Username:** manager | **Password:** manager123")
    
    # Step 2: OTP Verification
    else:
        st.subheader("Step 2: Verification (OTP)")
        st.info(f"We sent a verification code to {USERS_DB[st.session_state.username]['email']}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            otp_input = st.text_input("Enter OTP", placeholder="6-digit code", max_chars=6)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Verify", use_container_width=True):
                if otp_input == st.session_state.otp_code:
                    st.session_state.logged_in = True
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid OTP. Try again.")
        
        with col3:
            if st.button("Back", use_container_width=True):
                st.session_state.otp_sent = False
                st.session_state.otp_code = None
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"<p style='text-align: center; color: #999; font-size: 12px;'>OTP: {st.session_state.otp_code} (for demo)</p>", unsafe_allow_html=True)

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.otp_sent = False
    st.session_state.otp_code = None
    st.session_state.invoice = None
    st.session_state.audit_results = None

# DATA GENERATOR
# -------------------------------
def generate_invoice(difficulty="easy"):
    items = [
        {"name": "ItemA", "price": random.randint(100, 1000), "qty": random.randint(1, 3)}
        for _ in range(random.randint(1, 3))
    ]

    subtotal = sum(i["price"] * i["qty"] for i in items)
    tax = int(subtotal * 0.18)
    total = subtotal + tax

    invoice = {
        "invoice_id": str(uuid.uuid4())[:8],
        "vendor": random.choice(["ABC Ltd", "XYZ Corp", "Trusted Supplier"]),
        "date": "2024-02-10",
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }

    # Inject errors based on difficulty
    if difficulty == "easy":
        if random.choice([True, False]):
            del invoice["date"]
    elif difficulty == "medium":
        invoice["total"] += random.randint(50, 300)
    elif difficulty == "hard":
        invoice["vendor"] = "Fake Inc"
        invoice["total"] += random.randint(500, 1000)

    return invoice


# -------------------------------
# AUDIT AGENT (SIMULATION)
# -------------------------------
def audit_invoice(invoice):
    steps = []
    score = 0
    fraud = False

    steps.append("Checking required fields...")
    if "date" not in invoice:
        steps.append("Warning: Missing date detected")
        score += 0.2

    steps.append("Validating totals...")
    calc_total = invoice["subtotal"] + invoice["tax"]
    if calc_total != invoice["total"]:
        steps.append(f"Error: Total mismatch. Expected {calc_total}, Found {invoice['total']}")
        score += 0.3
        fraud = True
    else:
        steps.append("OK: Totals are correct")

    steps.append("Checking vendor...")
    if invoice["vendor"] == "Fake Inc":
        steps.append("Alert: Suspicious vendor detected")
        score += 0.5
        fraud = True
    else:
        steps.append("OK: Vendor looks valid")

    decision = "Fraud Detected" if fraud else "Valid Invoice"
    return steps, score, decision


# -------------------------------
# REPORT GENERATION
# -------------------------------
def generate_audit_report(invoice, steps, score, decision):
    """Generate detailed audit report as HTML"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    invoice_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; color: #333;">
    <!-- Header -->
    <div style="border-bottom: 3px solid #1f77b4; padding-bottom: 20px; margin-bottom: 30px;">
        <h1 style="color: #1f77b4; margin: 0;">AUDIT REPORT</h1>
        <p style="color: #666; margin: 5px 0;">Generated: {timestamp}</p>
    </div>

    <!-- Invoice Section -->
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h2 style="color: #333; margin-top: 0;">INVOICE DETAILS</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 10px; font-weight: bold;">Invoice ID:</td>
                <td style="padding: 10px;">{invoice.get('invoice_id', 'N/A')}</td>
                <td style="padding: 10px; font-weight: bold;">Date:</td>
                <td style="padding: 10px;">{invoice.get('date', 'N/A')}</td>
            </tr>
            <tr style="background: white;">
                <td style="padding: 10px; font-weight: bold;">Vendor:</td>
                <td style="padding: 10px;">{invoice.get('vendor', 'Unknown')}</td>
                <td style="padding: 10px; font-weight: bold;">Status:</td>
                <td style="padding: 10px; color: {'green' if 'Valid' in decision else 'red'}; font-weight: bold;">
                    {decision}
                </td>
            </tr>
        </table>
    </div>

    <!-- Amounts Section -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px;">
        <div style="background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="color: #666; margin: 0;">Subtotal</p>
            <h3 style="color: #2c3e50; margin: 5px 0;">₹{invoice.get('subtotal', 0):,}</h3>
        </div>
        <div style="background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="color: #666; margin: 0;">Tax</p>
            <h3 style="color: #2c3e50; margin: 5px 0;">₹{invoice.get('tax', 0):,}</h3>
        </div>
        <div style="background: #d5f4e6; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="color: #666; margin: 0;">Total</p>
            <h3 style="color: #27ae60; margin: 5px 0;">₹{invoice.get('total', 0):,}</h3>
        </div>
    </div>

    <!-- Items Section -->
    <div style="margin-bottom: 30px;">
        <h3 style="color: #333;">LINE ITEMS</h3>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
            <tr style="background: #34495e; color: white;">
                <th style="padding: 12px; text-align: left;">Item</th>
                <th style="padding: 12px; text-align: center;">Qty</th>
                <th style="padding: 12px; text-align: right;">Price</th>
                <th style="padding: 12px; text-align: right;">Total</th>
            </tr>
    """
    
    for i, item in enumerate(invoice.get('items', [])):
        bg_color = '#f8f9fa' if i % 2 == 0 else 'white'
        invoice_html += f"""
            <tr style="background: {bg_color}; border-bottom: 1px solid #ddd;">
                <td style="padding: 12px;">{item['name']}</td>
                <td style="padding: 12px; text-align: center;">{item['qty']}</td>
                <td style="padding: 12px; text-align: right;">₹{item['price']:,}</td>
                <td style="padding: 12px; text-align: right;">₹{item['price'] * item['qty']:,}</td>
            </tr>
        """
    
    invoice_html += """
        </table>
    </div>

    <!-- Audit Findings -->
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h3 style="color: #333; margin-top: 0;">AUDIT FINDINGS</h3>
        <ol style="color: #555; line-height: 1.8;">
    """
    
    for step in steps:
        step_class = "✓" if "OK" in step else "⚠" if "Warning" in step else "✗" if "Error" in step else "!"
        invoice_html += f"<li style='margin-bottom: 8px;'>{step}</li>"
    
    invoice_html += """
        </ol>
    </div>

    <!-- Risk Assessment -->
    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 30px;">
        <h3 style="color: #856404; margin-top: 0;">RISK ASSESSMENT</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 10px; font-weight: bold;">Fraud Score:</td>
                <td style="padding: 10px; font-weight: bold; color: red;">{score:.0%}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold;">Risk Level:</td>
                <td style="padding: 10px; font-weight: bold;">
                    {'🔴 HIGH RISK' if score >= 0.5 else '🟡 MEDIUM RISK' if score >= 0.2 else '🟢 LOW RISK'}
                </td>
            </tr>
        </table>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #ddd; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p>This is an automated audit report. For legal/compliance purposes, human verification is recommended.</p>
        <p>AI Financial Document Auditor | {timestamp}</p>
    </div>
    </div>
    """
    return invoice_html


def generate_audit_charts(invoice, steps, score):
    """Generate visualization charts for audit"""
    
    # Risk breakdown chart
    risks = {}
    for step in steps:
        if "Warning" in step or "Alert" in step:
            risks["Warnings"] = risks.get("Warnings", 0) + 1
        elif "Error" in step:
            risks["Errors"] = risks.get("Errors", 0) + 1
        else:
            risks["OK"] = risks.get("OK", 0) + 1
    
    if not risks:
        risks = {"OK": 1}
    
    fig1 = go.Figure(data=[go.Pie(
        labels=list(risks.keys()),
        values=list(risks.values()),
        marker=dict(colors=['#27ae60', '#f39c12', '#e74c3c']),
        hole=0.3
    )])
    fig1.update_layout(
        title_text="Audit Findings",
        height=300,
        showlegend=True
    )
    
    # Amount breakdown
    fig2 = go.Figure(data=[
        go.Bar(x=['Subtotal', 'Tax'], y=[invoice.get('subtotal', 0), invoice.get('tax', 0)],
               marker_color=['#3498db', '#e67e22'])
    ])
    fig2.update_layout(
        title_text="Invoice Breakdown",
        yaxis_title="Amount (₹)",
        height=300,
        showlegend=False
    )
    
    # Risk gauge
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fraud Risk Score"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#e74c3c"},
            'steps': [
                {'range': [0, 20], 'color': "#d5f4e6"},
                {'range': [20, 50], 'color': "#fef5e7"},
                {'range': [50, 100], 'color': "#fadbd8"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig3.update_layout(height=300)
    
    return fig1, fig2, fig3


def create_download_report(invoice, steps, score, decision):
    """Create downloadable report as text"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
================================================================================
                        FINANCIAL AUDIT REPORT
================================================================================
Generated: {timestamp}
Report Type: Automated Invoice Audit

--------------------------------------------------------------------------------
INVOICE INFORMATION
--------------------------------------------------------------------------------
Invoice ID:        {invoice.get('invoice_id', 'N/A')}
Vendor:            {invoice.get('vendor', 'Unknown')}
Date:              {invoice.get('date', 'N/A')}
Audit Decision:    {decision}

--------------------------------------------------------------------------------
FINANCIAL SUMMARY
--------------------------------------------------------------------------------
Subtotal:          ₹{invoice.get('subtotal', 0):,}
Tax (18%):         ₹{invoice.get('tax', 0):,}
Total Amount:      ₹{invoice.get('total', 0):,}

--------------------------------------------------------------------------------
LINE ITEMS
--------------------------------------------------------------------------------
"""
    
    for item in invoice.get('items', []):
        report += f"{item['name']:<30} Qty: {item['qty']:<5} ₹{item['price'] * item['qty']:>12,}\n"
    
    report += f"""
--------------------------------------------------------------------------------
AUDIT FINDINGS & ANALYSIS
--------------------------------------------------------------------------------
"""
    
    for i, step in enumerate(steps, 1):
        report += f"{i}. {step}\n"
    
    report += f"""
--------------------------------------------------------------------------------
RISK ASSESSMENT
--------------------------------------------------------------------------------
Fraud Score:       {score:.0%}
Risk Level:        {'HIGH RISK' if score >= 0.5 else 'MEDIUM RISK' if score >= 0.2 else 'LOW RISK'}

Recommendation:
"""
    
    if score >= 0.5:
        report += "REJECT - Manual verification required. Invoice shows suspicious patterns.\n"
    elif score >= 0.2:
        report += "REVIEW - Minor issues detected. Manual verification recommended.\n"
    else:
        report += "APPROVE - No issues detected. Safe for approval.\n"
    
    report += """
================================================================================
DISCLAIMER: This is an automated audit report. For legal/compliance purposes,
human verification is recommended.
================================================================================
"""
    
    return report


# -------------------------------
# MAIN APPLICATION
# -------------------------------

# Initialize session state
init_session_state()

# Check if user is logged in
if not st.session_state.logged_in:
    # Show login page
    login_page()
else:
    # Show authenticated dashboard
    st.set_page_config(page_title="AI Financial Auditor", layout="wide", initial_sidebar_state="expanded")
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown("---")
        user_info = USERS_DB.get(st.session_state.username, {})
        st.markdown(f"### 👤 {user_info.get('name', st.session_state.username)}")
        st.markdown(f"📧 {user_info.get('email', 'N/A')}")
        st.markdown(f"🔐 Username: `{st.session_state.username}`")
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()
    
    st.title("Financial Document Auditor")
    st.markdown("Streamline invoice validation with intelligent audit analysis. Choose your data input method and run the audit.")
    
    with st.sidebar:
        st.header("Data Input Options")
        
        input_method = st.radio("Choose how to add an invoice:", 
            ["Generate Sample", "Upload JSON", "Manual Entry"],
            horizontal=False
        )
        
        st.markdown("---")
        
        if input_method == "Generate Sample":
            st.subheader("Generate Sample Invoice")
            difficulty = st.selectbox("Select Difficulty", ["easy", "medium", "hard"])
            if st.button("Generate Invoice", key="gen_btn"):
                st.session_state.invoice = generate_invoice(difficulty)
                st.success("Invoice generated!")
        
        elif input_method == "Upload JSON":
            st.subheader("Upload Invoice (JSON)")
            uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])
            if uploaded_file is not None:
                try:
                    invoice_data = json.load(uploaded_file)
                    st.session_state.invoice = invoice_data
                    st.success("Invoice uploaded successfully!")
                except json.JSONDecodeError:
                    st.error("Invalid JSON file. Please check the format.")
            
            with st.expander("JSON Format Example"):
                example = {
                    "invoice_id": "INV001",
                    "vendor": "ABC Ltd",
                    "date": "2024-02-10",
                    "items": [
                        {"name": "Laptop", "price": 50000, "qty": 1},
                        {"name": "Mouse", "price": 500, "qty": 2}
                    ],
                    "subtotal": 51000,
                    "tax": 9180,
                    "total": 60180
                }
                st.code(json.dumps(example, indent=2), language="json")
        
        elif input_method == "Manual Entry":
            st.subheader("Create Invoice Manually")
            
            col1, col2 = st.columns(2)
            with col1:
                vendor = st.text_input("Vendor Name", value="ABC Ltd")
            with col2:
                inv_id = st.text_input("Invoice ID", value="INV001")
            
            date_input = st.date_input("Invoice Date", value=None)
            
            st.write("**Items**")
            num_items = st.number_input("Number of items", min_value=1, max_value=5, value=1)
            
            items = []
            for i in range(num_items):
                st.write(f"Item {i+1}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    item_name = st.text_input(f"Item name", value="Item", key=f"item_name_{i}")
                with col2:
                    item_price = st.number_input(f"Price", min_value=0, value=1000, key=f"item_price_{i}")
                with col3:
                    item_qty = st.number_input(f"Qty", min_value=1, value=1, key=f"item_qty_{i}")
                
                items.append({"name": item_name, "price": item_price, "qty": item_qty})
            
            col1, col2 = st.columns(2)
            with col1:
                subtotal = st.number_input("Subtotal", min_value=0, value=1000)
            with col2:
                tax = st.number_input("Tax", min_value=0, value=180)
            
            total = subtotal + tax
            st.write(f"**Total: ₹{total:,}**")
            
            if st.button("Create Invoice", key="manual_btn"):
                invoice_obj = {
                    "invoice_id": inv_id,
                    "vendor": vendor,
                    "date": date_input.strftime("%Y-%m-%d") if date_input else "N/A",
                    "items": items,
                    "subtotal": subtotal,
                    "tax": tax,
                    "total": total
                }
                st.session_state.invoice = invoice_obj
                st.success("Invoice created!")
        
        st.markdown("---")
        st.markdown("**Workflow:**  \n1. Select input method  \n2. Add invoice data  \n3. Run AI audit  \n4. Review findings")
    
    if st.session_state.invoice is None:
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.header("Welcome")
            st.write("Choose a data input method from the sidebar to get started. You can:")
            st.write("- **Generate samples** with varying difficulty levels")
            st.write("- **Upload JSON invoices** for realistic testing")
            st.write("- **Manually enter** invoice details")
        with col2:
            st.image("https://static.streamlit.io/examples/dice.jpg", caption="Financial audit", use_column_width=True)
    
    else:
        invoice = st.session_state.invoice
        st.subheader("Invoice Summary")

        metric_cols = st.columns(4)
        metric_cols[0].metric("Vendor", invoice.get("vendor", "Unknown"))
        metric_cols[1].metric("Invoice ID", invoice.get("invoice_id", "N/A"))
        metric_cols[2].metric("Subtotal", f"₹{invoice.get('subtotal', 0):,}")
        metric_cols[3].metric("Total", f"₹{invoice.get('total', 0):,}")

        detail_cols = st.columns([1, 2])
        with detail_cols[0]:
            st.markdown("**Details**")
            st.write(f"Date: {invoice.get('date', 'Missing')}")
            st.write(f"Tax: ₹{invoice.get('tax', 0):,}")
            st.write(f"Items: {len(invoice.get('items', []))}")

        with detail_cols[1]:
            if invoice.get("items"):
                st.table([
                    {
                        "Item": item["name"],
                        "Qty": item["qty"],
                        "Price": f"₹{item['price']:,}",
                        "Total": f"₹{item['price'] * item['qty']:,}",
                    }
                    for item in invoice.get("items", [])
                ])

        if st.button("Run Audit", use_container_width=True):
            steps, score, decision = audit_invoice(invoice)
            st.session_state.audit_results = (steps, score, decision)

    # Display audit results if they exist
    if "audit_results" in st.session_state and st.session_state.invoice:
        steps, score, decision = st.session_state.audit_results
        invoice = st.session_state.invoice
        
        st.markdown("---")
        st.header("Audit Results Dashboard")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "📄 Invoice", "📈 Charts", "📥 Report"])
        
        with tab1:
            st.subheader("Audit Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Decision", "✅ PASS" if "Valid" in decision else "❌ FAIL")
            with col2:
                st.metric("Fraud Score", f"{score:.0%}")
            with col3:
                risk_level = "🔴 HIGH" if score >= 0.5 else "🟡 MEDIUM" if score >= 0.2 else "🟢 LOW"
                st.metric("Risk Level", risk_level)
            
            st.markdown("### Audit Findings")
            findings_col, summary_col = st.columns([2, 1])
            
            with findings_col:
                for i, step in enumerate(steps, 1):
                    if "Warning" in step or "Alert" in step:
                        st.warning(f"{i}. {step}")
                    elif "Error" in step:
                        st.error(f"{i}. {step}")
                    else:
                        st.success(f"{i}. {step}")
            
            with summary_col:
                st.markdown("### Summary")
                ok_count = sum(1 for s in steps if "OK" in s)
                warn_count = sum(1 for s in steps if "Warning" in s or "Alert" in s)
                err_count = sum(1 for s in steps if "Error" in s)
                
                st.write(f"✅ Passed: {ok_count}")
                st.write(f"⚠️ Warnings: {warn_count}")
                st.write(f"❌ Errors: {err_count}")
            
            st.markdown("### Recommendation")
            if score >= 0.5:
                st.error("🔴 **REJECT** - This invoice shows suspicious patterns. Manual verification is mandatory.")
            elif score >= 0.2:
                st.warning("🟡 **REVIEW** - Minor issues detected. Manual verification recommended.")
            else:
                st.success("🟢 **APPROVE** - No significant issues detected. Safe to process.")
        
        with tab2:
            st.subheader("PDF-Style Invoice View")
            
            # Generate and display invoice HTML
            invoice_html = generate_audit_report(invoice, steps, score, decision)
            st.markdown(invoice_html, unsafe_allow_html=True)
            
            # Download invoice as HTML
            st.download_button(
                label="📥 Download Invoice (HTML)",
                data=invoice_html,
                file_name=f"invoice_{invoice.get('invoice_id', 'unknown')}.html",
                mime="text/html"
            )
        
        with tab3:
            st.subheader("Audit Analytics")
            
            fig_pie, fig_bar, fig_gauge = generate_audit_charts(invoice, steps, score)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_pie, use_container_width=True)
                st.write("Breakdown of audit findings across all checks")
            
            with col2:
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.write("Overall fraud risk assessment score")
            
            st.plotly_chart(fig_bar, use_container_width=True)
            st.write("Invoice amount composition")
        
        with tab4:
            st.subheader("Download Audit Report")
            
            # Generate report
            report_text = create_download_report(invoice, steps, score, decision)
            report_html = generate_audit_report(invoice, steps, score, decision)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Download as TXT",
                    data=report_text,
                    file_name=f"audit_report_{invoice.get('invoice_id', 'unknown')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                st.download_button(
                    label="📋 Download as HTML",
                    data=report_html,
                    file_name=f"audit_report_{invoice.get('invoice_id', 'unknown')}.html",
                    mime="text/html"
                )
            
            with col3:
                # JSON export
                report_json = json.dumps({
                    "invoice": invoice,
                    "audit": {
                        "steps": steps,
                        "score": score,
                        "decision": decision,
                        "timestamp": datetime.now().isoformat()
                    }
                }, indent=2)
                
                st.download_button(
                    label="💾 Download as JSON",
                    data=report_json,
                    file_name=f"audit_report_{invoice.get('invoice_id', 'unknown')}.json",
                    mime="application/json"
                )
            
            st.markdown("---")
            st.markdown("### Report Preview")
            st.text(report_text)
