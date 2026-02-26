import axios from 'axios';

const api = axios.create({
    baseURL: '',
    timeout: 120000,
});

export async function uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload-resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
}

export async function runSearch() {
    const response = await api.post('/run-search');
    return response.data;
}

export async function getJobs(category = null) {
    const params = {};
    if (category) params.category = category;
    const response = await api.get('/jobs', { params });
    return response.data;
}

export async function updateJobStatus(jobId, status) {
    const response = await api.put(`/update-status/${jobId}`, null, {
        params: { status },
    });
    return response.data;
}
