
export default function FilterBar({ search, onSearchChange }) {
    return (
        <div className="filter-bar">
            <input
                type="text"
                className="search-input"
                placeholder="Search by company or role..."
                value={search}
                onChange={(e) => onSearchChange(e.target.value)}
            />
        </div>
    );
}
