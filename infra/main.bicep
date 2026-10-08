metadata description = 'Foundry demo: resource group, Microsoft Foundry (new) resource and project, and the Foundry Guide container app.'

targetScope = 'subscription'

import { modelDeploymentType, principalType } from 'modules/types.bicep'

@description('Environment name.')
@allowed([
  'dev'
  'test'
  'prod'
])
param environmentName string = 'dev'

@description('Azure region; must support the Responses API and Foundry Agent Service.')
param location string = 'swedencentral'

@description('Azure region for the Container Apps environment and app. Defaults to location; override it when Container Apps capacity is constrained there.')
param appLocation string = location

@description('Workload name used in resource names.')
@minLength(3)
@maxLength(12)
param workload string = 'foundrydemo'

@description('Owner tag value.')
param owner string

@description('Cost center tag value.')
param costCenter string = 'demo'

@description('Data classification tag value.')
@allowed([
  'public'
  'internal'
  'confidential'
  'restricted'
])
param dataClassification string = 'public'

@description('Container image for the app. The default is a placeholder used until the first image is built.')
param containerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('Application version exposed as APP_VERSION (the deploy workflow passes the git SHA).')
param appVersion string = 'local'

@description('Foundry agent name.')
param agentName string = 'foundry-guide'

@description('Principals that receive Azure AI User and Cognitive Services Speech User on the Foundry resource.')
param presenterPrincipalIds principalType[] = []

@description('Primary model deployment used by the agent.')
param primaryModel modelDeploymentType = {
  name: 'gpt-5.4-mini'
  modelName: 'gpt-5.4-mini'
  modelVersion: '2026-03-17'
  skuName: 'GlobalStandard'
  capacity: 50
}

@description('Fast model deployment used for comparisons.')
param fastModel modelDeploymentType = {
  name: 'gpt-5.4-nano'
  modelName: 'gpt-5.4-nano'
  modelVersion: '2026-03-17'
  skuName: 'GlobalStandard'
  capacity: 50
}

var regionAbbreviations = {
  swedencentral: 'swc'
  francecentral: 'frc'
  germanywestcentral: 'gwc'
  westeurope: 'weu'
  northeurope: 'neu'
  uksouth: 'uks'
  norwayeast: 'noe'
  switzerlandnorth: 'chn'
  polandcentral: 'plc'
  italynorth: 'itn'
  spaincentral: 'spc'
  eastus: 'eus'
  eastus2: 'eus2'
  westus: 'wus'
  westus3: 'wus3'
  australiaeast: 'aue'
  japaneast: 'jpe'
}

var regionAbbreviation = regionAbbreviations[?location] ?? location
var resourceGroupName = 'rg-${workload}-${environmentName}-${regionAbbreviation}'

var tags = {
  env: environmentName
  workload: workload
  owner: owner
  costCenter: costCenter
  dataClassification: dataClassification
}

resource resourceGroup 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module resources 'modules/resources.bicep' = {
  name: 'foundrydemo-resources'
  scope: resourceGroup
  params: {
    location: location
    appLocation: appLocation
    environmentName: environmentName
    workload: workload
    tags: tags
    containerImage: containerImage
    appVersion: appVersion
    agentName: agentName
    primaryModel: primaryModel
    fastModel: fastModel
    presenterPrincipals: presenterPrincipalIds
  }
}

output resourceGroupName string = resourceGroup.name
output acrName string = resources.outputs.acrName
output acrLoginServer string = resources.outputs.acrLoginServer
output containerAppName string = resources.outputs.containerAppName
output containerAppFqdn string = resources.outputs.containerAppFqdn
output foundryAccountName string = resources.outputs.foundryAccountName
output foundryEndpoint string = resources.outputs.foundryEndpoint
output projectEndpoint string = resources.outputs.projectEndpoint
output uamiClientId string = resources.outputs.uamiClientId
