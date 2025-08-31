import streamlit as st
import pandas as pd
import pyodbc

# ---------- DATABASE CONNECTION ----------
@st.cache_resource
def get_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};' #Your Driver From SQL SERVER
        'SERVER=STARK\SQLEXPRESS;' #Your Server Name
        'DATABASE=OnlineRetailDB;' #Your Database (which include tables)
        'Trusted_Connection=yes;'
    )

# ---------- STREAMLIT APP ----------
st.set_page_config(page_title="Online Retail Dashboard", layout="wide")
st.title("🛍 Online Retail Dashboard")

menu = st.sidebar.selectbox(
    "📌 Select Option",
    ["View Tables", "Analytics", "Custom Query"]
)

# ---------- VIEW TABLES ----------
if menu == "View Tables":
    st.subheader("📋 View Tables")
    table = st.selectbox("Select a table", 
                         ["Customers", "Products", "Orders", "OrderItems", "Categories"])
    conn = get_connection()
    df = pd.read_sql(f"SELECT TOP 100 * FROM {table}", conn)  # preview 100 rows
    st.dataframe(df)

# ---------- ANALYTICS ----------
elif menu == "Analytics":
    st.subheader("📊 Analytics & Reports")
    conn = get_connection()

    # Top 5 customers by spending
    st.markdown("### 👥 Top 5 Customers by Spending")
    query1 = """
        SELECT TOP 5 
            c.FirstName + ' ' + c.LastName AS Customer,
            SUM(oi.Quantity * p.Price) AS TotalSpent
        FROM Orders o
        JOIN OrderItems oi ON o.OrderID = oi.OrderID
        JOIN Products p ON oi.ProductID = p.ProductID
        JOIN Customers c ON o.CustomerID = c.CustomerID
        GROUP BY c.FirstName, c.LastName
        ORDER BY TotalSpent DESC;
    """
    df1 = pd.read_sql(query1, conn)
    st.dataframe(df1)
    st.bar_chart(df1.set_index("Customer"))

    # Sales by category
    st.markdown("### 📦 Total Sales by Category")
    query2 = """
        SELECT c.CategoryName, SUM(oi.Quantity * p.Price) AS TotalSales
        FROM Categories c
        JOIN Products p ON c.CategoryID = p.CategoryID
        JOIN OrderItems oi ON p.ProductID = oi.ProductID
        GROUP BY c.CategoryName
        ORDER BY TotalSales DESC;
    """
    df2 = pd.read_sql(query2, conn)
    st.dataframe(df2)
    st.bar_chart(df2.set_index("CategoryName"))

    # Monthly sales trend
    st.markdown("### 📅 Monthly Sales Trend")
    query3 = """
        SELECT FORMAT(o.OrderDate, 'yyyy-MM') AS Month, SUM(oi.Quantity * p.Price) AS TotalRevenue
        FROM Orders o
        JOIN OrderItems oi ON o.OrderID = oi.OrderID
        JOIN Products p ON oi.ProductID = p.ProductID
        GROUP BY FORMAT(o.OrderDate, 'yyyy-MM')
        ORDER BY Month;
    """
    df3 = pd.read_sql(query3, conn)
    st.line_chart(df3.set_index("Month"))

# ---------- CUSTOM QUERY ----------
elif menu == "Custom Query":
    st.subheader("📝 Run Your Own SQL Query")
    query = st.text_area("Enter SQL query", "SELECT TOP 10 * FROM Customers;")
    if st.button("Run Query"):
        try:
            conn = get_connection()
            df = pd.read_sql(query, conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Error: {e}")