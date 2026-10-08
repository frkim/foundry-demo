using 'main.bicep'

param environmentName = 'dev'
param location = 'swedencentral'
// Container Apps capacity in swedencentral was constrained (AKSCapacityHeavyUsage) at deployment time.
param appLocation = 'francecentral'
param workload = 'foundrydemo'
param owner = 'frkim'
param costCenter = 'demo'
param dataClassification = 'public'

param presenterPrincipalIds = [
  {
    // Deployer service principal (GitHub Actions / local deployments)
    id: 'b8381ed6-10cc-4662-a577-ca4771835142'
    type: 'ServicePrincipal'
  }
  {
    // Local presenter service principal (demo laptop, video pipeline)
    id: '7c0314ef-8344-427f-bc8b-77cf373e9345'
    type: 'ServicePrincipal'
  }
]
