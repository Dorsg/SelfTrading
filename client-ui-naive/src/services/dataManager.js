import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export async function fetchAccountSnapshot() {
  try {
    const response = await axios.get(`${BASE_URL}/account/snapshot`);
    return response.data;
  } catch (error) {
    console.error('Error fetching account snapshot:', error);
    return null;
  }
}

export async function fetchOpenPositions() {
  try {
    const response = await axios.get(`${BASE_URL}/account/positions`);
    return response.data;
  } catch (error) {
    console.error('Error fetching open positions:', error);
    return null;
  }
}

export async function fetchOrders() {
  try {
    const response = await axios.get(`${BASE_URL}/orders`);
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    return null;
  }
}

export async function fetchExecutedTrades() {
  try {
    const response = await axios.get(`${BASE_URL}/executed-trades`);
    return response.data;
  } catch (error) {
    console.error('Error fetching executed trades:', error);
    return null;
  }
}


export async function createRunnerAPI(runnerData) {
  try {
    console.log("Sending runnerData:", runnerData);
    const response = await axios.post(`${BASE_URL}/runners`, runnerData);
    return response.data;
  } catch (error) {
    console.error('Error creating runner:', error);
    return null;
  }
}

export async function deleteRunnersAPI(ids) {
  try {
    const response = await axios.delete(`${BASE_URL}/runners`, {
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
    const response = await axios.post(`${BASE_URL}/runners/activate`, { ids });
    return response.data;
  } catch (error) {
    console.error('Error activating runners:', error);
    return null;
  }
}

export async function deactivateRunnersAPI(ids) {
  try {
    const response = await axios.post(`${BASE_URL}/runners/deactivate`, { ids });
    return response.data;
  } catch (error) {
    console.error('Error deactivating runners:', error);
    return null;
  }
}