export default function FilterBar({ filter, onFilterChange, search, onSearchChange }) {
    return (
        <div className="filter-bar">
            <div className="filter-bar-left">
                <select
                    className="filter-select"
                    value={filter || ''}
                    onChange={(e) => onFilterChange(e.target.value || null)}
                >
                    <option value="">All Categories</option>
                    <option value="High Priority">High Priority</option>
                    <option value="Good Match">Good Match</option>
                    <option value="Stretch">Stretch</option>
                </select>
            </div>
            <input
                className="filter-search"
                type="text"
                placeholder="Search by company or role"
                value={search}
                onChange={(e) => onSearchChange(e.target.value)}
            />
        </div>
    );
}
