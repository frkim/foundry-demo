metadata description = 'Microsoft Foundry (new) resource, project, model deployments and data-plane role assignments.'

import { modelDeploymentType, principalType } from 'types.bicep'

@description('Azure region (must support the Responses API and Foundry Agent Service).')
param location string

@description('Tags applied to every resource.')
param tags object

@description('Foundry resource name; also used as the custom subdomain.')
@minLength(2)
@maxLength(64)
param accountName string

@description('Foundry project name.')
param projectName string

@description('Foundry project display name.')
param projectDisplayName string

@description('Foundry project description.')
param projectDescription string

@description('Model deployments, created one at a time in the given order.')
param modelDeployments modelDeploymentType[]

@description('Name of the workload managed identity (same resource group).')
param workloadIdentityName string

@description('Additional principals (presenters, deployer) that call the Foundry data plane.')
param presenterPrincipals principalType[] = []

@description('Name of the Application Insights component connected to the project for tracing.')
param appInsightsName string

var azureAiUserRoleId = '53ca6127-db72-4b80-b1b0-d745d6d5456d'
var speechUserRoleId = 'f2dc8367-1007-4938-bd23-fe263f013447'

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource workloadIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = {
  name: workloadIdentityName
}

resource account 'Microsoft.CognitiveServices/accounts@2026-07-01' = {
  name: accountName
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: accountName
    allowProjectManagement: true
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2026-07-01' = {
  parent: account
  name: projectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: projectDisplayName
    description: projectDescription
  }
}

// Model deployments on the same account must not run concurrently.
@batchSize(1)
resource deployments 'Microsoft.CognitiveServices/accounts/deployments@2026-07-01' = [
  for model in modelDeployments: {
    parent: account
    name: model.name
    tags: tags
    sku: {
      name: model.skuName
      capacity: model.capacity
    }
    properties: {
      model: {
        format: model.?modelFormat ?? 'OpenAI'
        name: model.modelName
        version: model.modelVersion
      }
      versionUpgradeOption: 'NoAutoUpgrade'
    }
    dependsOn: [
      project
    ]
  }
]

// Lets the Foundry portal show traces from the project's Application Insights resource.
resource appInsightsConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2026-07-01' = {
  parent: project
  name: appInsights.name
  properties: {
    category: 'AppInsights'
    target: appInsights.id
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: appInsights.properties.ConnectionString
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: appInsights.id
    }
  }
  dependsOn: [
    deployments
  ]
}

resource workloadAiUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(account.id, workloadIdentity.id, azureAiUserRoleId)
  scope: account
  properties: {
    principalId: workloadIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', azureAiUserRoleId)
  }
}

resource presenterAiUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for principal in presenterPrincipals: {
    name: guid(account.id, principal.id, azureAiUserRoleId)
    scope: account
    properties: {
      principalId: principal.id
      principalType: principal.type
      roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', azureAiUserRoleId)
    }
  }
]

resource presenterSpeechUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for principal in presenterPrincipals: {
    name: guid(account.id, principal.id, speechUserRoleId)
    scope: account
    properties: {
      principalId: principal.id
      principalType: principal.type
      roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', speechUserRoleId)
    }
  }
]

output accountId string = account.id
output accountName string = account.name
output accountEndpoint string = account.properties.endpoint
output projectName string = project.name
output projectEndpoint string = '${account.properties.endpoints['AI Foundry API']}api/projects/${project.name}'
