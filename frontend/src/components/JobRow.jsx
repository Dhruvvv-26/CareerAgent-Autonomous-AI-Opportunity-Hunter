import { updateJobStatus, toggleBookmark, archiveJob } from '../api/api';

export default function JobCard({ job, onRefresh, onMailClick }) {
    const handleStatusChange = async (e) => {
        try {
            await updateJobStatus(job.id, e.target.value);
            onRefresh();
        } catch {
            alert('Failed to update status');
        }
    };

    const handleToggleBookmark = async () => {
        try {
            await toggleBookmark(job.id);
            onRefresh();
        } catch {
            // ignore
        }
    };

    const handleArchive = async () => {
        try {
            await archiveJob(job.id);
            onRefresh();
        } catch {
            // ignore
        }
    };

    const skills = (job.required_skills || '').split(',').map(s => s.trim()).filter(Boolean);
    const companyInitial = job.company ? job.company.charAt(0).toUpperCase() : '?';

    return (
        <div className="job-card">
            <div className="job-card-header">
                <div className="company-box">
                    <div className="company-logo">{companyInitial}</div>
                    <div className="job-info">
                        <h3>{job.role}</h3>
                        <div className="company-name">
                            {job.company} 
                            <span className="verified-badge">✓ Verified</span>
                        </div>
                    </div>
                </div>
                <button className="arrow-btn" title="View Details">↗</button>
            </div>

            <div className="badge-row">
                <span className="pill pill-accent">{job.source || 'Direct'}</span>
                <span className="pill">{job.location || 'Remote'}</span>
            </div>

            <div className="tag-row">
                {skills.slice(0, 4).map((skill, idx) => (
                    <span key={idx} className="tag">{skill}</span>
                ))}
                {skills.length > 4 && <span className="tag">+{skills.length - 4}</span>}
            </div>

            <div className="job-location">
                📍 {job.location || 'India'} • {job.date_added || 'Recently'}
            </div>

            <div className="job-card-footer">
                <div className="salary">
                    {job.stipend && job.stipend !== 'Not disclosed' ? job.stipend : 'Competitive'}
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button 
                        className={`nav-item ${job.is_bookmarked ? 'active' : ''}`} 
                        onClick={handleToggleBookmark}
                        style={{ background: 'none', border: 'none', fontSize: '1.2rem', padding: 0, width: 'auto', height: 'auto' }}
                    >
                        {job.is_bookmarked ? '★' : '☆'}
                    </button>
                    <button className="mail-btn" onClick={() => onMailClick(job.id)}>
                        ✉️ Mail
                    </button>
                    {job.link ? (
                        <a href={job.link} target="_blank" rel="noopener noreferrer" className="apply-btn-card">
                            Apply
                        </a>
                    ) : (
                        <button className="apply-btn-card" disabled>No Link</button>
                    )}
                </div>
            </div>

            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <select className="status-select" value={job.status} onChange={handleStatusChange}>
                    <option value="New">New</option>
                    <option value="High Priority">High Priority</option>
                    <option value="Good Match">Good Match</option>
                    <option value="Stretch">Stretch</option>
                    <option value="Applied">Applied</option>
                    <option value="Interview">Interview</option>
                    <option value="Rejected">Rejected</option>
                    <option value="Accepted">Accepted</option>
                </select>
                <button 
                    onClick={handleArchive} 
                    style={{ background: 'none', border: 'none', color: '#ff4444', fontSize: '0.8rem', cursor: 'pointer' }}
                >
                    Archive
                </button>
            </div>
        </div>
    );
}
