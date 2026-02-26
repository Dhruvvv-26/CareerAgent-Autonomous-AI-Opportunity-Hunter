import StatusBadge from './StatusBadge';
import { updateJobStatus } from '../api/api';

const STATUS_OPTIONS = ['Not Applied', 'Applied', 'Interview', 'Rejected', 'Accepted'];

export default function JobRow({ job, onRefresh }) {
    const handleStatusChange = async (e) => {
        const newStatus = e.target.value;
        if (!newStatus) return;
        try {
            await updateJobStatus(job.id, newStatus);
            onRefresh();
        } catch {
            // silent fail
        }
    };

    const getConfidenceClass = (score) => {
        if (score >= 80) return 'confidence-green';
        if (score >= 60) return 'confidence-blue';
        return 'confidence-yellow';
    };

    return (
        <tr>
            <td data-label="Company" className="cell-company">{job.company}</td>
            <td data-label="Role" className="cell-role">{job.role}</td>
            <td data-label="Location">{job.location}</td>
            <td data-label="Stipend">{job.stipend}</td>
            <td data-label="Confidence">
                <span className={`confidence-badge ${getConfidenceClass(job.confidence_score)}`}>
                    {job.confidence_score.toFixed(0)}%
                </span>
            </td>
            <td data-label="Reputation">{job.reputation_score.toFixed(0)}</td>
            <td data-label="Status">
                <StatusBadge status={job.status} />
            </td>
            <td data-label="Update">
                <select
                    className="status-select"
                    defaultValue=""
                    onChange={handleStatusChange}
                >
                    <option value="" disabled>Change…</option>
                    {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>
            </td>
            <td data-label="Apply">
                {job.link ? (
                    <a
                        href={job.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="apply-btn"
                    >
                        Apply
                    </a>
                ) : (
                    <span className="no-link-text">—</span>
                )}
            </td>
        </tr>
    );
}
