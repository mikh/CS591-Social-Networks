package entity;

import org.jgrapht.graph.DefaultWeightedEdge;

public class Edge extends DefaultWeightedEdge implements Comparable<Edge>{

	public Integer edgeId; 

	
	public int hiddenCode;
	public int visitCount;

	public boolean hidden;
	
	public Edge(Integer edgeId){
		super();
		
		this.edgeId = edgeId;
		
	}

	@Override
	public int compareTo(Edge o) {
		
		// TODO Auto-generated method stub
		return ((Double)this.getWeight()).compareTo((Double)o.getWeight());
	}
	
	@Override
	public double getWeight(){
	
		return super.getWeight();
	}
	
	public Integer sourceNodeId(){
		return (Integer) super.getSource();
	}
	public Integer destinationNodeId(){
		return (Integer) super.getTarget();
	}
}
