import streamlit as st


def main():
    st.title("NourishNet")

    # App Description
    st.write(
        """
    Welcome to NourishNet, an interactive tool for analyzing and visualizing nutritional data.

    ### About NourishNet:
    NourishNet provides various features for exploring nutritional data, including:

    - Analyzing dietary changes over time.
    - Clustering countries based on nutritional indicators.
    - Visualizing malnutrition trends.

    **Get started:** Use the sidebar to navigate through different sections and explore the features of NourishNet.

    #### Developer Information:
    NourishNet is developed using Streamlit, a powerful library for building interactive web applications with Python.

    **Developers:** Kishan Modi, Meet Patel, Malhar Raval, Aditya Tohan
    """
    )


if __name__ == "__main__":
    main()
