# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter

st.set_page_config(layout="wide")

# Inject external CSS file

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")


st.title("🎬 Netflix Data Analysis Dashboard")
st.markdown("An interactive dashboard to analyze and visualize Netflix content using Python and Streamlit.")


@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = df['date_added'].astype(str).str.strip()
    df['date_added'] = pd.to_datetime(df['date_added'], format='mixed', errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    df['listed_in'] = df['listed_in'].fillna('Unknown')
    df['type'] = df['type'].fillna('Unknown')
    df['title'] = df['title'].fillna('')
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    return df
df = load_data()


# Sidebar filters
st.sidebar.header("📌 Filters")

# Filter by content type
selected_types = st.sidebar.multiselect(
    "Select Content Type", 
    df['type'].dropna().unique(), 
    default=df['type'].dropna().unique()
)


# Filter the data based on selections
filtered = df[
    (df['type'].isin(selected_types)) 
]

# Extract release years from 'release_year' column
years = sorted(df['release_year'].unique(), reverse=True)
selected_years = st.sidebar.multiselect("Filter by Release Year", years)

# Apply filter
if selected_years:
    filtered = filtered[filtered['release_year'].isin(selected_years)]

# Extract countries
countries = df['country'].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect("Filter by Country", countries)

# Apply country filter
if selected_countries:
    filtered = filtered[filtered['country'].isin(selected_countries)]

# Cool looking metrics
st.markdown("### 🔢 Quick Stats")
col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='metric-box'>Total Titles<br>{len(df)}</div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-box'>Movies<br>{len(df[df['type']=='Movie'])}</div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-box'>TV Shows<br>{len(df[df['type']=='TV Show'])}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# ======= Tabs Section =======
tab1, tab2, tab3, tab4 = st.tabs(["🎭 Genres", "📈 Trends", "🌥️ Word Cloud","📊 Insights"])

# === TAB 1: Genres ===
with tab1:
    
    genre_list = []
    for genres in filtered['listed_in']:
        for g in genres.split(','):
            genre_list.append(g.strip())

    genre_freq = Counter(genre_list)
    genre_df = pd.DataFrame(genre_freq.items(), columns=["Genre", "Count"]).sort_values(by="Count", ascending=False)

 # Create 2 columns
    col1, col2 = st.columns(2)

# --- First Chart: Top 10 Genres ---
    with col1:
        st.subheader("Top 10 Genres")
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        sns.barplot(data=genre_df.head(10), x='Count', y='Genre', palette='Set2', ax=ax1)
        ax1.set_title("Most Frequent Genres")
        st.pyplot(fig1)

# --- Second Chart: Content Type Distribution ---
    with col2:
        st.subheader("Content Type Distribution")
        type_counts = filtered['type'].value_counts()
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        colors = ['#66B2FF', '#FF9999']
        ax2.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)


# === TAB 2: Trends ===
with tab2:
    st.subheader("Year-wise Release Trend")
    yearly = filtered['release_year'].value_counts().sort_index()
    fig3, ax3 = plt.subplots()
    yearly.plot(kind='line',marker='.', ax=ax3, color='purple')
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Number of Titles")
    st.pyplot(fig3)

    st.subheader("Release Trend Over the Years")
    year_counts = filtered['release_year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(x=year_counts.index, y=year_counts.values, ax=ax)
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Titles")
    st.pyplot(fig)


# === TAB 3: Word Cloud ===
with tab3:
    st.subheader("Word Cloud of Titles")
    title_text = ' '.join(filtered['title'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(title_text)
    fig4, ax4 = plt.subplots()
    ax4.imshow(wordcloud, interpolation='bilinear')
    ax4.axis('off')
    st.pyplot(fig4)

# === TAB 4: Insights ===

with tab4:
    st.subheader("📌 Top Genres by Country")
    genre_country = df[['country', 'listed_in']].dropna()
    genre_country['listed_in'] = genre_country['listed_in'].str.split(', ')
    genre_exploded = genre_country.explode('listed_in')

    top_grouped = genre_exploded.groupby(['country', 'listed_in']).size().reset_index(name='Count')
    top_grouped = top_grouped.sort_values(by='Count', ascending=False).head(10)

    fig5, ax5 = plt.subplots(figsize=(4, 3))
    sns.barplot(data=top_grouped, x='Count', y='listed_in', hue='country', ax=ax5)
    ax5.set_title("Top Genres by Country")
    st.pyplot(fig5)

    st.markdown("---")
    st.subheader("⏱️ Average Duration by Type")

    df_duration = df.copy()
    df_duration['duration_clean'] = df_duration['duration'].str.extract(r'(\d+)').astype(float)
    avg_duration = df_duration.groupby('type')['duration_clean'].mean().reset_index()

    fig6, ax6 = plt.subplots(figsize=(4, 3))
    sns.barplot(data=avg_duration, x='type', y='duration_clean', palette='coolwarm', ax=ax6)
    ax6.set_ylabel("Average Duration")
    ax6.set_title("Average Duration by Content Type")
    st.pyplot(fig6)

    st.markdown("---")
    st.subheader("📋 Filtered Data Table")
    st.dataframe(filtered[['title', 'type', 'country', 'release_year', 'listed_in', 'cast']].reset_index(drop=True))

