import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
import os

api_key = os.environ.get("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")
geminiData = {"countryDietChange": [], "countriesNutritionTrend": []}


# Function to generate content with insights
def generate_content_with_insights(document, document1, df, df2):
    combined_content = (
        f"{document}\n\n{df.to_string()} \n {document1}\n\n{df2.to_string()}"
    )
    response = model.generate_content(combined_content)
    return response


# Function to generate statement based on data
def generate_statement(df, df2):
    # Call the function with the document and the DataFrame
    try:
        document1 = "Provide Insight about this Data - This is about Trend in Diet in select country :"
        document2 = "Provide Insight about this Data - This is about absoulte change in nutrients intake :"
        response = generate_content_with_insights(document1, document2, df, df2)
        return response.text
    except Exception as e:
        return "Could not generate insight"


# Function to load data from CSV files
def load_data(file_path1, file_path2):
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)
    return df1, df2


# Function to plot dietary changes
def plot_dietary_changes(data, start_year, end_year, country, sex):
    # Filter data for the specified range of years and country
    filtered_data = data[
        (data["Year"] >= start_year)
        & (data["Year"] <= end_year)
        & (data["Country Name"] == country)
        & (data["Sex"] == sex)
    ]

    # Group by country and Nutrition, and calculate the change in median intake
    grouped_data = (
        filtered_data.groupby(["Country Name", "ISO", "Nutrition"])["Mean"]
        .agg(lambda x: x.iloc[-1] - x.iloc[0])
        .reset_index()
    )

    # Pivot the table to have Nutrition as columns
    pivot_table = grouped_data.pivot(
        index="Nutrition", columns="Country Name", values="Mean"
    )

    geminiData["countryDietChange"].append(pivot_table)
    # Plot a bar graph for the specified country's dietary changes
    fig = px.bar(pivot_table, x=pivot_table.index, y=pivot_table[country])
    fig.update_layout(
        title=f"Dietary Changes in {country} ({start_year}-{end_year})",
        xaxis_title="Dietary Factor",
        yaxis_title="Change in Median Intake",
    )
    st.plotly_chart(fig)


def plot_choropleth(data, gdd_variable_label):
    # Filter data for the specified GDD Variable Label and all genders
    filtered_data = data[
        (data["Sex"] == 999) & (data["Nutrition"] == gdd_variable_label)
    ]

    # Create the choropleth map
    fig = px.choropleth(
        filtered_data,
        locations="ISO",
        color="Mean",
        hover_name="Country Name",
        animation_frame="Year",
        color_continuous_scale=px.colors.sequential.Sunset,
        title=f"Median Intake of {gdd_variable_label} by Country Over the Years",
        # template="plotly_dark",  # Set template to a dark theme
    )

    # Update layout to hide frame and coastlines
    # Update layout to hide frame and coastlines, and increase map size
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=False),
        height=600,  # Adjust height as desired
        width=800,  # Adjust width as desired
    )

    # Show the figure within Streamlit
    st.plotly_chart(fig)


# Main function to create UI and plot graph
def main():
    st.title("Dietary Analysis")

    # Update the file paths below
    file_path1 = "JME_Malnutrition_Data.csv"  # Update with the file path for Table 1
    file_path2 = "Dietary_Data.csv"  # Update with the file path for Table 2

    # Load data from CSV files
    df1, df2 = load_data(file_path1, file_path2)

    # Sidebar for user input
    st.sidebar.title("Filter Options")
    selected_countries = st.sidebar.selectbox(
        "Select Countries",
        options=df2["Country Name"].unique(),
        index=df2["Country Name"].unique().tolist().index("Nigeria"),
    )
    start_year = st.sidebar.number_input(
        "Start Year",
        value=1990,
        min_value=df2["Year"].min(),
        max_value=df2["Year"].max(),
    )
    end_year = st.sidebar.number_input(
        "End Year", value=2018, min_value=df2["Year"].min(), max_value=df2["Year"].max()
    )

    gender_mapping = {"Male": 0, "Female": 1, "All": 999}
    selected_gender_name = st.sidebar.selectbox(
        "Select Gender", key="Male", options=["Male", "Female", "All"]
    )
    # Get the corresponding label from the mapping
    selected_gender = gender_mapping[selected_gender_name]
    selected_nutrition = st.sidebar.multiselect(
        "Select Nutrition",
        default=["Total processed meats"],
        options=df2["Nutrition"].unique(),
    )

    filtered_df2 = df2[(df2["Sex"] == selected_gender)]

    # Plot graph
    if (selected_nutrition) and (selected_gender_name) and (not filtered_df2.empty):
        fig = go.Figure()
        # Add lines for Table 2 (mean)
        for nutrition in selected_nutrition:
            temp_df2_country = filtered_df2[
                (filtered_df2["Country Name"] == selected_countries)
                & (filtered_df2["Nutrition"] == nutrition)
            ]

            geminiData["countriesNutritionTrend"].append(temp_df2_country)
            if not temp_df2_country.empty:
                fig.add_trace(
                    go.Scatter(
                        x=temp_df2_country["Year"],
                        y=temp_df2_country["Mean"],
                        mode="lines",
                        name=f"{selected_countries} - {nutrition} - Mean - Table 2",
                        line=dict(dash="dot"),
                    )
                )

        # Update layout for three-sided axis
        fig.update_layout(
            title=f"Malnutrition Trend for {selected_gender_name}s in Selected Countries",
            xaxis=dict(title="Year"),
            yaxis2=dict(title="Mean - Table 2", side="right", overlaying="y"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig)

        plot_dietary_changes(
            df2, start_year, end_year, selected_countries, selected_gender
        )

        if geminiData["countryDietChange"] and geminiData["countriesNutritionTrend"]:
            if st.button("Analyse the Graph."):
                with st.spinner("Analysing the data, It might take few seconds..."):
                    statement = generate_statement(
                        geminiData["countryDietChange"][0],
                        geminiData["countriesNutritionTrend"][0],
                    )  # Assuming generate_statement is your function
                    st.write(statement)

        st.subheader("Geographical Distribution of Nutrient Intake")
        for n in selected_nutrition:
            plot_choropleth(df2, n)

    else:
        st.warning(
            f"No data available for the selected {selected_gender_name}s in the selected countries."
        )


if __name__ == "__main__":
    main()
