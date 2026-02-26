import { useState } from 'react';
import { uploadResume } from '../api/api';
import ResumeSummaryCard from './ResumeSummaryCard';

export default function ResumeUpload() {
    const [file, setFile] = useState(null);
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [dragOver, setDragOver] = useState(false);

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setError('');
        try {
            const data = await uploadResume(file);
            if (data.error) {
                setError(data.error);
            } else {
                setProfile(data.profile);
            }
        } catch {
            setError('Upload failed. Make sure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const dropped = e.dataTransfer.files[0];
        if (dropped && dropped.name.toLowerCase().endsWith('.pdf')) {
            setFile(dropped);
            setError('');
        } else {
            setError('Only PDF files are accepted.');
        }
    };

    return (
        <div className="section">
            <div className="card">
                <h2 className="card-title">Upload Resume</h2>
                <p className="card-subtitle">
                    Upload your PDF resume to extract skills and personalize opportunity matching.
                </p>

                <div
                    className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('resume-input').click()}
                >
                    <input
                        id="resume-input"
                        type="file"
                        accept=".pdf"
                        style={{ display: 'none' }}
                        onChange={(e) => { setFile(e.target.files[0]); setError(''); }}
                    />
                    {file ? (
                        <div className="file-info">
                            <span>✓</span>
                            <span className="file-name">{file.name}</span>
                            <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                        </div>
                    ) : (
                        <>
                            <span className="upload-icon">↑</span>
                            <p className="upload-text">Drag & Drop PDF or Click to Upload</p>
                        </>
                    )}
                </div>

                <button
                    className="upload-btn"
                    onClick={handleUpload}
                    disabled={loading || !file}
                >
                    {loading ? (
                        <><span className="spinner"></span> Analyzing…</>
                    ) : (
                        'Extract Skills'
                    )}
                </button>

                {error && <div className="error-msg">{error}</div>}

                {profile && <ResumeSummaryCard profile={profile} />}
            </div>
        </div>
    );
}
