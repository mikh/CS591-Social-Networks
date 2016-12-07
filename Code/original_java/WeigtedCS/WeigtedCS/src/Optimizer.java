import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

import matlabcontrol.MatlabConnectionException;
import matlabcontrol.MatlabInvocationException;
import matlabcontrol.MatlabProxy;
import matlabcontrol.MatlabProxyFactory;
import matlabcontrol.MatlabProxyFactoryOptions;
import matlabcontrol.MatlabProxyFactoryOptions.Builder;
import matlabcontrol.extensions.MatlabNumericArray;
import matlabcontrol.extensions.MatlabTypeConverter;




public class Optimizer {

	public static synchronized double[] optimize(double[][] A, double[] Y, double[] X, double[] W, String name) throws Exception{
		
	    
		String path = "D:/A.txt"; // Matrix would be large, write to file and then read it from matlab is more efficient
		PrintWriter pr = new PrintWriter(new FileWriter(path));
		for(int i = 0 ; i < A.length ; i++){
			for(int j = 0 ; j < A[0].length ; j++){
		    	pr.print(A[i][j]);
		    	if(j < A[0].length - 1)
		    		pr.print(" ");
		    }
			pr.println();
	    }
		pr.close();
		
		
		
	    double [][] YY = new double[Y.length][1]  ;
	    for(int i = 0 ; i < Y.length ; i++){
	    	YY[i][0] = Y[i];
	    }
	    double [][] XX = new double[X.length][1]  ;
	    for(int i = 0 ; i < X.length ; i++){
	    	XX[i][0] = X[i];
	    }
	    
	    double [][] WW = new double[W.length][1]  ;
	    for(int i = 0 ; i < W.length ; i++){
	    	WW[i][0] = W[i];
	    }
		
		//Create a proxy, which we will use to control MATLAB
		MatlabProxyFactoryOptions options = new MatlabProxyFactoryOptions.Builder()
	    .setUsePreviouslyControlledSession(true)
//	    .setHidden(true)
//	    .setMatlabLocation("C:/Program Files/MATLAB/R2010a/bin/matlab.exe")
	    .build(); 

	    MatlabProxyFactory factory = new MatlabProxyFactory(options);
	    MatlabProxy proxy = factory.getProxy();

	    MatlabTypeConverter processor = new MatlabTypeConverter(proxy);
	    proxy.eval("clear;");
//	    proxy.eval("A = zeros("+A.length+","+A[0].length+");");
//	    for(int i = 0 ; i < A.length ; i++){
//	    	processor.setNumericArray("A("+(i+1)+")", new MatlabNumericArray(A[i], null));
//	    }
	    //processor.setNumericArray("A", new MatlabNumericArray(A, null));
	    processor.setNumericArray("Y", new MatlabNumericArray(YY, null));
	    processor.setNumericArray("XX", new MatlabNumericArray(XX, null));
	    processor.setNumericArray("WW", new MatlabNumericArray(WW, null));
	    proxy.eval("A = dlmread('"+path+"',' ');");
	    proxy.eval("num_link = "+	A[0].length);
	    proxy.eval("disp(['Optimization started...']);");
	    proxy.eval("cvx_clear;");
	    proxy.eval("cvx_precision('high');"); //low medium default high best
	    proxy.eval("cvx_quiet(false);");
	    proxy.eval("cvx_begin");
	    proxy.eval("variable X(num_link);");
	    proxy.eval("minimize(norm(X,1)+norm(A*X - Y,2));");
	    proxy.eval("cvx_end");
	    proxy.eval("error2=norm(XX-X,2)/norm(XX,2)");
	    
	    proxy.eval("save('"+ name + Statics.getFileName()+".mat');");
	    
	    proxy.disconnect();    	    
	    
		return null;
	}
	

}
//cvx_clear;
//cvx_precision('high');
//cvx_quiet(false);
//cvx_begin
//variable X(17215);
//minimize(norm(X,1)+norm(A*X - Y,2));
//cvx_end