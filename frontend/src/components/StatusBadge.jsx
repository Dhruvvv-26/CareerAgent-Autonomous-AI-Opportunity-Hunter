export default function StatusBadge({ status }) {
    const classMap = {
        'High Priority': 'status-high-priority',
        'Good Match': 'status-good-match',
        'Stretch': 'status-stretch',
        'Applied': 'status-applied',
        'Interview': 'status-interview',
        'Rejected': 'status-rejected',
        'Accepted': 'status-accepted',
        'Emailed': 'status-emailed',
        'New': 'status-not-applied',
        'Not Applied': 'status-not-applied',
    };

    return (
        <span className={`status-badge ${classMap[status] || 'status-not-applied'}`}>
            {status}
        </span>
    );
}
