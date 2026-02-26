export default function EmptyState() {
    return (
        <div className="empty-state">
            <span className="empty-icon">📭</span>
            <p className="empty-title">No opportunities found yet.</p>
            <p className="empty-sub">Run search to fetch matching opportunities.</p>
        </div>
    );
}
