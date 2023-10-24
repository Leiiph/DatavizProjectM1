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
    grouped_data = df.groupby('code_region')['conso'].sum().reset_index()
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_title("In 2021")
    plt.plot(grouped_data['code_region'], grouped_data['conso'])
    st.pyplot(fig, "simpleplot.png")
                
                
def overyear(df):
    #df = df[df['annee'].isin([2021, 2017, 2018])]

    df['annee'].value_counts()
    color = ['red', 'blue', 'orange', 'yellow', 'green', 'purple', 'pink', 'brown', 'grey', 'black']
    fig = px.histogram(df, x="conso", nbins=10, title='Repartition of consumption over the years', color=color)
    st.plotly_chart(fig)            

def main():
    st.title('DataViz Project: About Electricity and Gaz consumption in France')
    st.sidebar.image("frig.jpg", width=200, caption="picture of a frog")
    st.sidebar.write("Hello! I am Lena, a M1 Data Engineering student!")
    st.sidebar.write("You can find my work and me here:")
    st.sidebar.write("[Github](https://github.com/Leiiph)                  [Linkedin](https://www.linkedin.com/in/l%C3%A9nabrunier/)")
    df = load_clear_data("data.csv")
    option = st.selectbox('What do you want to know?', ('Introduction', 'Global distribution of the data', "year", 'Consumption by region', 'Consumption by category', 'Consumption by sector'))
    if option == 'Introduction':
        st.markdown('Hello! This is a DataViz project about electricity and gaz consumption in France.')
        st.write("Are you a company looking for some information on electricity and gaz comsumption in France? Or just a curious person?\n We got you covered!")
        st.write("On this website, you will find the following:\n - Information about the data and where they were collected\n - Distribution of gaz and electricity consumption in France\n - Dunno yet!")
        st.write("\n\n\n\n")
        st.write("The data can be found on [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/consommation-annuelle-delectricite-et-gaz-par-region-et-par-code-naf/)")
    elif option == 'Global distribution of the data':
        st.write("## Where did we collect the data?")
        st.write("We collected the data in France, over many years. Globally, here is the repartition of the collected data:")
        stbarchar(df)
        st.write("You can also see it on a map:")
        check = st.checkbox("Show the map")
        if check:
            francemap(df)
        st.write("## How did the consumption evolve over the years?")
        overyear(df)
        st.write("Let's look at two specific years: 2021 and 2018:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("# 2021")
        with col2:
            st.markdown("# 2018")
        col3, col4 = st.columns(2)
        with col3:
            simpleplot(df[df['annee'] == 2021])
        with col4:
            simpleplot(df[df['annee'] == 2018])
    
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