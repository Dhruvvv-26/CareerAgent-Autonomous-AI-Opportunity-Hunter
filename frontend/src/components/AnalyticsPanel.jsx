import { useState, useEffect } from 'react';
import { getJobStats } from '../api/api';
import {
    PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
    XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';

const COLORS = ['#bbf246', '#181818', '#7d7d7d', '#b5b5b5', '#ef4444'];
const CATEGORY_COLORS = { 'High Priority': '#22c55e', 'Good Match': '#bbf246', 'Stretch': '#facc15' };

export default function AnalyticsPanel() {
    const [stats, setStats] = useState(null);
    const [showCharts, setShowCharts] = useState(false);
    const [loading, setLoading] = useState(false);

    const fetchStats = async () => {
        setLoading(true);
        try {
            const data = await getJobStats();
            setStats(data);
        } catch {
            // ignore
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    if (loading || !stats) {
        return (
            <div className="stats-row">
                <div className="stat-card"><div className="spinner"></div></div>
                <div className="stat-card"><div className="spinner"></div></div>
                <div className="stat-card"><div className="spinner"></div></div>
            </div>
        );
    }

    return (
        <div className="analytics-section">
            <div className="stats-row">
                <div className="stat-card">
                    <div className="stat-value">{stats.total}</div>
                    <div className="stat-info">
                        <h4>Total Opportunities</h4>
                        <p>Found across all sources</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.emailed || 0}</div>
                    <div className="stat-info">
                        <h4>Applications</h4>
                        <p>Emails sent to recruiters</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.bookmarked}</div>
                    <div className="stat-info">
                        <h4>Saved Jobs</h4>
                        <p>Bookmarked for later</p>
                    </div>
                </div>
            </div>

            <div className="charts-toggle-container">
                <button 
                    className="btn btn-primary" 
                    onClick={() => setShowCharts(!showCharts)}
                    style={{ marginBottom: '24px' }}
                >
                    {showCharts ? 'Hide Market Insights' : 'Show Market Insights'}
                </button>
            </div>

            {showCharts && (
                <div className="charts-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '40px' }}>
                    <div className="job-card">
                        <h4 style={{ marginBottom: '16px' }}>Jobs by Source</h4>
                        <ResponsiveContainer width="100%" height={200}>
                            <PieChart>
                                <Pie
                                    data={Object.entries(stats.by_source || {}).map(([name, value]) => ({ name, value }))}
                                    cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value"
                                >
                                    {Object.entries(stats.by_source || {}).map((_, i) => (
                                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="job-card">
                        <h4 style={{ marginBottom: '16px' }}>Daily Trend</h4>
                        <ResponsiveContainer width="100%" height={200}>
                            <LineChart data={(stats.daily_trend || []).map(d => ({ date: d.date.substring(5), count: d.count }))}>
                                <XAxis dataKey="date" hide />
                                <YAxis hide />
                                <Tooltip />
                                <Line type="monotone" dataKey="count" stroke="#bbf246" strokeWidth={3} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
}
