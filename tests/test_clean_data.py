# tests/test_orders_unit.py
import pandas as pd
import numpy as np
from src.clean_data import clean_orders
import ipaddress

# -----------------------
# 1. Dates invalides / incohérentes
# -----------------------
def test_invalid_dates_removed():
    df = pd.DataFrame({
        "order_id": ["A1", "A2"],
        "order_ts": ["2025-02-30", "2025-01-01"],
        "ship_ts": ["2025-01-02", "2025-01-01"],
        "status": ["paid", "delivered"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":10}], [{"sku":"SKU","qty":1,"unit_price":10}]],
        "subtotal": [10, 10],
        "tax": [1, 1],
        "shipping_fee": [0, 0],
        "discount_amount": [0, 0],
        "card_last4": ["1234", "5678"],
        "ship_country": ["FR", "FR"],
        "ip_address": ["192.168.1.1", "10.0.0.1"],
        "ship_postal_code": ["75001", "75002"]
    })
    df_clean = clean_orders(df)
    assert df_clean["order_ts"].notna().all(), "Dates invalides non supprimées"

# -----------------------
# 2. ship_ts < order_ts
# -----------------------
def test_ship_before_order_removed():
    df = pd.DataFrame({
        "order_id": ["A1", "A2"],
        "order_ts": ["2025-01-02", "2025-01-01"],
        "ship_ts": ["2025-01-01", "2025-01-02"],
        "status": ["paid", "delivered"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":10}], [{"sku":"SKU","qty":1,"unit_price":10}]],
        "subtotal": [10, 10],
        "tax": [1, 1],
        "shipping_fee": [0, 0],
        "discount_amount": [0, 0],
        "card_last4": ["1234", "5678"],
        "ship_country": ["FR", "FR"],
        "ip_address": ["192.168.1.1", "10.0.0.1"],
        "ship_postal_code": ["75001", "75002"]
    })
    df_clean = clean_orders(df)
    assert ((df_clean["ship_ts"].notna()) & (df_clean["ship_ts"] >= df_clean["order_ts"])).all(), \
        "ship_ts < order_ts non filtré"

# -----------------------
# 3. Montants
# -----------------------
def test_amounts_cleaned():
    df = pd.DataFrame({
        "order_id": ["A1"],
        "order_ts": ["2025-01-01"],
        "ship_ts": ["2025-01-02"],
        "status": ["paid"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":"$10,50"}]],
        "subtotal": ["10,50"],
        "tax": ["1,05"],
        "shipping_fee": ["FREE"],
        "discount_amount": ["$-2,00"],
        "card_last4": ["1234"],
        "ship_country": ["FR"],
        "ip_address": ["192.168.1.1"],
        "ship_postal_code": ["75001"]
    })
    df_clean = clean_orders(df)
    for col in ["subtotal", "tax", "shipping_fee", "discount_amount"]:
        assert pd.api.types.is_float_dtype(df_clean[col]), f"{col} non converti en float"

# -----------------------
# 4. items_json invalides
# -----------------------
def test_items_json_invalid_removed():
    df = pd.DataFrame({
        "order_id": ["A1","A2"],
        "order_ts": ["2025-01-01","2025-01-01"],
        "ship_ts": ["2025-01-02","2025-01-02"],
        "status": ["paid","paid"],
        "items_json": ["not_json", [{"sku":"SKU","qty":0,"unit_price":10}]],
        "subtotal": [10,10],
        "tax": [1,1],
        "shipping_fee": [0,0],
        "discount_amount": [0,0],
        "card_last4": ["1234","5678"],
        "ship_country": ["FR","FR"],
        "ip_address": ["192.168.1.1","10.0.0.1"],
        "ship_postal_code": ["75001","75002"]
    })
    df_clean = clean_orders(df)
    assert df_clean["items_json"].notna().all(), "items_json invalides non supprimés"

# -----------------------
# 5. card_last4 nettoyage
# -----------------------
def test_card_last4_cleaned():
    df = pd.DataFrame({
        "order_id": ["A1","A2"],
        "order_ts": ["2025-01-01","2025-01-01"],
        "ship_ts": ["2025-01-02","2025-01-02"],
        "status": ["paid","paid"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":10}],[{"sku":"SKU","qty":1,"unit_price":10}]],
        "subtotal": [10,10],
        "tax": [1,1],
        "shipping_fee": [0,0],
        "discount_amount": [0,0],
        "card_last4": ["12A4", None],
        "ship_country": ["FR","FR"],
        "ip_address": ["192.168.1.1","10.0.0.1"],
        "ship_postal_code": ["75001","75002"]
    })
    df_clean = clean_orders(df)
    assert df_clean["card_last4"].str.isdigit().all(), "card_last4 non nettoyé"
    assert (df_clean["card_last4"].str.len() == 4).all(), "card_last4 pas 4 chiffres"

# -----------------------
# 6. Pays ISO2
# -----------------------
def test_country_cleaned():
    df = pd.DataFrame({
        "order_id": ["A1","A2"],
        "order_ts": ["2025-01-01","2025-01-01"],
        "ship_ts": ["2025-01-02","2025-01-02"],
        "status": ["paid","paid"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":10}],[{"sku":"SKU","qty":1,"unit_price":10}]],
        "subtotal": [10,10],
        "tax": [1,1],
        "shipping_fee": [0,0],
        "discount_amount": [0,0],
        "card_last4": ["1234","5678"],
        "ship_country": ["France","FRA"],
        "ip_address": ["192.168.1.1","10.0.0.1"],
        "ship_postal_code": ["75001","75002"]
    })
    df_clean = clean_orders(df)
    assert df_clean["ship_country"].isin({"FR","DE","GB","US","IT"}).all(), "Pays non ISO2"

# -----------------------
# 7. IP invalides
# -----------------------
def test_ip_cleaned():
    df = pd.DataFrame({
        "order_id": ["A1","A2"],
        "order_ts": ["2025-01-01","2025-01-01"],
        "ship_ts": ["2025-01-02","2025-01-02"],
        "status": ["paid","paid"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":10}],[{"sku":"SKU","qty":1,"unit_price":10}]],
        "subtotal": [10,10],
        "tax": [1,1],
        "shipping_fee": [0,0],
        "discount_amount": [0,0],
        "card_last4": ["1234","5678"],
        "ship_country": ["FR","FR"],
        "ip_address": ["192.168.1.1","256.256.1.1"],
        "ship_postal_code": ["75001","75002"]
    })
    df_clean = clean_orders(df)
    assert ipaddress.ip_address(df_clean["ip_address"].iloc[0]), "IP valide supprimée"

# -----------------------
# 8. Codes postaux
# -----------------------
def test_postal_code_not_empty():
    df = pd.DataFrame({
        "order_id": ["A1","A2"],
        "order_ts": ["2025-01-01","2025-01-01"],
        "ship_ts": ["2025-01-02","2025-01-02"],
        "status": ["paid","paid"],
        "items_json": [[{"sku":"SKU","qty":1,"unit_price":10}],[{"sku":"SKU","qty":1,"unit_price":10}]],
        "subtotal": [10,10],
        "tax": [1,1],
        "shipping_fee": [0,0],
        "discount_amount": [0,0],
        "card_last4": ["1234","5678"],
        "ship_country": ["FR","FR"],
        "ip_address": ["192.168.1.1","10.0.0.1"],
        "ship_postal_code": ["","75002"]
    })
    df_clean = clean_orders(df)
    assert (df_clean["ship_postal_code"] != "").all(), "Codes postaux vides"