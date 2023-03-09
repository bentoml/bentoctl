# AWS EC2 Deployment

AWS EC2 is great if you want to have larger models that require GPUs for inference or to have an instance running all the time to avoid cold starts.

[Github Repo](https://github.com/bentoml/aws-ec2-deploy)

## Installation
```
> bentoctl operator install aws-ec2
```

## Configuration

* `region`: AWS region for deployment
* `instance_type`: Instance type for the EC2 deployment.  See https://aws.amazon.com/ec2/instance-types/ for the entire list.
* `ami_id`: Amazon Machine Image (AMI) used for the EC2 instance. Check out https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html for more information.
* `ennable_gpus`: If using GPU-accelerated instance_types then ennable this.
* `environment_variables`: List of environment variables that should be passed to the instance.

## Troubleshooting

  To run any troubleshooting we will have to connect to the EC2 instance. The EC2 instance created with terraform has EC2-connect configured by default but you will have to open the SSH port to connect to it.
  
  ### Open SSH port
  
  To open the SSH port, open the `main.tf` that has been generated and add an additional ingress rule into the `aws_security_group` resource named `allow_bentoml`. 
  ```hcl
  resource "aws_security_group" "allow_bentoml" {
    name        = "${var.deployment_name}-bentoml-sg"
    description = "SG for bentoml server"

    ingress {
      description      = "HTTP for bentoml"
      from_port        = 80
      to_port          = 80
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }

    # add this to open SSH port for the EC2 instance.
    ingress {
      description      = "SSH access for server"
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }

    egress {
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  }
```
  Now you can run terraform apply again to make the changes to the resources.
  ```bash
  terraform apply -var-file=bentoctl.tfvars -auto-approve
  ```
  
  ### Connect to the EC2 instance
  You can connect to an instance using the Amazon EC2 console (browser-based client) by selecting the instance from the console and choosing to connect using EC2 Instance Connect. Instance Connect handles the permissions and provides a successful connection.

To connect to your instance using the browser-based client from the Amazon EC2 console

1. Open the Amazon EC2 console at https://console.aws.amazon.com/ec2/.
2. In the navigation pane, choose Instances.
3. Select the instance and choose Connect.
4. Choose EC2 Instance Connect.
5. Verify the user name and choose Connect to open a terminal window.

For more information check out the [official docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-methods.html#ec2-instance-connect-connecting-console)

### Check docker container logs
Once connected, make sure the docker container is running by running
```bash
docker ps
```
This will show all the containers running. Ideally, you should see something like
```
CONTAINER ID   IMAGE                              COMMAND                  CREATED         STATUS        PORTS                                   NAMES
4681b23e0c51   iris_classifier:kiouq7wmi2gmockr   "./env/docker/entryp…"   2 seconds ago   Up 1 second   0.0.0.0:80->3000/tcp, :::80->3000/tcp   bold_kirch
```
To view the logs from the container, run
```
docker logs <NAMES>
```
and it will output the logs from the container.

### Check cloud-init script logs
If the docker container is not running or if the `docker` command is not available in the ec2 instance then it could be an issue with the initialisation script. You can check the logs for the init-script by running
```bash
sudo cat /var/log/cloud-init-output.log
```
