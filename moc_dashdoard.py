# import streamlit as st
# import geopandas as gpd
# import folium
# from streamlit_folium import st_folium
# from folium.plugins import MeasureControl, Draw
# import pandas as pd
# import altair as alt
# import matplotlib.pyplot as plt

# # =========================================================
# # APP CONFIG
# # =========================================================
# st.set_page_config(layout="wide", page_title="Geospatial Enterprise Solution")
# st.title("🌍 Geospatial Enterprise Solution")

# # =========================================================
# # USERS AND ROLES
# # =========================================================
# USERS = {
#     "admin": {"password": "admin2025", "role": "Admin"},
#     "customer": {"password": "cust2025", "role": "Customer"},
# }

# # =========================================================
# # SESSION INIT
# # =========================================================
# if "auth_ok" not in st.session_state:
#     st.session_state.auth_ok = False
#     st.session_state.username = None
#     st.session_state.user_role = None
#     st.session_state.points_gdf = None  # Admin CSV
#     st.session_state.concession_gdf = None  # Concession points

# # =========================================================
# # LOGOUT
# # =========================================================
# def logout():
#     st.session_state.auth_ok = False
#     st.session_state.username = None
#     st.session_state.user_role = None
#     st.session_state.points_gdf = None
#     st.session_state.concession_gdf = None
#     st.rerun()

# # =========================================================
# # LOGIN
# # =========================================================
# if not st.session_state.auth_ok:
#     st.sidebar.header("🔐 Login")
#     username = st.sidebar.selectbox("User", list(USERS.keys()))
#     password = st.sidebar.text_input("Password", type="password")
#     if st.sidebar.button("Login"):
#         if password == USERS[username]["password"]:
#             st.session_state.auth_ok = True
#             st.session_state.username = username
#             st.session_state.user_role = USERS[username]["role"]
#             st.rerun()
#         else:
#             st.sidebar.error("❌ Incorrect password")
#     st.stop()

# # =========================================================
# # LOAD SE POLYGONS
# # =========================================================
# SE_URL = "https://raw.githubusercontent.com/Moccamara/web_mapping/master/data/SE.geojson"
# CONCESSION_URL = "https://raw.githubusercontent.com/Moccamara/web_mapping/master/data/concession.geojson"

# @st.cache_data
# def load_geojson(url):
#     gdf = gpd.read_file(url)
#     if gdf.crs is None:
#         gdf = gdf.set_crs(epsg=4326)
#     else:
#         gdf = gdf.to_crs(epsg=4326)
#     gdf.columns = gdf.columns.str.lower().str.strip()
#     return gdf

# # Load SE polygons
# try:
#     gdf_se = load_geojson(SE_URL)
#     gdf_se = gdf_se.rename(columns={"lregion":"region","lcercle":"cercle","lcommune":"commune"})
#     gdf_se = gdf_se[gdf_se.is_valid & ~gdf_se.is_empty]
# except:
#     st.error("❌ Unable to load SE.geojson")
#     st.stop()

# # Load concession points
# try:
#     gdf_concession = load_geojson(CONCESSION_URL)
#     st.session_state.concession_gdf = gdf_concession
# except:
#     st.warning("⚠️ Unable to load concession.geojson")

# # =========================================================
# # SIDEBAR
# # =========================================================
# with st.sidebar:
#     st.image("logo/logo_wgv.png", width=200)
#     st.markdown(f"**Logged in as:** {st.session_state.username} ({st.session_state.user_role})")
#     if st.button("Logout"):
#         logout()

# # =========================================================
# # FILTERS (SE)
# # =========================================================
# st.sidebar.markdown("### 🗂️ Attribute Query")
# region = st.sidebar.selectbox("Region", sorted(gdf_se["region"].dropna().unique()))
# gdf_r = gdf_se[gdf_se["region"]==region]

# cercle = st.sidebar.selectbox("Cercle", sorted(gdf_r["cercle"].dropna().unique()))
# gdf_c = gdf_r[gdf_r["cercle"]==cercle]

# commune = st.sidebar.selectbox("Commune", sorted(gdf_c["commune"].dropna().unique()))
# gdf_commune = gdf_c[gdf_c["commune"]==commune]

# idse_list = ["No filter"] + sorted(gdf_commune["idse_new"].dropna().unique())
# idse_selected = st.sidebar.selectbox("Unit_Geo", idse_list)
# gdf_idse = gdf_commune if idse_selected=="No filter" else gdf_commune[gdf_commune["idse_new"]==idse_selected]

# # =========================================================
# # CSV UPLOAD (Admin only)
# # =========================================================
# if st.session_state.user_role=="Admin":
#     st.sidebar.markdown("### 📥 Upload CSV Points")
#     csv_file = st.sidebar.file_uploader("Upload CSV (LAT,LON,Masculin,Feminin)", type=["csv"])
#     if csv_file:
#         df_csv = pd.read_csv(csv_file)
#         if {"LAT","LON","Masculin","Feminin"}.issubset(df_csv.columns):
#             df_csv = df_csv.dropna(subset=["LAT","LON"])
#             points_gdf = gpd.GeoDataFrame(
#                 df_csv,
#                 geometry=gpd.points_from_xy(df_csv["LON"], df_csv["LAT"]),
#                 crs="EPSG:4326"
#             )
#             st.session_state.points_gdf = points_gdf

# points_gdf = st.session_state.get("points_gdf")
# concession_gdf = st.session_state.get("concession_gdf")

# # =========================================================
# # MAP
# # =========================================================
# minx,miny,maxx,maxy = gdf_idse.total_bounds
# m = folium.Map(location=[(miny+maxy)/2,(minx+maxx)/2], zoom_start=17)
# folium.GeoJson(
#     gdf_idse,
#     style_function=lambda x: {"color":"blue","weight":2,"fillOpacity":0.15},
#     tooltip=folium.GeoJsonTooltip(fields=["idse_new"])
# ).add_to(m)

# # Add concession points
# if concession_gdf is not None:
#     for _, r in concession_gdf.iterrows():
#         folium.CircleMarker(
#             location=[r.geometry.y,r.geometry.x],
#             radius=3, color="green", fill=True, fill_opacity=0.7
#         ).add_to(m)

# # Add uploaded points
# if points_gdf is not None:
#     for _, r in points_gdf.iterrows():
#         folium.CircleMarker(
#             location=[r.geometry.y,r.geometry.x],
#             radius=3, color="red", fill=True, fill_opacity=0.7
#         ).add_to(m)

# MeasureControl().add_to(m)
# Draw(export=True).add_to(m)

# # =========================================================
# # LAYOUT
# # =========================================================
# col_map,col_chart = st.columns((3,1), gap="small")
# with col_map:
#     st_folium(m, height=500, use_container_width=True)

# with col_chart:
#     # --- Population Bar Chart from SE ---
#     st.subheader("📊 Population per SE")
#     if gdf_idse.empty:
#         st.info("Select an SE to view population data.")
#     else:
#         df_long = gdf_idse[["idse_new","pop_se","pop_se_ct"]].melt(
#             id_vars="idse_new",
#             value_vars=["pop_se","pop_se_ct"],
#             var_name="Variable",
#             value_name="Population"
#         )
#         df_long["Variable"] = df_long["Variable"].replace({"pop_se":"Pop SE","pop_se_ct":"Pop Actu"})
#         chart = (
#             alt.Chart(df_long)
#             .mark_bar()
#             .encode(
#                 x=alt.X("idse_new:N"),
#                 y=alt.Y("Population:Q"),
#                 color=alt.Color("Variable:N"),
#                 tooltip=["idse_new","Variable","Population"]
#             )
#             .properties(height=200)
#         )
#         st.altair_chart(chart, use_container_width=True)

#     # --- Sex Pie Chart from concession points ---
#     st.subheader("👥 Sex (M / F) inside selected SE")
#     if concession_gdf is not None and not gdf_idse.empty:
#         pts_inside = gpd.sjoin(concession_gdf, gdf_idse, predicate="within")
#         if not pts_inside.empty:
#             pts_inside["Masculin"] = pd.to_numeric(pts_inside.get("Masculin",0), errors="coerce").fillna(0)
#             pts_inside["Feminin"] = pd.to_numeric(pts_inside.get("Feminin",0), errors="coerce").fillna(0)
#             m_total = int(pts_inside["Masculin"].sum())
#             f_total = int(pts_inside["Feminin"].sum())
#         else:
#             m_total, f_total = 0,0

#         st.markdown(f"""
#         - 👨 **M**: {m_total}  
#         - 👩 **F**: {f_total}  
#         - 👥 **Total**: {m_total+f_total}
#         """)

#         fig, ax = plt.subplots(figsize=(3,3))
#         if m_total+f_total>0:
#             ax.pie([m_total,f_total], labels=["M","F"], autopct="%1.1f%%", startangle=90, textprops={"fontsize":10})
#         else:
#             ax.pie([1], labels=["No data"], colors=["lightgrey"])
#         ax.axis("equal")
#         st.pyplot(fig)
#     else:
#         st.info("Concession points not loaded or SE not selected.")


# # =========================================================
# # FOOTER
# # =========================================================
# st.markdown("""
# ---
# **Geospatial Enterprise Web Mapping**  
# **Mahamadou CAMARA, PhD – Geomatics Engineering** © 2025
# """)



