var nodes = new vis.DataSet(data2.nodes.map(n => {
    n.shape = 'dot';
    return n;
}));

// create an array with edges
let edges = [];
for (node1 of data2.nodes){
    for (node2 of data2.nodes){
        if (node1.id >= node2.id) continue;
        const dist = data2.dists[node1.id][node2.id];
        if (dist > 0.4){
            edges.push({from: node1.id, to: node2.id, width: dist * 2})
        }
    }
}

edges = new vis.DataSet(edges);
var container = document.getElementById("mynetwork");
var data = {
    nodes: nodes,
    edges: edges,
};
var options = {};
var network = new vis.Network(container, data, options);