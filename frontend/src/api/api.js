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

export async function getProfile() {
    const response = await api.get('/profile');
    return response.data;
}

export async function getEmailPreview(jobId) {
    const response = await api.get(`/email-preview/${jobId}`);
    return response.data;
}

export async function sendEmail({ job_id, to, subject, body }) {
    const response = await api.post('/send-email', { job_id, to, subject, body });
    return response.data;
}

export async function updateRecruiterEmail(jobId, email) {
    const response = await api.put(`/update-recruiter-email/${jobId}`, null, {
        params: { email },
    });
    return response.data;
}
