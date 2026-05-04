
export default function CategoryTabs({ active, onChange, counts }) {
    const tabs = [
        { id: null, label: 'All Openings', count: counts.total },
        { id: 'High Priority', label: 'High Priority', count: counts['High Priority'] },
        { id: 'Good Match', label: 'Good Match', count: counts['Good Match'] },
        { id: 'Stretch', label: 'Stretch', count: counts['Stretch'] },
    ];

    return (
        <div className="category-tabs">
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    className={`tab ${active === tab.id ? 'active' : ''}`}
                    onClick={() => onChange(tab.id)}
                >
                    {tab.label} {tab.count > 0 && <span style={{ opacity: 0.6, fontSize: '0.7rem', marginLeft: '4px' }}>({tab.count})</span>}
                </button>
            ))}
        </div>
    );
}
