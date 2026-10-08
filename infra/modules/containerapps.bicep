metadata description = 'Container Apps environment (Consumption) and the Foundry Guide container app.'

@description('Azure region.')
param location string

@description('Tags applied to every resource.')
param tags object

@description('Container Apps environment name.')
param environmentName string

@description('Container app name.')
@maxLength(32)
param appName string

@description('Resource ID of the Log Analytics workspace receiving environment logs.')
param logAnalyticsWorkspaceId string

@description('Name of the Application Insights component used by the app.')
param appInsightsName string

@description('Resource ID of the user-assigned managed identity.')
param identityId string

@description('Client ID of the user-assigned managed identity (AZURE_CLIENT_ID).')
param identityClientId string

@description('Login server of the container registry.')
param registryLoginServer string

@description('Container image. The quickstart placeholder listens on port 80 and has no health endpoints.')
param containerImage string

@description('Application version exposed as APP_VERSION.')
param appVersion string

@description('Foundry project endpoint.')
param projectEndpoint string

@description('Primary (agent) model deployment name.')
param modelDeploymentName string

@description('Fast model deployment name.')
param fastModelDeploymentName string

@description('Foundry agent name.')
param agentName string

@description('Minimum number of replicas.')
@minValue(0)
param minReplicas int = 1

@description('Maximum number of replicas.')
@minValue(1)
param maxReplicas int = 3

var isPlaceholder = startsWith(toLower(containerImage), 'mcr.microsoft.com/k8se/quickstart')
var appPort = 8000
var targetPort = isPlaceholder ? 80 : appPort

var probes = isPlaceholder
  ? []
  : [
      {
        type: 'Startup'
        httpGet: {
          path: '/health/live'
          port: appPort
          scheme: 'HTTP'
        }
        initialDelaySeconds: 3
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 24
      }
      {
        type: 'Liveness'
        httpGet: {
          path: '/health/live'
          port: appPort
          scheme: 'HTTP'
        }
        periodSeconds: 15
        timeoutSeconds: 5
        failureThreshold: 3
      }
      {
        type: 'Readiness'
        httpGet: {
          path: '/health/ready'
          port: appPort
          scheme: 'HTTP'
        }
        periodSeconds: 10
        timeoutSeconds: 5
        failureThreshold: 3
        successThreshold: 1
      }
    ]

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2026-01-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    zoneRedundant: false
  }
}

// Keyless log routing: the environment streams logs to Log Analytics through diagnostic settings.
// 2021-05-01-preview is the newest diagnosticSettings API and the first to support categoryGroup.
#disable-next-line use-recent-api-versions
resource environmentDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'to-log-analytics'
  scope: managedEnvironment
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

resource containerApp 'Microsoft.App/containerApps@2026-01-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identityId}': {}
    }
  }
  properties: {
    environmentId: managedEnvironment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: registryLoginServer
          identity: identityId
        }
      ]
      secrets: [
        {
          name: 'appinsights-connection-string'
          value: appInsights.properties.ConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'app'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'FOUNDRY_PROJECT_ENDPOINT'
              value: projectEndpoint
            }
            {
              name: 'FOUNDRY_MODEL_DEPLOYMENT'
              value: modelDeploymentName
            }
            {
              name: 'FOUNDRY_FAST_MODEL_DEPLOYMENT'
              value: fastModelDeploymentName
            }
            {
              name: 'FOUNDRY_AGENT_NAME'
              value: agentName
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: identityClientId
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              secretRef: 'appinsights-connection-string'
            }
            {
              name: 'APP_VERSION'
              value: appVersion
            }
          ]
          probes: probes
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output environmentName string = managedEnvironment.name
output appName string = containerApp.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
