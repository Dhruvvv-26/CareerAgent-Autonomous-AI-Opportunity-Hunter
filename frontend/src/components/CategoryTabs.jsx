export default function CategoryTabs({ active, onChange, counts }) {
    const tabs = [
        { label: 'All', value: null },
        { label: 'High Priority', value: 'High Priority' },
        { label: 'Good Match', value: 'Good Match' },
        { label: 'Stretch', value: 'Stretch' },
    ];

    return (
        <div className="category-tabs">
            {tabs.map((tab) => (
                <button
                    key={tab.label}
                    className={`category-tab ${active === tab.value ? 'active' : ''}`}
                    onClick={() => onChange(tab.value)}
                >
                    {tab.label}
                    <span className="tab-count">
                        {tab.value === null ? counts.total : (counts[tab.value] || 0)}
                    </span>
                </button>
            ))}
        </div>
    );
}
