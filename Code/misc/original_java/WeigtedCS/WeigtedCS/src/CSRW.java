
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.Stack;



import entity.Edge;
import entity.Network;


public class CSRW {
	Stack<Integer> visitedNodes = new Stack<Integer>();
	double [] startProbs ;
	
	public double[] seenW;
	
	public synchronized double[][] getMeasurmentMatrix(Network g, int numberOfMeasurments, int numberOfSteps){
		startProbs = new double[g.maxNodeId + 1];// nodeId start from 0 or 1
		double [][] A = new double[numberOfMeasurments][g.edgeSet().size()];
		seenW = new double[numberOfMeasurments];
		
		int currentNodeId = -1, nextNodeId = -1, edgeId = -1, m = 0;
		
		Edge e;
		for(int i = 0; i< numberOfMeasurments ; i++){
			
			currentNodeId = selectStartNode(g);

			System.out.println(m + " : " + currentNodeId + " ");

			for(int j = 0 ; j < numberOfSteps ; j++){
				nextNodeId = getNextNodeId(g, currentNodeId);
				
				if(nextNodeId != -1){
					e = g.getEdge(currentNodeId, nextNodeId);
					edgeId = e.edgeId;
					currentNodeId = nextNodeId ;
					A[i][edgeId]++;
					seenW[i] += e.getWeight();

				}else{//backtrack
					
					//would not be call
					System.out.println("isolated node");
				}
				
				
			}
//			System.out.println();
			m++;
			
		}
	
		
		
		
		
		return A;
	}
	
	
	
	
	
	private int selectStartNode(Network g) {
		
		Object[] nodes = g.vertexSet().toArray();
		int rnd = new Random().nextInt(nodes.length);
		return (Integer)nodes[rnd];

	}




	
	private Integer getNextNodeId(Network g, int cn){
		
		
		List<Integer> neighbors = g.neighborListOf(cn);
		if(neighbors.size() == 0)
			return -1;
		
		int index = new Random().nextInt(neighbors.size());
		
		Integer NodeId = neighbors.get(index);
		//g.getEdge(cn, NodeId).hidden = true;
		return NodeId;
		
		
	}
	
	
}
