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
    # Snowflake renvoie souvent en MAJ → on met en minuscules
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
    # (exemple futur)

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

# ---------- Tab 3 : Pleine lune – distribution des sentiments ----------
with tab3:
    st.subheader("Distribution des sentiments selon la pleine lune")

    sql_moon = f"""
        WITH counts AS (
            SELECT
                LOWER(TRIM(is_full_moon))      AS moon_flag,
                LOWER(TRIM(review_sentiment))   AS review_sentiment,
                COUNT(*)                        AS n
            FROM {SF_DATABASE}.{SF_SCHEMA}.mart_fullmoon_reviews
            WHERE review_sentiment IS NOT NULL
            GROUP BY 1,2
        ),
        totals AS (
            SELECT moon_flag, SUM(n) AS total
            FROM counts
            GROUP BY 1
        )
        SELECT
            c.moon_flag,
            c.review_sentiment,
            c.n,
            t.total,
            c.n / NULLIF(t.total,0)::float AS pct
        FROM counts c
        JOIN totals t USING (moon_flag)
        ORDER BY c.moon_flag, c.review_sentiment;
    """

    dfm = run_df(sql_moon)
    ensure_columns(dfm, {"moon_flag", "review_sentiment", "n", "total", "pct"}, "full moon sentiments")

    # Typage
    dfm["n"] = pd.to_numeric(dfm["n"], errors="coerce")
    dfm["total"] = pd.to_numeric(dfm["total"], errors="coerce")
    dfm["pct"] = pd.to_numeric(dfm["pct"], errors="coerce")

    col_l, col_r = st.columns([1, 2], gap="large")

    # ----- Tableau de proportions -----
    with col_l:
        st.markdown("**Proportion des sentiments (%)**")
        st.dataframe(
            dfm.assign(pct=lambda d: (d["pct"] * 100).round(2))
               .pivot(index="review_sentiment", columns="moon_flag", values="pct")
               .fillna(0.0)
               .sort_index(),
            use_container_width=True,
        )
        st.caption("Proportion par sentiment au sein de chaque groupe (Full / Not full).")

    # ----- Graphique empilé -----
    with col_r:
        st.markdown("**Répartition 100 % empilée**")
        chart_moon = (
            alt.Chart(dfm)
            .mark_bar()
            .encode(
                x=alt.X("moon_flag:N", title="Phase de lune"),
                y=alt.Y("pct:Q", title="Proportion", axis=alt.Axis(format="%")),
                color=alt.Color("review_sentiment:N", title="Sentiment"),
                tooltip=[
                    alt.Tooltip("moon_flag:N", title="Phase"),
                    alt.Tooltip("review_sentiment:N", title="Sentiment"),
                    alt.Tooltip("n:Q", title="Compteur", format=",.0f"),
                    alt.Tooltip("pct:Q", title="Proportion", format=".1%"),
                ],
            )
        )
        st.altair_chart(chart_moon, use_container_width=True)

    # ----- Test de proportion pour avis positifs -----
    import math

    pivot = dfm.pivot(index="review_sentiment", columns="moon_flag", values="n").fillna(0)
    n_pos_full  = pivot.loc["positive", "full moon"]     if "positive" in pivot.index and "full moon" in pivot.columns else 0
    n_tot_full  = dfm.loc[dfm["moon_flag"] == "full moon", "n"].sum()
    n_pos_not   = pivot.loc["positive", "not full moon"] if "positive" in pivot.index and "not full moon" in pivot.columns else 0
    n_tot_not   = dfm.loc[dfm["moon_flag"] == "not full moon", "n"].sum()

    if n_tot_full > 0 and n_tot_not > 0:
        p1 = n_pos_full / n_tot_full
        p2 = n_pos_not / n_tot_not
        p  = (n_pos_full + n_pos_not) / (n_tot_full + n_tot_not)
        se = math.sqrt(p * (1 - p) * (1/n_tot_full + 1/n_tot_not))
        z  = (p1 - p2) / se if se > 0 else float("nan")

        st.markdown("### Comparaison du taux d’avis positifs")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Full moon – % positifs", f"{p1*100:.2f}%")
        col_b.metric("Not full moon – % positifs", f"{p2*100:.2f}%")
        col_c.metric("Z-score (diff proportions)", f"{z:.2f}")
        st.caption("Règle : |z| > 1.96 ≈ différence significative à 5 % (approximation large).")
    else:
        st.info("Impossible de calculer le test : effectifs insuffisants.")

# ---------- Footer ----------
st.caption("Données créées par dbt, stockées dans Snowflake, visualisées avec Streamlit ✨")
