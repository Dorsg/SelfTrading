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