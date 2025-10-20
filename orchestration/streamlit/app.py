import os
import pandas as pd
import streamlit as st
import altair as alt
import snowflake.connector
from cryptography.hazmat.primitives import serialization

# ---------- Config Streamlit ----------
st.set_page_config(page_title="Airbnb – Mini BI", layout="wide")

# ---------- Paramètres Snowflake (depuis env) ----------
SF_ACCOUNT   = os.getenv("SNOWFLAKE_ACCOUNT")
SF_USER      = os.getenv("SNOWFLAKE_USER")
SF_ROLE      = os.getenv("SNOWFLAKE_ROLE", "TRANSFORM")
SF_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SF_DATABASE  = os.getenv("SNOWFLAKE_DATABASE", "AIRBNB")
SF_SCHEMA    = os.getenv("SNOWFLAKE_SCHEMA", "DEV")

PK_PATH = os.getenv("PRIVATE_KEY_PATH", "/run/secrets/snowflake_rsa.p8")
PK_PASSPHRASE = os.getenv("PRIVATE_KEY_PASSPHRASE")

# ---------- Connexion Snowflake ----------
def _load_pk_bytes():
    if not PK_PASSPHRASE:
        raise RuntimeError("Env manquante: PRIVATE_KEY_PASSPHRASE")
    if not os.path.exists(PK_PATH):
        raise FileNotFoundError(f"Clé privée introuvable: {PK_PATH}")
    with open(PK_PATH, "rb") as f:
        key_bytes = f.read()
    private_key = serialization.load_pem_private_key(
        key_bytes, password=PK_PASSPHRASE.encode("utf-8")
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

def get_conn():
    pk = _load_pk_bytes()
    con = snowflake.connector.connect(
        account     = SF_ACCOUNT,
        user        = SF_USER,
        private_key = pk,
        role        = SF_ROLE,
        warehouse   = SF_WAREHOUSE,
        database    = SF_DATABASE,
        schema      = SF_SCHEMA,
        client_session_keep_alive=True,
    )
    return con

# ---------- Helper SQL -> DataFrame ----------
@st.cache_data(ttl=600, show_spinner=False)
def run_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_conn() as con:
        df = pd.read_sql(sql, con, params=params)
    # Normaliser les noms de colonnes en minuscules (Snowflake renvoie souvent en MAJ)
    df.columns = [c.lower() for c in df.columns]
    return df

def ensure_columns(df: pd.DataFrame, expected: set[str], ctx: str):
    if df.empty:
        st.warning(f"Aucune donnée renvoyée ({ctx}).")
        st.stop()
    missing = expected - set(df.columns)
    if missing:
        st.error(f"Colonnes manquantes pour {ctx}: {missing}\nColonnes présentes: {list(df.columns)}")
        st.dataframe(df.head())
        st.stop()

# ---------- UI ----------
st.title("🏠 Airbnb – Mini BI (dbt → Snowflake → Streamlit)")
st.caption(f"Contexte : `{SF_DATABASE}.{SF_SCHEMA}`  •  Rôle : `{SF_ROLE}`  •  WH : `{SF_WAREHOUSE}`")

with st.sidebar:
    st.markdown("### Filtres globaux")
    # Exemple de filtre: année min pour reviews (optionnel)
    # year_min = st.number_input("Année min (reviews)", min_value=2008, max_value=2030, value=2008, step=1)

tab1, tab2, tab3 = st.tabs(["💶 Prix par type", "🏨 Listings + hosts", "🌕 Pleine lune"])

# ---------- Tab 1 : Prix moyen par type ----------
with tab1:
    st.subheader("Prix moyen par type de chambre")

    sql_prices = f"""
        SELECT room_type, AVG(price) AS avg_price, COUNT(*) AS n
        FROM {SF_DATABASE}.{SF_SCHEMA}.dim_listings_w_hosts
        GROUP BY room_type
        ORDER BY avg_price DESC
    """
    df = run_df(sql_prices)
    ensure_columns(df, {"room_type", "avg_price", "n"}, "prix par type")

    # Typage
    df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce")
    df["n"] = pd.to_numeric(df["n"], errors="coerce")

    st.dataframe(df, use_container_width=True)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("room_type:N", title="Type de chambre", sort='-y'),
            y=alt.Y("avg_price:Q", title="Prix moyen"),
            tooltip=[
                alt.Tooltip("room_type:N", title="Type"),
                alt.Tooltip("avg_price:Q", title="Prix moyen", format=",.2f"),
                alt.Tooltip("n:Q", title="Nb listings", format=",.0f"),
            ],
        )
    )
    st.altair_chart(chart, use_container_width=True)

# ---------- Tab 2 : Top hosts ----------
with tab2:
    st.subheader("Top hosts (par nb de listings)")
    top_n = st.slider("Nombre de hosts", 5, 50, 10)

    sql_hosts = f"""
        SELECT host_id, host_name, COUNT(*) AS listings
        FROM {SF_DATABASE}.{SF_SCHEMA}.dim_listings_w_hosts
        GROUP BY host_id, host_name
        ORDER BY listings DESC
        LIMIT {top_n}
    """
    dfh = run_df(sql_hosts)
    ensure_columns(dfh, {"host_id", "host_name", "listings"}, "top hosts")
    dfh["listings"] = pd.to_numeric(dfh["listings"], errors="coerce")
    st.dataframe(dfh, use_container_width=True)

# ---------- Tab 3 : Pleine lune ----------
with tab3:
    st.subheader("Reviews les jours de pleine lune")

    sql_fullmoon = f"""
        SELECT r.review_date::date AS day, COUNT(*) AS reviews
        FROM {SF_DATABASE}.{SF_SCHEMA}.fct_reviews r
        JOIN {SF_DATABASE}.{SF_SCHEMA}.mart_fullmoon_reviews m
          ON r.review_date::date = m.review_date::date
        GROUP BY day
        ORDER BY day
    """
    dfm = run_df(sql_fullmoon)
    ensure_columns(dfm, {"day", "reviews"}, "pleine lune")

    dfm["reviews"] = pd.to_numeric(dfm["reviews"], errors="coerce")
    # Aperçu & ligne
    st.dataframe(dfm.head(20), use_container_width=True)

    # Streamlit line_chart attend un index temporel si on lui donne une série
    try:
        dfm_idx = dfm.set_index("day").sort_index()
        st.line_chart(dfm_idx["reviews"])
    except Exception:
        # fallback Altair si besoin
        line = (
            alt.Chart(dfm)
            .mark_line(point=True)
            .encode(
                x=alt.X("day:T", title="Jour"),
                y=alt.Y("reviews:Q", title="Nb reviews"),
                tooltip=[alt.Tooltip("day:T", title="Jour"), alt.Tooltip("reviews:Q", title="Reviews")],
            )
        )
        st.altair_chart(line, use_container_width=True)

# ---------- Footer ----------
st.caption("Données créées par dbt, stockées dans Snowflake, visualisées avec Streamlit ✨")
