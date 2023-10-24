import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geodatasets as godt
import geopandas as gop
import plotly.express as px


def load_clear_data(file):
    df = pd.read_csv(file, delimiter=";", encoding='utf-8')
    todrop = ['operateur', 'nombre_mailles_secretisees', 'code_grand_secteur', 'code_naf']
    df.drop(columns=todrop, axis=1, inplace=True)
    df = df[df['libelle_categorie_consommation'] != "0"]
    df = df[df['code_region'] != 'XX']
    df = df[df['code_region'] != 'Fr']
    df.dropna(inplace=True)
    df.groupby('code_region')['conso'].sum().reset_index()
    return df

def stbarchar(df):
    st.bar_chart(df['code_region'].value_counts())
    
def francemap(df):
    france = gop.read_file(godt.get_path("geoda.guerry"))
    france['dept'] = france['dept'].astype(str)
    france['dept'] = france['dept'].str.replace('.0', '')
    merged_data = france.merge(df, left_on="dept", right_on="code_region")
    merged_data = france.merge(df, left_on="dept", right_on="code_region")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_title("Where we collected the data")
    france.boundary.plot(ax=ax, linewidth=1, color="black")
    merged_data.plot(column="conso", cmap="YlGnBu", linewidth=0.8, ax=ax, legend=True)
    st.pyplot(fig, "france.png")
    
def simpleplot(df):
    df2021 = df[df['annee'] == 2021]
    grouped_data = df2021.groupby('code_region')['conso'].sum().reset_index()
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_title("In 2021")
    plt.plot(grouped_data['code_region'], grouped_data['conso'])
    st.pyplot(fig, "simpleplot.png")
                

def main():
    st.title('DataViz Project: About Electricity and Gaz consumption in France')
    st.sidebar.image("frig.jpg", width=200, caption="picture of a frog")
    st.sidebar.write("Hello! I am Lena, a M1 Data Engineering student!")
    st.sidebar.write("You can find my work and me here:")
    st.sidebar.write("[Github](https://github.com/Leiiph)  [Linkedin](https://www.linkedin.com/in/l%C3%A9nabrunier/)")
    #st.sidebar.write("[Linkedin](https://www.linkedin.com/in/l%C3%A9nabrunier/)")
    df = load_clear_data("data.csv")
    option = st.selectbox('What do you want to know?', ('Introduction', 'Global distribution of the data', "year", 'Consumption by region', 'Consumption by category', 'Consumption by sector'))
    if option == 'Introduction':
        st.write('Hello! This is a DataViz project about electricity and gaz consumption in France.')
    elif option == 'Global distribution of the data':
        check = st.checkbox("Show the map?")
        if check:
            francemap(df)
        stbarchar(df)
        simpleplot(df)
    elif option == 'year':
        st.write('Here is the consumption by year')
        st.bar_chart(df['annee'].value_counts())
    elif option == 'Consumption by region':
        st.write('Here is the consumption by region')
        st.bar_chart(df['code_region'].value_counts())
    elif option == 'Consumption by category':
        st.write('Here is the consumption by category')
        st.bar_chart(df['libelle_categorie_consommation'].value_counts())
    else:
        st.write('Here is the consumption by sector')
        st.bar_chart(df['libelle_grand_secteur'].value_counts())
        df2021 = df[(df['annee'] == 2021) & (df['filiere'] == 'Electricité')]
        fig = px.histogram(df2021, x="conso", nbins=10, title='Histogram of consumption in 2021')
        st.plotly_chart(fig)
    
    
if __name__ == "__main__":
    main()