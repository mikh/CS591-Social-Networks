
public class Statics {
	
	public static int numberOfNodes;
	public static int numberOfEdges;
	public static int numberOfMeasurments;
	public static int numberOfSteps;
	public static int K; // K-sparse
	public static String graphName ;
	public static String type = "";
	
	public static String getFileName(){
		return "_"+graphName+"_"+numberOfMeasurments +"_"+ numberOfSteps +"_"+K;
	}
}
