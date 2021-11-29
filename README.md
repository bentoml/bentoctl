# BentoML Control (BentoCtl)


## Installing

`pip install --editable .`

To activate tab completion for you shell, source the script in
`bentoctl/completion`. For More info check [click docs](https://click.palletsprojects.com/en/8.0.x/shell-completion/)


## Example

### 1. With `heroku`

1. add `heroku` into bentoctl

  ```
  bentoctl operators add heroku
  ```

  2. you can list all available operators by running -
  ```
  bentoctl operators list
  ```

  3. Now you have bentoctl configured to do a deployment. Try interactive deployment
     by calling - 
     
     ```
     bentoctl deploy
     # or
     bentoctl deploy --name test --operator heroku --bento_bundle .
     ```

     fill in the values requested and it will create a deployment_spec.yaml file
     at the end


  4. You can deploy directly if you provide a deployment_spec.yaml file. Let try
     it with a test spec file

     ```
     bentoctl deploy ./tests/test_deployment_spec.yaml
     ```
