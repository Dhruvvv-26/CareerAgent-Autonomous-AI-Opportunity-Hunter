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

export async function getJobs(category = null, page = 1, perPage = 50, bookmarked = null) {
    const params = { page, per_page: perPage };
    if (category) params.category = category;
    if (bookmarked !== null) params.bookmarked = bookmarked;
    const response = await api.get('/jobs', { params });
    return response.data;
}

export async function getJobStats() {
    const response = await api.get('/job-stats');
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

export async function toggleBookmark(jobId) {
    const response = await api.put(`/toggle-bookmark/${jobId}`);
    return response.data;
}

export async function archiveJob(jobId) {
    const response = await api.put(`/archive-job/${jobId}`);
    return response.data;
}

export async function deleteJob(jobId) {
    const response = await api.delete(`/delete-job/${jobId}`);
    return response.data;
}

export async function getStatusHistory(jobId) {
    const response = await api.get(`/status-history/${jobId}`);
    return response.data;
}

export async function getEmailHistory(jobId) {
    const response = await api.get(`/email-history/${jobId}`);
    return response.data;
}

export function getExportUrl() {
    return '/export-jobs';
}
