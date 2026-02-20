# tests/test_orders_quality.py
import pandas as pd
import ipaddress
from src.clean_data import clean_orders
from pathlib import Path

CLEAN_DIR = Path("data/processed")  # ou où tu mets ton CSV nettoyé
RAW_FILE = Path("data/raw/orders_dirty_v1.csv")  # CSV d'origine

# -----------------------
# Chargement et nettoyage
# -----------------------
df_clean = clean_orders(pd.read_csv(RAW_FILE))


# =========================
# 1. Dates
# =========================
def test_dates():
    invalid_order_ts = df_clean["order_ts"].isna().sum()
    future_order_ts = (df_clean["order_ts"] > pd.Timestamp.now(tz='UTC')).sum()
    ship_before_order = ((df_clean["ship_ts"].notna()) & (df_clean["ship_ts"] < df_clean["order_ts"])).sum()
    assert invalid_order_ts == 0, "Dates de commande invalides"
    assert future_order_ts == 0, "Dates de commande futures"
    assert ship_before_order == 0, "ship_ts < order_ts"


# =========================
# 2. Status
# =========================
def test_status():
    valid_status = {"paid", "shipped", "delivered", "cancelled", "refund"}
    invalid_status = (~df_clean["status"].str.lower().isin(valid_status)).sum()
    assert invalid_status == 0, "Status invalides"


# =========================
# 3. Montants
# =========================
def test_amounts():
    for col in ["subtotal", "tax", "shipping_fee", "discount_amount"]:
        assert df_clean[col].notna().all(), f"{col} contient des NaN"


# =========================
# 4. items_json
# =========================
def test_items_json():
    def items_invalid(x):
        if not isinstance(x, list):
            return True
        for item in x:
            if item.get("qty", 1) <= 0:
                return True
        return False
    invalid_items = df_clean["items_json"].apply(items_invalid).sum()
    assert invalid_items == 0, "items_json invalides ou qty <= 0"


# =========================
# 5. card_last4
# =========================
def test_card_last4():
    invalid = (~df_clean["card_last4"].str.isdigit()).sum()
    assert invalid == 0, "card_last4 invalides"


# =========================
# 6. Pays
# =========================
def test_country():
    iso_countries = {"FR","DE","GB","US","IT"}
    invalid = (~df_clean["ship_country"].isin(iso_countries)).sum()
    assert invalid == 0, "Pays non ISO2"


# =========================
# 7. IP
# =========================
def test_ip():
    def is_invalid_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return False
        except:
            return True
    invalid = df_clean["ip_address"].apply(is_invalid_ip).sum()
    assert invalid == 0, "IP invalides"


# =========================
# 8. Codes postaux
# =========================
def test_postal_code():
    empty = df_clean["ship_postal_code"].isna().sum()
    assert empty == 0, "Codes postaux vides"