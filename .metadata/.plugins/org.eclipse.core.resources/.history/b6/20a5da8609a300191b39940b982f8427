package cloud;


import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import javax.faces.bean.ManagedBean;
import javax.faces.bean.RequestScoped;

import javax.servlet.http.Part;

@ManagedBean
@RequestScoped
public class UploadBean {

	private String containerName;
	private Part file;
	private String name;
	
	public UploadBean() {
		
	}
	
	
	//create getter&setter Methods
	public String getContainerName() {
		return containerName;
	}

	public void setContainerName(String containerName) {
		this.containerName = containerName;
	}
	
	public Part getFile() {
		return file;
	}

	public void setFile(Part file) {
		this.file = file;
	}
	
	public String getName() {
			return name;
	}

	public void setName(String name) {
			this.name = name;
	}
	public void createInstance() {
		String command = "cmd /c python D:\\eclipse-workspace\\MyDeploymentScript\\src\\my_deployment_script.py";
//		String command = "cmd /c python D:\\eclipse-workspace\\MyDeploymentScript\\src\\scaleOut.py";
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
	
	

	//get user name to create container
	public String goToUploadPage() {
//		createInstance();
		String command = "python /tmp/cloud_computing/MyDeploymentScript/src/create_container.py";
//		String command = "cmd /c python D:\\eclipse-workspace\\MyDeploymentScript\\src\\create_container.py";
		try {
			Process p = Runtime.getRuntime().exec(command + " " + this.name);
			BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
			br.lines().forEach(line -> System.out.println(line));
			br.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return "myresponse";
	}
	
	
	
	//upload image in container of openstack
	public String upload() throws IOException {
		
		this.containerName=String.valueOf(this.name);
		
		if (this.file != null) {

	       
			String objectName = this.file.getSubmittedFileName();
			String filePath = "/tmp/" + this.file.getSubmittedFileName();
//			String filePath = "D:\\" + this.file.getSubmittedFileName();
			this.file.write(filePath);
			String command = "python /tmp/cloud_computing/MyDeploymentScript/src/upload_object.py";
//			String command = "cmd /c python D:\\eclipse-workspace\\MyDeploymentScript\\src\\upload_object.py";
//			String command = "cmd /c python D:\\test.py";
			try {
				Process p = Runtime.getRuntime().exec(command + " " + containerName + " " + objectName + " " + filePath);
				BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
				br.lines().forEach(line -> System.out.println(line));
				br.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}	
		return "myresponse";
	}

}
	
