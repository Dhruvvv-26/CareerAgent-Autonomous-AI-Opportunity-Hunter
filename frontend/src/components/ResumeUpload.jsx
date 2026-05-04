import { useState } from 'react';
import { uploadResume } from '../api/api';

export default function ResumeUpload({ onUploadSuccess }) {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setMsg('');
        try {
            await uploadResume(file);
            setMsg('Resume updated successfully!');
            if (onUploadSuccess) onUploadSuccess();
        } catch {
            setMsg('Upload failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="job-card" style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '4px' }}>Targeting & Profile</h3>
                    <p style={{ color: '#7d7d7d', fontSize: '0.85rem' }}>Upload your latest resume to update search keywords.</p>
                </div>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <input 
                        type="file" 
                        accept=".pdf" 
                        onChange={handleFileChange} 
                        style={{ fontSize: '0.8rem' }}
                    />
                    <button className="btn btn-accent" onClick={handleUpload} disabled={loading || !file}>
                        {loading ? 'Processing...' : 'Update Resume'}
                    </button>
                </div>
            </div>
            {msg && <div style={{ marginTop: '12px', fontSize: '0.85rem', color: '#22c55e' }}>{msg}</div>}
        </div>
    );
}
