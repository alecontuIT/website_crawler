import plotly.graph_objects as go
import plotly.offline as offline
import networkx as nx
import json


class networkPlotter:
    def __init__(self, network_data=None, listed_url=None, home_url=None, header_urls=None, footer_urls=None):
        self._network = nx.Graph()
        self.home_url=home_url
        if network_data == None:
            assert home_url is not None, 'Must provide the URL of website homepage'
            website_name = home_url.replace('https://','').replace('www.','').replace('/','')
            self._network_data = None
            with open(website_name+'_urls_network.json') as f:
                self._network_data = json.load(f)
        else:
            self._network_data = network_data
        
        if listed_url == None:
            assert home_url is not None, 'Must provide the URL of website homepage'
            website_name = home_url.replace('https://','').replace('www.','').replace('/','')
            listed_url = None
            with open(website_name+'_listed_url.json') as f:
                listed_url = json.load(f)
        else:
            listed_url = listed_url
        #####self._network_weight = list(self._network_weight.values())
        
        # Add all the nodes to the network
        complete_node_list = list(self._network_data.keys())
        for url_i in range(len(list(self._network_data.values()))):
            complete_node_list += list(self._network_data.values())[url_i]
            
            
        if header_urls == None:
            assert home_url is not None, 'Must provide the URL of website homepage'
            with open(website_name+'_header_urls.json') as f:
                header_urls = json.load(f)['header_urls']
        for url in header_urls:
            complete_node_list.remove(url)
        if footer_urls == None:
            assert home_url is not None, 'Must provide the URL of website homepage'
            with open(website_name+'_footer_urls.json') as f:
                footer_urls = json.load(f)['footer_urls']
        for url in footer_urls:
            complete_node_list.remove(url)
            
            
        self._network.add_nodes_from(complete_node_list)
        
        self._network_weight = []
        for url in complete_node_list:
            self._network_weight.append(listed_url[url])
        # Node weight is given by the number of time it is cited in all the website
        # Normalize this value for plotting visualiation reasons
        self._network_weight = self.normalize_weight(self._network_weight, 5, 20)
        
        # Compute all the edges (node_1, node_2)
        edges = []
        # Iterazione sul dizionario
        for key, values in self._network_data.items():
            # Iterazione sui valori per la chiave corrente
            for value in values:
                if (value not in header_urls) and (value not in footer_urls):
                    # Aggiunta della tupla alla lista
                    edges.append((key, value))
                
        self._network.add_edges_from(edges)
        self._pos = nx.spring_layout(self._network)
        
        
    def plot(self):
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )


        fig = go.Figure(layout = layout)

        for trace in self.get_edge_trace():
            fig.add_trace(trace)
        
        fig.add_trace(self.get_node_trace())

        fig.update_layout(title='Network map of: '+self.home_url,
                          showlegend = False)

        fig.update_xaxes(showticklabels = False)

        fig.update_yaxes(showticklabels = False)
        #fig.show()
        offline.plot(fig, filename='network.html')

        
        
    @staticmethod
    def make_edge(x, y, width=1):
        '''Creates a scatter trace for the edge between x's and y's with given width

        Parameters
        ----------
        x    : a tuple of the endpoints' x-coordinates in the form, tuple([x0, x1, None])

        y    : a tuple of the endpoints' y-coordinates in the form, tuple([y0, y1, None])

        width: the width of the line

        Returns
        -------
        An edge trace that goes between x0 and x1 with specified width.
        '''
        return  go.Scatter(x         = x,
                           y         = y,
                           line      = dict(width = width,
                                       color = 'cornflowerblue'
                                           ),
                           opacity   = .1,
                           mode      = 'lines')

    def get_edge_trace(self):
        # For each edge, make an edge_trace, append to list
        edge_trace = []
        for edge in self._network.edges():
            char_1 = edge[0]
            char_2 = edge[1]

            x0, y0 = self._pos[char_1]
            x1, y1 = self._pos[char_2]
            trace  = self.make_edge([x0, x1, None], [y0, y1, None], 1)
            edge_trace.append(trace)
        return edge_trace
    
    def get_node_trace(self):
        # Make a node trace
        node_trace = go.Scatter(x         = [],
                                y         = [],
                                text      = [],
                                mode      = 'markers',
                                hoverinfo = 'text',
                                marker    = dict(color = [],
                                                 size  = [],
                                                 line  = None))
        
        idx = 0
        for node in self._network.nodes():
            x, y = self._pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['marker']['color'] += tuple(['cornflowerblue'])
            node_trace['marker']['size'] += tuple([self._network_weight[idx]])
            node_trace['text'] += tuple(['<b>' + node + '</b>'])
            idx+=1
        return node_trace
    
    @staticmethod
    def normalize_weight(input_list, new_min, new_max):
        # Find min and max of the input list
        old_min = min(input_list)
        old_max = max(input_list)

        # Compute the range of the input list
        old_range = old_max - old_min

        # Compute the new range
        new_range = new_max - new_min

        # Normalize each value of the list
        normalized_list = []
        for value in input_list:
            # Compute the normalized value
            normalized_value = ((value - old_min) / old_range) * new_range + new_min
            normalized_list.append(normalized_value)

        return normalized_list
