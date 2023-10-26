####### IMPORT #########

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geodatasets as godt
import geopandas as gop
import plotly.express as px

####### FUNCTIONS #########

##### Loading data
def load_clear_data(file):
    '''Load the data into a dataframe and clear it from useless columns and rows'''
    df = pd.read_csv(file, delimiter=";", encoding='utf-8')
    todrop = ['operateur', 'nombre_mailles_secretisees', 'code_grand_secteur', 'code_naf']
    df.drop(columns=todrop, axis=1, inplace=True)
    #We remove all data that could impact our study or are not clearly useful
    df = df[df['libelle_categorie_consommation'] != "0"]
    df = df[df['code_region'] != 'XX']
    df = df[df['code_region'] != 'Fr']
    df.dropna(inplace=True)
    df.groupby('code_region')['conso'].sum().reset_index()
    return df

##### Cache functions
@st.cache_data                
def consodepartement(df):
    '''Function to plot the consumption for each departement. As the function is quite heavy, we store it in the cache afterwards.'''
    fig = px.bar(df, x="code_region", y="conso", color="filiere", barmode="group", title='Consumption for each departement')
    st.plotly_chart(fig) 
    
@st.cache_data    
def francemap(df):
    '''Generate the map of France. As the function is heavy, we store it in the cache afterwards'''
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
    
##### Plot functions    
def stbarchar(df):
    '''Generate the bar chart for the geographical repartition of the data'''
    st.bar_chart(df['code_region'].value_counts()) 
       
def simpleplot(df):
    '''Plot of the consumption over a specific year'''
    grouped_data = df.groupby('code_region')['conso'].sum().reset_index()
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_title("Consumption over a specific year")
    plt.plot(grouped_data['code_region'], grouped_data['conso'])
    st.pyplot(fig, "simpleplot.png")
    
    
    
def consumption(df):
    '''Function dedicated to the whole consumption part of the streamlit app'''
    st.write('# How are our data distributed?')
    st.write("Now that we looked at the geographical repartition of our data and a bit at the year's one, let's take a look at the consumption itself. Here are some stats:")
    st.write('We already saw that plot on the geographical repartition. But let\'s put it here again:')
    st.bar_chart(df['code_region'].value_counts())
    
    st.write('With that in mind, we can now take a look at the consumption by category:')
    st.bar_chart(df['libelle_categorie_consommation'].value_counts())
    st.write("As seenable, the entreprises are the ones that consume the most. This might explain the high consumption in the 11th departement, as it is known for its wine industry, which requires a lot of energy. This might also explains why we have a so big difference in the electricity consumption between the countryside and the capital: maybe the entreprises around the capital use more electrcity than gaz?")
    
    st.write('To see this, we can firstly take a look at the consumption by sector:')
    value = df['libelle_grand_secteur'].value_counts()
    fig1 = px.pie(df, names=value.index, values=value.values, title='Consumption by sector')
    st.plotly_chart(fig1)
    
    #info message for the types of sectors
    st.info('To inform you!\n - Tertiaire sector is related to the production of services,\n - Industrie refers to the production of goods,\n - Résidentiel refers to the houses, appartements and so on,\n - And agriculture is the production of food.')
    st.write("The tertiaire sector is almost half of all sectors within our dataset. This might explain the high consumption of electricity in the capital, as it is the place where most of the services are located. As for the high differences between gaz and électricité for the 32sd and 44th departement, we can look at the industry repartition:")
    grouped_data = df[df['libelle_grand_secteur'] == 'Industrie'].groupby('code_region')['conso'].sum().reset_index()
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_title("Industry sector consumption by region")
    plt.bar(grouped_data['code_region'], grouped_data['conso'])
    st.pyplot(fig)
    st.write("The two main spikes are the 32sd and 44th departement, which match a very high consumption in gaz in both of these departements. For example, in the 44th departement, the naval industry is very developped, which explains that difference of consumption.")
    
    st.write("In the end, to go further, we can check the usual average gaz consumption in 2021:")
    df2021 = df[(df['annee'] == 2021) & (df['filiere'] == 'Gaz')]
    fig = px.histogram(df2021, x="conso", nbins=10, title='Histogram of consumption in 2021')
    st.plotly_chart(fig) 
    st.write("While most of our data are close to OM, they are in fact more closer to 2M if we zoom in. With more than 80% of our data being in the 2-2.5M range, we can conclude that the average gaz consumption in France is around 2M, mostly done by industries.")
    
    
def globalrepartition(df):
    '''Function to compute how the consumption is distributed between gaz and électricité'''
    dfconsoc = df.groupby('filiere')['conso'].sum()
    fig = px.pie(dfconsoc, names=dfconsoc.index, title='Distribution of gaz and électricité in France over the years')
    st.plotly_chart(fig)  
                           

####### MAIN #########

def main():
    st.title('DataViz Project: About Electricity and Gaz consumption in France')
    option = st.sidebar.selectbox('# What do you want to know?', ('Introduction', 'Geographical repartition', 'Gaz consumption'))
    st.sidebar.write('------------------------------')
    st.sidebar.image("frig.jpg", width=180)
    st.sidebar.write("Hello! I am Léna, a M1 Data Engineering student!")
    st.sidebar.write("You can find my work and me here:")
    st.sidebar.write("[Github](https://github.com/Leiiph)                  [Linkedin](https://www.linkedin.com/in/l%C3%A9nabrunier/)")
    df = load_clear_data("data.csv")
    
    if option == 'Introduction':
        st.markdown('Hello! This is a DataViz project about electricity and gaz consumption in France.')
        st.write("Are you a company looking for some information on the repartition of electricity and gaz comsumption in France? Perhaps you to see Gaz to some entity but don't know which one (category & sector) would be the best to do so? Or just a curious person?\n We got you covered!")
        st.write("On this website, you will find the following:\n - Information about the data and where they were collected\n - Repartition of the consumption over the category and the sector")
        st.write("The data can be found on [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/consommation-annuelle-delectricite-et-gaz-par-region-et-par-code-naf/)")
    elif option == 'Geographical repartition':
        st.write("## Where did we collect the data?")
        st.write("As this is a project about energy consumption in France, all of our data are from french departements. Thus, let's firstly see the global repartition of the collected data:")
        stbarchar(df)
        st.write("Troubles finding out which departement is what? You can take a look at a French map to help you:")
        check = st.checkbox("Show the map")
        if check:
            francemap(df)
        st.write("As you can see, we don't have a lot of data from a lot of different departements. But that's fine! We can still do some analysis on those departements. We just need to be very careful when we will draw conclusions at the end of the project.")
        st.write("## What is the energy prefered by the French?")
        st.write("Electricity or Gaz? Using our data, we can take a look at this:")
        globalrepartition(df)
        st.write("As you can see, we have a perfect distribution! Half of the French population uses electricity and the other half uses gaz.")
        st.write("To have a better idea, we can take a look at the consumption each for each departement:")
        consodepartement(df)
        st.write("And now, we can see some interesting things! Firstly is that the consumption, especially for Gaz, is very high in the 11th departement (Aude), which corresponds to what we could see on the French map. Secondly, and the most interesting thing to notice here, is that as soon as we get near the capital (75 - Paris), we switch from a preference for gaz to a preference for electricity.")
        st.write("Now, what could explain such thing? Maybe more habitants? Or a preference? Or maybe companies located in the countryside that mainly use gaz? We will look into that later, but we can already get the global idea here.")
        st.write("Now, let's have a look at two specific years: 2018 and 2021:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("# 2018")
        with col2:
            st.markdown("# 2021")
        col3, col4 = st.columns(2)
        with col3:
            simpleplot(df[df['annee'] == 2018])
        with col4:
            simpleplot(df[df['annee'] == 2021])
        st.write("With these two plots, we notice that mainly, consumption did not increase over the years and especially after covid. This is true for all departements except for one: 44 (Loire-Atlantique).")
        st.write("Indeed, we have a clearly seenable increase for the 44th departement. What could explain that?")
        st.write("- More people moved into a big city in 44?\n - Companies moved in 44?\n - Just more gathered data?\n - Or maybe we just have more data for 2021?")
        st.write("Quite the mystery! But we will try to solve it later.")
    elif option == 'Gaz consumption':
        consumption(df)
    
if __name__ == "__main__":
    main()