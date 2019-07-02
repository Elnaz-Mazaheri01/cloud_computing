package cloud;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import javax.faces.bean.ManagedBean;
import javax.faces.bean.RequestScoped;

@ManagedBean
@RequestScoped
public class Scale {
	
	public Scale() {
		
	}
	
	public void scaleOut() {
//		String command = "cmd /c python D:\\eclipse-workspace\\MyDeploymentScript\\src\\my_deployment_script.py";
		String command = "cmd /c python D:\\eclipse-workspace\\MyDeploymentScript\\src\\scaleOut.py";
		try {
			Process p = Runtime.getRuntime().exec(command);
			BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
			br.lines().forEach(line -> System.out.println(line));
			br.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	

}

