import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_segment_meta, get_customer_profile

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Retail Intelligence & RFM Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern enterprise aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* KPI Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        margin-bottom: 12px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Segment Hero Card */
    .segment-hero {
        background: #ffffff;
        border-radius: 14px;
        padding: 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .badge-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 8px;
    }
    
    /* Recommendations Box */
    .recom-box {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        margin-top: 15px;
    }
    
    /* General card */
    .content-box {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Data Ingestion
# ---------------------------------------------------------
df_clean, rfm_df, stats = load_data()

# ---------------------------------------------------------
# Sidebar Navigation & Global Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0 20px 0;">
        <span style="font-size: 2rem;">🛍️</span>
        <div>
            <div style="font-weight: 700; font-size: 1.15rem; color: #1E293B;">Retail Insights</div>
            <div style="font-size: 0.78rem; color: #64748B;">Analytics & RFM Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=["📊 Business Overview", "🎯 Customer RFM Analysis"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📌 Dataset Synopsis")
    st.markdown(f"""
    - **Total Cleaned Rows**: `{len(df_clean):,}`
    - **Active Customers**: `{df_clean['CustomerID'].nunique():,}`
    - **Total Invoices**: `{df_clean['InvoiceNo'].nunique():,}`
    - **Date Range**: `{df_clean['InvoiceDate'].dt.date.min()}` to `{df_clean['InvoiceDate'].dt.date.max()}`
    - **Snapshot Date**: `{stats['snapshot_date']}`
    """)
    st.markdown("---")
    st.caption("Powered by Streamlit, Plotly & Pandas • Dec 2010 - Dec 2011 Dataset")


# =========================================================
# PAGE 1: BUSINESS OVERVIEW
# =========================================================
if page == "📊 Business Overview":
    st.title("📊 Executive Business Overview")
    st.markdown("Comprehensive commercial performance metrics, sales trends, geographic distribution, and product analytics based on `Retail_Analysis.ipynb`.")

    # -----------------------------------------------------
    # Top-Level Executive KPI Cards
    # -----------------------------------------------------
    total_rev = df_clean["Revenue"].sum()
    unique_custs = df_clean["CustomerID"].nunique()
    total_orders = df_clean["InvoiceNo"].nunique()
    total_units = df_clean["Quantity"].sum()
    
    order_revs = df_clean.groupby("InvoiceNo")["Revenue"].sum()
    mean_aov = order_revs.mean()
    median_aov = order_revs.median()
    
    return_rate_orders = stats.get("return_rate_orders", 14.81)
    cancelled_orders = stats.get("cancelled_invoices", 3836)
    raw_total_orders = stats.get("total_invoices_raw", 25900)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">£{total_rev:,.0f}</div>
            <div class="metric-sub">£{total_rev:,.2f} net sales</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Customers</div>
            <div class="metric-value">{unique_custs:,}</div>
            <div class="metric-sub">Across 37 countries</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Order Value (AOV)</div>
            <div class="metric-value">£{mean_aov:.2f}</div>
            <div class="metric-sub">Median: £{median_aov:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Return / Cancel Rate</div>
            <div class="metric-value" style="color: #EF4444;">{return_rate_orders:.2f}%</div>
            <div class="metric-sub">{cancelled_orders:,} of {raw_total_orders:,} orders</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Units Sold</div>
            <div class="metric-value">{total_units:,.0f}</div>
            <div class="metric-sub">{total_orders:,} fulfilled orders</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # Section 1: Revenue & Order Trends Over Time
    # -----------------------------------------------------
    st.subheader("📈 Revenue Trends & Order Dynamics")
    
    monthly_trends = df_clean.groupby("YearMonth").agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units_Sold=("Quantity", "sum"),
        Active_Customers=("CustomerID", "nunique")
    ).reset_index()

    order_summary = df_clean.groupby("InvoiceNo").agg(
        Order_Revenue=("Revenue", "sum"),
        InvoiceDate=("InvoiceDate", "first")
    ).reset_index()
    order_summary["YearMonth"] = order_summary["InvoiceDate"].dt.strftime("%Y-%m")
    
    monthly_aov = order_summary.groupby("YearMonth").agg(
        Mean_AOV=("Order_Revenue", "mean"),
        Median_AOV=("Order_Revenue", "median")
    ).reset_index()

    trend_tab1, trend_tab2, trend_tab3 = st.tabs([
        "📊 Monthly Revenue & Order Volume", 
        "💳 Monthly AOV Dynamics (Mean vs Median)",
        "📦 Order Value Distribution"
    ])

    with trend_tab1:
        fig_monthly = go.Figure()
        # Bar for Revenue
        fig_monthly.add_trace(go.Bar(
            x=monthly_trends["YearMonth"],
            y=monthly_trends["Revenue"],
            name="Revenue (£)",
            marker_color="#3B82F6",
            opacity=0.85,
            yaxis="y1",
            hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.2f}<extra></extra>"
        ))
        # Line for Orders
        fig_monthly.add_trace(go.Scatter(
            x=monthly_trends["YearMonth"],
            y=monthly_trends["Orders"],
            name="Unique Orders",
            marker=dict(size=8, color="#EF4444"),
            line=dict(width=3, color="#EF4444"),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>"
        ))
        fig_monthly.update_layout(
            title="Monthly Commercial Trajectory: Revenue (£) vs Order Volume (Dec 2010 - Dec 2011)",
            template="plotly_white",
            height=430,
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode="x unified",
            xaxis=dict(title="Year-Month", tickangle=-45),
            yaxis=dict(
                title=dict(text="Revenue (£)", font=dict(color="#3B82F6")),
                tickfont=dict(color="#3B82F6"),
                tickformat="£,~s"
            ),
            yaxis2=dict(
                title=dict(text="Order Volume", font=dict(color="#EF4444")),
                tickfont=dict(color="#EF4444"),
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with trend_tab2:
        fig_aov = go.Figure()
        fig_aov.add_trace(go.Scatter(
            x=monthly_aov["YearMonth"],
            y=monthly_aov["Mean_AOV"],
            mode="lines+markers",
            name="Mean AOV (£)",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>Mean AOV: £%{y:.2f}<extra></extra>"
        ))
        fig_aov.add_trace(go.Scatter(
            x=monthly_aov["YearMonth"],
            y=monthly_aov["Median_AOV"],
            mode="lines+markers",
            name="Median AOV (£)",
            line=dict(color="#10B981", width=3, dash="dot"),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>Median AOV: £%{y:.2f}<extra></extra>"
        ))
        fig_aov.update_layout(
            title="Monthly Average Order Value Stability (Mean vs Median £)",
            template="plotly_white",
            height=430,
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode="x unified",
            xaxis=dict(title="Year-Month", tickangle=-45),
            yaxis=dict(title="Order Value (£)", tickprefix="£"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_aov, use_container_width=True)

    with trend_tab3:
        q95 = order_summary["Order_Revenue"].quantile(0.95)
        filtered_orders = order_summary[order_summary["Order_Revenue"] <= q95]
        
        fig_dist = px.histogram(
            filtered_orders,
            x="Order_Revenue",
            nbins=50,
            title=f"Order Revenue Distribution (Clipped at 95th Percentile: £{q95:.2f})",
            labels={"Order_Revenue": "Order Value (£)"},
            color_discrete_sequence=["#8B5CF6"]
        )
        fig_dist.add_vline(x=mean_aov, line_dash="dash", line_color="#EF4444", annotation_text=f"Mean: £{mean_aov:.2f}")
        fig_dist.add_vline(x=median_aov, line_dash="dot", line_color="#10B981", annotation_text=f"Median: £{median_aov:.2f}")
        fig_dist.update_layout(template="plotly_white", height=430, yaxis_title="Number of Orders")
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # Section 2: Geographic Analysis
    # -----------------------------------------------------
    st.subheader("🌍 Geographic Distribution & Global Markets")
    
    geo_summary = df_clean.groupby("Country").agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units_Sold=("Quantity", "sum"),
        Customers=("CustomerID", "nunique")
    ).reset_index()
    geo_summary["AOV"] = (geo_summary["Revenue"] / geo_summary["Orders"]).round(2)
    geo_summary["Revenue_Share_%"] = ((geo_summary["Revenue"] / total_rev) * 100).round(2)
    geo_summary = geo_summary.sort_values(by="Revenue", ascending=False).reset_index(drop=True)

    # Choropleth Map
    fig_map = px.choropleth(
        geo_summary,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        hover_data={"Revenue": ":£,.2f", "Orders": ":,", "Customers": ":,", "AOV": ":£,.2f"},
        color_continuous_scale="Blues",
        title="Global Sales Penetration: Revenue Heatmap by Country"
    )
    fig_map.update_layout(
        template="plotly_white",
        height=450,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth")
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col_geo1, col_geo2 = st.columns([1, 1])

    with col_geo1:
        st.markdown("##### 🌐 Top 10 International Markets (Excl. UK)")
        st.caption("Since the UK represents 88.9% of total revenue, international markets are analyzed separately to benchmark expansion opportunities.")
        top_intl = geo_summary[geo_summary["Country"] != "United Kingdom"].head(10).sort_values(by="Revenue", ascending=True)
        
        fig_intl_rev = px.bar(
            top_intl,
            x="Revenue",
            y="Country",
            orientation="h",
            text="Revenue",
            color="Revenue",
            color_continuous_scale="Blues",
            labels={"Revenue": "Revenue (£)"}
        )
        fig_intl_rev.update_traces(texttemplate="£%{x:,.0f}", textposition="outside")
        fig_intl_rev.update_layout(template="plotly_white", height=380, showlegend=False, margin=dict(l=20, r=40, t=20, b=20))
        st.plotly_chart(fig_intl_rev, use_container_width=True)

    with col_geo2:
        st.markdown("##### 💰 Average Order Value (AOV) by Country")
        st.caption("Top 10 countries ranked by highest average basket value (£ per order).")
        top_aov_countries = geo_summary[geo_summary["Orders"] >= 5].sort_values(by="AOV", ascending=False).head(10).sort_values(by="AOV", ascending=True)
        
        fig_aov_geo = px.bar(
            top_aov_countries,
            x="AOV",
            y="Country",
            orientation="h",
            text="AOV",
            color="AOV",
            color_continuous_scale="Oranges",
            labels={"AOV": "AOV (£)"}
        )
        fig_aov_geo.update_traces(texttemplate="£%{x:.1f}", textposition="outside")
        fig_aov_geo.update_layout(template="plotly_white", height=380, showlegend=False, margin=dict(l=20, r=40, t=20, b=20))
        st.plotly_chart(fig_aov_geo, use_container_width=True)

    # Detailed Geographic Table
    with st.expander("📋 View Complete Geographic Performance Table"):
        display_geo = geo_summary.copy()
        display_geo["Revenue"] = display_geo["Revenue"].apply(lambda x: f"£{x:,.2f}")
        display_geo["AOV"] = display_geo["AOV"].apply(lambda x: f"£{x:,.2f}")
        display_geo["Revenue_Share_%"] = display_geo["Revenue_Share_%"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(display_geo, use_container_width=True, height=280)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # Section 3: Product Performance Analytics
    # -----------------------------------------------------
    st.subheader("🛍️ Product Performance & Best-Sellers")
    
    col_prod_ctrl1, col_prod_ctrl2 = st.columns([1, 2])
    with col_prod_ctrl1:
        top_n = st.slider("Select Top N Products to Display", min_value=5, max_value=25, value=10, step=5)

    prod_summary = df_clean.groupby(["StockCode", "Description"]).agg(
        Total_Revenue=("Revenue", "sum"),
        Units_Sold=("Quantity", "sum"),
        Total_Orders=("InvoiceNo", "nunique"),
        Avg_Price=("UnitPrice", "mean")
    ).reset_index()

    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        st.markdown(f"##### 💎 Top {top_n} Products by Revenue")
        top_rev_prod = prod_summary.sort_values(by="Total_Revenue", ascending=False).head(top_n).sort_values(by="Total_Revenue", ascending=True)
        # Shorten very long titles for chart readability
        top_rev_prod["Short_Desc"] = top_rev_prod["Description"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
        
        fig_p1 = px.bar(
            top_rev_prod,
            x="Total_Revenue",
            y="Short_Desc",
            orientation="h",
            text="Total_Revenue",
            color="Total_Revenue",
            color_continuous_scale="Viridis",
            hover_name="Description",
            hover_data={"StockCode": True, "Units_Sold": ":,", "Total_Revenue": ":£,.2f"}
        )
        fig_p1.update_traces(texttemplate="£%{x:,.0f}", textposition="outside")
        fig_p1.update_layout(template="plotly_white", height=420, showlegend=False, yaxis_title="")
        st.plotly_chart(fig_p1, use_container_width=True)

    with col_prod2:
        st.markdown(f"##### 📦 Top {top_n} Products by Quantity Sold")
        top_qty_prod = prod_summary.sort_values(by="Units_Sold", ascending=False).head(top_n).sort_values(by="Units_Sold", ascending=True)
        top_qty_prod["Short_Desc"] = top_qty_prod["Description"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
        
        fig_p2 = px.bar(
            top_qty_prod,
            x="Units_Sold",
            y="Short_Desc",
            orientation="h",
            text="Units_Sold",
            color="Units_Sold",
            color_continuous_scale="Magma",
            hover_name="Description",
            hover_data={"StockCode": True, "Units_Sold": ":,", "Total_Revenue": ":£,.2f"}
        )
        fig_p2.update_traces(texttemplate="%{x:,}", textposition="outside")
        fig_p2.update_layout(template="plotly_white", height=420, showlegend=False, yaxis_title="")
        st.plotly_chart(fig_p2, use_container_width=True)


# =========================================================
# PAGE 2: CUSTOMER RFM ANALYSIS
# =========================================================
else:
    st.title("🎯 Customer RFM Segmentation & Individual Lookup")
    st.markdown("Perform deep-dive segmentation analysis, inspect macro segment dynamics, and look up individual customer profiles with personalized marketing recommendations based on `RFM_Analysis.ipynb`.")

    # -----------------------------------------------------
    # Macro RFM Segment Overview Tabs
    # -----------------------------------------------------
    segment_summary = rfm_df.groupby("Segment").agg(
        Customer_Count=("CustomerID", "count"),
        Total_Revenue=("Monetary", "sum"),
        Mean_Recency=("Recency", "mean"),
        Mean_Frequency=("Frequency", "mean"),
        Mean_Monetary=("Monetary", "mean")
    ).reset_index()

    segment_summary["Customer_Share_%"] = (segment_summary["Customer_Count"] / len(rfm_df) * 100).round(2)
    segment_summary["Revenue_Share_%"] = (segment_summary["Total_Revenue"] / rfm_df["Monetary"].sum() * 100).round(2)
    segment_summary = segment_summary.sort_values(by="Total_Revenue", ascending=False).reset_index(drop=True)

    with st.expander("📊 View Customer Base RFM Segment Distribution (Macro Overview)", expanded=False):
        macro_c1, macro_c2 = st.columns(2)
        with macro_c1:
            fig_seg_cust = px.bar(
                segment_summary.sort_values(by="Customer_Count", ascending=True),
                x="Customer_Count",
                y="Segment",
                orientation="h",
                text="Customer_Count",
                color="Customer_Count",
                color_continuous_scale="Teal",
                title="Customer Headcount by Segment"
            )
            fig_seg_cust.update_traces(texttemplate="%{x:,}", textposition="outside")
            fig_seg_cust.update_layout(template="plotly_white", height=320, showlegend=False, yaxis_title="")
            st.plotly_chart(fig_seg_cust, use_container_width=True)

        with macro_c2:
            fig_seg_rev = px.bar(
                segment_summary.sort_values(by="Total_Revenue", ascending=True),
                x="Total_Revenue",
                y="Segment",
                orientation="h",
                text="Total_Revenue",
                color="Total_Revenue",
                color_continuous_scale="Purp",
                title="Revenue Contribution by Segment (£)"
            )
            fig_seg_rev.update_traces(texttemplate="£%{x:,.0f}", textposition="outside")
            fig_seg_rev.update_layout(template="plotly_white", height=320, showlegend=False, yaxis_title="")
            st.plotly_chart(fig_seg_rev, use_container_width=True)

        st.markdown("###### RFM Segment Matrix Summary")
        disp_seg = segment_summary.copy()
        disp_seg["Customer_Count"] = disp_seg["Customer_Count"].apply(lambda x: f"{x:,}")
        disp_seg["Total_Revenue"] = disp_seg["Total_Revenue"].apply(lambda x: f"£{x:,.2f}")
        disp_seg["Customer_Share_%"] = disp_seg["Customer_Share_%"].apply(lambda x: f"{x:.2f}%")
        disp_seg["Revenue_Share_%"] = disp_seg["Revenue_Share_%"].apply(lambda x: f"{x:.2f}%")
        disp_seg["Mean_Recency"] = disp_seg["Mean_Recency"].apply(lambda x: f"{x:.1f} days")
        disp_seg["Mean_Frequency"] = disp_seg["Mean_Frequency"].apply(lambda x: f"{x:.1f} orders")
        disp_seg["Mean_Monetary"] = disp_seg["Mean_Monetary"].apply(lambda x: f"£{x:,.2f}")
        st.dataframe(disp_seg, use_container_width=True)

    st.markdown("---")

    # -----------------------------------------------------
    # Customer Selector & Lookup Section
    # -----------------------------------------------------
    st.subheader("🔍 Individual Customer Search & Lookup")
    
    lookup_col1, lookup_col2, lookup_col3 = st.columns([1.5, 2, 1])

    # Filter by segment
    all_segments = ["All Segments"] + sorted(rfm_df["Segment"].unique().tolist())
    with lookup_col1:
        selected_segment_filter = st.selectbox(
            "Filter by Segment",
            options=all_segments,
            index=0,
            help="Filter customer list by marketing segment"
        )

    # Filtered customer IDs
    if selected_segment_filter != "All Segments":
        filtered_rfm = rfm_df[rfm_df["Segment"] == selected_segment_filter].sort_values(by="Monetary", ascending=False)
    else:
        filtered_rfm = rfm_df.sort_values(by="Monetary", ascending=False)

    customer_options = filtered_rfm["CustomerID"].tolist()
    
    # Store selected customer in session state for random pick or dropdown change
    if "selected_cust_id" not in st.session_state:
        st.session_state.selected_cust_id = int(customer_options[0])
    elif st.session_state.selected_cust_id not in customer_options:
        st.session_state.selected_cust_id = int(customer_options[0])

    with lookup_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🎲 Random Customer", use_container_width=True, help="Pick a random customer from the current filter"):
            import random
            st.session_state.selected_cust_id = int(random.choice(customer_options))
            st.rerun()

    with lookup_col2:
        # Format customer option labels: ID | Segment | Lifetime Spend
        def format_cust(cid):
            row = rfm_df[rfm_df["CustomerID"] == cid].iloc[0]
            return f"Customer #{cid} — {row['Segment']} (£{row['Monetary']:,.2f})"

        try:
            curr_index = customer_options.index(st.session_state.selected_cust_id)
        except ValueError:
            curr_index = 0

        selected_customer = st.selectbox(
            "Select Customer ID (or type to search)",
            options=customer_options,
            index=curr_index,
            format_func=format_cust,
            help="Type Customer ID or browse list"
        )
        st.session_state.selected_cust_id = selected_customer

    # Fetch Customer Profile
    profile = get_customer_profile(df_clean, rfm_df, st.session_state.selected_cust_id)

    if profile is None:
        st.error(f"Customer #{st.session_state.selected_cust_id} not found.")
    else:
        meta = get_segment_meta(profile["segment"])

        # -------------------------------------------------
        # Customer Profile Hero Card & Strategic Recommendations
        # -------------------------------------------------
        st.markdown(f"""
        <div class="segment-hero" style="border-top: 4px solid {meta['color']};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div>
                    <span class="badge-pill" style="background-color: {meta['bg_color']}; color: {meta['color']}; border: 1px solid {meta['border_color']};">
                        {meta['emoji']} {profile['segment']} ({meta['badge']})
                    </span>
                    <h2 style="margin: 4px 0 6px 0; color: #0F172A;">Customer #{profile['customer_id']}</h2>
                    <p style="margin: 0; color: #64748B; font-size: 0.95rem;">{meta['summary']}</p>
                </div>
                <div style="text-align: right; margin-top: 8px;">
                    <div style="font-size: 0.8rem; color: #64748B; font-weight: 600;">RFM COMPOSITE SCORE</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: {meta['color']};">{profile['rfm_score']} <span style="font-size: 1rem; color: #94A3B8;">/ 15</span></div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: #475569;">Group: <code>{profile['rfm_group']}</code> (R:{profile['r_score']} | F:{profile['f_score']} | M:{profile['m_score']})</div>
                </div>
            </div>
            
            <div class="recom-box" style="border-left-color: {meta['color']};">
                <div style="font-weight: 700; color: #1E293B; margin-bottom: 8px; font-size: 0.98rem;">
                    🎯 Tailored Marketing Strategy & Strategic Recommendations:
                </div>
                <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 0.92rem; line-height: 1.6;">
                    {''.join([f"<li>{r}</li>" for r in meta['recommendations']])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------------------------
        # Customer Profile Key Metrics Section
        # -------------------------------------------------
        st.markdown("#### 👤 Customer Profile & Financial Summary")
        m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

        with m_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📍 Country</div>
                <div class="metric-value" style="font-size: 1.3rem;">{profile['country']}</div>
                <div class="metric-sub">Primary Market</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">💰 Lifetime Spend</div>
                <div class="metric-value" style="font-size: 1.3rem;">£{profile['total_revenue']:,.2f}</div>
                <div class="metric-sub">M-Score: {profile['m_score']} of 5</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">💳 Customer AOV</div>
                <div class="metric-value" style="font-size: 1.3rem;">£{profile['aov']:,.2f}</div>
                <div class="metric-sub">Across {profile['total_orders']} orders</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🛒 Total Orders</div>
                <div class="metric-value" style="font-size: 1.3rem;">{profile['total_orders']}</div>
                <div class="metric-sub">F-Score: {profile['f_score']} of 5</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⏱️ Recency</div>
                <div class="metric-value" style="font-size: 1.3rem;">{profile['recency_days']} d</div>
                <div class="metric-sub">R-Score: {profile['r_score']} of 5</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📅 Relationship Span</div>
                <div class="metric-value" style="font-size: 1.3rem;">{profile['tenure_days']} d</div>
                <div class="metric-sub">{profile['first_purchase'].strftime('%b %Y')} - {profile['last_purchase'].strftime('%b %Y')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # -------------------------------------------------
        # Customer Visual Analytics (Top Products & Categories)
        # -------------------------------------------------
        cust_tab1, cust_tab2, cust_tab3 = st.tabs([
            "📦 Top Products Purchased", 
            "🏷️ Product Categories Breakdown", 
            "📈 Monthly Spend History & Invoices"
        ])

        with cust_tab1:
            top_p = profile["top_products"].head(10).sort_values(by="Total_Revenue", ascending=True)
            top_p["Short_Desc"] = top_p["Description"].apply(lambda x: x[:35] + "..." if len(x) > 35 else x)
            
            fig_cust_p = px.bar(
                top_p,
                x="Total_Revenue",
                y="Short_Desc",
                orientation="h",
                text="Total_Revenue",
                color="Total_Quantity",
                color_continuous_scale="Viridis",
                labels={"Total_Revenue": "Total Spend (£)", "Total_Quantity": "Units Purchased", "Short_Desc": "Product"},
                title=f"Top Items Purchased by Customer #{profile['customer_id']} (Colored by Units Sold)"
            )
            fig_cust_p.update_traces(texttemplate="£%{x:,.2f}", textposition="outside")
            fig_cust_p.update_layout(template="plotly_white", height=380, margin=dict(l=20, r=40, t=50, b=20))
            st.plotly_chart(fig_cust_p, use_container_width=True)

        with cust_tab2:
            cat_df = profile["category_summary"]
            c_col1, c_col2 = st.columns([1, 1])

            with c_col1:
                fig_cat_pie = px.pie(
                    cat_df,
                    names="Category",
                    values="Revenue",
                    hole=0.45,
                    title=f"Spending Allocation by Product Category (£)",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_cat_pie.update_traces(textposition="inside", textinfo="percent+label")
                fig_cat_pie.update_layout(template="plotly_white", height=350, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_cat_pie, use_container_width=True)

            with c_col2:
                fig_cat_bar = px.bar(
                    cat_df.sort_values(by="Revenue", ascending=True),
                    x="Revenue",
                    y="Category",
                    orientation="h",
                    text="Revenue",
                    color="Units",
                    color_continuous_scale="Blues",
                    title="Revenue & Volume per Category"
                )
                fig_cat_bar.update_traces(texttemplate="£%{x:,.2f}", textposition="outside")
                fig_cat_bar.update_layout(template="plotly_white", height=350, margin=dict(l=20, r=40, t=50, b=20))
                st.plotly_chart(fig_cat_bar, use_container_width=True)

        with cust_tab3:
            monthly_c = profile["monthly_spend"]
            if len(monthly_c) > 0:
                fig_cust_m = px.bar(
                    monthly_c,
                    x="YearMonth",
                    y="Revenue",
                    text="Revenue",
                    labels={"YearMonth": "Month", "Revenue": "Spend (£)"},
                    title=f"Monthly Spend Trajectory for Customer #{profile['customer_id']}",
                    color_discrete_sequence=["#2563EB"]
                )
                fig_cust_m.update_traces(texttemplate="£%{y:,.2f}", textposition="outside")
                fig_cust_m.update_layout(template="plotly_white", height=300)
                st.plotly_chart(fig_cust_m, use_container_width=True)

            st.markdown("###### Detailed Order Log")
            invoice_table = profile["orders_df"][["InvoiceNo", "InvoiceDate", "StockCode", "Description", "Quantity", "UnitPrice", "Revenue", "Category"]].copy()
            invoice_table["InvoiceDate"] = invoice_table["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M")
            invoice_table["UnitPrice"] = invoice_table["UnitPrice"].apply(lambda x: f"£{x:.2f}")
            invoice_table["Revenue"] = invoice_table["Revenue"].apply(lambda x: f"£{x:.2f}")
            st.dataframe(invoice_table, use_container_width=True, height=250)

