metadata description = 'All workload resources inside the resource group.'

import { modelDeploymentType, principalType } from 'types.bicep'

@description('Azure region.')
param location string

@description('Azure region for the Container Apps environment and app.')
param appLocation string

@description('Environment name, for example dev.')
param environmentName string

@description('Workload name used in resource names.')
param workload string

@description('Tags applied to every resource.')
param tags object

@description('Container image for the app.')
param containerImage string

@description('Application version exposed as APP_VERSION.')
param appVersion string

@description('Foundry agent name.')
param agentName string

@description('Primary (agent) model deployment.')
param primaryModel modelDeploymentType

@description('Fast model deployment used for comparisons.')
param fastModel modelDeploymentType

@description('Principals that receive Azure AI User and Cognitive Services Speech User on the Foundry resource.')
param presenterPrincipals principalType[]

var suffix = take(uniqueString(subscription().id, resourceGroup().name), 5)
var baseName = '${workload}-${environmentName}'

var names = {
  foundry: 'aif-${baseName}-${suffix}'
  project: 'proj-${baseName}'
  identity: 'id-${baseName}'
  logAnalytics: 'log-${baseName}'
  appInsights: 'appi-${baseName}'
  containerEnvironment: 'cae-${baseName}'
  containerApp: 'ca-${baseName}'
  registry: 'cr${replace(workload, '-', '')}${environmentName}${suffix}'
}

module monitoring 'monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location: location
    tags: tags
    logAnalyticsName: names.logAnalytics
    appInsightsName: names.appInsights
  }
}

module identity 'identity.bicep' = {
  name: 'identity'
  params: {
    location: location
    tags: tags
    identityName: names.identity
  }
}

module registry 'registry.bicep' = {
  name: 'registry'
  params: {
    location: location
    tags: tags
    registryName: names.registry
    pullIdentityName: names.identity
  }
  dependsOn: [
    identity
  ]
}

module foundry 'foundry.bicep' = {
  name: 'foundry'
  params: {
    location: location
    tags: tags
    accountName: names.foundry
    projectName: names.project
    projectDisplayName: 'Foundry demo (${environmentName})'
    projectDescription: 'Foundry Guide demo agent for the Microsoft Foundry session.'
    modelDeployments: [
      primaryModel
      fastModel
    ]
    workloadIdentityName: names.identity
    presenterPrincipals: presenterPrincipals
    appInsightsName: names.appInsights
  }
  dependsOn: [
    identity
    monitoring
  ]
}

module containerApps 'containerapps.bicep' = {
  name: 'containerapps'
  params: {
    location: appLocation
    tags: tags
    environmentName: names.containerEnvironment
    appName: names.containerApp
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsId
    appInsightsName: names.appInsights
    identityId: identity.outputs.id
    identityClientId: identity.outputs.clientId
    registryLoginServer: registry.outputs.loginServer
    containerImage: containerImage
    appVersion: appVersion
    projectEndpoint: foundry.outputs.projectEndpoint
    modelDeploymentName: primaryModel.name
    fastModelDeploymentName: fastModel.name
    agentName: agentName
  }
}

output acrName string = registry.outputs.name
output acrLoginServer string = registry.outputs.loginServer
output containerAppName string = containerApps.outputs.appName
output containerAppFqdn string = containerApps.outputs.fqdn
output foundryAccountName string = foundry.outputs.accountName
output foundryEndpoint string = foundry.outputs.accountEndpoint
output projectEndpoint string = foundry.outputs.projectEndpoint
output uamiClientId string = identity.outputs.clientId
