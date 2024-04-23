import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from plotly.subplots import make_subplots
import base64, os
import google.generativeai as genai

api_key = os.environ.get("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")


# Function to generate content with insights
def generate_content_with_insights(document, df):
    combined_content = f"{document}\n\n{df.to_string()}"
    response = model.generate_content(combined_content)
    return response


# Function to generate statement based on data
def generate_statement(df, mal_type):
    try:
        if mal_type == "Mean":
            mal_type = "Mean Malnutrition (Stunting+Wasting) Children"

        document = f"Provide Insight about this Data, Malnutrition - Children Under 5 Type is: {mal_type}:"
        response = generate_content_with_insights(document, df)
        return response.text
    except Exception as e:
        return "Could not generate insight"


# Function to load data from CSV file
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df


# Function to create histograms
def create_histograms(data_list, titles, colors):
    fig = go.Figure()

    for data, title, color in zip(data_list, titles, colors):
        fig.add_trace(
            go.Histogram(
                x=data.iloc[:, 0],
                name=title,
                marker=dict(color=color),
                opacity=0.7,
                marker_line_color="black",
            )
        )

    fig.update_layout(
        barmode="overlay",
        title="World's Children Malnutrition Histogram",
        title_font_size=20,
        xaxis_title="Percentage",
        yaxis_title="Number of Countries",
    )

    return fig


# Function to create malnutrition histograms
def create_malnutrition_histogram(df):
    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Mean Malnutrition Percentage",
            "Overweight Percentage",
            "Wasting Percentage",
            "Stunting Percentage",
        ),
    )

    # Add histograms to each subplot
    fig.add_trace(
        go.Histogram(
            x=df["Mean"],
            marker=dict(color="lightblue"),
            opacity=0.7,
            marker_line_color="black",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Histogram(
            x=df["Overweight"],
            marker=dict(color="lightgreen"),
            opacity=0.7,
            marker_line_color="black",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Histogram(
            x=df["Wasting"],
            marker=dict(color="lightcoral"),
            opacity=0.7,
            marker_line_color="black",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Histogram(
            x=df["Stunting"],
            marker=dict(color="lightskyblue"),
            opacity=0.7,
            marker_line_color="black",
        ),
        row=2,
        col=2,
    )

    # Update layout
    fig.update_layout(
        title="World's Children Malnutrition Histogram",
        title_font_size=20,
        height=600,
        width=800,
    )

    # Update x and y axis labels
    fig.update_xaxes(title_text="Mean Malnutrition Percentage", row=1, col=1)
    fig.update_xaxes(title_text="Overweight Percentage", row=1, col=2)
    fig.update_xaxes(title_text="Wasting Percentage", row=2, col=1)
    fig.update_xaxes(title_text="Stunting Percentage", row=2, col=2)

    fig.update_yaxes(title_text="Number of Countries", row=1, col=1)
    fig.update_yaxes(title_text="Number of Countries", row=1, col=2)
    fig.update_yaxes(title_text="Number of Countries", row=2, col=1)
    fig.update_yaxes(title_text="Number of Countries", row=2, col=2)

    return fig


# Function to create malnutrition boxplot
def create_malnutrition_boxplot(
    combined_df, mal_type=["Mean", "Overweight", "Wasting", "Stunting"]
):
    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Mean Malnutrition", "Overweight", "Waste", "Stunt"),
    )

    # Add boxplots to the subplots
    fig.add_trace(
        go.Box(y=combined_df[mal_type[0]], name="Mean Malnutrition"), row=1, col=1
    )
    fig.add_trace(go.Box(y=combined_df[mal_type[1]], name="Overweight"), row=1, col=2)
    fig.add_trace(go.Box(y=combined_df[mal_type[2]], name="Waste"), row=2, col=1)
    fig.add_trace(go.Box(y=combined_df[mal_type[3]], name="Stunt"), row=2, col=2)

    # Update layout
    fig.update_layout(title="World's Children Malnutrition Boxplot")

    # Update axis labels
    fig.update_xaxes(title_text="Malnutrition Type", row=1, col=1)
    fig.update_xaxes(title_text="Malnutrition Type", row=1, col=2)
    fig.update_xaxes(title_text="Malnutrition Type", row=2, col=1)
    fig.update_xaxes(title_text="Malnutrition Type", row=2, col=2)

    fig.update_yaxes(title_text="Percentage", row=1, col=1)
    fig.update_yaxes(title_text="Percentage", row=1, col=2)
    fig.update_yaxes(title_text="Percentage", row=2, col=1)
    fig.update_yaxes(title_text="Percentage", row=2, col=2)

    return fig


# Function to create heatmap
def create_heatmap(df):
    # Selecting the required columns
    selected_columns = ["Year", "Overweight", "Stunting", "Mean", "Wasting"]
    selected_corr = df[selected_columns].corr()

    # Define heatmap
    heatmap = go.Heatmap(
        z=selected_corr.values,
        x=selected_corr.index.values,
        y=selected_corr.columns.values,
        colorscale="Blues",
        colorbar=dict(title="Correlation"),
        zmin=-1,
        zmax=1,
    )

    # Add text annotations
    annotations = []
    for i, row in enumerate(selected_corr.index):
        for j, col in enumerate(selected_corr.columns):
            annotations.append(
                dict(
                    x=col,
                    y=row,
                    text=str(round(selected_corr.iloc[i, j], 2)),
                    font=dict(
                        color="white" if selected_corr.iloc[i, j] > 0.5 else "black"
                    ),
                    showarrow=False,
                )
            )

    # Create layout
    layout = go.Layout(
        title="Correlation heatmap for selected malnutrition types",
        titlefont=dict(size=20),
        xaxis=dict(title="Malnutrition Types"),
        yaxis=dict(title="Malnutrition Types"),
        annotations=annotations,
        height=600,
        width=600,
    )

    # Create figure
    fig = go.Figure(data=[heatmap], layout=layout)
    return fig


# Function to perform K-means clustering
def kmeans_clustering(combined_df, start_year, end_year):
    # Filter data based on the specified year range
    filtered_df = combined_df[
        (combined_df["Year"] >= start_year) & (combined_df["Year"] <= end_year)
    ]
    # Group by country and calculate the means for specific columns
    country_means_df = (
        filtered_df.groupby(["ISO", "Country Name"])[
            ["Overweight", "Wasting", "Stunting", "Mean"]
        ]
        .mean()
        .reset_index()
    )

    # Select numeric columns for clustering
    numeric_columns = ["Overweight", "Wasting", "Stunting", "Mean"]
    # Drop rows with NaN values
    country_means_df = country_means_df.dropna(subset=numeric_columns)

    if country_means_df.empty:
        st.warning("No data available for clustering in the selected year range.")
        return

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(country_means_df[numeric_columns])

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(scaled_data)

    # Get cluster assignments
    labels = kmeans.labels_

    # Add cluster labels to the DataFrame
    country_means_df["Cluster"] = labels

    # Plot the data using Plotly
    fig = px.scatter(
        country_means_df,
        x="Stunting",
        y="Wasting",
        color="Cluster",
        title=f"K-Means Clustering of Countries ({start_year}-{end_year})",
        labels={"Wasting": "Waste Percentage", "Stunting": "Stunt Percentage"},
        template="plotly_white",
        hover_name="Country Name",
    )
    fig.update_layout(
        title=f"K-Means Clustering of Countries ({start_year}-{end_year})",
        height=800,
        width=800,
    )

    # Render the plot in Streamlit
    st.plotly_chart(fig)


# Function to predict and display values
def predict_and_display(country_name, mean_type, data):
    # Function to predict values for a country and type of analysis
    def predict_country_values(country_name, mean_type, data):
        # Filter data for the specified country
        country_data = data[
            (data["Country Name"] == country_name) & (data["Sex"] == 999)
        ]

        # Train a linear regression model
        X = country_data[["Year"]]

        if mean_type == "Stunting":
            y = country_data["Stunting"]
        elif mean_type == "Wasting":
            y = country_data["Wasting"]
        elif mean_type == "Overweight":
            y = country_data["Overweight"]
        else:  # Default to 'Mean'
            y = country_data["Mean"]

        linear_model = LinearRegression()
        linear_model.fit(X, y)

        # Predict for the next 10 years using linear regression
        future_years = pd.DataFrame(
            {
                "Year": range(
                    country_data["Year"].max() + 1, country_data["Year"].max() + 11
                )
            }
        )
        linear_predictions = linear_model.predict(future_years)

        # Train an ARIMA model
        arima_model = ARIMA(y, order=(5, 1, 0))  # Example ARIMA order, adjust as needed
        arima_fitted_model = arima_model.fit()

        # Predict for the next 10 years using ARIMA
        arima_predictions = arima_fitted_model.forecast(steps=10)

        return linear_predictions, arima_predictions, country_data

    # Load data
    combined_df = data.copy()

    # Predict values
    linear_preds, arima_preds, country_data = predict_country_values(
        country_name, mean_type, combined_df
    )

    # Plot predictions
    linear_prediction_years = list(
        range(country_data["Year"].max() + 1, country_data["Year"].max() + 11)
    )

    # Create subplots
    fig = make_subplots(
        rows=1,
        cols=1,
        subplot_titles=(f"Predictions for {mean_type} in {country_name}"),
    )

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=country_data["Year"],
            y=country_data[mean_type],
            mode="lines",
            name="Actual Data",
            line=dict(color="blue"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=linear_prediction_years,
            y=linear_preds,
            mode="lines",
            name="Linear Regression Predictions",
            line=dict(color="green"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=linear_prediction_years,
            y=arima_preds,
            mode="lines",
            name="ARIMA Predictions",
            line=dict(color="red"),
        ),
        row=1,
        col=1,
    )

    # Update layout
    fig.update_layout(
        title=f"Predictions for {mean_type} in {country_name}", showlegend=True
    )

    # Show plot
    st.plotly_chart(fig)


# Function to read a file as a base64-encoded string
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Function to display a GIF
def display_gif(gif_filepath):
    with open(gif_filepath, "rb") as f:
        gif_base64 = get_base64_of_bin_file(gif_filepath)
        st.markdown(
            f'<img src="data:image/gif;base64,{gif_base64}" alt="gif" width="750">',
            unsafe_allow_html=True,
        )


# Main function to create UI and plot graphs
def main():
    st.title("Malnutrition Analysis")

    file_path = "JME_Malnutrition_Data.csv"

    # Load data from CSV file
    df = load_data(file_path)

    static_df = df.copy()
    static_df1 = df.copy()

    ## ----------------- Sidebar ----------------- ##
    # Get unique countries and analysis types
    st.sidebar.subheader("Prediction Filter")
    unique_countries = static_df1["ISO"].unique()
    analysis_types = ["Mean", "Stunting", "Wasting", "Overweight"]

    # Select box for country
    selected_country = st.sidebar.selectbox(
        "Select Country",
        options=df["Country Name"].unique(),
        index=df["Country Name"].unique().tolist().index("United States"),
    )

    # Select box for analysis type
    selected_analysis = st.sidebar.selectbox("Select Analysis Type", analysis_types)
    st.sidebar.divider()

    # Sidebar for user input
    st.sidebar.subheader("Malnutrition Filter")
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        default=["United States"],
        options=df["Country Name"].unique(),
    )

    gender_mapping = {"Male": 0, "Female": 1, "All": 999}
    selected_gender_name = st.sidebar.selectbox(
        "Select Gender", ["Male", "Female", "All"]
    )
    # Get the corresponding label from the mapping
    selected_gender = gender_mapping[selected_gender_name]
    selected_y_axis = st.sidebar.selectbox(
        "Select Y-axis",
        key="Overweight",
        options=["Overweight", "Stunting", "Wasting", "Mean"],
        index=3,
    )

    # -------------------------------------------------------#
    # ----------------- Main Page Content -------------------#

    # Filter data based on user selection
    filtered_df = df[
        (df["Country Name"].isin(selected_countries)) & (df["Sex"] == selected_gender)
    ]

    # Plot dynamic graph
    st.subheader("Dynamic Analysis Graph")
    # Call function to predict and display

    try:
        predict_and_display(selected_country, selected_analysis, static_df1)
    except ValueError:  # Adjust the exception type based on the actual exception raised
        st.warning(
            f"Not enough data available for the {selected_analysis} in the selected country."
        )

    st.subheader(
        f"Malnutrition Trend for {selected_gender_name}s in Selected Countries"
    )
    if not filtered_df.empty:
        fig = go.Figure()
        # Add lines for Table 1
        for country in selected_countries:
            temp_df = filtered_df[filtered_df["Country Name"] == country]
            fig.add_trace(
                go.Scatter(
                    x=temp_df["Year"],
                    y=temp_df[selected_y_axis],
                    mode="lines",
                    name=f"{country}",
                )
            )
        # Update layout
        fig.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title=selected_y_axis),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig)
        if st.button("Analyse the Graph."):
            with st.spinner("Analysing the data, It might take few seconds..."):
                statement = generate_statement(filtered_df, selected_y_axis)
                st.write(statement)
    else:
        st.warning(
            f"No data available for the selected {selected_gender_name}s in the selected countries."
        )

    st.divider()
    # Plot static bar graphs
    st.header("Static Analysis Graphs")
    st.plotly_chart(
        create_histograms(
            [
                static_df[["Mean"]],
                static_df[["Overweight"]],
                static_df[["Wasting"]],
                static_df[["Stunting"]],
            ],
            ["Mean Malnutrition", "Overweight", "Waste", "Stunt"],
            ["deepskyblue", "royalblue", "orange", "forestgreen"],
        )
    )
    st.plotly_chart(create_malnutrition_histogram(static_df))
    st.plotly_chart(create_malnutrition_boxplot(static_df))
    st.plotly_chart(create_heatmap(static_df))

    st.divider()
    st.subheader(
        f"K Mean Clustering of Countries based on Malnutrition Types for Different Year Ranges"
    )
    # Call the function for different year ranges
    kmeans_clustering(static_df, 1990, 1995)
    kmeans_clustering(static_df, 1995, 2001)
    kmeans_clustering(static_df, 2000, 2005)
    kmeans_clustering(static_df, 2006, 2010)
    kmeans_clustering(static_df, 2011, 2015)
    kmeans_clustering(static_df, 2016, 2021)
    kmeans_clustering(static_df, df["Year"].min(), static_df["Year"].max())

    st.subheader(
        "Overweight: Percentage of children who are overweight in countries 1986 - 2021"
    )
    display_gif("assets/overweight.gif")
    st.subheader(
        "Stunting: Percentage of children who are stunted in countries 1986 - 2021"
    )
    display_gif("assets/stunt.gif")
    st.subheader(
        "Wasting: Percentage of children who are wasted in countries 1986 - 2021"
    )
    display_gif("assets/waste.gif")


if __name__ == "__main__":
    main()
