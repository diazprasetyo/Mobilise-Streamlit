import streamlit as st
import pandas as pd
import plotly.express as px

# ----------- LOAD MERGED DATA -----------
@st.cache_data
def load_data():
    df_merged = pd.read_csv('data/clean_MERGED_All_Data.csv')
    return df_merged

df_merged = load_data()

# ----------- SIDEBAR NAVIGATION -----------
st.sidebar.title("Mobilise Kickstarter Dashboard")
page = st.sidebar.radio(
    "Go to Page:",
    (
        "1. Program Reach & Demographics",
        "2. Housing Stability & Outcomes",
        "3. Financial & Social Impact"
    )
)

st.title("Mobilise Kickstarter Program Dashboard")

if page == "1. Program Reach & Demographics":
    # ----------- PAGE 1 VISUALISATION CODE -----------
    with st.sidebar.expander("Filter Participants"):
        gender_options = df_merged['ZAPIER_Gender'].dropna().unique().tolist() if 'ZAPIER_Gender' in df_merged else []
        org_options = df_merged['Organisation Code'].dropna().unique().tolist() if 'Organisation Code' in df_merged else []
        age_group_options = df_merged['ZAPIER_Age Group'].dropna().unique().tolist() if 'ZAPIER_Age Group' in df_merged else []
        state_options = df_merged['State Code'].dropna().unique().tolist()

        selected_genders = st.multiselect("Gender", gender_options, default=gender_options)
        selected_orgs = st.multiselect("Referral Org", org_options, default=org_options)
        selected_age_groups = st.multiselect("Age Group", age_group_options, default=age_group_options)
        selected_states = st.multiselect("State Code", state_options, default=state_options)

    df_filtered = df_merged[
        df_merged['ZAPIER_Gender'].isin(selected_genders) &
        df_merged['Organisation Code'].isin(selected_orgs) &
        df_merged['ZAPIER_Age Group'].isin(selected_age_groups) &
        df_merged['State Code'].isin(selected_states)
    ]

    st.header("1. Program Reach & Demographics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Participants", df_merged['IDENTIFIER'].nunique())
    col2.metric("Avg. Age", f"{df_filtered['ZAPIER_Age'].mean():.1f}" if not df_filtered.empty else "N/A")
    col3.metric("Avg. Dependents", f"{df_filtered['ZAPIER_Dependents'].mean():.2f}" if not df_filtered.empty else "N/A")
    col4.metric("Org Count", df_filtered['Organisation Code'].nunique())

    st.divider()
    st.subheader("Age Distribution")
    if not df_filtered.empty and 'ZAPIER_Age' in df_filtered.columns:
        st.bar_chart(df_filtered['ZAPIER_Age'].value_counts().sort_index())
    st.subheader("Gender Distribution")
    if not df_filtered.empty and 'ZAPIER_Gender' in df_filtered.columns:
        gender_counts = df_filtered['ZAPIER_Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(
            gender_counts,
            names='Gender',
            values='Count',
            title='Gender Distribution of Participants',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Participants by State")
    if not df_filtered.empty and 'State Code' in df_filtered.columns:
        state_counts = df_filtered['State Code'].value_counts().sort_index()
        import plotly.express as px
        fig_state = px.bar(
            x=state_counts.index.astype(str),
            y=state_counts.values,
            labels={'x': 'State Code', 'y': 'Participants'},
            title='Participant Distribution by State'
        )
        fig_state.update_layout(xaxis_tickangle=0)
        st.plotly_chart(fig_state, use_container_width=True)
    st.subheader("Number of Dependents")
    if not df_filtered.empty and 'ZAPIER_Dependents' in df_filtered.columns:
        st.bar_chart(df_filtered['ZAPIER_Dependents'].value_counts().sort_index())
    st.subheader("Program Uptake by Referral Org")
    if not df_filtered.empty and 'Organisation Code' in df_filtered.columns:
        st.bar_chart(df_filtered['Organisation Code'].value_counts())
    st.subheader("Entry Rent & Income (Scatter)")
    if not df_filtered.empty and 'Total monthly rent' in df_filtered.columns and 'Monthly Income' in df_filtered.columns:
        st.caption("Each point is a participant (filtered)")
        st.scatter_chart(df_filtered[['Total monthly rent', 'Monthly Income']].dropna())
    col5, col6 = st.columns(2)
    col5.metric("Avg. Monthly Rent", f"${df_filtered['Total monthly rent'].mean():.2f}" if not df_filtered.empty else "N/A")
    col6.metric("Avg. Monthly Income", f"${df_filtered['Monthly Income'].mean():.2f}" if not df_filtered.empty else "N/A")
    st.info("All metrics and charts update based on sidebar filters.")

elif page == "2. Housing Stability & Outcomes":
    st.header("2. Housing Stability & Participant Outcomes")

    # --- FILTERS (reuse from page 1 for consistency) ---
    with st.sidebar.expander("Filter Participants"):
        gender_options = df_merged['ZAPIER_Gender'].dropna().unique().tolist() if 'ZAPIER_Gender' in df_merged else []
        org_options = df_merged['Organisation Code'].dropna().unique().tolist() if 'Organisation Code' in df_merged else []
        age_group_options = df_merged['ZAPIER_Age Group'].dropna().unique().tolist() if 'ZAPIER_Age Group' in df_merged else []
        selected_genders = st.multiselect("Gender", gender_options, default=gender_options)
        selected_orgs = st.multiselect("Referral Org", org_options, default=org_options)
        selected_age_groups = st.multiselect("Age Group", age_group_options, default=age_group_options)

    df_filtered = df_merged[
        df_merged['ZAPIER_Gender'].isin(selected_genders) &
        df_merged['Organisation Code'].isin(selected_orgs) &
        df_merged['ZAPIER_Age Group'].isin(selected_age_groups)
    ]

    # --- 1. % Still Housed (3mo/6mo) ---
    st.subheader("% Still Housed (3 and 6 months)")
    col1, col2 = st.columns(2)
    # 3 Months
    if 'SM3_I am still living in the same property that I was when I got approved for Kickstarter' in df_filtered.columns:
        sm3_housed = df_filtered['SM3_I am still living in the same property that I was when I got approved for Kickstarter']
        housed_3mo = sm3_housed.str.lower().eq('yes').sum()
        total_3mo = sm3_housed[sm3_housed != "No"].count()  # Count only non-"No" responses
        pct_3mo = (housed_3mo / total_3mo * 100) if total_3mo > 0 else 0
        col1.metric("Still Housed (3mo)", f"{pct_3mo:.1f}% ({housed_3mo}/{total_3mo})")
    # 6 Months
    if 'SM6_I am still living in the same property that I was when I got approved for Kickstarter2' in df_filtered.columns:
        sm6_housed = df_filtered['SM6_I am still living in the same property that I was when I got approved for Kickstarter2']
        housed_6mo = sm6_housed.str.lower().eq('yes').sum()
        total_6mo = sm6_housed[sm6_housed != "No"].count()
        pct_6mo = (housed_6mo / total_6mo * 100) if total_6mo > 0 else 0
        col2.metric("Still Housed (6mo)", f"{pct_6mo:.1f}% ({housed_6mo}/{total_6mo})")

    st.divider()

    # --- 2. Housing Situation (3mo/6mo) ---
    st.subheader("Housing Situation (3mo/6mo)")
    import plotly.express as px
    # 3 Months
    col3, col4 = st.columns(2)
    col_name_3mo = 'SM3_Which best describes where you are now living?This helps us understand if/how the Kickstarter payments have helped you.'
    col_name_6mo = 'SM6_Which best describes where you are now living?This helps us understand if/how the Kickstarter payments have helped you. The answer to your question will not affect your survey payment.'
    if col_name_3mo in df_filtered.columns:
        counts3 = df_filtered[col_name_3mo].value_counts()
        fig3 = px.bar(
            x=counts3.index.astype(str),
            y=counts3.values,
            labels={'x': 'Housing Situation (3mo)', 'y': 'Count'},
            title='Housing Situation (3 Months)'
        )
        fig3.update_layout(xaxis_tickangle=30)
        col3.plotly_chart(fig3, use_container_width=True)
    # 6 Months
    if col_name_6mo in df_filtered.columns:
        counts6 = df_filtered[col_name_6mo].value_counts()
        fig6 = px.bar(
            x=counts6.index.astype(str),
            y=counts6.values,
            labels={'x': 'Housing Situation (6mo)', 'y': 'Count'},
            title='Housing Situation (6 Months)'
        )
        fig6.update_layout(xaxis_tickangle=30)
        col4.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # --- 3. Rent Affordability (3mo/6mo) ---
    st.subheader("Rent Affordability (3mo/6mo)")
    col5, col6 = st.columns(2)
    col_ra_3 = 'SM3_I feel I could pay my rent now, without getting an extra boost via the Kickstarter program.'
    col_ra_6 = 'SM6_I feel my current rent is affordable for me.'
    if col_ra_3 in df_filtered.columns:
        yes3 = df_filtered[col_ra_3].str.lower().eq('yes').sum()
        tot3 = df_filtered[col_ra_3][df_filtered[col_ra_3] != "No"].count()
        pct3 = (yes3 / tot3 * 100) if tot3 > 0 else 0
        col5.metric("Rent Affordable (3mo)", f"{pct3:.1f}% ({yes3}/{tot3})")
    if col_ra_6 in df_filtered.columns:
        yes6 = df_filtered[col_ra_6].str.lower().eq('yes').sum()
        tot6 = df_filtered[col_ra_6][df_filtered[col_ra_6] != "No"].count()
        pct6 = (yes6 / tot6 * 100) if tot6 > 0 else 0
        col6.metric("Rent Affordable (6mo)", f"{pct6:.1f}% ({yes6}/{tot6})")

    st.divider()

    # --- 4. Safety Perception (Home/Area) ---
    st.subheader("Safety Perception (Home/Area)")
    col7, col8 = st.columns(2)
    # 3 Months: Home
    col_home3 = 'SM3_I feel safe in my current home:'
    if col_home3 in df_filtered.columns:
        valc = df_filtered[col_home3].value_counts()
        top = valc.get("Always", 0) + valc.get("Usually", 0)
        total = valc.sum()
        pct = (top / total * 100) if total > 0 else 0
        col7.metric("Feel Safe at Home (3mo)", f"{pct:.1f}%")
        fig = px.bar(valc, title="Safety at Home (3mo)")
        col7.plotly_chart(fig, use_container_width=True)
    # 3 Months: Area
    col_area3 = 'SM3_I feel safe in the area I live:'
    if col_area3 in df_filtered.columns:
        valc = df_filtered[col_area3].value_counts()
        top = valc.get("Always", 0) + valc.get("Usually", 0)
        total = valc.sum()
        pct = (top / total * 100) if total > 0 else 0
        col8.metric("Feel Safe in Area (3mo)", f"{pct:.1f}%")
        fig = px.bar(valc, title="Safety in Area (3mo)")
        col8.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 5. Confidence Paying Rent (3mo/6mo) ---
    st.subheader("Confidence Paying Rent (3mo/6mo)")
    col9, col10 = st.columns(2)
    col_conf3 = 'SM3_I feel I could pay my rent now, without getting an extra boost via the Kickstarter program.'
    col_conf6 = 'SM6_I feel my current rent is affordable for me.'
    if col_conf3 in df_filtered.columns:
        yes = df_filtered[col_conf3].str.lower().eq('yes').sum()
        tot = df_filtered[col_conf3][df_filtered[col_conf3] != "No"].count()
        pct = (yes / tot * 100) if tot > 0 else 0
        col9.metric("Confident Paying Rent (3mo)", f"{pct:.1f}% ({yes}/{tot})")
    if col_conf6 in df_filtered.columns:
        yes = df_filtered[col_conf6].str.lower().eq('yes').sum()
        tot = df_filtered[col_conf6][df_filtered[col_conf6] != "No"].count()
        pct = (yes / tot * 100) if tot > 0 else 0
        col10.metric("Confident Paying Rent (6mo)", f"{pct:.1f}% ({yes}/{tot})")

    st.info("All metrics and charts update based on sidebar filters.")

elif page == "3. Financial & Social Impact":
    st.header("3. Financial & Social Impact")

    # --- FILTERS (reuse from page 1 for consistency) ---
    with st.sidebar.expander("Filter Participants"):
        gender_options = df_merged['ZAPIER_Gender'].dropna().unique().tolist() if 'ZAPIER_Gender' in df_merged else []
        org_options = df_merged['Organisation Code'].dropna().unique().tolist() if 'Organisation Code' in df_merged else []
        age_group_options = df_merged['ZAPIER_Age Group'].dropna().unique().tolist() if 'ZAPIER_Age Group' in df_merged else []
        selected_genders = st.multiselect("Gender", gender_options, default=gender_options)
        selected_orgs = st.multiselect("Referral Org", org_options, default=org_options)
        selected_age_groups = st.multiselect("Age Group", age_group_options, default=age_group_options)

    df_filtered = df_merged[
        df_merged['ZAPIER_Gender'].isin(selected_genders) &
        df_merged['Organisation Code'].isin(selected_orgs) &
        df_merged['ZAPIER_Age Group'].isin(selected_age_groups)
    ]

    # --- 1. Total Rent/Bond Disbursed ---
    st.subheader("Total Rent/Bond Disbursed")
    total_disbursed = df_filtered['ZAPIER_Total Bill Amount'].sum() if 'ZAPIER_Total Bill Amount' in df_filtered else 0
    st.metric("Total Disbursed", f"${total_disbursed:,.2f}")

    # Histogram of Disbursed Amount
    st.subheader("Distribution of Rent/Bond Disbursed")
    if 'ZAPIER_Total Bill Amount' in df_filtered:
        import plotly.express as px
        disbursed = df_filtered['ZAPIER_Total Bill Amount'].dropna()
        fig = px.histogram(disbursed, nbins=20, labels={'value': 'Disbursed Amount'}, title="Distribution of Individual Disbursed Amounts")
        st.plotly_chart(fig, use_container_width=True)

    # --- 2. % Improved Bill Payment Ability (or % not struggling, as fallback) ---
    st.subheader("% Improved Bill Payment Ability")
    # If you have an explicit "improved" column, use that; else show % NOT struggling to pay bills
    improvement_col = 'SM3_How do you feel about having enough money to pay your rent and cover all your other important expenses with what you currently have?'
    if improvement_col in df_filtered:
        # Example mapping: 3 = "I now feel I have it covered"
        improved = df_filtered[improvement_col].astype(str).str.contains("cover", case=False).sum()
        total = df_filtered[improvement_col].notna().sum()
        pct = (improved / total * 100) if total > 0 else 0
        st.metric("% Reporting Improved Ability", f"{pct:.1f}% ({improved}/{total})")
    else:
        # Fallback: show % NOT reporting bill struggles (all SM3_* bill cols)
        bill_cols = [
            'SM3_Electricity, gas or phone bill - No money to pay bills last 2 month',
            'SM3_Car repair, rego or insurance  - No money to pay bills last 2 month',
            'SM3_Food  - No money to pay bills last 2 month',
            'SM3_Credit card balance or debts, e.g. Afterpay  - No money to pay bills last 2 month',
            'SM3_All expenses  - No money to pay bills last 2 month'
        ]
        struggle_any = df_filtered[bill_cols].apply(lambda row: (row.astype(str).str.lower() == 'yes').any(), axis=1)
        pct_not_struggle = 100 - struggle_any.mean() * 100
        st.metric("% Not Struggling to Pay Bills", f"{pct_not_struggle:.1f}%")

    # --- 3. Essential Items/Volunteer Interactions ---
    st.subheader("Essential Items & Volunteer Interactions")
    # Essential items
    if 'Essential items count' in df_filtered:
        st.metric("Essential Items Provided", int(df_filtered['Essential items count'].sum()))
    else:
        st.info("Essential items data not available in uploaded data.")

    # Volunteer Interactions
    if 'Volunteer interactions' in df_filtered:
        st.metric("Volunteer Interactions", int(df_filtered['Volunteer interactions'].sum()))
    else:
        st.info("Volunteer interaction data not available in uploaded data.")

    # --- 4. Participant Feedback ---
    st.subheader("Participant Feedback (Financial Confidence, 3mo Survey)")
    feedback_col = 'SM3_How do you feel about having enough money to pay your rent and cover all your other important expenses with what you currently have?'
    if feedback_col in df_filtered.columns:
        feedback_counts = df_filtered[feedback_col].value_counts()
        import plotly.express as px
        feedback_fig = px.pie(
            values=feedback_counts.values,
            names=feedback_counts.index,
            title="Participants' Financial Confidence (3mo Survey)"
        )
        st.plotly_chart(feedback_fig, use_container_width=True)
    else:
        st.info("No financial confidence feedback found.")

    st.info("All metrics and charts update based on sidebar filters.")

st.markdown("---")
st.caption("Use the sidebar to navigate. More features and visualizations coming soon!")
