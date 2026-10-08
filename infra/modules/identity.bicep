metadata description = 'User-assigned managed identity used by the workload.'

@description('Azure region.')
param location string

@description('Tags applied to every resource.')
param tags object

@description('Managed identity name.')
param identityName string

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: identityName
  location: location
  tags: tags
}

output id string = identity.id
output name string = identity.name
output principalId string = identity.properties.principalId
output clientId string = identity.properties.clientId
