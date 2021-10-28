# bento-cloud-deployment-tool (BCDT)

This is the prototype for the deployment-tool, design docs is here (https://www.notion.so/bentoml/bento-cloud-deploy-tool-bcdt-e9c2b7e2d851455f822730d27e31e2fc)

## Installing

`pip install --editable .`

To activate tab completion for you shell, source the script in
`bcdt/completion`. For More info check [click docs](https://click.palletsprojects.com/en/8.0.x/shell-completion/)


## Example

### 1. With `testop` - a test operator for testing purposes.

1. add `testop` into bcdt. Since `testop` is present in local filesystem we are
   using that mode for adding the operator.

  ```
  bcdt operators add tests/testop
  ```

  2. you can list all available operators by running -
  ```
  bcdt operators list
  ```

  3. Now you have bcdt configured to do a deployment. Try interactive deployment
     by calling - 
     
     ```
     bcdt deploy
     ```

     fill in the values requested and it will create a deployment_spec.yaml file
     at the end


  4. You can deploy directly if you provide a deployment_spec.yaml file. Let try
     it with a test spec file

     ```
     bcdt deploy ./tests/test_deployment_spec.yaml
     ```
