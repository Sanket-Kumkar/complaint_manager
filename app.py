import streamlit as st
import pandas as pd
import os
from database import *
import time
import qrcode
from io import BytesIO
st.set_page_config(layout="wide")

create_table()
create_default_users()

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# -----------------------
# SESSION
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

# -----------------------
# LOGIN
# -----------------------
if not st.session_state.logged_in:

    st.title("🏢 Mutke Girls Hostel")
    st.subheader("Complaint Portal Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login_user(username, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[3]
            st.session_state.username = user[1]
            st.rerun()

        else:
            st.error("Wrong Login")

    st.stop()

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("🏢 Mutke Girls Hostel")
st.sidebar.success(
    f"{st.session_state.username} ({st.session_state.role})"
)

menu_items = ["Dashboard", "Submit Complaint"]

if st.session_state.role == "superadmin":
    menu_items.append("Manage Users")
    menu_items.append("Manage Clients")

menu = st.sidebar.selectbox("Menu", menu_items)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# -----------------------
# SUBMIT
# -----------------------
if menu == "Submit Complaint":

    st.title("📢 Register Complaint")

    clients = get_clients()

    if not clients:
        st.warning("No societies added yet.")
        st.stop()

    client_names = {x[1]: x[0] for x in clients}

    selected = st.selectbox(
        "Select Society",
        list(client_names.keys())
    )

    client_id = client_names[selected]

    name = st.text_input("Name")
    room = st.text_input("Room Number")
    phone = st.text_input("Phone")

    category = st.selectbox(
        "Category",
        ["Electricity", "Plumbing", "Cleaning", "Internet", "Other"]
    )

    details = st.text_area("Complaint Details")

    image = st.file_uploader(
        "Upload Photo",
        type=["png","jpg","jpeg"]
    )

    if st.button("Submit"):

        filename = ""

        if image:
            filename = f"uploads/{int(time.time())}_{image.name}"
            with open(filename, "wb") as f:
                f.write(image.read())

        add_complaint(
            client_id,
            name,
            room,
            phone,
            category,
            details,
            filename
        )

        st.success("Complaint Registered")

        st.info("📲 WhatsApp alert can be triggered here later.")

# -----------------------
# DASHBOARD
# -----------------------
elif menu == "Dashboard":

    st.subheader("Complaint Form QR code")
    url = "https://complaint-manager.streamlit.app/"
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    st.image(buffer.getvalue(), width=250)

    st.download_button(
        "Download QR",
        data=buffer.getvalue(),
        file_name="complaint_qr.png",
        mime="image/png"
    )

    st.title("📊 Complaint Dashboard")

    data = get_all_complaints()

    df = pd.DataFrame(data, columns=[
        "ID","Name","Room","Phone",
        "Category","Details","Image",
        "Status","Created"
    ])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df))
    col2.metric("Pending",
        len(df[df["Status"]=="Pending"]))
    col3.metric("Completed",
        len(df[df["Status"]=="Completed"]))

    st.bar_chart(df["Category"].value_counts())

    st.dataframe(df, use_container_width=True)

    st.subheader("Update Status")

    cid = st.number_input("Complaint ID", min_value=1)
    status = st.selectbox(
        "Status",
        ["Pending","In Process","Completed"]
    )

    if st.button("Update"):
        update_status(cid, status)
        st.success("Updated")

    if st.session_state.role == "superadmin":

        st.subheader("Delete Complaint")

        did = st.number_input(
            "Delete ID",
            min_value=1,
            key="del"
        )

        if st.button("Delete"):
            delete_complaint(did)
            st.success("Deleted")

# -----------------------
# USERS
# -----------------------
elif menu == "Manage Users":

    st.title("👥 Manage Users")

    uname = st.text_input("Username")
    pwd = st.text_input("Password")
    role = st.selectbox(
        "Role",
        ["admin","superadmin"]
    )

    if st.button("Create User"):
        add_user(uname, pwd, role)
        st.success("Created")

elif menu == "Manage Clients":

    st.title("🏢 Manage Societies")

    cname = st.text_input("Society Name")

    if st.button("Add Society"):
        add_client(cname)
        st.success("Society Added")

    st.subheader("Existing Societies")

    st.write(get_clients())
