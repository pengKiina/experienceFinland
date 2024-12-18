import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import time  # For performance monitoring


# Inject custom JavaScript to hide the sidebar initially
#st.set_page_config(initial_sidebar_state="collapsed")
# Set the page configuration
st.set_page_config(
    layout="wide",  # Wide layout
    page_title="VTT/UEF-Finland Experience Industry"  # Page title
)


# Monitor performance
start_time = time.time()

# Cache data loading
@st.cache_data
def load_data(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)

finEI_df = load_data(r'data_base//finEI_stream.xlsx', 'finEI_simple')
onlyBase_df = load_data(r'data_base//finEI_stream.xlsx', 'onlyBaseEdges')
basePlus_df = load_data(r'data_base//finEI_stream.xlsx', 'basePlusEdges')

# Cache graph construction
@st.cache_data
def create_graph(finEI_df,onlyBase_df):
    edges = [(x, y, z) for x, y, z in zip(onlyBase_df.iloc[:, 0], onlyBase_df.iloc[:, 1], onlyBase_df.iloc[:, 2])]
    
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges, weight='width')
 
    
   

    # Process data for regions and colors
    region_names = sorted(set(finEI_df.regionFI))
    baseMK_Dict = finEI_df.set_index(finEI_df.website_main.str.lower())['regionFI'].to_dict()
    loc_colors = ['lavender', 'blue', 'green', 'orange', 'aquamarine', 'yellow', 'cyan', 'magenta', 
                'lime', 'pink', 'teal', 'black', 'brown', 'beige', 'maroon', 'olive', 
                'coral', 'navy', 'purple', 'indigo']
    color_map = dict(zip(region_names, loc_colors))
    print(color_map)
    # Update graph nodes with attributes
    for node in G.nodes:
        G.nodes[node]['attribute_loc'] = baseMK_Dict[node]

                
    return G,region_names,baseMK_Dict,color_map


G,region_names,baseMK_Dict,color_map = create_graph(finEI_df,onlyBase_df)


st.subheader("Finland Experience Network", divider=True)
col1, col2 = st.columns([1,5])  # Adjust column widths as needed

with col1:
   
    with st.expander("Filters", expanded=True): 
        min_weight = st.slider('Minimum Edge Weight:', min_value=1, max_value=100, value=11)

        selectRegions = st.multiselect(
            'Select Regions:',
            options=['all_regions'] + region_names,
            default='all_regions',
        )
        selectRegions = region_names if 'all_regions' in selectRegions else selectRegions

        selectNodes0 = st.multiselect(
            'Select Nodes:',
            options=['all_nodes'] + list(G.nodes),
            default='businessfinland.fi',
        )
        selectNodes = list(G.nodes) if 'all_nodes' in selectNodes0 else selectNodes0
with col2:

    @st.cache_resource
    def create_subGraph(filtered_edges):
        
        filtered_G = nx.DiGraph()
        filtered_G.add_weighted_edges_from(filtered_edges, weight='width')
        
        for node in filtered_G.nodes:
            try:
                filtered_G.nodes[node]['attribute_loc'] = baseMK_Dict[node]
                filtered_G.nodes[node]['color'] = color_map[filtered_G.nodes[node]['attribute_loc']]
                filtered_G.nodes[node]['title'] = f"{node}: {filtered_G.degree(node)}: {filtered_G.nodes[node]['attribute_loc']}"
                filtered_G.nodes[node]['size'] = filtered_G.degree(node) / 5 + 5
            except KeyError:
                filtered_G.nodes[node]['attribute_loc'] = '1'
                filtered_G.nodes[node]['color'] = 'gray'
                filtered_G.nodes[node]['title'] = f"{node}: {filtered_G.degree(node)}"
                filtered_G.nodes[node]['size'] = filtered_G.degree(node) / 5 + 5
                
            # Add nodes and edges with attributes
        for u, v, data in filtered_G.edges(data=True):
            #label = f"Weight: {data['width']}"
            try:
                filtered_G.edges[u,v]['title'] = u +' → ' + v +':' + str(data['width'])
            except:
                pass
            
        return filtered_G


    @st.cache_data
    def showFiltered(min_weight,selectRegions,selectNodes):
        
        
        # Filter the graph
        filtered_edges = [
            (u, v,d) for u, v, d in G.edges(data=True)
            if d['width'] >= min_weight and 
            G.nodes[u]['attribute_loc'] in selectRegions and 
            (u in selectNodes or v in selectNodes)
            ]
        
        #filtered_G = G.edge_subgraph(filtered_edges) # can inherit the G nodes and edges attributes such as size. 
        
        filtered_G = create_subGraph(filtered_edges)  # all nodes and edges attribtues are updaged in the filtered_G 
        
        if len(selectRegions)==20:
            selectRegions1 = ['AllRegions']
        else:
            selectRegions1 = selectRegions
            
        region_names1 = [] 
        
        for x in selectRegions1:
            if'-' in x:
                y1s = []
                for y in x.split('-'):
                    y1 = y[:1]
                    y1s.append(y1)
                y2 = "-".join(y1s)
            else:
                y2 = x[:3]
            region_names1.append(y2)
                
        # Create the Pyvis network
        heading = f"Region(s):{region_names1}- {len(filtered_G.nodes)} node(s)- min_weight:{min_weight}"
        nt1 = Network("800px", "110%", heading=heading, notebook=True, directed=True, cdn_resources='remote')
        nt1.from_nx(filtered_G)
        nt1.show_buttons(filter_=['physics'])

        # Show the network
        st.components.v1.html(nt1.generate_html(), height=660, scrolling=True)

    showFiltered(min_weight,selectRegions,selectNodes)





# Display Power BI dashboard
st.subheader('Finland Experience Success Measurement', divider=True)
if st.button("Load Power BI Dashboard"):
    powerBi = """
    <iframe title="allFinExSuccess_pbi" width="100%" height="800" 
    src="https://app.powerbi.com/reportEmbed?reportId=a62ddc63-4447-4326-bf93-8af050c92e58&autoAuth=true&ctid=87879f2e-7304-4bf2-baf2-63e7f83f3c34" 
    frameborder="0" allowFullScreen="true"></iframe>"""
    st.components.v1.html(powerBi, height=800)


spider_file_path = r"data_base//FinEX_spider_updated.html"

# Read the content of the HTML file
with open(spider_file_path, "r") as file:
    html_content = file.read()

# Use st.components.v1.html to render the HTML
#st.components.v1.html(html_content, height=800)

# Set viewport height to 100% for full-screen rendering (consider responsiveness)
html_viewport_style = """
<style>
  html, body {
    height: 100vh;
    margin: 0;
  }
</style>
"""

# Combine the viewport style with your HTML content
full_html = html_viewport_style + html_content

# Optionally adjust height for specific content or user interactions
adjusted_height = 700 # Set a specific pixel value if needed

# Render the HTML using st.components.v1.html
st.components.v1.html(full_html, height=adjusted_height)


# Display execution time
st.write("Execution Time:", round(time.time() - start_time, 2), "seconds")
