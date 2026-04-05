import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Documents
export const uploadDocument = async (file: File, tenantId: string = 'tenant_demo', documentType: string = 'brd') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('tenant_id', tenantId);
  formData.append('document_type', documentType);

  const response = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const listDocuments = async (tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/documents?tenant_id=${tenantId}`);
  return response.data;
};

export const getDocument = async (documentId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/documents/${documentId}?tenant_id=${tenantId}`);
  return response.data;
};

// Requirements
export const parseRequirements = async (documentId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.post('/requirements/parse', {
    document_id: documentId,
    tenant_id: tenantId,
  });
  return response.data;
};

export const listRequirements = async (tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/requirements?tenant_id=${tenantId}`);
  return response.data;
};

export const getRequirement = async (requirementId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/requirements/${requirementId}?tenant_id=${tenantId}`);
  return response.data;
};

// Configurations
export const generateConfiguration = async (
  requirementId: string,
  tenantId: string = 'tenant_demo',
  configName?: string
) => {
  const response = await api.post('/configurations/generate', {
    requirement_id: requirementId,
    tenant_id: tenantId,
    config_name: configName,
  });
  return response.data;
};

// Alias for consistency
export const generateConfig = generateConfiguration;

export const listConfigurations = async (tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/configurations?tenant_id=${tenantId}`);
  return response.data;
};

export const getConfiguration = async (configId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/configurations/${configId}?tenant_id=${tenantId}`);
  return response.data;
};

export const compareConfigurations = async (
  configIdA: string,
  configIdB: string,
  tenantId: string = 'tenant_demo'
) => {
  const response = await api.post('/configurations/compare', {
    config_id_a: configIdA,
    config_id_b: configIdB,
    tenant_id: tenantId,
  });
  return response.data;
};

export const getConfigVersions = async (configId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/configurations/${configId}/versions?tenant_id=${tenantId}`);
  return response.data;
};

// Simulations
export const runSimulation = async (configId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.post('/simulations/run', {
    config_id: configId,
    tenant_id: tenantId,
  });
  return response.data;
};

export const listSimulations = async (tenantId: string = 'tenant_demo', configId?: string) => {
  let url = `/simulations?tenant_id=${tenantId}`;
  if (configId) url += `&config_id=${configId}`;
  const response = await api.get(url);
  return response.data;
};

export const getSimulation = async (simulationId: string, tenantId: string = 'tenant_demo') => {
  const response = await api.get(`/simulations/${simulationId}?tenant_id=${tenantId}`);
  return response.data;
};

// Adapters
export const listAdapters = async (serviceType?: string) => {
  let url = '/adapters';
  if (serviceType) url += `?service_type=${serviceType}`;
  const response = await api.get(url);
  return response.data;
};

export const getAdapter = async (adapterId: string) => {
  const response = await api.get(`/adapters/${adapterId}`);
  return response.data;
};

export const getAdapterSchema = async (adapterId: string) => {
  const response = await api.get(`/adapters/${adapterId}/schema`);
  return response.data;
};

// Health
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
