import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.Stack;

import org.jgrapht.UndirectedGraph;

import entity.Edge;
import entity.Network;


public class CSUCSW {

	 Stack<Integer> visitedNodes = new Stack<Integer>();
	
	 double totalStartProbs;
	 double [] startProbs ;

	 double[] edgeProbs;
	
	 double[] seenW;
	 boolean seperateGoodBad = true; 
	
	public  double[][] getMeasurmentMatrix(Network g, int numberOfMeasurments, int numberOfSteps){
		startProbs = new double[g.maxNodeId + 1];// nodeId start from 0 or 1
		edgeProbs = new double[g.numberOfEdges()];
		
		double [][] A = new double[numberOfMeasurments][g.edgeSet().size()];
		
		seenW = new double[numberOfMeasurments];
		
		startProbs = getStartProb(g);

		
		int currentNodeId = -1, nextNodeId = -1, m = 0;
		Edge e;
		for(int i = 0; i< numberOfMeasurments ; i++){
			
			g.unhideAllEdges();
			
			currentNodeId = selectStartNode();
			visitedNodes.removeAllElements();
			visitedNodes.push(currentNodeId);
			
			System.out.println(m + " : " + currentNodeId + " ");
			
			for(int j = 0 ; j < numberOfSteps ; j++){
				nextNodeId = getNextNodeId(g, currentNodeId);
				//g.lessHideAll();
				if(nextNodeId != -1){
					e = g.getEdge(currentNodeId, nextNodeId);					
					currentNodeId = nextNodeId ;
					visitedNodes.push(currentNodeId);
					A[i][e.edgeId]++;
					seenW[i] += e.getWeight();
					g.hideEdge(e);
					
				}else{//backtrack
					//System.out.print(" bt ");
					if(visitedNodes.size() < 2) break;
					visitedNodes.pop(); // isolated node	(current Node)				
					nextNodeId = visitedNodes.pop(); // last visited Node 
					visitedNodes.push(nextNodeId); //push again
					
					e = g.getEdge(currentNodeId, nextNodeId);					
					currentNodeId = nextNodeId ;
					seenW[i] += e.getWeight();
					A[i][e.edgeId]++;
					
//					g.hideEdge(e);
					
				}
				
				
			}
			//System.out.println();
			
			m++;
		}
	
		
		
		
		
		return A;
	}
	
	
	
	
	private int selectStartNode() {
		
		
//		Object[] nodes = g.vertexSet().toArray();
//		int rnd = new Random().nextInt(nodes.length);
//		return (Integer)nodes[rnd];
		
		
		double rnd = new Random().nextDouble() * totalStartProbs;
		if(rnd <= startProbs[0])
			return 0;
		for(int i = 1; i < startProbs.length ; i++){
			if(startProbs[i] >= rnd && startProbs[i - 1] < rnd)
				return i; 
		}
		
		return -1;
		
	}



	public  double[] getStartProb(Network g){
		
		double total = 0;
		for (Integer v : g.vertexSet()) {
			startProbs[v] = (double)g.degreeOf(v)/g.totalDegree() + (double)g.getNodeWeight(v)/g.totalNodesWeight();
			total +=startProbs[v];
		}
		
		for (Integer v : g.vertexSet()) { // normalize
			startProbs[v] = startProbs[v]/total; //T
		}
		
		for (Integer v : g.vertexSet()) {
			startProbs[v] =  ((double)1/(g.numberOfNodes() - 1))*(1 - startProbs[v]);
		}
		
		totalStartProbs = startProbs[0];
		for(int i = 1 ; i< startProbs.length ; i++){
			totalStartProbs += startProbs[i];
			startProbs[i] += startProbs[i-1];
		}
		
		
		
		return startProbs;
	}
	
	private  Integer getNextNodeId(Network g, int cn){
		HashMap<Integer, Double> neighborsProb = getNeighborsProb(g, cn);
		
		if(neighborsProb == null || neighborsProb.size() == 0)
			return -1;
		

		
		double[] nbp = new double[neighborsProb.size()]; //probability of nodes
		int[] nbi = new int[neighborsProb.size()];		 //map NodeId to index of above array
		
		int i = 0;

		for(Integer index : neighborsProb.keySet() ){
			if(i == 0)
				nbp[i] = neighborsProb.get(index);
			else
				nbp[i] = nbp[i - 1] + neighborsProb.get(index);
			nbi[i] = index;
			i++;
		}

		
		
		double rnd = new Random().nextDouble() * nbp[nbp.length - 1]; // lastindex has total prob
		
		int Index = -1;
			
		if(rnd <= nbp[0])
			Index = 0;
		for(int j = 1 ; j < nbp.length ; j++){
			if(nbp[j] >= rnd && nbp[j - 1] < rnd)
				Index = j; 
		}
		
		if(Index == -1)
			return Index;
		
		g.nodeSeenCount[nbi[Index]]++;
		
		return nbi[Index];
		
		
		
	}
	
	private static HashMap<Integer, Double> getNeighborsProb(Network g, int cn){
		
		List<Integer> neighbors = g.neighborListOf(cn);
		HashMap<Integer, Double> badNeighborsProb = new HashMap<Integer, Double>(); // P(w) > P (CurrentNode)
		HashMap<Integer, Double> goodNeighborsProb = new HashMap<Integer, Double>(); // P(w) < p(CurrentNode)
		HashMap<Integer, Double> neighborsProb = new HashMap<Integer, Double>(); // return list
		double p = 0, total = 0;
		Edge e;
		


		//-- 2
		neighborsProb =  g.getNeighborProb_UCSWN(cn);
		double currentNodeProb = neighborsProb.get(-1);
		neighborsProb.remove(-1);
		
//		if(!seperateGoodBad){
//			return neighborsProb;
//		}
		
		for(Integer v : neighborsProb.keySet()){
			p = neighborsProb.get(v);
			if(p >= currentNodeProb){
				goodNeighborsProb.put(v, p);
			}
			else{
				badNeighborsProb.put(v, p);
			}
		}
		

		
		
		
		if(goodNeighborsProb.size() > 0){

			return goodNeighborsProb;
			
			
		}else if(badNeighborsProb.size() > 0){

			return badNeighborsProb;
			
		}else{
			return null;
		}
		
		
		
		
		
	}
	
}
