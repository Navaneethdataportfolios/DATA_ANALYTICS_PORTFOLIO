import os
import json
import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st

@st.cache_data(show_spinner="Loading retail data and RFM segments...")
def load_data():
    """
    Loads cleaned retail dataset, RFM segmentation, and raw summary metrics.
    Uses fast parquet files if available, otherwise generates them from Online Retail.xlsx.
    """
    parquet_clean = "online_retail_cleaned.parquet"
    parquet_rfm = "rfm_segmented.parquet"
    stats_file = "raw_stats.json"

    # If parquet cache exists, load directly
    if os.path.exists(parquet_clean) and os.path.exists(parquet_rfm):
        df_clean = pd.read_parquet(parquet_clean)
        rfm_df = pd.read_parquet(parquet_rfm)
        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats = json.load(f)[0]
        else:
            stats = {
                "total_invoices_raw": 25900,
                "cancelled_invoices": 3836,
                "return_rate_orders": 14.81,
                "return_rate_qty": 7.45,
                "snapshot_date": "2011-12-10"
            }
        # Ensure correct datetime formats
        if not pd.api.types.is_datetime64_any_dtype(df_clean["InvoiceDate"]):
            df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
        return df_clean, rfm_df, stats

    # Fallback to computing from raw Excel
    df = pd.read_excel("Online Retail.xlsx")
    total_invoices = df["InvoiceNo"].nunique()
    cancelled_invoices = df[df["InvoiceNo"].astype(str).str.startswith("C")]["InvoiceNo"].nunique()
    return_rate_orders = cancelled_invoices / total_invoices * 100
    
    total_items_sold = df[df["Quantity"] > 0]["Quantity"].sum()
    total_items_returned = abs(df[df["Quantity"] < 0]["Quantity"].sum())
    return_rate_qty = total_items_returned / (total_items_sold + total_items_returned) * 100

    df_clean = df.drop_duplicates().copy()
    df_clean = df_clean.dropna(subset=["CustomerID", "Description"])
    df_clean = df_clean[~df_clean["InvoiceNo"].astype(str).str.startswith("C")]
    df_clean = df_clean[(df_clean["Quantity"] > 0) & (df_clean["UnitPrice"] > 0)]
    df_clean["CustomerID"] = df_clean["CustomerID"].astype(int)
    df_clean["InvoiceNo"] = df_clean["InvoiceNo"].astype(str)
    df_clean["StockCode"] = df_clean["StockCode"].astype(str)
    df_clean["Description"] = df_clean["Description"].astype(str).str.strip()
    df_clean["Revenue"] = (df_clean["Quantity"] * df_clean["UnitPrice"]).round(2)
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
    df_clean["YearMonth"] = df_clean["InvoiceDate"].dt.strftime("%Y-%m")

    def categorize_item(desc):
        desc = str(desc).upper()
        if any(k in desc for k in ["BAG", "SHOPPER", "TOTE", "PURSE", "WALLET", "CARRIER"]):
            return "Bags & Luggage"
        if any(k in desc for k in ["CAKE", "BAKING", "MUG", "CUP", "BOWL", "PLATE", "CUTLERY", "TEAPOT", "KITCHEN", "PAN", "JAR", "DISH"]):
            return "Kitchen & Dining"
        if any(k in desc for k in ["LIGHT", "CANDLE", "LANTERN", "LAMP", "T-LIGHT", "HOLDER", "TORCH"]):
            return "Lighting & Candles"
        if any(k in desc for k in ["CHRISTMAS", "XMAS", "PARTY", "BUNTING", "EASTER", "HALLOWEEN", "BIRTHDAY", "CRACKER"]):
            return "Party & Seasonal"
        if any(k in desc for k in ["HEART", "ORNAMENT", "CLOCK", "FRAME", "SIGN", "MIRROR", "CUSHION", "DECORATION", "SLATE", "PLAQUE"]):
            return "Home Decor & Gifts"
        if any(k in desc for k in ["BOX", "STORAGE", "TIN", "BASKET", "DRAWER", "CONTAINER", "CHEST", "CASE"]):
            return "Storage & Organization"
        if any(k in desc for k in ["CARD", "NOTEBOOK", "PAPER", "PEN", "PENCIL", "STICKER", "WRAP", "TAPE", "BOOK"]):
            return "Stationery & Paper"
        if any(k in desc for k in ["TOY", "GAME", "DOLL", "PLUSH", "TEDDY", "PUZZLE"]):
            return "Toys & Novelties"
        return "Other Gifts & Accents"

    df_clean["Category"] = df_clean["Description"].apply(categorize_item)

    snapshot_date = df_clean["InvoiceDate"].max() + dt.timedelta(days=1)
    rfm = df_clean.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda date: (snapshot_date - date.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum")
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Group"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    rfm["RFM_Score"] = rfm[["R_Score", "F_Score", "M_Score"]].sum(axis=1)

    def assign_rfm_segment(row):
        r = row["R_Score"]
        f = row["F_Score"]
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 2 and f >= 3:
            return "Loyal Customers"
        elif r >= 3 and f <= 2:
            return "Potential Loyalists"
        elif r == 1 and f >= 4:
            return "At Risk / Can't Lose Them"
        elif r == 1 and f in [2, 3]:
            return "Hibernating"
        elif r == 1 and f == 1:
            return "Lost / Churned"
        elif r in [2, 3] and f == 1:
            return "About to Sleep"
        elif r in [2, 3] and f == 2:
            return "Customers Needing Attention"
        else:
            return "Promising"

    rfm["Segment"] = rfm.apply(assign_rfm_segment, axis=1)

    stats = {
        "total_invoices_raw": total_invoices,
        "cancelled_invoices": cancelled_invoices,
        "return_rate_orders": round(return_rate_orders, 2),
        "return_rate_qty": round(return_rate_qty, 2),
        "snapshot_date": snapshot_date.strftime("%Y-%m-%d")
    }

    df_clean.to_parquet(parquet_clean, index=False)
    rfm.to_parquet(parquet_rfm, index=False)
    with open(stats_file, "w") as f:
        json.dump([stats], f)

    return df_clean, rfm, stats


def get_segment_meta(segment_name):
    """
    Returns rich metadata, UI color tags, and personalized business recommendations for each RFM segment.
    """
    segment_info = {
        "Champions": {
            "emoji": "🏆",
            "color": "#10B981",
            "bg_color": "rgba(16, 185, 129, 0.12)",
            "border_color": "#10B981",
            "badge": "Elite VIPs & Top Spenders",
            "summary": "Recent buyers who purchase very frequently and generate the highest monetary value.",
            "recommendations": [
                "**VIP Concierge & Recognition**: Enroll in premier status with free priority shipping and dedicated account assistance.",
                "**Early Access & Exclusives**: Provide first-look privileges on new product lines and seasonal collections.",
                "**Advocacy & Referral Programs**: Offer luxury branded incentives for referring corporate peers and business partners.",
                "**Value-Add, Not Discounts**: Avoid aggressive price slashing; focus on prestige service, personalized packaging, and bespoke perks."
            ]
        },
        "Loyal Customers": {
            "emoji": "💎",
            "color": "#3B82F6",
            "bg_color": "rgba(59, 130, 246, 0.12)",
            "border_color": "#3B82F6",
            "badge": "Core Steady Buyers",
            "summary": "Consistent, trustworthy customers with high order frequency and steady cumulative spend.",
            "recommendations": [
                "**Upsell & Tiered Bundles**: Propose higher-margin complementary merchandise and multi-pack sets.",
                "**Loyalty Tier Upgrades**: Give clear milestone targets (e.g., 'Spend £200 more to reach Champions tier').",
                "**Review & Social Proof**: Encourage authentic reviews and user-generated photos in exchange for loyalty bonus points.",
                "**Automated Reordering**: Introduce scheduled replenishment reminders for fast-moving items."
            ]
        },
        "Potential Loyalists": {
            "emoji": "🌟",
            "color": "#8B5CF6",
            "bg_color": "rgba(139, 92, 246, 0.12)",
            "border_color": "#8B5CF6",
            "badge": "High-Potential Growth",
            "summary": "Recent buyers who have spent well across 1-2 orders; prime candidates for nurturing into regular buyers.",
            "recommendations": [
                "**Personalized Welcome Series**: Follow up post-purchase with care instructions, styling guides, and brand story.",
                "**Next-Order Incentive**: Provide a time-limited 10% voucher or free shipping voucher valid for 30 days.",
                "**Cross-Category Discovery**: Showcase bestsellers from categories complementary to their previous cart.",
                "**Community Onboarding**: Invite to brand newsletter with curated trends and design inspiration."
            ]
        },
        "Promising": {
            "emoji": "🌱",
            "color": "#06B6D4",
            "bg_color": "rgba(6, 182, 212, 0.12)",
            "border_color": "#06B6D4",
            "badge": "Emerging Recent Buyers",
            "summary": "Shopped recently with moderate spend; showing positive signals but need brand habituation.",
            "recommendations": [
                "**Trending Highlights**: Display top-rated trending items in their browsing categories.",
                "**Conversion Triggers**: Test threshold perks (e.g., 'Add £15 more for free gifts').",
                "**Fast Feedback**: Solicit immediate satisfaction feedback to resolve any friction before order #2."
            ]
        },
        "Customers Needing Attention": {
            "emoji": "⚠️",
            "color": "#F59E0B",
            "bg_color": "rgba(245, 158, 11, 0.12)",
            "border_color": "#F59E0B",
            "badge": "Slipping Engagement",
            "summary": "Above-average buyers whose recency is starting to lag; risk falling into dormancy if neglected.",
            "recommendations": [
                "**Reactivation Trigger**: Send personalized 'We Miss You' emails featuring items similar to their favorites.",
                "**Limited-Time Flash Perk**: Offer 48-hour bonus loyalty points or free gift with purchase.",
                "**Catalog Refresh Notification**: Highlight newly stocked products in categories they previously purchased."
            ]
        },
        "About to Sleep": {
            "emoji": "⏳",
            "color": "#F97316",
            "bg_color": "rgba(249, 115, 22, 0.12)",
            "border_color": "#F97316",
            "badge": "At Risk of Falling Dormant",
            "summary": "Below-average recency and frequency; haven't purchased in months.",
            "recommendations": [
                "**Aggressive Win-Back Offer**: Share compelling clearance or seasonal discounts.",
                "**Pulse Check Survey**: Deliver a 1-question poll to identify why purchases stopped (pricing, assortment, service).",
                "**Multi-Channel Retargeting**: Retarget via social ads and email with crowd-favorite products."
            ]
        },
        "At Risk / Can't Lose Them": {
            "emoji": "🚨",
            "color": "#EF4444",
            "bg_color": "rgba(239, 68, 68, 0.15)",
            "border_color": "#EF4444",
            "badge": "High-Value Churn Alert",
            "summary": "Previously frequent and heavy spenders who haven't made a purchase in a long time. Highest risk of revenue loss!",
            "recommendations": [
                "**Urgent High-Touch Outreach**: Trigger personal outreach from client relations manager or account executive.",
                "**Substantial Win-Back Voucher**: Provide an exclusive £25-£50 credit or 20% discount on their next order.",
                "**Executive Service Review**: Inquire directly if an order issue, fulfillment delay, or service defect occurred.",
                "**Customized Re-engagement Pack**: Send printed seasonal catalog or bespoke product samples."
            ]
        },
        "Hibernating": {
            "emoji": "💤",
            "color": "#64748B",
            "bg_color": "rgba(100, 116, 139, 0.12)",
            "border_color": "#64748B",
            "badge": "Dormant Low Spenders",
            "summary": "Purchased long ago with low frequency and low spend.",
            "recommendations": [
                "**Deep Clearance Promotions**: Include in annual clearance and warehouse blow-out email blasts.",
                "**Low-Cost Channels**: Rely strictly on automated email rather than expensive paid ad retargeting.",
                "**Preference Cleanup**: Provide an opt-in renewal option to avoid spam complaint penalties."
            ]
        },
        "Lost / Churned": {
            "emoji": "🛑",
            "color": "#475569",
            "bg_color": "rgba(71, 85, 105, 0.12)",
            "border_color": "#475569",
            "badge": "Inactive Churned Customers",
            "summary": "Lowest recency, frequency, and spend scores. Inactive for nearly a full year.",
            "recommendations": [
                "**Annual Automated Reactivation**: Limit communications to major seasonal events (Holiday/Black Friday).",
                "**Suppress from Paid Campaigns**: Suppress customer emails from Meta and Google ads to optimize ROAS.",
                "**Root Cause Analytics**: Study cohort drop-off drivers to refine onboarding and retention for current active customers."
            ]
        }
    }
    return segment_info.get(segment_name, {
        "emoji": "📌",
        "color": "#3B82F6",
        "bg_color": "rgba(59, 130, 246, 0.12)",
        "border_color": "#3B82F6",
        "badge": "Standard Customer",
        "summary": "Valued retail customer.",
        "recommendations": ["Nurture relationship with personalized marketing and top-selling merchandise recommendations."]
    })


def get_customer_profile(df_clean, rfm_df, customer_id):
    """
    Aggregates full detailed profile for a selected CustomerID.
    """
    cust_rfm = rfm_df[rfm_df["CustomerID"] == customer_id]
    if cust_rfm.empty:
        return None

    cust_rfm_row = cust_rfm.iloc[0]
    cust_orders = df_clean[df_clean["CustomerID"] == customer_id].copy()

    # Basic demographics and purchase history
    country = cust_orders["Country"].iloc[0]
    first_purchase = cust_orders["InvoiceDate"].min()
    last_purchase = cust_orders["InvoiceDate"].max()
    tenure_days = (last_purchase - first_purchase).days
    total_revenue = cust_orders["Revenue"].sum()
    total_orders = cust_orders["InvoiceNo"].nunique()
    total_units = cust_orders["Quantity"].sum()
    total_skus = cust_orders["StockCode"].nunique()
    aov = (total_revenue / total_orders) if total_orders > 0 else 0.0

    # Top products purchased
    top_products = cust_orders.groupby(["StockCode", "Description"]).agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Revenue=("Revenue", "sum"),
        Order_Count=("InvoiceNo", "nunique"),
        Avg_Price=("UnitPrice", "mean")
    ).reset_index().sort_values(by="Total_Revenue", ascending=False)

    # Category breakdown
    category_summary = cust_orders.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Units=("Quantity", "sum"),
        Items_Count=("StockCode", "count")
    ).reset_index().sort_values(by="Revenue", ascending=False)

    # Monthly spending trend
    monthly_spend = cust_orders.groupby("YearMonth").agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units=("Quantity", "sum")
    ).reset_index().sort_values(by="YearMonth")

    return {
        "customer_id": customer_id,
        "country": country,
        "segment": cust_rfm_row["Segment"],
        "rfm_group": cust_rfm_row["RFM_Group"],
        "rfm_score": cust_rfm_row["RFM_Score"],
        "r_score": cust_rfm_row["R_Score"],
        "f_score": cust_rfm_row["F_Score"],
        "m_score": cust_rfm_row["M_Score"],
        "recency_days": cust_rfm_row["Recency"],
        "frequency_orders": cust_rfm_row["Frequency"],
        "monetary_spend": cust_rfm_row["Monetary"],
        "first_purchase": first_purchase,
        "last_purchase": last_purchase,
        "tenure_days": tenure_days,
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_units": total_units,
        "total_skus": total_skus,
        "aov": aov,
        "top_products": top_products,
        "category_summary": category_summary,
        "monthly_spend": monthly_spend,
        "orders_df": cust_orders.sort_values(by="InvoiceDate", ascending=False)
    }

