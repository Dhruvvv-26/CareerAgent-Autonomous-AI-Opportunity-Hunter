import JobRow from './JobRow';
import EmptyState from './EmptyState';

export default function JobTable({ jobs, onRefresh }) {
    if (jobs.length === 0) {
        return <EmptyState />;
    }

    return (
        <div className="table-wrap">
            <table className="job-table">
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Role</th>
                        <th>Location</th>
                        <th>Stipend</th>
                        <th>Confidence</th>
                        <th>Reputation</th>
                        <th>Status</th>
                        <th>Update</th>
                        <th>Apply</th>
                    </tr>
                </thead>
                <tbody>
                    {jobs.map((job) => (
                        <JobRow key={job.id} job={job} onRefresh={onRefresh} />
                    ))}
                </tbody>
            </table>
        </div>
    );
}
