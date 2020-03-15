import sys
from io import StringIO
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from collections import Counter


class Eda(object):

    def __init__(self, path: str = "./input/2020_opendatascience_poll_data.csv.gz"):
        df = pd.read_csv(path)
        self.df = df

        self._prepare_data()

    def _prepare_data(self):

        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        mapper = {
            "Your timezone (we need that to schedule post timing better)": "Timezone",
            "Work status": "Work",
            "What is your residence country (where are you from?)": "Country",
            "Data Science expertise  level": "Experience",
            "Are you satisfied with channel update frequency?": "Sat_update",
            "Are you satisfied with channel's material complexity?": "Sat_material",
            "What field are you interested in (multiple choices are possible)": "Interests",
            "How did you find out about the channel?": "How_found",
            "How likely are you going to recommend a channel to your friend or colleague?": "Recommend",
            "What’s the main reason for your score? *": "Why",
        }

        self.df = self.df.rename(columns=mapper)

        self.date_count = self.df['Timestamp'].dt.date.value_counts().sort_index(). \
            cumsum().to_frame().reset_index().rename(columns={'index': 'Date', 'Timestamp': 'Count'})

        self.countries = self.df["Country"].value_counts().to_frame().reset_index() \
            .rename(columns={"Country": "Count", "index": "Country"})
        self.countries = self.countries.sort_values(by="Country", ascending=False)

        self.countries_to_plot = self.countries.sort_values(by="Count", ascending=False)

    def plot_date_count(self):
        return px.line(self.date_count, x='Date', y='Count', title='Cummulative number of respondees by day',
                       hover_data=['Count'])

    def plot_top_countries(self, top_n: int = 18):
        countries_to_plot = self.countries_to_plot[
                            top_n::-1]  # select K countries with more responses
        fig = px.bar(countries_to_plot, x='Count', y='Country', title=f'Top {top_n} countries of the audience',
                     hover_data=['Count'], color='Count', orientation='h')
        fig.update_layout(
            yaxis_tickfont_size=10
        )
        return fig

    def plot_feature_count(self, feature: str = 'Work', title: str = ''):
        data = self.df[feature].value_counts().to_frame().reset_index().rename(
            columns={feature: "Count", "index": feature})
        data = data.sort_values(by="Count", ascending=True)
        fig = px.bar(data, x='Count', y=feature, title=title,
                     hover_data=['Count'], color='Count', orientation='h')
        fig.update_layout(
            yaxis_tickfont_size=10
        )
        return fig

    def plot_work_country(self, top_n: int = 5):
        top_k_countries = self.countries_to_plot["Country"][:top_n]
        df_top_countries = self.df.loc[self.df['Country'].isin(top_k_countries)].copy()
        mapper = {
            "Employed remotely": "Employed remotely",
            "Self-employed (freelance)": "Freelencer",
            "Student + part time job": "Worker student",
            "Self-employed (co-founder / owner)": "Self-employed",
            "Student": "Student",
            "Unemployed": "Unemployed",
            "Employed": "Employed",
            "Student + part time remote job": "Remote Worker student"
        }
        df_top_countries["Work"] = df_top_countries["Work"].map(mapper)

        fig = px.violin(df_top_countries, y="Work", x="Country", title="Relationship between country and work status",
                        hover_data=self.df.columns)
        return fig

    def plot_age(self):
        top_k_countries = self.countries_to_plot["Country"][:5]
        df_top_countries = self.df.loc[self.df['Country'].isin(top_k_countries)].copy()
        df_top_countries_by_age = df_top_countries.sort_values(by="Age", ascending=True)
        return px.violin(df_top_countries_by_age, y="Age", x="Country", title="Relationship between countries and age",
                         hover_data=self.df.columns)

    def plot_age_experience(self):
        return sns.catplot("Age", col="Experience", col_wrap=3, data=self.df, kind="count", size=3, aspect=1.4,
                           order=['18-', '18-24', '25-30', '31-42', '42+'])

    def plot_satistaction(self):
        mapper = {
            "Need more beginners' stuff": "Too complex",
            "Need more specific and complicated materials": "Too simple",
            "It's all ok": "Perfect"
        }

        self.df["Sat_material"] = self.df["Sat_material"].map(mapper)
        return px.violin(self.df, y="Sat_material", x="Work", hover_data=self.df.columns,
                         title='Distribution of satisfaction for material complexity')

    def display_wordcloud_image(self, feature: str = ''):
        text = ' '.join(self.df[feature].values)
        """Function for displaying wordcloud of the provided text."""
        plt.figure(figsize=(12, 8))
        wordcloud = WordCloud(max_font_size=None, background_color='white', collocations=True,
                              width=1200, height=1000).generate(text)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()

    def plot_countries_interests(self, top_n: int = 4):
        top_k_countries = self.countries_to_plot["Country"][-top_n:]
        df_top_countries = self.df.loc[self.df['Country'].isin(top_k_countries)].copy()

        specs = [[{'type': 'domain'}, {'type': 'domain'}], [{'type': 'domain'}, {'type': 'domain'}]]

        def countries_groupper(x):
            """Groups countries."""
            # will looks like: [('#WhereToStart', 81), ('#EntryLevel', 81), ('#Novice', 81)]
            most_common = Counter(x["Interests"].sum().split()).most_common(3)
            # extract the first element, the label
            labels = [e[0] for e in most_common]
            # extract the second element, the value
            values = [e[1] for e in most_common]

            return labels, values

        g = df_top_countries.groupby("Country").apply(countries_groupper)

        fig = None
        r, c = 1, 1  # stands for row and column
        for country, (label, value) in zip(g.index, g.values):

            if fig is None:
                fig = make_subplots(rows=2, cols=2, specs=specs,
                                    subplot_titles=g.index)  # we create a grid of 2x2. Each cell will contain a plot

            fig.add_trace(go.Pie(labels=label, values=value), r, c)
            c = c + 1  # to place correcly each subplot into the 2x2 grid
            if c % 3 == 0:
                r = r + 1
                c = 1

        # Tune layout
        fig.update(layout_title_text='Distribution of top 3 topics in the 4 top countries',
                   layout_showlegend=True)
        fig = go.Figure(fig)
        return fig
