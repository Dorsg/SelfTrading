import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export async function fetchAccountSnapshot() {
  try {
    const response = await axios.get(`${BASE_URL}/account/snapshot`);
    return response.data;
  } catch (error) {
    console.error('Error fetching account snapshot:', error);
    throw error;
  }
}

export async function fetchOpenPositions() {
  try {
    const response = await axios.get(`${BASE_URL}/account/positions`);
    return response.data;
  } catch (error) {
    console.error('Error fetching open positions:', error);
    throw error;
  }
}

export async function fetchOrders() {
  try {
    const response = await axios.get(`${BASE_URL}/orders`);
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
}

export async function fetchExecutedTrades() {
  try {
    const response = await axios.get(`${BASE_URL}/executed-trades`);
    return response.data;
  } catch (error) {
    console.error('Error fetching executed trades:', error);
    throw error;
  }
}