# Heroku Deployment
Heroku is a popular platform as a service(PaaS) based on managed container system. It provides a complete solution for building, running, and scaling the ML models. It is very good if you want to experiment fast but does have limitations on the model size.

## Installation
```
> bentoctl operator install heroku
```

## Configuration Options
This is the list of configurations you can use to deploy your bento to Heroku. For more information about options check the corresponding Heroku docs provided.

- `dyno_counts`: Number of dynos running for the deployment. A dyno is an isolated, virtualized Linux container that is designed to execute your code. Check the [docs](https://devcenter.heroku.com/articles/dyno-types#default-scaling-limits), and [article](https://www.heroku.com/dynos) for more information
- `dyno_type`: Dyno (instance) type. Each dyno type provides a certain number of RAM, CPU share, Compute, and whether it sleeps. Check the [docs](https://devcenter.heroku.com/articles/dyno-types) for more information
