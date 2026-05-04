
import JobCard from './JobRow'; // We'll update JobRow to be a Card
import EmptyState from './EmptyState';

export default function JobGrid({ jobs, onRefresh, onMailClick }) {
    if (jobs.length === 0) {
        return <EmptyState />;
    }

    return (
        <div className="job-grid">
            {jobs.map((job) => (
                <JobCard
                    key={job.id}
                    job={job}
                    onRefresh={onRefresh}
                    onMailClick={onMailClick}
                />
            ))}
        </div>
    );
}
