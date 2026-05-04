export default function Pagination({ page, totalPages, onPageChange }) {
    if (totalPages <= 1) return null;

    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
        pages.push(i);
    }

    return (
        <div className="pagination">
            <button
                className="page-btn"
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
            >
                ← Prev
            </button>

            {start > 1 && (
                <>
                    <button className="page-btn" onClick={() => onPageChange(1)}>1</button>
                    {start > 2 && <span className="page-ellipsis">…</span>}
                </>
            )}

            {pages.map((p) => (
                <button
                    key={p}
                    className={`page-btn ${p === page ? 'active' : ''}`}
                    onClick={() => onPageChange(p)}
                >
                    {p}
                </button>
            ))}

            {end < totalPages && (
                <>
                    {end < totalPages - 1 && <span className="page-ellipsis">…</span>}
                    <button className="page-btn" onClick={() => onPageChange(totalPages)}>
                        {totalPages}
                    </button>
                </>
            )}

            <button
                className="page-btn"
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
            >
                Next →
            </button>
        </div>
    );
}
