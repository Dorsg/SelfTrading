import axios from 'axios';

axios.defaults.baseURL = "";

export async function fetchAccountSnapshot() {
  try {
    const response = await axios.get(`/api/account/snapshot`);
    return response.data;
  } catch (error) {
    console.error('Error fetching account snapshot:', error);
    return null;
  }
}

export async function fetchOpenPositions() {
  try {
    const response = await axios.get(`/api/account/positions`);
    return response.data;
  } catch (error) {
    console.error('Error fetching open positions:', error);
    return null;
  }
}

export async function fetchOrders() {
  try {
    const response = await axios.get(`/api/orders`);
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    return null;
  }
}

export async function fetchExecutedTrades() {
  try {
    const response = await axios.get(`/api/executed-trades`);
    return response.data;
  } catch (error) {
    console.error('Error fetching executed trades:', error);
    return null;
  }
}


export async function createRunnerAPI(runnerData) {
  try {
    console.log("Sending runnerData:", runnerData);
    const response = await axios.post(`/api/runners`, runnerData);
    return response.data;
  } catch (error) {
    console.error('Error creating runner:', error);
    return null;
  }
}

export async function deleteRunnersAPI(ids) {
  try {
    const response = await axios.delete(`/api/runners`, {
      data: { ids }, // sending array of IDs
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting runners:', error);
    return null;
  }
}

export async function activateRunnersAPI(ids) {
  try {
    const response = await axios.post(`/api/runners/activate`, { ids });
    return response.data;
  } catch (error) {
    console.error('Error activating runners:', error);
    return null;
  }
}

export async function deactivateRunnersAPI(ids) {
  try {
    const response = await axios.post(`/api/runners/deactivate`, { ids });
    return response.data;
  } catch (error) {
    console.error('Error deactivating runners:', error);
    return null;
  }
}

export async function fetchIbStatus() {
  try {
    const { data } = await axios.get(`/api/ib/status`);
    return data.connected;   
  } catch (err) {
    console.error('Error fetching IB status:', err);
    return false;                 // pessimistic fallback
  }
}