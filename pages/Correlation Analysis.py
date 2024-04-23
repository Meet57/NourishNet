import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
import os

# Configure GenAI
api_key = os.environ.get("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")

# Store data temporarily
geminiData = {"dietData": None, "malnutritionData": None}


# Function to generate content with insights
def generate_content_with_insights(document1, document2, df1, df2):
    combined_content = f"{document1}\n\n{df1.to_string()} \n {document2}\n\n{df2.to_string()} \n\n Provide Correlation Analysis on Malnutrition and Diet Data Provided Above\n\n"
    response = model.generate_content(combined_content)
    return response


# Function to generate statement based on data
def generate_statement(df1, df2, malnutrition):
    try:
        document1 = "Provide Insight about this Data - This is about absoulte change in nutrients intake (Concise) :"
        document2 = f"Provide Insight about this Data - This is A Malnutrition {malnutrition} trend in country (Concise):"
        response = generate_content_with_insights(document1, document2, df1, df2)
        return response.text
    except Exception as e:
        return "Could not generate insight"


# Function to load data from CSV files
def load_data(file_path1, file_path2):
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)
    return df1, df2


# Function to load data from MySQL
# def load_data_from_mysql():
#     import mysql.connector
#
#     mydb = mysql.connector.connect(
#         host="localhost", user="root", password="my-secret-pw", database="ADT"
#     )
#     mycursor = mydb.cursor()
#     mycursor.execute("SELECT * FROM malnutrition;")
#     myresult = mycursor.fetchall()
#     df1 = pd.DataFrame(myresult)
#     mycursor.execute("SELECT * FROM nutrition_data;")
#     myresult = mycursor.fetchall()
#     df2 = pd.DataFrame(myresult)
#     df1.head()
#     df2.head()
#     # return df1, df2


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

    # Store filtered data for later use
    geminiData["dietData"] = filtered_data

    # Plot a bar graph for the specified country's dietary changes
    fig = px.bar(pivot_table, x=pivot_table.index, y=pivot_table[country])
    fig.update_layout(
        title=f"Dietary Changes in {country} ({start_year}-{end_year})",
        xaxis_title="Dietary Factor",
        yaxis_title="Change in Median Intake",
    )
    st.plotly_chart(fig)


# Main function to create UI and plot graph
def main():
    file_path1 = "JME_Malnutrition_Data.csv"
    file_path2 = "Dietary_Data.csv"

    # Load data from CSV file
    df1, df2 = load_data(file_path1, file_path2)

    st.title("Correlation Analysis")

    ## ----------------- Sidebar ----------------- ##
    st.sidebar.subheader("Filter Options")

    selected_country = st.sidebar.selectbox(
        "Select Countries",
        options=df2["Country Name"].unique(),
        index=df2["Country Name"].unique().tolist().index("United States"),
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

    selected_y_axis = st.sidebar.selectbox(
        "Select Y-axis",
        key="Overweight",
        options=["Overweight", "Stunting", "Wasting", "Mean"],
        index=3,
    )

    plot_dietary_changes(df2, start_year, end_year, selected_country, 999)

    # Filter malnutrition data
    filtered_df = df1[(df1["Country Name"] == selected_country) & (df1["Sex"] == 999)]

    if not filtered_df.empty:
        geminiData["malnutritionData"] = filtered_df
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=filtered_df["Year"],
                y=filtered_df[selected_y_axis],
                mode="lines",
                name=f"{selected_country}",
            )
        )
        # Update layout
        fig.update_layout(
            xaxis=dict(title="Year"),
            yaxis=dict(title=selected_y_axis),
            title=f"Malnutrition in {selected_country} -- {selected_y_axis} vs Year",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig)

    if (
        geminiData["malnutritionData"] is not None
        and geminiData["dietData"] is not None
    ):
        if st.button("Analyse the Graph."):
            with st.spinner("Analysing the data, It might take few seconds..."):
                statement = generate_statement(
                    geminiData["dietData"],
                    geminiData["malnutritionData"],
                    selected_y_axis,
                )
                st.write(statement)
    else:
        st.warning("Malnutrition data is not available for the selected country.")


if __name__ == "__main__":
    main()
