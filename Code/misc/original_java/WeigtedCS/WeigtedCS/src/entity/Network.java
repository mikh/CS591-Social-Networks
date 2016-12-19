package entity;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;


import org.jgrapht.Graphs;

import org.jgrapht.graph.SimpleWeightedGraph;
import org.omg.CORBA.NVList;
import org.w3c.dom.traversal.NodeFilter;



public class Network extends SimpleWeightedGraph<Integer, Edge> {

	
	//for fast access
	public int[] degrees;
	public double[] weights;
	public int[] nodeSeenCount;
	
	public int maxNodeId; // max nodeId not always equals to number of nodes
	
	
	
	public Network(Class<Edge> class1) {
		super(class1);
	}
	

	public void initFastAccessArrays(){
		weights  = new double[maxNodeId + 1];
		degrees = new int[maxNodeId + 1];
		nodeSeenCount = new int[maxNodeId + 1];
		for (Integer i : this.vertexSet()) {
			degrees[i] = degreeOf(i);
			weights[i] = getNodeWeight(i);
		}
	}


	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	
	
	public int totalDegree(){
		
		int sum = 0;
		for (Integer i : this.vertexSet()) {
			sum += degreeOf(i);
		}
		
		return sum;
	}
	
	public int numberOfNodes(){
		return this.vertexSet().size();
	}
	
	public int numberOfEdges(){
		return this.edgeSet().size();
	}
	

	
	
	public List<Integer> neighborListOf(int nodeId){
		
		return Graphs.neighborListOf(this, nodeId);
	}
	
	public List<Integer> visibleNeighborListOf(int nodeId){
		
		List<Integer> nbrs = neighborListOf(nodeId);
		List<Integer> nbrs_visible = new ArrayList<Integer>();
		Edge e;
		for(Integer nb : nbrs){
			e = this.getEdge(nodeId, nb);
			if(e.hidden)
				nbrs_visible.add(nb);
		}
		return nbrs_visible;
	}
	
	
	public double getNodeWeight(int nodeId){
		
		double sum = 0;				

		for (Integer n : neighborListOf(nodeId)) {
			sum += this.getEdgeWeight(this.getEdge(nodeId, n));
		}

		return sum;
	}
	
	public double getNodeWeightOnDeg(int nodeId){
		
		if(degrees[nodeId] == 0)
			return 0;
		return weights[nodeId] / degrees[nodeId]; 
		
	}
	public	double sameNbrCnt(Edge e){
		int cnt = 0;
		Integer s = e.sourceNodeId();
		Integer d = e.destinationNodeId();
		for(Integer nb : neighborListOf(s)){
			if(neighborListOf(d).contains(nb)){
				cnt++;
			}
		}
		return cnt;
	}
	
	public HashMap<Integer, Double> getNeighborProb(Integer cn){
		
		
		List<Integer> neighbors = neighborListOf(cn);
		HashMap<Integer, Double> neighborsProb = new HashMap<Integer, Double>(); 

		Edge e;
		double totalp = 0;;
		
		double p;
		for(Integer nb : neighbors){
			e = getEdge(cn, nb);
			if(e.hidden){
				continue;
			}else{
				
				if(degrees[nb] ==0 || weights[nb] == 0){
					System.err.println("wowow");
					continue;
				}
				
				 p = (double)1/degrees[cn] * Math.min(1, (double)degrees[cn]/degrees[nb]) 
							+
					 (double)getEdgeWeight(cn, nb)/weights[cn] * (Math.min(1, weights[cn]/weights[nb]));
				neighborsProb.put(nb, p);
				totalp += p;
			}						
		}
		
		double totalnp =0;
		for(Integer v : neighborsProb.keySet()){
			p = neighborsProb.get(v)/totalp;
			neighborsProb.put(v, p);
			totalnp +=p;
		}
		
		
		
		neighborsProb.put(-1, 1 - totalnp);
		
		return neighborsProb;
	}
	
	
	public HashMap<Integer, Double> getNeighborProb_UCSWN(Integer cn){
		
		List<Integer> neighbors = neighborListOf(cn);
		HashMap<Integer, Double> neighborsProb = new HashMap<Integer, Double>(); 

		Edge e;
		double totalp = 0;;
		
		double p;
		for(Integer nb : neighbors){
			e = getEdge(cn, nb);
			if(e.hiddenCode > 0){
				continue;
			}else{
				 p = (double)1/degrees[cn] * Math.min(1, (double)degrees[cn]/degrees[nb]);
				neighborsProb.put(nb, p);
				totalp += p;
			}						
		}
		
		neighborsProb.put(-1, 1 - totalp);
		
		return neighborsProb;
	}
	

	public double totalNodesWeight(){
		double sum = 0;				
		for(Integer v : this.vertexSet()){
			sum += getNodeWeight(v);
		}
		
		return sum;
	}
	
	public double totalEdgesWeight(){
		double sum = 0;				
		for(Edge e : this.edgeSet()){
			sum += this.getEdgeWeight(e);
		}
		
		return sum;
	}
	
	public double getEdgeWeight(int sourceNodeId, int destinationNodeId){
		return this.getEdgeWeight(this.getEdge(sourceNodeId, destinationNodeId));
	}
	

	
	public void hideEdge(Edge e){
		e.hidden = true;
		
		if(e.hiddenCode == 0){
			degrees[e.sourceNodeId()]--;
			degrees[e.destinationNodeId()]--;
			
			weights[e.sourceNodeId()] -= e.getWeight();
			weights[e.destinationNodeId()] -= e.getWeight();
		}
		tempHide(e);
	}
	
	
	public void tempHide(Edge e){
		e.visitCount++;
		e.hiddenCode = (int) Math.pow(2, e.visitCount);

	}
	public void lessHideAll(){
		for(Edge e : this.edgeSet()){
			if(e.hiddenCode > 0)
				lessHide(e);
		}
	}
	public void lessHide(Edge e){
		e.hiddenCode--;
		if(e.hiddenCode == 0){
			degrees[e.sourceNodeId()]++;
			degrees[e.destinationNodeId()]++;
			
			weights[e.sourceNodeId()] += e.getWeight();
			weights[e.destinationNodeId()] += e.getWeight();
			
			if(weights[e.sourceNodeId()] == 0 || weights[e.destinationNodeId()] ==0)
				System.out.println( "    " + degrees[e.sourceNodeId()]);
		}
	}

	public void unhideAllEdges() {
		for(Edge e : this.edgeSet()){
			e.hidden = false;
			e.hiddenCode = 0;
			e.visitCount = 0;
		}
		initFastAccessArrays();
		
	}
	
	public HashMap<Integer, Double> getNbrPrb_CSWeighted(Integer cn) {

		List<Integer> neighbors = neighborListOf(cn);
		HashMap<Integer, Double> neighborsProb = new HashMap<Integer, Double>();

		Edge e;
		double p,q, totalp = 0;

		
		for (Integer nb : neighbors) {
			e = getEdge(cn, nb);
			if (e.hidden) {
				continue;
			} else {
				q = (double)1/degrees[cn] * Math.min(1, (double)degrees[cn]/degrees[nb]);
				p = (double)getEdgeWeight(cn, nb)/weights[cn] * (Math.min(1, weights[cn]/weights[nb]));//(getEdgeWeight(cn, nb) )
				p =  q * (double) 1/p;// //1 -(double)getEdgeWeight(cn, nb)/  (weights[cn]);  (double)1/(getEdgeWeight(cn, nb) + 1)
				//p = (double) 1 /getEdgeWeight(cn, nb);
				totalp += p;
				neighborsProb.put(nb, p);
			}
		}

		return neighborsProb;

	}


	
		

	
	
	public void writeToFile(String fileName){
		PrintWriter writer = null;
		try {
			writer = new PrintWriter(new File(fileName));
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		for(Edge e : this.edgeSet()){
			writer.println(e.sourceNodeId() +" " + e.destinationNodeId() +" "+ e.getWeight());
		}
		writer.close();	}


}
