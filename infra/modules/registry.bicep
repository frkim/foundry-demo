metadata description = 'Azure Container Registry (Basic, admin user disabled) with AcrPull for the workload identity.'

@description('Azure region.')
param location string

@description('Tags applied to every resource.')
param tags object

@description('Registry name (alphanumeric, globally unique).')
@minLength(5)
@maxLength(50)
param registryName string

@description('Name of the workload managed identity (same resource group) that pulls images.')
param pullIdentityName string

var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = {
  name: pullIdentityName
}

resource registry 'Microsoft.ContainerRegistry/registries@2025-11-01' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    anonymousPullEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, pullIdentity.id, acrPullRoleId)
  scope: registry
  properties: {
    principalId: pullIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
  }
}

output id string = registry.id
output name string = registry.name
output loginServer string = registry.properties.loginServer
