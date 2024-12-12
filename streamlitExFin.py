import streamlit as st 

import networkx as nx 
import math , pandas as pd 
from pyvis.network import Network



# Set the page configuration to wide layout
st.set_page_config(
    layout="wide",  # Allows the app to stretch across the screen
    page_title="Finland Experience Industry / VTT-UEF",  # Optional: Title for the tab
    #page_icon="VTT-UEF",  # Optional: Favicon
)





finEI_df = pd.read_excel(r'./data_base\finEI_stream.xlsx',sheet_name='finEI_simple')
onlyBase_df = pd.read_excel(r'data_base\finEI_stream.xlsx',sheet_name='onlyBaseEdges')
basePlus_df = pd.read_excel(r'data_base\finEI_stream.xlsx',sheet_name='basePlusEdges')



def getEdegs (df):
    """ st.write('hello')

    st.title('simple data dashbaord')

    uploaded_file = st.file_uploader('choos a csv file',type='csv')

    st.subheader('Data summary')
    st.selectbox('select',[1,2,3])
    """
    edges = [(x,y,z) for x,y,z in zip(df.iloc[:,0].tolist(),df.iloc[:,1].tolist(),df.iloc[:,2].tolist())]
    return edges 

edges = getEdegs(onlyBase_df)
G = nx.DiGraph()

G.add_weighted_edges_from(edges,weight='width') # to match the pyvis 'width'
#G.add_nodes_from(list(set(nodesBase))) # some nodes do not have edge

region_names = list(set(finEI_df.regionFI))
#region_names  # '0' is unknown region , internatonal companies in Finland 

baseMK_Dict = finEI_df.set_index(finEI_df.website_main.str.lower())['regionFI'].to_dict() 
loc_colors = ['black', 'blue', 'green', 'orange', 'purple', 'yellow', 'cyan', 'magenta', 
          'lime', 'pink', 'teal', 'lavender', 'brown', 'beige', 'maroon', 'olive', 
          'coral', 'navy', 'aquamarine','indigo']  # red, black 

color_map = dict(zip(region_names,loc_colors)) 

for node in G.nodes:
    try:
        G.nodes[node]['attribute_loc'] = baseMK_Dict[node]  # add location region attribute to node 
        G.nodes[node]['color'] = color_map[G.nodes[node]['attribute_loc']]
        G.nodes[node]['title'] = node + ':' +str(G.degree(node)) + ':' + str(G.nodes[node]['attribute_loc']) 
        G.nodes[node]['size'] = G.degree(node)/10 +10
    except: # not nodes in amadeus (not base nodes )
        G.nodes[node]['attribute_loc'] = '1'
        G.nodes[node]['color'] = 'gray'
        G.nodes[node]['title'] = node + ':' +str(G.degree(node))
        G.nodes[node]['size'] = G.degree(node)/10 +10

#selectRegion = st.selectbox('select',region_names)
#st.write(f"You selected: {selectRegion}")
#print(selectRegion)
#selectRegion = 'Lappi'  


selectNodes0 = st.multiselect(
    'Select multiple multiple nodes:',
    options= ['all_nodes'] + list(G.nodes) ,
    default= 'all_nodes',
    
)

if 'all_nodes'in selectNodes0:
    selectNodes = list(G.nodes)
else:
    selectNodes = selectNodes0
#print('selectNodes',selectNodes)

selectRegions=[]
selectRegions = st.multiselect(
    'Select multiple regions:',
    options=  ['all_regions'] +region_names ,
    default= 'all_regions' ,
    label_visibility="hidden" # Optional default selections
)

if 'all_regions' in selectRegions:
    selectRegions = region_names
#print('selectRegions',selectRegions) 

min_weight = st.selectbox('select minimum edge weight',range(1,100),index=10)
   
G2 = G.copy()

heading = 'Finland Experience Network'
nt1 = Network("1080px", "1920px", heading=heading, notebook=True,directed= True, cdn_resources='remote',filter_menu=True) # Set notebook=False if not in Jupyter
#min_sector_weight = 4
filtered_edges = [(u, v) for u, v, d in G2.edges(data=True) if (d['width'] >= min_weight) & (G2.nodes[u]['attribute_loc'] in selectRegions) &(u in selectNodes or v in selectNodes)]

filtered_G = G2.edge_subgraph(filtered_edges)


nt1.from_nx(filtered_G)

# Show the network
#nt1.show_buttons(filter_=['physics'])
#nt1.show(f'data_base/{selectRegions[0]}.html')
#nt1.save_graph('data_base/finEx2a.html')
#st.html(f'finEx2a.html')

# with open(f'data_base/{selectRegions[0]}.html', "r") as f:
   # html_content = f.read()


# Use Streamlit to render the HTML
st.components.v1.html(nt1.generate_html(), height=800)

st.subheader('Finland Experience Sucess Measurement',divider=True)
powerBi = """
<iframe title="allFinExSuccess_pbi" width="120%" height="800" 
src="https://app.powerbi.com/reportEmbed?reportId=a62ddc63-4447-4326-bf93-8af050c92e58&autoAuth=true&ctid=87879f2e-7304-4bf2-baf2-63e7f83f3c34" 
frameborder="0" allowFullScreen="true"></iframe>"""
st.components.v1.html(powerBi, height=1080)
