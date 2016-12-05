import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Scanner;

//import org.jgraph.graph.DefaultEdge;
import org.jgrapht.UndirectedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;
import org.jgrapht.graph.SimpleGraph;
import org.jgrapht.graph.SimpleWeightedGraph;

import entity.Edge;
import entity.Network;
import entity.Node;





public class Parser {

	

	
	
	
	
	public static Network getGraph(String filepath){
		
		
		File file = new File(filepath);
		Scanner scaner = null;
		try {
			scaner = new Scanner(file);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		Network g = new Network(Edge.class);
		
		//UndirectedGraph<Node, Integer> g = new SimpleGraph<Node, Integer>(Integer.class);
		//ArrayList<Node> allNods = new ArrayList<Node>();
		//for(int i = 1; i <= numberOfNodes; i++){
			//allNods.add(new Node(i));
		//	g.addVertex(i);
		//}
		//g.vertexSet().addAll(allNods);
		
		String line ="";
		String[] data;
		Integer v1, v2;double w;
		DefaultWeightedEdge e;
		Integer edgeId = 0;
		while(scaner.hasNext()){
			line = scaner.nextLine().trim();
			if(line.startsWith("#") || line.startsWith("*")) continue;
			data = line.split(" ");
			v1 = Integer.parseInt(data[0]);
			v2 = Integer.parseInt(data[1]);
			w = Double.parseDouble(data[2]);
			
			if(!g.containsVertex(v1)){
				g.addVertex(v1);
				if(v1 > g.maxNodeId) g.maxNodeId = v1;
			}
			if(!g.containsVertex(v2)){
				g.addVertex(v2);
				if(v2 > g.maxNodeId) g.maxNodeId = v2;
			}
			
			if(v1.equals(v2))
				continue;
			
			e = new Edge(edgeId);
			boolean add = g.addEdge(v1, v2, (Edge)e);
			g.setEdgeWeight((Edge)e, w);
			if(add)
				edgeId++;
			

		}

		
		return g;
		
				
	}
	

}
