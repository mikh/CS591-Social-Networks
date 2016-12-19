import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import entity.Edge;
import entity.Network;

public class Main {

	public static void main(String[] args) {

		// if(args.length < 3)
		// return;

		// Statics.graphName = args[0];
		// final String filepath = args[1];//"realDataset/" +Statics.graphName
		// +".txt";
		// Integer type = Integer.parseInt(args[2]);

		Statics.graphName = "Bernard";
		final String filepath = "D:/CS/DataSet/_test/" + Statics.graphName
				+ ".txt";

		final Network g = Parser.getGraph(filepath);

		System.out.println("edges : " + g.edgeSet().size());

		Statics.K = g.numberOfEdges() / 10;
		Statics.numberOfSteps = g.numberOfEdges() / 5;

		double[] original_X = distributeData(g, Statics.K);

		double[][] A;
		double[] Y;

		double RW_num = .05;
		double RW_num_end = .225;
		if (args.length == 4) {
			RW_num_end = .45;
		}
		double RW_num_step = 0.025;

		while (RW_num <= RW_num_end) {

			Statics.numberOfMeasurments = (int) (RW_num * g.numberOfEdges());
			RW_num = RW_num + RW_num_step;

			for (int i = 0; i < 0; i++) {
				CSRW rnd = new CSRW();
				A = rnd.getMeasurmentMatrix(g, Statics.numberOfMeasurments,
						Statics.numberOfSteps);
				Y = getMeasurments(A, original_X);
				try {
					Optimizer.optimize(A, Y, original_X, rnd.seenW, "_RW" + i);

				} catch (Exception e) {
					e.printStackTrace();
				}
			}
			CSWeighted rnd;
			for (int i = 0; i < 1; i++) {
				rnd = new CSWeighted();
				A = rnd.getMeasurmentMatrix(g, Statics.numberOfMeasurments,
						Statics.numberOfSteps);
				Y = getMeasurments(A, original_X);
				try {
					Optimizer.optimize(A, Y, original_X, rnd.seenW, "_mahyar"
							+ i);

				} catch (Exception e) {
					e.printStackTrace();
				}
			}
			CSUCSW ucs;
			for (int i = 0; i < 0; i++) {
				ucs = new CSUCSW();
				A = ucs.getMeasurmentMatrix(g, Statics.numberOfMeasurments,
						Statics.numberOfSteps);
				Y = getMeasurments(A, original_X);

				try {
					Optimizer.optimize(A, Y, original_X, ucs.seenW, "_UCS" + i);

				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}

	}

	public static double[] distributeData(Network g, int K) {

		List<Edge> edges = new ArrayList<Edge>(g.edgeSet());

		Collections.sort(edges);

		double[] original_X = new double[g.numberOfEdges()];
		for (int i = 0; i < K; i++) {
			System.out.print(edges.get(i).getWeight() + " , ");
			original_X[edges.get(i).edgeId] = 5;
		}

		return original_X;

	}

	public static double[] getMeasurments(double[][] A, double[] X) { // Consider
																		// X as
																		// a 1*n
																		// matrix

		double[] Y = new double[A.length];

		double t = 0;
		for (int i = 0; i < A.length; i++) {

			for (int j = 0; j < A[0].length; j++) {
				t += A[i][j] * X[j];
			}
			Y[i] = t;
			t = 0;
		}
		return Y;

	}
}
