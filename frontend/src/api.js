const API_BASE = 'http://127.0.0.1:5000';

export const fetchGameStatus = async () => {
    const res = await fetch(`${API_BASE}/api/latest`);
    return res.json();
};

export const fetchHistory = async (limit = 100) => {
    const res = await fetch(`${API_BASE}/api/history?limit=${limit}`);
    return res.json();
};

export const fetchPrediction = async (algorithm = 'algo1') => {
    const res = await fetch(`${API_BASE}/api/prediction?algorithm=${algorithm}`);
    return res.json();
};

// Alias for compatibility
export const fetchPredictions = fetchPrediction;

export const fetchAllPredictions = async () => {
    const res = await fetch(`${API_BASE}/api/predictions/all`);
    return res.json();
};

export const fetchAlgorithms = async () => {
    const res = await fetch(`${API_BASE}/api/algorithms`);
    return res.json();
};

export const fetchSystemStatus = async () => {
    const res = await fetch(`${API_BASE}/api/status`);
    return res.json();
};

export const fetchAlgorithmHistory = async (algoId, limit = 100) => {
    const res = await fetch(`${API_BASE}/api/algorithm/${algoId}/history?limit=${limit}`);
    return res.json();
};

export const fetchAlgorithmsStats = async () => {
    const res = await fetch(`${API_BASE}/api/algorithms/stats`);
    return res.json();
};

export const queryIssue = async (issue) => {
    const res = await fetch(`${API_BASE}/api/query/${issue}`);
    return res.json();
};
