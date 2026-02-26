import { useState, useEffect, useCallback, useMemo } from 'react';
import { getJobs, runSearch } from '../api/api';
import CategoryTabs from './CategoryTabs';
import FilterBar from './FilterBar';
import JobTable from './JobTable';

export default function Dashboard() {
    const [jobs, setJobs] = useState([]);
    const [category, setCategory] = useState(null);
    const [filter, setFilter] = useState(null);
    const [search, setSearch] = useState('');
    const [searching, setSearching] = useState(false);
    const [loading, setLoading] = useState(false);
    const [resultMsg, setResultMsg] = useState('');
    const [resultType, setResultType] = useState('');

    const fetchJobs = useCallback(async () => {
        setLoading(true);
        try {
            const data = await getJobs(category);
            setJobs(data);
        } catch {
            // silent
        } finally {
            setLoading(false);
        }
    }, [category]);

    useEffect(() => {
        fetchJobs();
    }, [fetchJobs]);

    const handleSearch = async () => {
        setSearching(true);
        setResultMsg('');
        try {
            const data = await runSearch();
            if (data.error) {
                setResultMsg(data.error);
                setResultType('error');
            } else {
                setResultMsg(data.message);
                setResultType('success');
                fetchJobs();
            }
        } catch {
            setResultMsg('Search failed. Make sure backend is running and resume is uploaded.');
            setResultType('error');
        } finally {
            setSearching(false);
        }
    };

    const handleCategoryChange = (value) => {
        setCategory(value);
        setFilter(value);
    };

    const handleFilterChange = (value) => {
        setFilter(value);
        setCategory(value);
    };

    const counts = useMemo(() => {
        const all = jobs;
        return {
            total: all.length,
            'High Priority': all.filter((j) => j.status === 'High Priority').length,
            'Good Match': all.filter((j) => j.status === 'Good Match').length,
            'Stretch': all.filter((j) => j.status === 'Stretch').length,
        };
    }, [jobs]);

    const filteredJobs = useMemo(() => {
        if (!search.trim()) return jobs;
        const q = search.toLowerCase();
        return jobs.filter(
            (j) =>
                j.company.toLowerCase().includes(q) ||
                j.role.toLowerCase().includes(q)
        );
    }, [jobs, search]);

    return (
        <div className="section">
            <div className="card">
                <div className="dashboard-header">
                    <h2 className="dashboard-title">Opportunity Dashboard</h2>
                    <button
                        className="search-btn"
                        onClick={handleSearch}
                        disabled={searching}
                    >
                        {searching ? (
                            <><span className="spinner"></span> Searching…</>
                        ) : (
                            'Run Search'
                        )}
                    </button>
                </div>

                {resultMsg && (
                    <div className={`result-banner ${resultType}`}>
                        {resultMsg}
                    </div>
                )}

                <CategoryTabs
                    active={category}
                    onChange={handleCategoryChange}
                    counts={counts}
                />

                <FilterBar
                    filter={filter}
                    onFilterChange={handleFilterChange}
                    search={search}
                    onSearchChange={setSearch}
                />

                {loading ? (
                    <div className="spinner center"></div>
                ) : (
                    <JobTable jobs={filteredJobs} onRefresh={fetchJobs} />
                )}
            </div>
        </div>
    );
}
