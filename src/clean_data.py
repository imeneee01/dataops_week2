import pandas as pd
import json
import ipaddress

def clean_orders(df):
    df = df.copy()

    # =========================
    # 1. Dates
    # =========================
    df["order_ts"] = pd.to_datetime(df["order_ts"], errors="coerce", utc=True)
    df["ship_ts"] = pd.to_datetime(df["ship_ts"], errors="coerce", utc=True)

    # Supprimer dates invalides
    df = df[df["order_ts"].notna()]

    # Supprimer ship_ts < order_ts
    df = df[(df["ship_ts"].isna()) | (df["ship_ts"] >= df["order_ts"])]

    # Filtrer commandes futures
    now = pd.Timestamp.now(tz='UTC')
    df = df[df["order_ts"] <= now]

    # =========================
    # 2. Status
    # =========================
    df["status"] = df["status"].str.lower()

    # =========================
    # 3. Montants (virgules, FREE…)
    # =========================
    def clean_money(x):
        if pd.isna(x):
            return 0.0
        if isinstance(x, str):
            x = x.replace(",", ".").replace("$", "").strip()
            if x.lower() == "free":
                return 0.0
        try:
            return float(x)
        except:
            return 0.0

    for col in ["subtotal", "tax", "shipping_fee", "discount_amount"]:
        df[col] = df[col].apply(clean_money)

    # =========================
    # 4. items_json
    # =========================
    def clean_items(x):
        try:
            items = json.loads(x) if isinstance(x, str) else x
            for item in items:
                item["qty"] = int(item["qty"])
                price = str(item["unit_price"]).replace(",", ".").replace("$", "")
                item["unit_price"] = float(price)
                if item["qty"] <= 0:
                    return None
            return items
        except:
            return None

    df["items_json"] = df["items_json"].apply(clean_items)
    df = df[df["items_json"].notna()]

    # =========================
    # 5. card_last4 validation
    # =========================
    df["card_last4"] = df["card_last4"].fillna('').astype(str)
    df["card_last4"] = df["card_last4"].apply(lambda x: x if x.isdigit() else '')
    df["card_last4"] = df["card_last4"].str.zfill(4)  # complète à 4 chiffres

    # =========================
    # 6. Pays → ISO2
    # =========================
    country_map = {
        "France": "FR", "FRA": "FR", "FR": "FR",
        "Germany": "DE", "DE": "DE",
        "UK": "GB", "GB": "GB",
        "US": "US",
        "IT": "IT"
    }
    df["ship_country"] = df["ship_country"].map(country_map)

    # =========================
    # 7. IP validation
    # =========================
    def valid_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return ip
        except:
            return None

    df["ip_address"] = df["ip_address"].apply(valid_ip)
    df = df[df["ip_address"].notna()]



    # =========================
    # 8. Codes postaux simples
    # =========================
    df["ship_postal_code"] = df["ship_postal_code"].astype(str).str.strip()
    df = df[df["ship_postal_code"] != ""]

    return df