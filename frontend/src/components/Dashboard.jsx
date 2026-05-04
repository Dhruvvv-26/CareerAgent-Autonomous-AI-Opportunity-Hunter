import { useState, useEffect, useCallback, useMemo } from 'react';
import { getJobs, runSearch, getEmailPreview, getProfile } from '../api/api';
import AnalyticsPanel from './AnalyticsPanel';
import CategoryTabs from './CategoryTabs';
import FilterBar from './FilterBar';
import JobGrid from './JobTable'; // We'll rename the component internally to Grid
import Pagination from './Pagination';
import EmailPreviewModal from './EmailPreviewModal';

export default function Dashboard() {
    const [jobs, setJobs] = useState([]);
    const [profile, setProfile] = useState(null);
    const [category, setCategory] = useState(null);
    const [filter, setFilter] = useState(null);
    const [search, setSearch] = useState('');
    const [searching, setSearching] = useState(false);
    const [loading, setLoading] = useState(false);
    const [resultMsg, setResultMsg] = useState('');
    const [resultType, setResultType] = useState('');

    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [showBookmarked, setShowBookmarked] = useState(false);

    const [emailPreview, setEmailPreview] = useState(null);
    const [loadingPreview, setLoadingPreview] = useState(false);

    const fetchJobs = useCallback(async () => {
        setLoading(true);
        try {
            const data = await getJobs(
                category,
                page,
                50,
                showBookmarked ? true : null
            );
            setJobs(data.jobs || []);
            if (data.pagination) {
                setTotalPages(data.pagination.total_pages);
                setTotal(data.pagination.total);
            }
        } catch {
            // silent
        } finally {
            setLoading(false);
        }
    }, [category, page, showBookmarked]);

    const fetchProfile = async () => {
        try {
            const data = await getProfile();
            setProfile(data);
        } catch {
            // silent
        }
    };

    useEffect(() => {
        fetchJobs();
        fetchProfile();
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
                setPage(1);
                fetchJobs();
            }
        } catch {
            setResultMsg('Search failed. Check backend.');
            setResultType('error');
        } finally {
            setSearching(false);
        }
    };

    const handleMailClick = async (jobId) => {
        setLoadingPreview(true);
        try {
            const data = await getEmailPreview(jobId);
            if (data.error) {
                setResultMsg(data.error);
                setResultType('error');
            } else {
                setEmailPreview(data);
            }
        } catch {
            setResultMsg('Failed to load email preview.');
            setResultType('error');
        } finally {
            setLoadingPreview(false);
        }
    };

    const counts = useMemo(() => ({
        total: total,
        'High Priority': jobs.filter((j) => j.status === 'High Priority').length,
        'Good Match': jobs.filter((j) => j.status === 'Good Match').length,
        'Stretch': jobs.filter((j) => j.status === 'Stretch').length,
    }), [jobs, total]);

    const filteredJobs = useMemo(() => {
        if (!search.trim()) return jobs;
        const q = search.toLowerCase();
        return jobs.filter((j) => 
            j.company.toLowerCase().includes(q) || j.role.toLowerCase().includes(q)
        );
    }, [jobs, search]);

    return (
        <div className="dashboard">
            <header className="top-header">
                <h1 className="welcome-text">
                    Welcome back, {profile?.full_name || 'Hunter'}!
                </h1>
                <p className="sub-welcome">Here's your overview for today</p>
            </header>

            <AnalyticsPanel />

            <div className="controls-row">
                <h2 className="section-title">Latest Job Openings</h2>
                <div className="action-btns">
                    <button 
                        className={`btn btn-primary ${showBookmarked ? 'active' : ''}`}
                        onClick={() => { setShowBookmarked(!showBookmarked); setPage(1); }}
                    >
                        {showBookmarked ? '★ Saved' : '☆ All'}
                    </button>
                    <button className="btn btn-accent" onClick={handleSearch} disabled={searching}>
                        {searching ? 'Searching...' : 'Run Search'}
                    </button>
                </div>
            </div>

            {resultMsg && <div className={`result-banner ${resultType}`}>{resultMsg}</div>}

            <CategoryTabs active={category} onChange={(v) => {setCategory(v); setPage(1);}} counts={counts} />
            
            <FilterBar search={search} onSearchChange={setSearch} />

            {loading ? (
                <div className="spinner center"></div>
            ) : (
                <>
                    <JobGrid jobs={filteredJobs} onRefresh={fetchJobs} onMailClick={handleMailClick} />
                    <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
                </>
            )}

            {emailPreview && (
                <EmailPreviewModal
                    preview={emailPreview}
                    onClose={() => setEmailPreview(null)}
                    onSent={fetchJobs}
                />
            )}
        </div>
    );
}
