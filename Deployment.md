# Deployment Instructions
Since this repo has a Dockerfile, the bot can be deployed to any environment that supports running containers.

For Azure Container Apps, you can follow [this guide](https://learn.microsoft.com/en-us/azure/container-apps/get-started?tabs=bash) to create the resources and then deploy the bot with:

`az containerapp up -n <containerapp name> --resource-group <resource group name> --location <location> --environment '<environment name>' --image <container image name> --target-port 80 --ingress external`