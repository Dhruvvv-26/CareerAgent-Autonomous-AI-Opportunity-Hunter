
export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">J</div>
            <nav className="sidebar-nav">
                <div className="nav-item active" title="Dashboard">🏠</div>
                <div className="nav-item" title="My Applications">📄</div>
                <div className="nav-item" title="Bookmarks">🔖</div>
                <div className="nav-item" title="Messages">💬</div>
            </nav>
            <div className="sidebar-footer">
                <div className="nav-item" title="Settings">⚙️</div>
                <div className="nav-item" title="Logout">🚪</div>
            </div>
        </aside>
    );
}
