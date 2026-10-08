metadata description = 'Shared user-defined types for the Foundry demo infrastructure.'

@export()
@description('A Microsoft Entra principal that receives data-plane roles on the Foundry resource.')
type principalType = {
  @description('Object ID of the principal.')
  id: string

  @description('Principal type used by the role assignment.')
  type: 'User' | 'Group' | 'ServicePrincipal'
}

@export()
@description('A Foundry model deployment.')
type modelDeploymentType = {
  @description('Deployment name (used by the application).')
  name: string

  @description('Model name in the Foundry catalog.')
  modelName: string

  @description('Model version.')
  modelVersion: string

  @description('Model format / publisher.')
  modelFormat: string?

  @description('Deployment SKU, for example GlobalStandard.')
  skuName: string

  @description('Capacity in thousands of tokens per minute.')
  @minValue(1)
  capacity: int
}
